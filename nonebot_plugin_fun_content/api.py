import httpx
from typing import Dict, Any, List, Union
from .config import plugin_config
import logging
import random
from functools import wraps
import tempfile
import asyncio
from urllib.parse import urlparse
from pathlib import Path

# 设置日志记录
logger = logging.getLogger(__name__)

class API:
    def __init__(self):
        """
        初始化 API 类
        设置 HTTP 客户端、一言处理器和处理函数字典
        """
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
        """
        一言处理器的装饰器
        用于创建处理不同一言 API 响应的函数

        :param url: API 的 URL
        :return: 装饰器函数
        """
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
        """
        设置一言处理器
        为不同的一言 API 创建处理函数
        """
        self.hitokoto_handlers = [
            self.hitokoto_handler("https://v2.api-m.com/api/yiyan?type=hitokoto")(self._process_hitokoto_original),
            self.hitokoto_handler("https://uapis.cn/api/say")(self._process_hitokoto_text),
            self.hitokoto_handler("https://tenapi.cn/v2/yiyan")(self._process_hitokoto_text),
            self.hitokoto_handler("https://api.vvhan.com/api/ian/rand?type=json")(self._process_hitokoto_vvhan)
        ]

    async def get_content(self, endpoint: str) -> str:
        """
        获取指定 API 端点的内容

        :param endpoint: API 端点名称
        :return: 处理后的 API 响应内容
        :raises ValueError: 如果 API 请求失败或处理出错
        """
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
        """
        获取一言内容
        尝试所有可用的一言 API，直到获取成功

        :return: 一言内容
        :raises ValueError: 如果所有 API 请求都失败
        """
        random.shuffle(self.hitokoto_handlers)
        
        for handler in self.hitokoto_handlers:
            result = await handler(self)
            if result:
                return result
        
        raise ValueError("所有一言 API 请求失败")

    async def _get_dog_content(self) -> str:
        """
        获取舔狗日记内容
        尝试所有可用的舔狗日记 API，直到获取成功

        :return: 舔狗日记内容
        :raises ValueError: 如果所有 API 请求都失败
        """
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
        """
        获取 CP 内容（图片）

        :param args: 包含两个角色名称的字符串
        :return: 图片数据（字节串）
        :raises ValueError: 如果参数不足或 API 请求失败
        """
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
        """
        获取随机美女图片 URL

        :return: 图片 URL
        :raises ValueError: 如果所有 API 请求都失败
        """
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

    async def get_lazy_song(self) -> Path:
        """
        获取懒洋洋唱歌的音频文件

        :return: 音频文件的 Path 对象
        :raises ValueError: 如果 API 请求失败或音频处理出错
        """
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
        """
        从 API 获取 MP4 URL

        :param api_url: API 的 URL
        :return: MP4 的 URL
        :raises ValueError: 如果 API 响应不包含有效的 URL
        """
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
        """
        检查 URL 是否是有效的 MP4 URL

        :param url: 要检查的 URL
        :return: 如果是有效的 MP4 URL 则返回 True，否则返回 False
        """
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        return path.endswith('.mp4') or 'mp4' in parsed_url.query

    async def close(self):
        """
        关闭 HTTP 客户端
        """
        await self.client.aclose()

    # 以下是各种 API 响应的处理函数
    # 每个函数都负责解析特定类型的 API 响应并提取所需的内容

    def _process_hitokoto_multiple(self, data: Union[Dict[str, Any], str]) -> str:
        """
        处理多个一言 API 的响应

        :param data: API 响应数据，可能是字典或字符串
        :return: 处理后的一言内容，如果无法处理则返回默认消息
        """
        return "没有获取到一言内容"

    @staticmethod
    def _process_hitokoto_original(data: Dict[str, Any]) -> str:
        """
        处理原始一言 API 的响应

        :param data: API 响应数据字典
        :return: 从响应中提取的一言内容
        """
        return data.get("data", "没有获取到一言内容")

    @staticmethod
    def _process_hitokoto_text(data: str) -> str:
        """
        处理纯文本格式的一言 API 响应

        :param data: API 响应的文本内容
        :return: 去除首尾空白的一言内容
        """
        return data.strip() if data else "没有获取到一言内容"

    @staticmethod
    def _process_hitokoto_vvhan(data: Dict[str, Any]) -> str:
        """
        处理 vvhan 一言 API 的响应

        :param data: API 响应数据字典
        :return: 从响应中提取的一言内容
        """
        if data.get("success"):
            return data.get("data", {}).get("content", "没有获取到一言内容")
        return "没有获取到一言内容"

    def _process_twq(self, data: Dict[str, Any]) -> str:
        """
        处理土味情话 API 的响应

        :param data: API 响应数据字典
        :return: 从响应中提取的土味情话内容
        """
        return data.get("content", "没有获取到土味情话")

    def _process_dog(self, data: Dict[str, Any]) -> str:
        """
        处理舔狗日记 API 的响应

        :param data: API 响应数据字典
        :return: 从响应中提取的舔狗日记内容
        """
        if isinstance(data, dict):
            if "code" in data and data["code"] in [200, "200"]:
                if "data" in data:
                    return data.get("data", "没有获取到舔狗日记")
                elif "content" in data:
                    return data.get("content", "没有获取到舔狗日记")
        return "没有获取到舔狗日记"
    
    def _process_wangyiyun(self, data: List[Dict[str, Any]]) -> str:
        """
        处理网易云热评 API 的响应

        :param data: API 响应数据列表
        :return: 从响应中提取的网易云热评内容
        """
        if data and isinstance(data, list) and len(data) > 0:
            return data[0].get("wangyiyunreping", "没有获取到网易云热评")
        return "没有获取到网易云热评"

    def _process_renjian(self, data: Dict[str, Any]) -> str:
        """
        处理人间凑数 API 的响应

        :param data: API 响应数据字典
        :return: 从响应中提取的人间凑数内容
        """
        return data.get("data", "没有获取到人间凑数内容")

    def _process_weibo_hot(self, data: Dict[str, Any]) -> str:
        """
        处理微博热搜 API 的响应

        :param data: API 响应数据字典
        :return: 格式化后的微博热搜列表
        """
        if data.get("code") == 200:
            hot_data = data.get("data", [])
            if hot_data:
                return "当前微博热搜：\n" + "\n".join(
                    f"{item['index']}. {item['title']} ({item['hot']})"
                    for item in hot_data[:10]
                )
        return "没有获取到微博热搜内容喵~"

    def _process_aiqinggongyu(self, data: Dict[str, Any]) -> str:
        """
        处理爱情公寓语录 API 的响应

        :param data: API 响应数据字典
        :return: 从响应中提取的爱情公寓语录
        """
        return data.get("data", "没有获取到爱情公寓语录")

    def _process_shenhuifu(self, data: List[Dict[str, Any]]) -> str:
        """
        处理神回复 API 的响应

        :param data: API 响应数据列表
        :return: 从响应中提取的神回复内容
        """
        if data and isinstance(data, list) and len(data) > 0:
            return data[0].get("shenhuifu", "没有获取到神回复内容").replace("<br>", "\n")
        return "没有获取到神回复内容"

    def _process_joke(self, data: Dict[str, Any]) -> str:
        """
        处理笑话 API 的响应

        :param data: API 响应数据字典
        :return: 从响应中提取的笑话内容
        """
        if data.get("success"):
            joke_data = data.get("data", {})
            return joke_data.get("content", "没有获取到笑话内容")
        return "没有获取到笑话内容"

    def _process_beauty_pic(self, data: Dict[str, Any]) -> str:
        """
        处理美女图片 API 的响应

        :param data: API 响应数据字典
        :return: 从响应中提取的图片 URL
        """
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
        """
        处理抖音热搜 API 的响应

        :param data: API 响应数据字典
        :return: 格式化后的抖音热搜列表
        """
        if data.get("success"):
            hot_data = data.get("data", [])
            if hot_data:
                return "当前抖音热搜：\n" + "\n".join(
                    f"{item['index']}. {item['title']} ({item['hot']})"
                    for item in hot_data[:10]
                )
        return "没有获取到抖音热搜内容喵~"

# 实例化 API 类
api = API()