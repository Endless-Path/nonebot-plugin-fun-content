import httpx
from typing import Dict, Any, List
import json
from .config import config

class API:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)

    async def get_content(self, endpoint: str) -> str:
        """
        获取内容并根据不同的端点进行特定处理
        :param endpoint: API 端点
        :return: 处理后的内容
        """
        url = config.fun_content_api_urls.get(endpoint)
        if not url:
            return "未知的 API 端点"

        response = await self.client.get(url)
        response.raise_for_status()
        data = response.json()
        
        # 根据不同的端点调用对应的处理函数
        process_functions = {
            "hitokoto": self._process_hitokoto,
            "twq": self._process_twq,
            "dog": self._process_dog,
            "renjian": self._process_renjian,
            "weibo_hot": self._process_weibo_hot,
            "aiqinggongyu": self._process_aiqinggongyu,
            "shenhuifu": self._process_shenhuifu
        }
        
        if endpoint in process_functions:
            return process_functions[endpoint](data)
        else:
            return "未知的 API 端点"

    async def get_cp_content(self, args: str) -> str:
        """
        获取 CP 内容
        :param args: 包含两个角色名称的字符串
        :return: CP 内容
        """
        names = args.split()
        if len(names) < 2:
            raise ValueError('未匹配到两个角色名称！请提供两个角色名称喵~')
    
        url = config.fun_content_api_urls.get("cp")
        response = await self.client.get(url, params={"n1": names[0], "n2": names[1]})
        return response.content

    async def get_baisi_image(self) -> str:
        """
        获取随机白丝图片 URL
        :return: 图片 URL
        """
        headers = {
        'User-Agent': 'xiaoxiaoapi/1.0.0 (https://api-m.com)'
        }
        url = config.fun_content_api_urls.get("baisi")
        response = await self.client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return self._process_baisi(data)

    def _process_hitokoto(self, data: Dict[str, Any]) -> str:
        """处理一言 API 的响应"""
        return data.get("data", "没有获取到一言内容")

    def _process_twq(self, data: Dict[str, Any]) -> str:
        """处理土味情话 API 的响应"""
        return data.get("content", "没有获取到土味情话")

    def _process_dog(self, data: Dict[str, Any]) -> str:
        """处理舔狗日记 API 的响应"""
        return data.get("data", "没有获取到舔狗日记")

    def _process_renjian(self, data: Dict[str, Any]) -> str:
        """处理人间凑数 API 的响应"""
        return data.get("data", "没有获取到人间凑数内容")

    def _process_weibo_hot(self, data: Dict[str, Any]) -> str:
        """处理微博热搜 API 的响应"""
        if data.get("code") == 200:
            hot_data = data.get("data", [])
            if hot_data:
                return "当前微博热搜：\n" + "\n".join(
                    f"{item['index']}. {item['title']} ({item['hot']})"
                    for item in hot_data[:10]
                )
        return "没有获取到微博热搜内容喵~"

    def _process_aiqinggongyu(self, data: Dict[str, Any]) -> str:
        """处理爱情公寓 API 的响应"""
        return data.get("data", "没有获取到爱情公寓语录")

    def _process_baisi(self, data: Dict[str, Any]) -> str:
        """处理随机白丝图片 API 的响应"""
        return data.get("data", "没有获取到图片链接")

    def _process_shenhuifu(self, data: List[Dict[str, Any]]) -> str:
        """处理神回复 API 的响应"""
        if data and isinstance(data, list) and len(data) > 0:
            return data[0].get("shenhuifu", "没有获取到神回复内容").replace("<br>", "\n")
        return "没有获取到神回复内容"

api = API()     #定义了API对象