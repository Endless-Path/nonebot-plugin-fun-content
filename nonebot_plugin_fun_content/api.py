import httpx

from nonebot import logger
from .config import plugin_config
from .database import db_manager
from .response_handler import response_handler


class API:
    def __init__(self):
        """初始化API客户端"""
        # 创建异步HTTP客户端，设置超时和重定向策略
        self.client = httpx.AsyncClient(timeout=10.0, follow_redirects=True)
        # 注册不同API端点对应的响应处理器
        self.process_functions = {
            "weibo_hot": response_handler.process_hot_list,
            "douyin_hot": response_handler.process_hot_list,
        }

    async def get_content(self, endpoint):
        """获取指定API端点的内容
        
        Args:
            endpoint: API端点名称，如"weibo_hot"、"shenhuifu"等
        
        Returns:
            格式化后的内容字符串
        
        Raises:
            ValueError: 当端点无效或获取内容失败时
        """
        # 特殊端点处理逻辑
        if endpoint == "cp":
            raise ValueError("CP命令需要使用get_cp_content方法并提供参数")
        elif endpoint == "beauty_pic":
            # 从数据库获取随机美女图片
            try:
                result = await db_manager.get_random_beauty_pic()
                if result:
                    return result
            except Exception as e:
                error_msg = response_handler.format_error(e, endpoint)
                logger.error(f"从数据库获取{endpoint}失败: {error_msg}")
                raise ValueError(f"获取{endpoint}失败")

        # 处理需要调用在线API的端点
        elif endpoint in ["weibo_hot", "douyin_hot"]:
            return await self._get_online_content(endpoint)

        # 从本地数据库获取其他类型内容
        try:
            if endpoint == "shenhuifu":
                # 获取神回复内容（问答形式）
                result = await db_manager.get_random_shenhuifu()
                if result:
                    return f"问：{result['question']}\n答：{result['answer']}"
            else:
                # 获取其他随机内容
                result = await db_manager.get_random_content(endpoint)
                if result:
                    return result

        except Exception as e:
            error_msg = response_handler.format_error(e, endpoint)
            logger.error(f"从数据库获取{endpoint}失败: {error_msg}")
            raise ValueError(f"获取{endpoint}失败")

        # 未知端点处理
        raise ValueError(f"未知的API端点: {endpoint}")

    async def _get_online_content(self, endpoint):
        """从在线API获取内容（私有方法）
        
        Args:
            endpoint: 在线API端点名称
        
        Returns:
            处理后的内容字符串
        """
        # 从配置中获取API URL
        url = plugin_config.fun_content_api_urls.get(endpoint)
        if not url:
            raise ValueError(f"未知的API端点: {endpoint}")

        try:
            logger.info(f"Sending request to {url}")
            response = await self.client.get(url)
            response.raise_for_status()  # 检查HTTP响应状态
            data = response.json()  # 解析JSON响应
            logger.success(f"Received response from {url}")

            # 使用注册的处理器处理响应数据
            process_func = self.process_functions.get(endpoint)
            if process_func:
                return process_func(data, endpoint)
            raise ValueError(f"未知的API端点: {endpoint}")
        except Exception as e:
            error_msg = response_handler.format_error(e, endpoint)
            logger.error(error_msg)
            raise ValueError(error_msg)

    async def get_cp_content(self, args):
        """获取CP内容（角色配对图片）
        
        Args:
            args: 包含两个角色名称的字符串，用空格分隔
        
        Returns:
            图片二进制数据
        """
        names = args.split()
        if len(names) < 2:
            raise ValueError('请提供两个角色名称！')

        # 获取CP API URL并发送请求
        url = plugin_config.fun_content_api_urls.get("cp")
        if not url:
            raise ValueError("CP API配置错误")

        try:
            response = await self.client.get(url, params={"n1": names[0], "n2": names[1]})
            response.raise_for_status()
            return response.content  # 返回图片二进制数据
        except Exception as e:
            error_msg = response_handler.format_error(e, "cp")
            logger.error(error_msg)
            raise ValueError(error_msg)

    async def close(self):
        """关闭HTTP客户端连接池"""
        await self.client.aclose()


# API单例实例
api = API()