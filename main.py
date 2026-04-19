import aiohttp
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig
from astrbot.api.provider import ProviderRequest

from .adapters import get_adapter

@register("astrbot_plugin_external_knowledgebase", "Developer", "知识库自动检索插件 (支持 Dify/RAGFlow/Flowise)", "1.2.0")
class KnowledgeBasePlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

    async def _get_history_str(self, event: AstrMessageEvent) -> str:
        try:
            conv_mgr = self.context.conversation_manager
            curr_cid = await conv_mgr.get_curr_conversation_id(event.unified_msg_origin)
            if not curr_cid:
                return ""
            conversation = await conv_mgr.get_conversation(event.unified_msg_origin, curr_cid)
            if not conversation or not conversation.history:
                return ""
            
            # Take the last 6 relevant messages
            messages = []
            for msg in conversation.history[-6:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                text = ""
                if isinstance(content, list):
                    # parse content list (like [TextPart(text=...)])
                    for part in content:
                        if isinstance(part, dict) and 'text' in part:
                            text += part['text']
                elif isinstance(content, str):
                    text = content
                else:
                    text = str(content)
                
                if text:
                    messages.append(f"{role}: {text}")
            return "\n".join(messages)
        except Exception as e:
            logger.debug(f"[知识库插件] 获取历史对话发生异常: {e}")
            return ""

    async def _llm_generate(self, event: AstrMessageEvent, prompt: str) -> str:
        # Check custom LLM provider
        provider_id = self.config.get("custom_llm_provider", "").strip()
        try:
            if not provider_id:
                provider_id = await self.context.get_current_chat_provider_id(umo=event.unified_msg_origin)
                
            llm_resp = await self.context.llm_generate(
                chat_provider_id=provider_id,
                prompt=prompt
            )
            return llm_resp.completion_text
        except Exception as e:
            logger.error(f"[知识库插件] 决策/重写 LLM 网络请求失败: {e}")
            return ""

    @filter.on_llm_request()
    async def intercept_llm_request(self, event: AstrMessageEvent, req: ProviderRequest):
        # 1. 检查插件开关
        if not self.config.get("enable", True):
            return

        user_msg = event.message_str.strip()
        if not user_msg:
            return

        # 获取历史对话用于 Rewrite 和 L3 判意图
        history_str = await self._get_history_str(event)
        
        # 2. Query Rewrite
        enable_rewrite = self.config.get("enable_query_rewrite", False)
        if enable_rewrite and history_str:
            rewrite_prompt_tmpl = self.config.get("rewrite_prompt", "")
            if rewrite_prompt_tmpl:
                prompt = rewrite_prompt_tmpl.replace("{history}", history_str).replace("{user_msg}", user_msg)
                rewritten = await self._llm_generate(event, prompt)
                if rewritten:
                    rewritten_clean = rewritten.strip()
                    # Just in case model returns the original prompt or empty, we ignore it if it's too weird
                    if rewritten_clean and len(rewritten_clean) < 500:
                        user_msg = rewritten_clean
                        logger.info(f"[知识库插件] Query 被重写为: {user_msg}")

        # 3. Decision Layer
        mode = self.config.get("decision_mode", "L1")
        should_query = False
        
        if mode == "L1":
            should_query = True
        elif mode == "L2":
            keywords_str = self.config.get("keywords", "请问,解释,文档,是什么,介绍,怎么,如何,帮我,可以,帮")
            keywords = [kw.strip() for kw in keywords_str.split(',') if kw.strip()]
            should_query = any(kw in user_msg for kw in keywords)
        elif mode == "L3":
            l3_prompt_tmpl = self.config.get("l3_prompt", "")
            if l3_prompt_tmpl:
                prompt = l3_prompt_tmpl.replace("{history}", history_str).replace("{user_msg}", user_msg)
                decision = await self._llm_generate(event, prompt)
                if decision:
                    decision_clean = decision.strip().upper()
                    if "YES" in decision_clean:
                        should_query = True

        if not should_query:
            logger.debug("[知识库插件] 决策树判断无需查询，跳出。")
            return

        # 4. 初始化对应的适配器
        backend_type = self.config.get("backend_type", "dify").strip()
        api_endpoint = self.config.get("api_endpoint", "https://api.dify.ai/v1").strip()
        api_key = self.config.get("api_key", "").strip()
        dataset_id = self.config.get("dataset_id", "").strip()
        top_k = self.config.get("top_k", 3)
        score_threshold = self.config.get("score_threshold", 0.5)

        adapter = get_adapter(backend_type, api_endpoint, api_key, dataset_id, top_k, score_threshold)

        # 5. 调用对应的后端 API 获取知识库分段
        try:
            contexts = await adapter.retrieve(user_msg)
            
            if not contexts:
                logger.info(f"[{backend_type}] 知识库: 未检索到关于 '{user_msg}' 的匹配分段。")
                return
                
            # 6. 将查找到的记录组装成文本块，修改系统提示词
            context_str = "\n\n".join([f"---片段 {i+1}---\n{c}" for i, c in enumerate(contexts)])
            knowledge_prompt_template = self.config.get(
                "knowledge_prompt_template", 
                "\n\n请参考以下背景知识来回答用户的问题（如果背景知识与问题无关可以忽略）：\n{context_str}\n\n请结合以上背景知识回答问题。\n"
            )
            # Add context safely
            knowledge_prompt = knowledge_prompt_template.replace("{context_str}", context_str)
            
            # 将知识库内容拼接到请求 LLM 的 system_prompt
            req.system_prompt += knowledge_prompt
            logger.info(f"[{backend_type}] 知识库插件: 成功为本次对话注入 {len(contexts)} 条知识库片段作为背景知识。")
            
        except aiohttp.ClientError as e:
            logger.error(f"[{backend_type}] 知识库检索网络异常: {e}")
        except Exception as e:
            logger.error(f"[{backend_type}] 知识库检索异常: {e}")
