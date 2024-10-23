import httpx
from typing import Dict, Any, List, Union, Optional
from .config import plugin_config
from .database import db_manager
from .response_handler import response_handler
import logging
import random
from functools import wraps
from pathlib import Path
from io import BytesIO

# 设置日志记录
logger = logging.getLogger(__name__)

class API:
    def __init__(self):
        """初始化 API 类"""
        self.client = httpx.AsyncClient(timeout=10.0, follow_redirects=True)
        self.hitokoto_handlers = []
        self.process_functions = {
            "hitokoto": self._process_hitokoto_multiple,
            "twq": self._process_twq,
            "dog": self._process_dog,
            "renjian": self._process_renjian,
            "weibo_hot": self._process_weibo_hot,
            "aiqinggongyu": self._process_aiqinggongyu,
            "shenhuifu": self._process_shenhuifu,
            "joke": self._process_joke,
            "beauty_pic": self._process_beauty_pic,
            "douyin_hot": self._process_douyin_hot,
        }
        self._setup_hitokoto_handlers()

    @staticmethod
    def hitokoto_handler(url):
        """一言处理器的装饰器"""
        def decorator(func):
            @wraps(func)
            async def wrapper(self):
                try:
                    logger.info(f"Sending hitokoto request to {url}")
                    response = await self.client.get(url)
                    response.raise_for_status()
                    
                    if response.headers.get('content-type', '').startswith('application/json'):
                        data = response.json()
                    else:
                        data = response.text
                    
                    logger.info(f"Received hitokoto response from {url}")
                    return func(data)
                except Exception as e:
                    logger.error(f"Error in hitokoto API: {e}")
                return None
            return wrapper
        return decorator

    def _setup_hitokoto_handlers(self):
        """设置一言处理器"""
        self.hitokoto_handlers = [
            self.hitokoto_handler("https://v2.api-m.com/api/yiyan?type=hitokoto")(self._process_hitokoto_original),
            self.hitokoto_handler("https://uapis.cn/api/say")(self._process_hitokoto_text),
            self.hitokoto_handler("https://tenapi.cn/v2/yiyan")(self._process_hitokoto_text),
            self.hitokoto_handler("https://api.vvhan.com/api/ian/rand?type=json")(self._process_hitokoto_vvhan)
        ]

    async def get_content(self, endpoint: str) -> str:
        """获取指定API端点的内容
        
        Args:
            endpoint: API端点名称
            
        Returns:
            str: 获取的内容
            
        Raises:
            ValueError: 如果获取失败
        """
        # 特殊处理的端点
        if endpoint == "hitokoto":
            return await self._get_hitokoto_content()
        elif endpoint == "beauty_pic":
            return await self.get_beauty_pic()
        elif endpoint == "dog":
            return await self._get_dog_content()
            
        # 尝试从本地数据库获取
        try:
            if endpoint in plugin_config.DATABASE_SUPPORTED_COMMANDS:
                if endpoint == "shenhuifu":
                    result = await db_manager.get_random_shenhuifu()
                    if result:
                        return f"问：{result['question']}\n答：{result['answer']}"
                else:
                    result = await db_manager.get_random_content(endpoint)
                    if result:
                        return result
                        
        except Exception as e:
            logger.warning(f"Failed to get content from local database for {endpoint}: {e}")

        # 如果本地数据库获取失败或不支持的端点，使用在线API
        return await self._get_online_content(endpoint)

    async def _get_online_content(self, endpoint: str) -> str:
        """从在线API获取内容"""
        url = plugin_config.fun_content_api_urls.get(endpoint)
        if not url:
            raise ValueError(f"未知的API端点: {endpoint}")

        try:
            logger.info(f"Sending request to {url}")
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Received response from {url}")

            process_func = self.process_functions.get(endpoint)
            if process_func:
                return process_func(data)
            raise ValueError(f"未知的API端点: {endpoint}")
        except Exception as e:
            logger.error(f"Error getting content from online API: {e}")
            raise ValueError(str(e))

    async def _get_hitokoto_content(self) -> str:
        """获取一言内容"""
        try:
            result = await db_manager.get_random_content("hitokoto")
            if result:
                return result
        except Exception as e:
            logger.warning(f"Failed to get hitokoto from local database: {e}")

        # 如果本地获取失败，尝试在线API
        random.shuffle(self.hitokoto_handlers)
        for handler in self.hitokoto_handlers:
            result = await handler(self)
            if result:
                return result
        
        raise ValueError("获取一言失败")

    async def _get_dog_content(self) -> str:
        """获取舔狗日记内容"""
        try:
            result = await db_manager.get_random_content("dog")
            if result:
                return result
        except Exception as e:
            logger.warning(f"Failed to get dog diary from local database: {e}")

        # 如果本地获取失败，尝试在线API
        urls = plugin_config.fun_content_api_urls.get("dog", [])
        random.shuffle(urls)
        
        for url in urls:
            try:
                response = await self.client.get(url)
                response.raise_for_status()
                data = response.json()
                result = self._process_dog(data)
                if result:
                    return result
            except Exception as e:
                logger.error(f"Error in dog API {url}: {e}")
                continue
        
        raise ValueError("获取舔狗日记失败")

    async def get_beauty_pic(self) -> str:
        """获取随机美女图片URL"""
        try:
            result = await db_manager.get_random_beauty_pic()
            if result:
                return result
        except Exception as e:
            logger.warning(f"Failed to get beauty pic from local database: {e}")

        # 如果本地获取失败，尝试在线API
        urls = plugin_config.fun_content_api_urls.get("beauty_pic", [])
        random.shuffle(urls)
        
        for url in urls:
            try:
                response = await self.client.get(url)
                response.raise_for_status()
                data = response.json()
                result = self._process_beauty_pic(data)
                if result:
                    return result
            except Exception as e:
                logger.error(f"Error in beauty pic API {url}: {e}")
                continue
        
        raise ValueError("获取美女图片失败")

    async def get_cp_content(self, args: str) -> bytes:
        """获取CP内容"""
        names = args.split()
        if len(names) < 2:
            raise ValueError('请提供两个角色名称！')

        url = plugin_config.fun_content_api_urls.get("cp")
        if not url:
            raise ValueError("CP API配置错误")

        try:
            response = await self.client.get(url, params={"n1": names[0], "n2": names[1]})
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Error in CP API: {e}")
            raise ValueError("生成CP图片失败")

    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()

    # API响应处理函数
    @staticmethod
    def _process_hitokoto_original(data: Dict[str, Any]) -> str:
        return data.get("data", "获取一言失败")

    @staticmethod
    def _process_hitokoto_text(data: str) -> str:
        return data.strip() if data else "获取一言失败"

    @staticmethod
    def _process_hitokoto_vvhan(data: Dict[str, Any]) -> str:
        return data.get("data", {}).get("content", "获取一言失败") if data.get("success") else "获取一言失败"

    def _process_hitokoto_multiple(self, data: Union[Dict[str, Any], str]) -> str:
        return "获取一言失败"

    def _process_twq(self, data: Dict[str, Any]) -> str:
        return response_handler.process_api_text(data, "获取土味情话失败")

    def _process_dog(self, data: Dict[str, Any]) -> str:
        if isinstance(data, dict):
            if data.get("code") in [200, "200"]:
                content = data.get("data") or data.get("content")
                if content:
                    return content
        return "获取舔狗日记失败"
    
    def _process_renjian(self, data: Dict[str, Any]) -> str:
        return response_handler.process_api_text(data, "获取人间凑数内容失败")

    def _process_weibo_hot(self, data: Dict[str, Any]) -> str:
        return response_handler.process_hot_list(data, "微博热搜")

    def _process_aiqinggongyu(self, data: Dict[str, Any]) -> str:
        return response_handler.process_api_text(data, "获取爱情公寓语录失败")

    def _process_shenhuifu(self, data: List[Dict[str, Any]]) -> str:
        if isinstance(data, list) and data:
            return data[0].get("shenhuifu", "获取神回复失败").replace("<br>", "\n")
        return "获取神回复失败"

    def _process_joke(self, data: Dict[str, Any]) -> str:
        if data.get("success"):
            return data.get("data", {}).get("content", "获取笑话失败")
        return "获取笑话失败"

    def _process_beauty_pic(self, data: Dict[str, Any]) -> str:
        """处理美女图片API的响应"""
        if 'code' in data:
            if data['code'] in [200, '10000']:
                if 'data' in data:
                    if isinstance(data['data'], str):
                        return data['data']
                    elif isinstance(data['data'], list) and data['data']:
                        return data['data'][0]
                elif 'url' in data:
                    return data['url']
        return ""

    def _process_douyin_hot(self, data: Dict[str, Any]) -> str:
        """处理抖音热搜API的响应"""
        return response_handler.process_hot_list(data, "抖音热搜")

# 创建API实例
api = API()