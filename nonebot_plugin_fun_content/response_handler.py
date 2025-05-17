import re
import sqlite3
from typing import Any, Dict, List, Union

import httpx

from nonebot import logger


class ResponseHandler:
    """统一处理API响应和错误的工具类"""

    @staticmethod
    def format_error(error: Exception, endpoint: str) -> str:
        """统一格式化错误消息

        Args:
            error (Exception): 异常对象
            endpoint (str): API端点名称

        Returns:
            str: 格式化后的错误消息
        """
        base_messages = {
            "hitokoto": "获取一言",
            "twq": "获取土味情话",
            "dog": "获取舔狗日记",
            "renjian": "获取人间凑数内容",
            "weibo_hot": "获取微博热搜",
            "douyin_hot": "获取抖音热搜",
            "aiqinggongyu": "获取爱情公寓语录",
            "beauty_pic": "获取美女图片",
            "shenhuifu": "获取神回复",
            "joke": "获取笑话",
            "cp": "生成CP图片"
        }

        base_msg = f"{base_messages.get(endpoint, '请求')}失败"

        if isinstance(error, httpx.TimeoutException):
            return f"{base_msg}：请求超时"
        elif isinstance(error, httpx.HTTPStatusError):
            return f"{base_msg}：服务器响应错误 ({error.response.status_code})"
        elif isinstance(error, ValueError):
            return f"{base_msg}：{str(error)}"
        elif isinstance(error, sqlite3.Error):
            return f"{base_msg}：数据库访问出错"
        else:
            logger.error(f"Unexpected error in {endpoint}: {error}", exc_info=True)
            return f"{base_msg}：发生未知错误"

    @classmethod
    def process_hot_list(cls, data: Dict[str, Any], endpoint: str) -> str:
        """处理热搜榜数据

        Args:
            data (Dict[str, Any]): API返回的数据
            title (str): 热搜榜标题

        Returns:
            str: 格式化后的热搜榜内容
        """
        # 定义端点到显示名称的映射
        endpoint_to_title = {
            "weibo_hot": "微博热搜",
            "douyin_hot": "抖音热搜",
        }
        display_title = endpoint_to_title.get(endpoint, "热搜")
        if data.get('code') == 200 or data.get('success'):
            items = data.get('data', [])
            if items:
                return f"当前{display_title}：\n" + "\n".join(
                    f"{item['index']}. {item['title']} ({item.get('hot', '')})"
                    for item in items[:10]
                )
        return f"获取{display_title}失败"

    @staticmethod
    def process_api_text(data: Dict[str, Any], error_msg: str) -> str:
        """处理文本类API响应，将HTML格式转换为纯文本。

        Args:
            data (Dict[str, Any]): API返回的数据
            error_msg (str): 错误消息

        Returns:
            str: 处理后的纯文本内容或错误信息
        """
        # 检查响应是否为字典并且响应码成功
        if isinstance(data, dict) and (data.get('code') in [200, '200'] or data.get('success')):
            content = data.get('data') or data.get('content')

            if content:
                # 替换常见的HTML标签为换行或空格
                content = content.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
                content = content.replace("&nbsp;", " ").replace("&amp;", "&")

                # 使用正则表达式去除所有其他HTML标签
                content = re.sub(r'<[^>]+>', '', content)

                # 去除多余的空格和空行
                content = re.sub(r'\n\s*\n', '\n', content).strip()

                return content

        return error_msg  # 返回错误信息，如果响应不符合预期或无内容

    @staticmethod
    def process_beauty_pic(data: Dict[str, Any]) -> str:
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

    @staticmethod
    def process_shenhuifu(data: List[Dict[str, Any]]) -> str:
        if isinstance(data, list) and data:
            return data[0].get("shenhuifu", "获取神回复失败").replace("<br>", "\n")
        return "获取神回复失败"

    @staticmethod
    def process_hitokoto_original(data: Dict[str, Any]) -> str:
        return data.get("data", "获取一言失败")

    @staticmethod
    def process_hitokoto_text(data: str) -> str:
        return data.strip() if data else "获取一言失败"

    @staticmethod
    def process_hitokoto_vvhan(data: Dict[str, Any]) -> str:
        return data.get("data", {}).get("content", "获取一言失败") if data.get("success") else "获取一言失败"

    @staticmethod
    def process_hitokoto_multiple(data: Union[Dict[str, Any], str]) -> str:
        return "获取一言失败"

    @staticmethod
    def process_twq(data: Dict[str, Any]) -> str:
        return ResponseHandler.process_api_text(data, "获取土味情话失败")

    @staticmethod
    def process_dog(data: Dict[str, Any]) -> str:
        if isinstance(data, dict):
            if data.get("code") in [200, "200"]:
                content = data.get("data") or data.get("content")
                if content:
                    return content
        return "获取舔狗日记失败"

    @staticmethod
    def process_renjian(data: Dict[str, Any]) -> str:
        return ResponseHandler.process_api_text(data, "获取人间凑数内容失败")

    @staticmethod
    def process_weibo_hot(data: Dict[str, Any]) -> str:
        return ResponseHandler.process_hot_list(data, "微博热搜")

    @staticmethod
    def process_aiqinggongyu(data: Dict[str, Any]) -> str:
        return ResponseHandler.process_api_text(data, "获取爱情公寓语录失败")

    @staticmethod
    def process_joke(data: Dict[str, Any]) -> str:
        if data.get("success"):
            return data.get("data", {}).get("content", "获取笑话失败")
        return "获取笑话失败"

    @staticmethod
    def process_douyin_hot(data: Dict[str, Any]) -> str:
        return ResponseHandler.process_hot_list(data, "抖音热搜")


response_handler = ResponseHandler()