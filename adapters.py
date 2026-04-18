import aiohttp
import logging
from typing import List

logger = logging.getLogger("astrbot")

class BaseKnowledgeBaseAdapter:
    def __init__(self, api_endpoint: str, api_key: str, dataset_id: str, top_k: int, score_threshold: float):
        self.api_endpoint = api_endpoint.rstrip('/')
        self.api_key = api_key
        self.dataset_id = dataset_id
        self.top_k = top_k
        self.score_threshold = score_threshold

    async def retrieve(self, query: str) -> List[str]:
        raise NotImplementedError

class DifyAdapter(BaseKnowledgeBaseAdapter):
    async def retrieve(self, query: str) -> List[str]:
        if not self.api_key or not self.dataset_id:
            logger.debug("Dify API Key 或 Dataset ID 未配置，跳过知识库检索")
            return []

        url = f"{self.api_endpoint}/datasets/{self.dataset_id}/retrieve"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "retrieval_model": {
                "search_method": "semantic_search",
                "reranking_enable": False,
                "top_k": self.top_k,
                "score_threshold": self.score_threshold,
                "score_threshold_enabled": True
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=15) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise Exception(f"HTTP {resp.status} - {error_text}")
                data = await resp.json()
                
        records = data.get("records", [])
        contexts = []
        for record in records:
            segment = record.get("segment", {})
            content = segment.get("content", "").strip()
            if content:
                contexts.append(content)
                
        return contexts

class RAGFlowAdapter(BaseKnowledgeBaseAdapter):
    async def retrieve(self, query: str) -> List[str]:
        if not self.api_key or not self.dataset_id:
            logger.debug("RAGFlow API Key 或 Dataset ID 未配置，跳过知识库检索")
            return []

        url = f"{self.api_endpoint}/api/v1/retrieval"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "question": query,
            "dataset_ids": [d.strip() for d in self.dataset_id.split(",") if d.strip()],
            "top_k": self.top_k,
            "similarity_threshold": self.score_threshold
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=15) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise Exception(f"HTTP {resp.status} - {error_text}")
                data = await resp.json()
                
        chunks = data.get("data", {}).get("chunks", [])
        contexts = []
        for chunk in chunks:
            content = chunk.get("content", "").strip()
            if content:
                contexts.append(content)
                
        return contexts

class FlowiseAdapter(BaseKnowledgeBaseAdapter):
    async def retrieve(self, query: str) -> List[str]:
        if not self.dataset_id:
            logger.debug("Flowise Store ID (Dataset ID) 未配置，跳过知识库检索")
            return []

        url = f"{self.api_endpoint}/document-store/vectorstore/query"
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        payload = {
            "storeId": self.dataset_id,
            "query": query
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=15) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise Exception(f"HTTP {resp.status} - {error_text}")
                data = await resp.json()
                
        docs = data.get("docs", [])
        contexts = []
        for doc in docs[:self.top_k]:  # Flowise query often doesn't strictly adhere to top_k locally inside payload based on some versions
            content = doc.get("pageContent", "").strip()
            if content:
                contexts.append(content)
                
        return contexts

def get_adapter(backend_type: str, api_endpoint: str, api_key: str, dataset_id: str, top_k: int, score_threshold: float) -> BaseKnowledgeBaseAdapter:
    backend_type = backend_type.lower()
    if backend_type == "ragflow":
        return RAGFlowAdapter(api_endpoint, api_key, dataset_id, top_k, score_threshold)
    elif backend_type == "flowise":
        return FlowiseAdapter(api_endpoint, api_key, dataset_id, top_k, score_threshold)
    else:
        return DifyAdapter(api_endpoint, api_key, dataset_id, top_k, score_threshold)
