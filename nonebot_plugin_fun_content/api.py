import httpx
from typing import Dict, Any, List, Union
from .config import plugin_config
import logging
import asyncio
import random

# 设置日志记录
logger = logging.getLogger(__name__)

class API:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)
        self.process_functions = {
            "hitokoto": self._process_hitokoto,
            "twq": self._process_twq,
            "dog": self._process_dog,
            "renjian": self._process_renjian,
            "weibo_hot": self._process_weibo_hot,
            "aiqinggongyu": self._process_aiqinggongyu,
            "shenhuifu": self._process_shenhuifu,
            "joke": self._process_joke,
            "beauty_pic": self._process_beauty_pic,
        }

    async def get_content(self, endpoint: str) -> str:
        url = plugin_config.fun_content_api_urls.get(endpoint)
        if not url:
            logger.error(f"Unknown API endpoint: {endpoint}")
            raise ValueError(f"未知的 API 端点: {endpoint}")

        try:
            logger.info(f"Sending request to {url}")
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Received response from {url}: {data}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise ValueError(f"API 请求失败: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {e}")
            raise ValueError("网络请求错误，请稍后重试")
        except ValueError as e:
            logger.error(f"JSON decoding failed: {e}")
            raise ValueError("API 返回了无效的数据格式")

        process_func = self.process_functions.get(endpoint)
        if process_func:
            try:
                return process_func(data)
            except Exception as e:
                logger.error(f"Error processing data for {endpoint}: {e}")
                raise ValueError(f"处理 {endpoint} 数据时出错")
        else:
            logger.error(f"No process function for endpoint: {endpoint}")
            raise ValueError(f"未知的 API 端点: {endpoint}")

    async def get_cp_content(self, args: str) -> bytes:
        names = args.split()
        if len(names) < 2:
            raise ValueError('未匹配到两个角色名称！请提供两个角色名称喵~')

        url = plugin_config.fun_content_api_urls.get("cp")
        if not url:
            logger.error("CP API URL not found in configuration")
            raise ValueError("CP API 配置错误")

        try:
            logger.info(f"Sending CP request to {url} with names: {names}")
            response = await self.client.get(url, params={"n1": names[0], "n2": names[1]})
            response.raise_for_status()
            image_data = response.content
            logger.info(f"Received CP image data, size: {len(image_data)} bytes")
            return image_data
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred in CP API: {e}")
            raise ValueError(f"CP API 请求失败: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Request error occurred in CP API: {e}")
            raise ValueError("网络请求错误，请稍后重试")

    async def get_beauty_pic(self) -> str:
        urls = plugin_config.fun_content_api_urls.get("beauty_pic")
        if not urls:
            logger.error("Beauty pic API URLs not found in configuration")
            raise ValueError("Beauty pic API 配置错误")

        random.shuffle(urls)  # 随机打乱 URL 顺序
        
        for url in urls:
            try:
                logger.info(f"Sending beauty pic request to {url}")
                response = await self.client.get(url)
                response.raise_for_status()
                data = response.json()
                logger.info(f"Received beauty pic response: {data}")
                return self._process_beauty_pic(data)
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred in beauty pic API: {e}")
            except httpx.RequestError as e:
                logger.error(f"Request error occurred in beauty pic API: {e}")
            except ValueError as e:
                logger.error(f"JSON decoding failed in beauty pic API: {e}")
        
        raise ValueError("所有随机美女 API 请求失败")

    async def close(self):
        await self.client.aclose()

    def _process_hitokoto(self, data: Dict[str, Any]) -> str:
        return data.get("data", "没有获取到一言内容")

    def _process_twq(self, data: Dict[str, Any]) -> str:
        return data.get("content", "没有获取到土味情话")

    def _process_dog(self, data: Dict[str, Any]) -> str:
        return data.get("data", "没有获取到舔狗日记")

    def _process_renjian(self, data: Dict[str, Any]) -> str:
        return data.get("data", "没有获取到人间凑数内容")

    def _process_weibo_hot(self, data: Dict[str, Any]) -> str:
        if data.get("code") == 200:
            hot_data = data.get("data", [])
            if hot_data:
                return "当前微博热搜：\n" + "\n".join(
                    f"{item['index']}. {item['title']} ({item['hot']})"
                    for item in hot_data[:10]
                )
        return "没有获取到微博热搜内容喵~"

    def _process_aiqinggongyu(self, data: Dict[str, Any]) -> str:
        return data.get("data", "没有获取到爱情公寓语录")

    def _process_shenhuifu(self, data: List[Dict[str, Any]]) -> str:
        if data and isinstance(data, list) and len(data) > 0:
            return data[0].get("shenhuifu", "没有获取到神回复内容").replace("<br>", "\n")
        return "没有获取到神回复内容"

    def _process_joke(self, data: Dict[str, Any]) -> str:
        if data.get("success"):
            joke_data = data.get("data", {})
            return joke_data.get("content", "没有获取到笑话内容")
        return "没有获取到笑话内容"

    def _process_beauty_pic(self, data: Dict[str, Any]) -> str:
        if data.get("code") == 200:
            return data.get("data", "")
        return ""

# 实例化 API 类
api = API()