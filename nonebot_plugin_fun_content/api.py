import httpx
from typing import Dict, Any, List, Union, Callable
from .config import plugin_config
import logging
import random
from functools import wraps
import tempfile
import os
import asyncio
from urllib.parse import urlparse
from pathlib import Path

# 设置日志记录
logger = logging.getLogger(__name__)

class API:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0, follow_redirects=True)
        self.hitokoto_handlers = []
        self.process_functions = {
            "hitokoto": self._process_hitokoto_multiple,
            "twq": self._process_twq,
            "dog": self._process_dog,
            "wangyiyun": self._process_wangyiyun, 
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
                except httpx.HTTPStatusError as e:
                    logger.error(f"HTTP error occurred in hitokoto API: {e}")
                except httpx.RequestError as e:
                    logger.error(f"Request error occurred in hitokoto API: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error in hitokoto API: {e}")
                return None
            return wrapper
        return decorator

    def _setup_hitokoto_handlers(self):
        self.hitokoto_handlers = [
            self.hitokoto_handler("https://v2.api-m.com/api/yiyan?type=hitokoto")(self._process_hitokoto_original),
            self.hitokoto_handler("https://uapis.cn/api/say")(self._process_hitokoto_text),
            self.hitokoto_handler("https://tenapi.cn/v2/yiyan")(self._process_hitokoto_text),
            self.hitokoto_handler("https://api.vvhan.com/api/ian/rand?type=json")(self._process_hitokoto_vvhan)
        ]

    async def get_content(self, endpoint: str) -> str:
        if endpoint == "hitokoto":
            return await self._get_hitokoto_content()
        elif endpoint == "beauty_pic":
            return await self.get_beauty_pic()
        elif endpoint == "dog":
            return await self._get_dog_content()
        
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

    async def _get_hitokoto_content(self) -> str:
        random.shuffle(self.hitokoto_handlers)
        
        for handler in self.hitokoto_handlers:
            result = await handler(self)
            if result:
                return result
        
        raise ValueError("所有一言 API 请求失败")

    async def _get_dog_content(self) -> str:
        urls = plugin_config.fun_content_api_urls.get("dog")
        if not urls:
            logger.error("Dog API URLs not found in configuration")
            raise ValueError("Dog API 配置错误")

        random.shuffle(urls)
        
        for url in urls:
            try:
                logger.info(f"Sending dog diary request to {url}")
                response = await self.client.get(url)
                response.raise_for_status()
                data = response.json()
                logger.info(f"Received dog diary response: {data}")
                result = self._process_dog(data)
                if result:
                    return result
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred in dog API: {e}")
            except httpx.RequestError as e:
                logger.error(f"Request error occurred in dog API: {e}")
            except ValueError as e:
                logger.error(f"JSON decoding failed in dog API: {e}")
        
        raise ValueError("所有舔狗日记 API 请求失败")

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

        random.shuffle(urls)
        
        for url in urls:
            try:
                logger.info(f"Sending beauty pic request to {url}")
                response = await self.client.get(url)
                response.raise_for_status()
                data = response.json()
                logger.info(f"Received beauty pic response: {data}")
                result = self._process_beauty_pic(data)
                if result:
                    return result
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred in beauty pic API: {e}")
            except httpx.RequestError as e:
                logger.error(f"Request error occurred in beauty pic API: {e}")
            except ValueError as e:
                logger.error(f"JSON decoding failed in beauty pic API: {e}")
        
        raise ValueError("所有随机美女 API 请求失败")

    async def close(self):
        await self.client.aclose()

    def _process_hitokoto_multiple(self, data: Union[Dict[str, Any], str]) -> str:
        return "没有获取到一言内容"

    @staticmethod
    def _process_hitokoto_original(data: Dict[str, Any]) -> str:
        return data.get("data", "没有获取到一言内容")

    @staticmethod
    def _process_hitokoto_text(data: str) -> str:
        return data.strip() if data else "没有获取到一言内容"

    @staticmethod
    def _process_hitokoto_vvhan(data: Dict[str, Any]) -> str:
        if data.get("success"):
            return data.get("data", {}).get("content", "没有获取到一言内容")
        return "没有获取到一言内容"

    def _process_twq(self, data: Dict[str, Any]) -> str:
        return data.get("content", "没有获取到土味情话")

    def _process_dog(self, data: Dict[str, Any]) -> str:
        if isinstance(data, dict):
            if "code" in data and data["code"] in [200, "200"]:
                if "data" in data:
                    return data.get("data", "没有获取到舔狗日记")
                elif "content" in data:
                    return data.get("content", "没有获取到舔狗日记")
        return "没有获取到舔狗日记"
    
    def _process_wangyiyun(self, data: List[Dict[str, Any]]) -> str:
        if data and isinstance(data, list) and len(data) > 0:
            return data[0].get("wangyiyunreping", "没有获取到网易云热评")
        return "没有获取到网易云热评"

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
        if 'code' in data:
            if data['code'] == 200 or data['code'] == '10000':
                if 'data' in data:
                    if isinstance(data['data'], str):
                        return data['data']
                    elif isinstance(data['data'], list) and len(data['data']) > 0:
                        return data['data'][0]
                elif 'url' in data:
                    return data['url']
        return ""

    def _process_douyin_hot(self, data: Dict[str, Any]) -> str:
        if data.get("success"):
            hot_data = data.get("data", [])
            if hot_data:
                return "当前抖音热搜：\n" + "\n".join(
                    f"{item['index']}. {item['title']} ({item['hot']})"
                    for item in hot_data[:10]
                )
        return "没有获取到抖音热搜内容喵~"
    
    async def get_lazy_song(self) -> Path:
        api_url = plugin_config.fun_content_api_urls.get("lazy_sing")
        mp4_url = await self._get_mp4_url(api_url)
        logger.info(f"Extracted MP4 URL: {mp4_url}")

        if not self._is_valid_mp4_url(mp4_url):
            raise ValueError(f"Invalid MP4 URL: {mp4_url}")

        # 创建临时目录
        temp_dir = Path(tempfile.mkdtemp())
        mp4_file = temp_dir / "temp_video.mp4"
        mp3_file = temp_dir / "converted_audio.mp3"

        try:
            # 下载MP4文件
            logger.info(f"Downloading MP4 from: {mp4_url}")
            async with self.client.stream("GET", mp4_url) as response:
                response.raise_for_status()  # 确保请求成功
                with mp4_file.open("wb") as f:
                    async for chunk in response.aiter_bytes():
                        f.write(chunk)
            logger.info(f"MP4 downloaded to: {mp4_file}")

            # 转换MP4为MP3
            logger.info("Starting FFmpeg conversion")
            process = await asyncio.create_subprocess_exec(
                "ffmpeg", "-i", str(mp4_file), "-q:a", "0", "-map", "a", str(mp3_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                logger.error(f"FFmpeg conversion failed. Error: {stderr.decode()}")
                raise Exception("音频转换失败")
            logger.info(f"MP3 converted to: {mp3_file}")

            return mp3_file

        except Exception as e:
            logger.error(f"Error in get_lazy_song: {e}")
            raise
        finally:
            # 清理MP4文件
            if mp4_file.exists():
                mp4_file.unlink()

    async def _get_mp4_url(self, api_url: str) -> str:
        try:
            response = await self.client.get(api_url)
            response.raise_for_status()
            content = response.text.strip()
            logger.info(f"API Response: {content}")
            
            if content.startswith('http'):
                return content
            else:
                raise ValueError(f"No valid URL found in API response: {content}")
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {e}")
            raise ValueError("网络请求错误，请稍后重试")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise ValueError(f"API 请求失败: {e.response.status_code}")

    def _is_valid_mp4_url(self, url: str) -> bool:
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        return path.endswith('.mp4') or 'mp4' in parsed_url.query

    async def close(self):
        await self.client.aclose()

# 实例化 API 类
api = API()