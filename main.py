import asyncio
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
import os

from core.discovery.discovery_service import DiscoveryService
from agents.search.search_agent import SearchAgent
from agents.paper.paper_agent import PaperAgent

# 加载环境变量
load_dotenv()

# 检查必要的环境变量
required_env_vars = {
    "SERPER_API_KEY": "Serper API密钥用于搜索功能"
}

for var, description in required_env_vars.items():
    if not os.getenv(var):
        raise ValueError(f"缺少环境变量 {var}：{description}")

async def start_discovery_service(host: str = "localhost", port: int = 8000):
    """启动发现服务"""
    app = FastAPI(title="Discovery Service")
    discovery_service = DiscoveryService()
    
    # 注册路由
    app.post("/register")(discovery_service.register_agent)
    app.delete("/unregister/{agent_id}")(discovery_service.unregister_agent)
    app.put("/heartbeat/{agent_id}")(discovery_service.update_heartbeat)
    app.get("/agents")(discovery_service.list_agents)
    app.get("/agent/{agent_id}")(discovery_service.get_agent_info)
    
    config = uvicorn.Config(app, host=host, port=port)
    server = uvicorn.Server(config)
    await server.serve()

async def start_search_agent(host: str = "localhost", port: int = 8001):
    """启动搜索智能体"""
    agent = SearchAgent(discovery_service_url="http://localhost:8000")
    await agent.start(host=host, port=port)
    config = uvicorn.Config(agent.app, host=host, port=port)
    server = uvicorn.Server(config)
    await server.serve()

async def start_paper_agent(host: str = "localhost", port: int = 8002):
    """启动论文智能体"""
    agent = PaperAgent(discovery_service_url="http://localhost:8000")
    await agent.start(host=host, port=port)
    config = uvicorn.Config(agent.app, host=host, port=port)
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    """启动所有服务"""
    # 创建任务
    discovery_task = asyncio.create_task(start_discovery_service())
    search_task = asyncio.create_task(start_search_agent())
    paper_task = asyncio.create_task(start_paper_agent())
    
    # 等待所有任务完成
    await asyncio.gather(
        discovery_task,
        search_task,
        paper_task
    )

if __name__ == "__main__":
    print("启动多智能体系统...")
    print("发现服务运行在: http://localhost:8000")
    print("搜索智能体运行在: http://localhost:8001")
    print("论文智能体运行在: http://localhost:8002")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n系统正在关闭...")
    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        print("系统已关闭")
