from typing import Dict, List, Any, Optional
import json
from pydantic import BaseModel

class ToolResult(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None

class Tool(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    agent_type: str  # 指定哪种类型的智能体可以执行此工具

class ToolExecutor:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """注册默认工具"""
        self.register_tool(Tool(
            name="web_search",
            description="使用搜索智能体执行网络搜索",
            parameters={
                "query": {
                    "type": "string",
                    "description": "搜索查询"
                }
            },
            agent_type="search"
        ))

        self.register_tool(Tool(
            name="paper_search",
            description="使用论文智能体在arXiv上搜索论文",
            parameters={
                "query": {
                    "type": "string",
                    "description": "论文搜索查询"
                },
                "max_results": {
                    "type": "integer",
                    "description": "最大结果数量",
                    "default": 5
                }
            },
            agent_type="paper"
        ))

    def register_tool(self, tool: Tool):
        """注册新工具"""
        self.tools[tool.name] = tool

    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """获取工具定义"""
        return self.tools.get(tool_name)

    def list_tools(self) -> List[Tool]:
        """列出所有可用工具"""
        return list(self.tools.values())

    def get_tools_for_agent(self, agent_type: str) -> List[Tool]:
        """获取特定类型智能体可用的工具"""
        return [tool for tool in self.tools.values() if tool.agent_type == agent_type]

    def validate_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> bool:
        """验证工具参数"""
        tool = self.get_tool(tool_name)
        if not tool:
            return False

        required_params = {
            name: param for name, param in tool.parameters.items()
            if "default" not in param
        }

        # 检查所有必需参数是否都提供了
        for param_name in required_params:
            if param_name not in parameters:
                return False

        # 检查参数类型
        for param_name, value in parameters.items():
            if param_name in tool.parameters:
                expected_type = tool.parameters[param_name]["type"]
                if expected_type == "string" and not isinstance(value, str):
                    return False
                elif expected_type == "integer" and not isinstance(value, int):
                    return False
                # 可以添加更多类型检查

        return True

    def format_tool_description(self, tool_name: str) -> str:
        """格式化工具描述，用于AI模型理解"""
        tool = self.get_tool(tool_name)
        if not tool:
            return f"未找到工具: {tool_name}"

        params_desc = []
        for name, param in tool.parameters.items():
            required = "default" not in param
            default_value = param.get("default", "无")
            params_desc.append(
                f"- {name} ({param['type']}, {'必需' if required else '可选'}): "
                f"{param['description']} (默认值: {default_value})"
            )

        return f"""
工具名称: {tool.name}
描述: {tool.description}
执行智能体: {tool.agent_type}
参数:
{chr(10).join(params_desc)}
"""

    def format_result(self, result: Any) -> ToolResult:
        """格式化工具执行结果"""
        try:
            if isinstance(result, str):
                # 尝试解析JSON字符串
                try:
                    result = json.loads(result)
                except json.JSONDecodeError:
                    pass
            
            return ToolResult(
                success=True,
                result=result
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )
