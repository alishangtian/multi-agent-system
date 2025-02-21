import aiohttp
from typing import Dict, Any, Optional
import json
import asyncio
from pydantic import BaseModel

class NetworkResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class NetworkManager:
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self._retry_count = 3
        self._timeout = aiohttp.ClientTimeout(total=30)

    async def ensure_session(self):
        """确保aiohttp会话已创建"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self._timeout)

    async def close(self):
        """关闭网络管理器"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> NetworkResponse:
        """执行HTTP请求"""
        await self.ensure_session()
        
        try:
            async with self._session.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data
            ) as response:
                if response.status == 429:  # Rate limit
                    if retry_count < self._retry_count:
                        await asyncio.sleep(2 ** retry_count)  # 指数退避
                        return await self._make_request(
                            method, url, headers, json_data, retry_count + 1
                        )
                    else:
                        return NetworkResponse(
                            success=False,
                            error="Rate limit exceeded after retries"
                        )

                try:
                    data = await response.json()
                except:
                    data = await response.text()

                if response.status >= 400:
                    return NetworkResponse(
                        success=False,
                        error=f"HTTP {response.status}: {data}"
                    )

                return NetworkResponse(success=True, data=data)

        except asyncio.TimeoutError:
            if retry_count < self._retry_count:
                return await self._make_request(
                    method, url, headers, json_data, retry_count + 1
                )
            return NetworkResponse(
                success=False,
                error="Request timed out after retries"
            )
        except Exception as e:
            return NetworkResponse(success=False, error=str(e))

    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None
    ) -> NetworkResponse:
        """执行GET请求"""
        return await self._make_request("GET", url, headers)

    async def post(
        self,
        url: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> NetworkResponse:
        """执行POST请求"""
        return await self._make_request("POST", url, headers, data)

    async def put(
        self,
        url: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> NetworkResponse:
        """执行PUT请求"""
        return await self._make_request("PUT", url, headers, data)

    async def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None
    ) -> NetworkResponse:
        """执行DELETE请求"""
        return await self._make_request("DELETE", url, headers)

    def set_retry_count(self, count: int):
        """设置重试次数"""
        self._retry_count = max(0, count)

    def set_timeout(self, timeout: int):
        """设置超时时间（秒）"""
        self._timeout = aiohttp.ClientTimeout(total=timeout)

# 使用示例
async def example_usage():
    network = NetworkManager()
    
    try:
        # GET请求示例
        response = await network.get(
            "https://api.example.com/data",
            headers={"Authorization": "Bearer token"}
        )
        if response.success:
            print("Data:", response.data)
        else:
            print("Error:", response.error)

        # POST请求示例
        response = await network.post(
            "https://api.example.com/create",
            data={"name": "test"},
            headers={"Content-Type": "application/json"}
        )
        if response.success:
            print("Created:", response.data)
        else:
            print("Error:", response.error)

    finally:
        await network.close()

if __name__ == "__main__":
    asyncio.run(example_usage())
