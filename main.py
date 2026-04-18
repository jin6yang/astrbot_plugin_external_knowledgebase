import aiohttp
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig
from astrbot.api.provider import ProviderRequest

from .adapters import get_adapter

@register("astrbot_plugin_dify_knowledgebase", "Developer", "知识库自动检索插件 (支持 Dify/RAGFlow/Flowise)", "1.1.0")
class KnowledgeBasePlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

    @filter.on_llm_request()
    async def intercept_llm_request(self, event: AstrMessageEvent, req: ProviderRequest):
        # 1. 检查插件开关
        if not self.config.get("enable", True):
            return

        backend_type = self.config.get("backend_type", "dify").strip()
        api_endpoint = self.config.get("api_endpoint", "https://api.dify.ai/v1").strip()
        api_key = self.config.get("api_key", "").strip()
        dataset_id = self.config.get("dataset_id", "").strip()
        top_k = self.config.get("top_k", 3)
        score_threshold = self.config.get("score_threshold", 0.5)

        # 2. 提取用户最新的问题
        user_msg = event.message_str.strip()
        if not user_msg:
            return

        # 3. 初始化对应的适配器
        adapter = get_adapter(backend_type, api_endpoint, api_key, dataset_id, top_k, score_threshold)

        # 4. 调用对应的后端 API 获取知识库分段
        try:
            contexts = await adapter.retrieve(user_msg)
            
            if not contexts:
                logger.info(f"[{backend_type}] 知识库: 未检索到关于 '{user_msg}' 的匹配分段。")
                return
                
            # 5. 将查找到的记录组装成文本块，修改系统提示词
            context_str = "\n\n".join([f"---片段 {i+1}---\n{c}" for i, c in enumerate(contexts)])
            knowledge_prompt = f"\n\n请参考以下背景知识来回答用户的问题（如果背景知识与问题无关可以忽略）：\n{context_str}\n\n请结合以上背景知识回答问题。\n"
            
            # 6. 将知识库内容拼接到请求 LLM 的 system_prompt
            req.system_prompt += knowledge_prompt
            logger.info(f"[{backend_type}] 知识库插件: 成功为本次对话注入 {len(contexts)} 条知识库片段作为背景知识。")
            
        except aiohttp.ClientError as e:
            logger.error(f"[{backend_type}] 知识库检索网络异常: {e}")
        except Exception as e:
            logger.error(f"[{backend_type}] 知识库检索异常: {e}")
