from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import time

class AgentInfo(BaseModel):
    agent_id: str
    agent_type: str
    capabilities: List[str]
    endpoint: str
    last_heartbeat: float

class DiscoveryService:
    def __init__(self):
        self.agents: Dict[str, AgentInfo] = {}
        self.heartbeat_timeout = 30  # 30秒超时

    def register_agent(self, agent_info: AgentInfo) -> bool:
        """注册新的智能体"""
        agent_info.last_heartbeat = time.time()
        self.agents[agent_info.agent_id] = agent_info
        return True

    def unregister_agent(self, agent_id: str) -> bool:
        """注销智能体"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            return True
        return False

    def update_heartbeat(self, agent_id: str) -> bool:
        """更新智能体心跳"""
        if agent_id in self.agents:
            self.agents[agent_id].last_heartbeat = time.time()
            return True
        return False

    def get_agent_info(self, agent_id: str) -> Optional[AgentInfo]:
        """获取智能体信息"""
        return self.agents.get(agent_id)

    def list_agents(self, agent_type: Optional[str] = None) -> List[AgentInfo]:
        """列出所有活跃的智能体"""
        current_time = time.time()
        active_agents = []
        
        for agent in self.agents.values():
            if current_time - agent.last_heartbeat <= self.heartbeat_timeout:
                if agent_type is None or agent.agent_type == agent_type:
                    active_agents.append(agent)
                    
        return active_agents

    def cleanup_inactive_agents(self):
        """清理不活跃的智能体"""
        current_time = time.time()
        inactive_agents = [
            agent_id for agent_id, agent in self.agents.items()
            if current_time - agent.last_heartbeat > self.heartbeat_timeout
        ]
        
        for agent_id in inactive_agents:
            del self.agents[agent_id]

# FastAPI应用实例
app = FastAPI(title="Agent Discovery Service")

@app.post("/register")
async def register_agent(agent_info: AgentInfo):
    discovery_service = DiscoveryService()
    success = discovery_service.register_agent(agent_info)
    if not success:
        raise HTTPException(status_code=400, detail="Registration failed")
    return {"status": "success", "agent_id": agent_info.agent_id}

@app.delete("/unregister/{agent_id}")
async def unregister_agent(agent_id: str):
    discovery_service = DiscoveryService()
    success = discovery_service.unregister_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"status": "success"}

@app.put("/heartbeat/{agent_id}")
async def update_heartbeat(agent_id: str):
    discovery_service = DiscoveryService()
    success = discovery_service.update_heartbeat(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"status": "success"}

@app.get("/agents")
async def list_agents(agent_type: Optional[str] = None):
    discovery_service = DiscoveryService()
    agents = discovery_service.list_agents(agent_type)
    return {"agents": agents}

@app.get("/agent/{agent_id}")
async def get_agent_info(agent_id: str):
    discovery_service = DiscoveryService()
    agent_info = discovery_service.get_agent_info(agent_id)
    if not agent_info:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_info
