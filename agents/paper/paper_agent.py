from typing import Dict, List, Optional
import arxiv
from fastapi import FastAPI, HTTPException
from ..base.base_agent import BaseAgent, Message
import json
import asyncio

class PaperAgent(BaseAgent):
    def __init__(self, discovery_service_url: str):
        super().__init__(
            agent_type="paper",
            capabilities=["paper_search"],
            discovery_service_url=discovery_service_url
        )
        self.client = arxiv.Client()
        self.app = FastAPI()
        self.setup_routes()

    def setup_routes(self):
        @self.app.post("/message")
        async def handle_message(message: Message):
            return await self.handle_message(message)

        @self.app.post("/query")
        async def handle_query(query: Dict[str, str]):
            return await self.process_query(query["text"])

    async def handle_message(self, message: Message):
        """处理接收到的消息"""
        if message.message_type == "paper_search_request":
            result = await self.search_papers(message.content)
            response = Message(
                sender_id=self.agent_id,
                content=json.dumps(result, ensure_ascii=False),
                message_type="paper_search_response"
            )
            return response
        return {"status": "error", "message": "Unsupported message type"}

    async def process_query(self, query: str) -> str:
        """处理论文搜索查询"""
        try:
            results = await self.search_papers(query)
            return json.dumps(results, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"论文搜索失败: {str(e)}"

    async def search_papers(self, query: str, max_results: int = 5) -> List[Dict]:
        """搜索arXiv论文"""
        try:
            # 使用asyncio.to_thread来避免阻塞
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )

            results = []
            async for result in self._async_search(search):
                paper_info = {
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "summary": result.summary,
                    "published": result.published.strftime("%Y-%m-%d"),
                    "pdf_url": result.pdf_url,
                    "arxiv_url": result.entry_id,
                    "categories": result.categories
                }
                results.append(paper_info)

            return results
        except Exception as e:
            print(f"Paper search failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _async_search(self, search):
        """异步迭代搜索结果"""
        for result in self.client.results(search):
            yield result
            # 添加小延迟以避免过快请求
            await asyncio.sleep(0.1)

# 启动服务示例
if __name__ == "__main__":
    import uvicorn
    import asyncio
    
    async def start_agent():
        agent = PaperAgent(discovery_service_url="http://localhost:8000")
        await agent.start(host="localhost", port=8002)
        return agent

    agent = asyncio.run(start_agent())
    uvicorn.run(agent.app, host="localhost", port=8002)
