import aiohttp
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig
from astrbot.api.provider import ProviderRequest

@register("astrbot_plugin_dify_knowledgebase", "Developer", "Dify 知识库自动检索插件", "1.0.0")
class DifyKnowledgeBasePlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

    @filter.on_llm_request()
    async def intercept_llm_request(self, event: AstrMessageEvent, req: ProviderRequest):
        # 1. 检查插件开关
        if not self.config.get("enable", True):
            return

        api_endpoint = self.config.get("api_endpoint", "https://api.dify.ai/v1").rstrip('/')
        api_key = self.config.get("api_key", "").strip()
        dataset_id = self.config.get("dataset_id", "").strip()
        top_k = self.config.get("top_k", 3)
        score_threshold = self.config.get("score_threshold", 0.5)

        # 2. 检查必要配置
        if not api_key or not dataset_id:
            logger.debug("Dify API Key 或 Dataset ID 未配置，跳过知识库检索")
            return
            
        # 3. 提取用户最新的问题
        user_msg = event.message_str.strip()
        if not user_msg:
            return

        # 4. 调用 Dify Retrieve API
        url = f"{api_endpoint}/datasets/{dataset_id}/retrieve"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建请求体: 这里仅传入最基本的 query, 将检索阈值传入 retrieval_model
        payload = {
            "query": user_msg,
            "retrieval_model": {
                "top_k": top_k,
                "score_threshold": score_threshold,
                "score_threshold_enabled": True
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=15) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"Dify 检索请求失败: HTTP {resp.status} - {error_text}")
                        return
                    data = await resp.json()
                    
            records = data.get("records", [])
            if not records:
                logger.info(f"Dify 知识库: 未检索到关于 '{user_msg}' 的匹配分段。")
                return
                
            # 5. 提取匹配的文本特征段 (Chunks)
            contexts = []
            for record in records:
                segment = record.get("segment", {})
                content = segment.get("content", "").strip()
                if content:
                    contexts.append(content)
                    
            if not contexts:
                return
                
            # 6. 将查找到的记录组装成文本块，修改系统提示词
            context_str = "\n\n".join([f"---片段 {i+1}---\n{c}" for i, c in enumerate(contexts)])
            knowledge_prompt = f"\n\n请参考以下背景知识来回答用户的问题（如果背景知识与问题无关可以忽略）：\n{context_str}\n\n请结合以上背景知识回答问题。\n"
            
            # 将知识库内容拼接到请求 LLM 的 system_prompt
            req.system_prompt += knowledge_prompt
            logger.info(f"Dify 知识库插件: 成功为本次对话注入 {len(contexts)} 条知识库片段作为背景知识。")
            
        except aiohttp.ClientError as e:
            logger.error(f"Dify 知识库检索网络异常: {e}")
        except Exception as e:
            logger.error(f"Dify 知识库检索发生未知错误: {e}")
