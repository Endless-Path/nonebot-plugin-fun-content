from typing import Dict, Any, Union, List
import httpx
import sqlite3
import logging

logger = logging.getLogger(__name__)

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
            "joke": "获取笑话"
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
    def process_hot_list(cls, data: Dict[str, Any], title: str) -> str:
        """处理热搜榜数据
        
        Args:
            data (Dict[str, Any]): API返回的数据
            title (str): 热搜榜标题
            
        Returns:
            str: 格式化后的热搜榜内容
        """
        if data.get('code') == 200 or data.get('success'):
            items = data.get('data', [])
            if items:
                return f"当前{title}：\n" + "\n".join(
                    f"{item['index']}. {item['title']} ({item.get('hot', '')})"
                    for item in items[:10]
                )
        return f"获取{title}失败"

    @staticmethod
    def process_api_text(data: Dict[str, Any], error_msg: str) -> str:
        """处理文本类API响应
        
        Args:
            data (Dict[str, Any]): API返回的数据
            error_msg (str): 错误消息
            
        Returns:
            str: 处理后的内容
        """
        # 检查响应码
        if isinstance(data, dict):
            if data.get('code') in [200, '200'] or data.get('success'):
                content = data.get('data') or data.get('content')
                if content:
                    return content.replace("<br>", "\n").strip()
        return error_msg

response_handler = ResponseHandler()