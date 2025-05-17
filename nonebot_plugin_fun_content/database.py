import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

import aiosqlite

from nonebot import logger
from .config import plugin_config


class DatabasePool:
    """数据库连接池
    - 管理多个数据库连接，提高并发访问效率
    - 实现连接的获取、释放和自动回收
    """
    def __init__(self, db_path: Path, pool_size: int = 5):
        self.db_path = db_path
        self.pool_size = pool_size
        self._pool: List[aiosqlite.Connection] = []  # 连接池列表
        self._pool_lock = asyncio.Lock()  # 用于线程安全的锁
        self._initialized = False  # 初始化状态标志

    async def initialize(self):
        """初始化连接池
        - 创建指定数量的数据库连接
        - 设置数据库连接参数
        """
        if self._initialized:
            return

        async with self._pool_lock:
            if self._initialized:  # 双重检查锁定模式
                return

            for _ in range(self.pool_size):
                conn = await self._create_connection()
                self._pool.append(conn)

            self._initialized = True
            logger.success(f"Database pool initialized with {self.pool_size} connections")

    async def _create_connection(self) -> aiosqlite.Connection:
        """创建新的数据库连接
        - 设置数据库连接参数
        - 启用WAL模式提高并发性能
        - 启用外键约束
        """
        conn = await aiosqlite.connect(self.db_path)
        await conn.execute("PRAGMA journal_mode=WAL")  # 启用WAL模式
        await conn.execute("PRAGMA foreign_keys=ON")   # 启用外键约束
        conn.row_factory = aiosqlite.Row  # 设置行工厂为字典类型
        return conn

    @asynccontextmanager
    async def acquire(self):
        """获取数据库连接的上下文管理器
        - 从连接池获取连接或创建新连接
        - 使用完毕后自动释放连接回池中
        - 发生异常时关闭连接
        """
        if not self._initialized:
            await self.initialize()

        async with self._pool_lock:
            # 从池中获取连接
            if self._pool:
                conn = self._pool.pop()
            else:
                # 如果池为空，创建新连接
                conn = await self._create_connection()
                logger.warning("Connection pool exhausted, creating new connection")

        try:
            yield conn
            # 将连接放回池中
            async with self._pool_lock:
                if len(self._pool) < self.pool_size:
                    self._pool.append(conn)
                else:
                    await conn.close()
        except Exception as e:
            # 发生错误时，确保连接被关闭而不是放回池中
            await conn.close()
            raise

    async def close_all(self):
        """关闭所有连接
        - 清理连接池中的所有连接
        - 设置初始化状态为False
        """
        async with self._pool_lock:
            for conn in self._pool:
                await conn.close()
            self._pool.clear()
            self._initialized = False
        logger.success("All database connections closed")


