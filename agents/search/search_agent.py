from typing import Dict, List, Optional
import os
import requests
from fastapi import FastAPI, HTTPException
from ..base.base_agent import BaseAgent, Message
import json
from dotenv import load_dotenv

load_dotenv()

class SearchAgent(BaseAgent):
    def __init__(self, discovery_service_url: str):
        super().__init__(
            agent_type="search",
            capabilities=["web_search"],
            discovery_service_url=discovery_service_url
        )
        self.api_key = os.getenv("SERPER_API_KEY")
        if not self.api_key:
            raise ValueError("SERPER_API_KEY environment variable is required")
        
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
        if message.message_type == "search_request":
            result = await self.search(message.content)
            response = Message(
                sender_id=self.agent_id,
                content=json.dumps(result),
                message_type="search_response"
            )
            return response
        return {"status": "error", "message": "Unsupported message type"}

    async def process_query(self, query: str) -> str:
        """处理搜索查询"""
        try:
            results = await self.search(query)
            return json.dumps(results, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"搜索失败: {str(e)}"

    async def search(self, query: str) -> Dict:
        """使用Serper API执行搜索"""
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query,
            "gl": "cn",  # 地理位置代码，这里设置为中国
            "hl": "zh-cn"  # 语言设置为中文
        }
        
        try:
            response = requests.post(
                "https://google.serper.dev/search",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Search failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

# 启动服务示例
if __name__ == "__main__":
    import uvicorn
    import asyncio
    
    async def start_agent():
        agent = SearchAgent(discovery_service_url="http://localhost:8000")
        await agent.start(host="localhost", port=8001)
        return agent

    agent = asyncio.run(start_agent())
    uvicorn.run(agent.app, host="localhost", port=8001)
