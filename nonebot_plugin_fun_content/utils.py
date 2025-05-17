import time
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from nonebot import logger
from .config import plugin_config


class Utils:
    # 提取硬编码字符串为类属性
    SWITCH_KEY = "开关"
    SCHEDULED_KEY = "定时"

    def __init__(self):
        """初始化工具类
        - 管理命令冷却
        - 处理数据持久化
        - 提供功能开关和定时任务管理
        """
        self.cooldowns: Dict[str, Dict[str, Dict[str, float]]] = {}  # 命令冷却时间记录
        self.persistent_data_file = Path(plugin_config.persistent_data_file)  # 持久化数据文件路径
        self.default_data: Dict[str, Dict[str, Any]] = {  # 默认数据结构
            self.SWITCH_KEY: {},
            self.SCHEDULED_KEY: {}
        }
        self.persistent_data = self._load_persistent_data()  # 加载持久化数据

    def _ensure_file_exists(self) -> None:
        """确保持久化数据文件存在"""
        if not self.persistent_data_file.exists():
            logger.info(f"创建持久化数据文件: {self.persistent_data_file}")
            self._save_persistent_data(self.default_data)

    def _load_persistent_data(self) -> Dict[str, Any]:
        """
        从JSON文件加载持久化数据
        - 自动创建不存在的文件
        - 处理加载过程中的异常情况
        Returns:
            Dict[str, Any]: 加载的数据，失败时返回默认数据
        """
        self._ensure_file_exists()
        try:
            data = json.loads(self.persistent_data_file.read_text(encoding='utf-8'))
            logger.info(f"成功加载持久化数据: {self.persistent_data_file}")
            # 确保必要的键存在
            data.setdefault(self.SWITCH_KEY, {})
            data.setdefault(self.SCHEDULED_KEY, {})
            return data
        except json.JSONDecodeError:
            logger.error(f"JSON解析错误: {self.persistent_data_file}")
        except FileNotFoundError:
            logger.error(f"文件不存在: {self.persistent_data_file}")
        except Exception as e:
            logger.error(f"加载数据时发生未知错误: {e}")
        return self.default_data  # 出错时返回默认数据

    def _save_persistent_data(self, data: Optional[Dict[str, Any]] = None) -> None:
        """
        将数据保存到JSON文件
        Args:
            data: 要保存的数据，默认为当前持久化数据
        """
        data_to_save = data if data is not None else self.persistent_data
        try:
            self._ensure_directory_exists()  # 确保目录存在
            # 写入格式化的JSON数据
            self.persistent_data_file.write_text(
                json.dumps(data_to_save, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
            logger.info(f"成功保存持久化数据: {self.persistent_data_file}")
        except (PermissionError, TypeError, ValueError) as e:
            logger.error(f"保存数据失败: {e}")
        except Exception as e:
            logger.error(f"保存数据时发生未知错误: {e}")

    def _ensure_directory_exists(self) -> None:
        """确保持久化数据文件所在目录存在"""
        self.persistent_data_file.parent.mkdir(parents=True, exist_ok=True)

    def _get_group_sub_data(self, key: str, group_id: str) -> Dict[str, Any]:
        """
        获取群组特定的数据子项
        Args:
            key: 数据键（如"开关"或"定时"）
            group_id: 群组ID
        Returns:
            Dict[str, Any]: 群组数据子项，不存在时初始化
        """
        if key == self.SWITCH_KEY:
            # 开关数据默认所有命令都开启
            self.persistent_data[key].setdefault(
                group_id, 
                {cmd: True for cmd in plugin_config.COMMANDS}
            )
        else:
            self.persistent_data[key].setdefault(group_id, {})
        return self.persistent_data[key][group_id]

    def get_group_config(self, group_id: str) -> Dict[str, Any]:
        """
        获取群组完整配置
        Args:
            group_id: 群组ID
        Returns:
            Dict[str, Any]: 包含开关和定时任务的配置
        """
        return {
            self.SWITCH_KEY: self._get_group_sub_data(self.SWITCH_KEY, group_id),
            self.SCHEDULED_KEY: self._get_group_sub_data(self.SCHEDULED_KEY, group_id)
        }

    def is_function_enabled(self, group_id: str, function: str) -> bool:
        """
        检查功能是否启用
        Args:
            group_id: 群组ID
            function: 功能名称
        Returns:
            bool: 功能是否启用，默认True
        """
        return self._get_group_sub_data(self.SWITCH_KEY, group_id).get(function, True)

    def disable_function(self, group_id: str, function: str) -> None:
        """
        禁用指定功能并保存配置
        Args:
            group_id: 群组ID
            function: 功能名称
        """
        self._get_group_sub_data(self.SWITCH_KEY, group_id)[function] = False
        self._save_persistent_data()  # 保存更改

    def enable_function(self, group_id: str, function: str) -> None:
        """
        启用指定功能并保存配置
        Args:
            group_id: 群组ID
            function: 功能名称
        """
        self._get_group_sub_data(self.SWITCH_KEY, group_id)[function] = True
        self._save_persistent_data()  # 保存更改

    def get_scheduled_tasks(self, group_id: str) -> Dict[str, List[str]]:
        """
        获取群组的定时任务配置
        Args:
            group_id: 群组ID
        Returns:
            Dict[str, List[str]]: 定时任务配置
        """
        return self._get_group_sub_data(self.SCHEDULED_KEY, group_id)

    def add_scheduled_task(self, group_id: str, command: str, time_str: str) -> None:
        """
        添加定时任务并保存配置
        Args:
            group_id: 群组ID
            command: 命令名称
            time_str: 执行时间（HH:MM格式）
        """
        self._get_group_sub_data(self.SCHEDULED_KEY, group_id).setdefault(command, []).append(time_str)
        self._save_persistent_data()  # 保存更改

    def remove_scheduled_task(self, group_id: str, command: str, time_str: str) -> bool:
        """
        移除定时任务并保存配置
        Args:
            group_id: 群组ID
            command: 命令名称
            time_str: 执行时间
        Returns:
            bool: 是否成功移除
        """
        tasks = self._get_group_sub_data(self.SCHEDULED_KEY, group_id).get(command, [])
        if time_str in tasks:
            tasks.remove(time_str)
            # 清理空数据结构
            if not tasks:
                del self.persistent_data[self.SCHEDULED_KEY][group_id][command]
            if not self.persistent_data[self.SCHEDULED_KEY][group_id]:
                del self.persistent_data[self.SCHEDULED_KEY][group_id]
            self._save_persistent_data()  # 保存更改
            return True
        return False

    def is_valid_time_format(self, time_str: str) -> bool:
        """
        验证时间格式是否为HH:MM
        Args:
            time_str: 时间字符串
        Returns:
            bool: 格式是否有效
        """
        try:
            hours, minutes = map(int, time_str.split(':'))
            return 0 <= hours < 24 and 0 <= minutes < 60
        except ValueError:
            return False

    def is_in_cooldown(self, command: str, user_id: str, group_id: str) -> bool:
        """
        检查命令是否在冷却中
        Args:
            command: 命令名称
            user_id: 用户ID
            group_id: 群组ID
        Returns:
            bool: 是否在冷却中
        """
        current_time = time.time()
        last_use = self.cooldowns.get(command, {}).get(group_id, {}).get(user_id, 0)
        return current_time < last_use

    def set_cooldown(self, command: str, user_id: str, group_id: str, duration: int) -> None:
        """
        设置命令冷却时间
        Args:
            command: 命令名称
            user_id: 用户ID
            group_id: 群组ID
            duration: 冷却时长（秒）
        """
        self.cooldowns.setdefault(command, {}).setdefault(group_id, {})[user_id] = time.time() + duration

    def get_cooldown_time(self, command: str, user_id: str, group_id: str) -> float:
        """
        获取命令剩余冷却时间
        Args:
            command: 命令名称
            user_id: 用户ID
            group_id: 群组ID
        Returns:
            float: 剩余冷却时间（秒）
        """
        last_use = self.cooldowns.get(command, {}).get(group_id, {}).get(user_id, 0)
        return max(0, last_use - time.time())


# 创建 Utils 实例
utils = Utils()