class DatabaseManager:
    def __init__(self):
        """初始化数据库管理器
        - 加载数据库配置
        - 初始化数据库连接池
        - 配置各数据表结构信息
        """
        self.db_path = plugin_config.fun_content_db_path
        if not self.db_path.exists():
            logger.error(f"Database file not found at {self.db_path}")
            raise FileNotFoundError(f"Database file not found at {self.db_path}")

        self.pool = DatabasePool(self.db_path)

        # 定义数据库表配置
        self.table_config = {
            "hitokoto": {
                "table": "hitokoto",
                "content_column": "content",
                "process_br": True
            },
            "twq": {
                "table": "twq",
                "content_column": "content",
                "process_br": True
            },
            "dog": {
                "table": "dog",
                "content_column": "content",
                "process_br": True
            },
            "aiqinggongyu": {
                "table": "aiqinggongyu",
                "content_column": "content",
                "process_br": True
            },
            "renjian": {
                "table": "renjian",
                "content_column": "content",
                "process_br": True
            },
            "joke": {
                "table": "jokes",
                "content_column": "content",
                "process_br": True
            },
            "shenhuifu": {
                "table": "shenhuifu",
                "questions_column": "questions",
                "answers_column": "answers",
                "process_br": False
            },
            "beauty_pic": {
                "table": "beauty_pic",
                "content_column": "url",
                "process_br": False
            }
        }

    @staticmethod
    def _process_text(content: str) -> str:
        """处理文本内容
        - 替换HTML换行标签为实际换行符
        - 去除多余空格和空行
        """
        if not content:
            return ""
        content = content.replace("<br>", "\n").replace("<br/>", "\n")
        return "\n".join(line.strip() for line in content.split("\n") if line.strip())

    async def _fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """执行查询并获取单条结果
        - 使用连接池获取数据库连接
        - 执行SQL查询并返回字典形式的结果
        """
        try:
            async with self.pool.acquire() as conn:
                async with conn.execute(query, params) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return {key: row[key] for key in row.keys()}
            return None
        except Exception as e:
            logger.error(f"Database query error: {str(e)}")
            raise

    async def get_random_content(self, command: str) -> Optional[str]:
        """获取随机内容
        Args:
            command: 命令名称，对应不同的内容类型
        Returns:
            Optional[str]: 随机内容，如果出错则返回None
        Raises:
            ValueError: 如果命令未知
        """
        config = self.table_config.get(command)
        if not config:
            raise ValueError(f"Unknown command: {command}")

        table = config["table"]
        content_column = config["content_column"]
        process_br = config.get("process_br", False)

        query = f"SELECT {content_column} FROM {table} ORDER BY RANDOM() LIMIT 1"

        try:
            result = await self._fetch_one(query)
            if not result:
                return None

            content = result[content_column]
            return self._process_text(content) if process_br else content
        except Exception as e:
            logger.error(f"Error getting random content for {command}: {e}")
            return None

    async def get_random_shenhuifu(self) -> Optional[Dict[str, str]]:
        """获取随机神回复
        Returns:
            Optional[Dict[str, str]]: 包含问题和答案的字典
        """
        config = self.table_config["shenhuifu"]
        query = f"""
            SELECT {config['questions_column']}, {config['answers_column']}
            FROM {config['table']}
            ORDER BY RANDOM()
            LIMIT 1
        """

        try:
            result = await self._fetch_one(query)
            if not result:
                return None

            return {
                "question": result[config['questions_column']],
                "answer": result[config['answers_column']]
            }
        except Exception as e:
            logger.error(f"Error getting random shenhuifu: {e}")
            return None

    async def get_random_beauty_pic(self) -> Optional[str]:
        """获取随机美女图片URL
        Returns:
            Optional[str]: 图片URL
        """
        config = self.table_config["beauty_pic"]
        query = f"SELECT {config['content_column']} FROM {config['table']} ORDER BY RANDOM() LIMIT 1"

        try:
            result = await self._fetch_one(query)
            return result[config['content_column']] if result else None
        except Exception as e:
            logger.error(f"Error getting random beauty pic URL: {e}")
            return None

    async def batch_get_random_content(self, commands: List[str],
                                       batch_size: int = 10) -> Dict[str, List[str]]:
        """批量获取随机内容
        Args:
            commands: 要获取内容的命令列表
            batch_size: 每个命令获取的数量
        Returns:
            Dict[str, List[str]]: 命令到内容列表的映射
        """
        results = {}
        async with self.pool.acquire() as conn:
            for command in commands:
                try:
                    config = self.table_config.get(command)
                    if not config:
                        continue

                    query = f"""
                        SELECT {config['content_column']} 
                        FROM {config['table']} 
                        ORDER BY RANDOM() 
                        LIMIT {batch_size}
                    """

                    contents = []
                    async with conn.execute(query) as cursor:
                        async for row in cursor:
                            content = row[0]
                            if config.get('process_br', False):
                                content = self._process_text(content)
                            contents.append(content)

                    results[command] = contents
                except Exception as e:
                    logger.error(f"Error in batch getting content for {command}: {e}")
                    results[command] = []

        return results

    async def close(self):
        """关闭数据库连接池"""
        await self.pool.close_all()


# 创建数据库管理器实例
db_manager = DatabaseManager()

# 确保程序退出时关闭连接池
import atexit
import asyncio


def cleanup_db():
    """清理数据库连接"""
    loop = asyncio.get_event_loop()
    if not loop.is_closed():
        loop.run_until_complete(db_manager.close())


atexit.register(cleanup_db)