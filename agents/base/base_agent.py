from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import requests
import json
from pydantic import BaseModel
import uuid

class Message(BaseModel):
    sender_id: str
    content: str
    message_type: str = "text"
    metadata: Optional[Dict] = None

class BaseAgent(ABC):
    def __init__(self, agent_type: str, capabilities: List[str], discovery_service_url: str):
        """
        初始化基础智能体
        
        Args:
            agent_type: 智能体类型
            capabilities: 智能体能力列表
            discovery_service_url: 发现服务地址
        """
        self.agent_id = f"{agent_type}-{str(uuid.uuid4())[:8]}"
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.discovery_service_url = discovery_service_url
        self.endpoint = None  # 将在启动时设置

    async def start(self, host: str, port: int):
        """启动智能体服务"""
        self.endpoint = f"http://{host}:{port}"
        # 向发现服务注册
        self._register()

    def _register(self):
        """向发现服务注册自己"""
        registration_data = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "capabilities": self.capabilities,
            "endpoint": self.endpoint,
            "last_heartbeat": 0
        }
        
        try:
            response = requests.post(
                f"{self.discovery_service_url}/register",
                json=registration_data
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Registration failed: {str(e)}")
            return False

    def send_message(self, target_agent_id: str, message: Message):
        """发送消息到目标智能体"""
        try:
            # 首先从发现服务获取目标智能体信息
            response = requests.get(
                f"{self.discovery_service_url}/agent/{target_agent_id}"
            )
            response.raise_for_status()
            target_info = response.json()
            
            # 发送消息到目标智能体
            response = requests.post(
                f"{target_info['endpoint']}/message",
                json=message.dict()
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Failed to send message: {str(e)}")
            return False

    def update_heartbeat(self):
        """更新心跳"""
        try:
            response = requests.put(
                f"{self.discovery_service_url}/heartbeat/{self.agent_id}"
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Heartbeat update failed: {str(e)}")
            return False

    @abstractmethod
    async def handle_message(self, message: Message):
        """处理接收到的消息"""
        pass

    @abstractmethod
    async def process_query(self, query: str) -> str:
        """处理查询请求"""
        pass

    def find_agents_by_type(self, agent_type: str) -> List[Dict]:
        """查找特定类型的智能体"""
        try:
            response = requests.get(
                f"{self.discovery_service_url}/agents",
                params={"agent_type": agent_type}
            )
            response.raise_for_status()
            return response.json()["agents"]
        except Exception as e:
            print(f"Failed to find agents: {str(e)}")
            return []

    def shutdown(self):
        """关闭智能体"""
        try:
            requests.delete(f"{self.discovery_service_url}/unregister/{self.agent_id}")
        except Exception as e:
            print(f"Unregister failed: {str(e)}")
