import time
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from .config import plugin_config

# 设置日志记录器
logger = logging.getLogger(__name__)

class Utils:
    def __init__(self):
        self.cooldowns: Dict[str, Dict[str, Dict[str, float]]] = {}
        self.persistent_data = self._load_persistent_data()

    def _load_persistent_data(self) -> Dict[str, Any]:
        """从文件加载持久化数据"""
        file_path = Path(plugin_config.persistent_data_file)
        default_data = {"开关": {}, "定时": {}}

        if not file_path.exists():
            logger.info(f"Persistent data file not found. Creating new file at {file_path}")
            self._save_persistent_data(default_data)
            return default_data

        try:
            with file_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Successfully loaded persistent data from {file_path}")

            # 确保数据结构正确
            data.setdefault("开关", {})
            data.setdefault("定时", {})
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {file_path}: {str(e)}")
            return default_data
        except Exception as e:
            logger.error(f"Unexpected error loading data: {str(e)}")
            return default_data

    def _save_persistent_data(self, data: Optional[Dict[str, Any]] = None) -> None:
        """保存持久化数据到文件"""
        data_to_save = data if data is not None else self.persistent_data
        file_path = Path(plugin_config.persistent_data_file)

        try:
            # 自动创建父目录
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with file_path.open('w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully saved persistent data to {file_path}")
        except (PermissionError, TypeError, ValueError) as e:
            logger.error(f"Failed to save data: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error while saving: {str(e)}")

    def get_group_config(self, group_id: str) -> Dict[str, Any]:
        """
        获取指定群组的配置

        :param group_id: 群组 ID
        :return: 包含群组配置的字典
        """
        if group_id not in self.persistent_data["开关"]:
            self.persistent_data["开关"][group_id] = {cmd: True for cmd in plugin_config.COMMANDS}
        if group_id not in self.persistent_data["定时"]:
            self.persistent_data["定时"][group_id] = {}
        return {
            "开关": self.persistent_data["开关"][group_id],
            "定时": self.persistent_data["定时"][group_id]
        }

    def is_function_enabled(self, group_id: str, function: str) -> bool:
        """
        检查指定群组中的功能是否启用

        :param group_id: 群组 ID
        :param function: 功能名称
        :return: 如果功能启用则返回 True，否则返回 False
        """
        return self.get_group_config(group_id)["开关"].get(function, True)

    def disable_function(self, group_id: str, function: str) -> None:
        """
        禁用指定群组中的功能

        :param group_id: 群组 ID
        :param function: 要禁用的功能名称
        """
        self.persistent_data["开关"].setdefault(group_id, {})[function] = False
        self._save_persistent_data()

    def enable_function(self, group_id: str, function: str) -> None:
        """
        启用指定群组中的功能

        :param group_id: 群组 ID
        :param function: 要启用的功能名称
        """
        self.persistent_data["开关"].setdefault(group_id, {})[function] = True
        self._save_persistent_data()

    def get_scheduled_tasks(self, group_id: str) -> Dict[str, List[str]]:
        """
        获取指定群组的定时任务

        :param group_id: 群组 ID
        :return: 包含该群组定时任务的字典
        """
        return self.persistent_data["定时"].get(group_id, {})

    def add_scheduled_task(self, group_id: str, command: str, time: str) -> None:
        """
        添加定时任务

        :param group_id: 群组 ID
        :param command: 要执行的命令
        :param time: 执行时间
        """
        if group_id not in self.persistent_data["定时"]:
            self.persistent_data["定时"][group_id] = {}
        if command not in self.persistent_data["定时"][group_id]:
            self.persistent_data["定时"][group_id][command] = []
        if time not in self.persistent_data["定时"][group_id][command]:
            self.persistent_data["定时"][group_id][command].append(time)
            self._save_persistent_data()

    def remove_scheduled_task(self, group_id: str, command: str, time: str) -> bool:
        """
        移除定时任务

        :param group_id: 群组 ID
        :param command: 要移除的命令
        :param time: 执行时间
        :return: 如果成功移除返回 True，否则返回 False
        """
        if (group_id in self.persistent_data["定时"] and 
            command in self.persistent_data["定时"][group_id] and 
            time in self.persistent_data["定时"][group_id][command]):
            self.persistent_data["定时"][group_id][command].remove(time)
            if not self.persistent_data["定时"][group_id][command]:
                del self.persistent_data["定时"][group_id][command]
            if not self.persistent_data["定时"][group_id]:
                del self.persistent_data["定时"][group_id]
            self._save_persistent_data()
            return True
        return False

    def is_valid_time_format(self, time_str: str) -> bool:
        """
        检查时间格式是否有效

        :param time_str: 时间字符串
        :return: 如果格式有效返回 True，否则返回 False
        """
        try:
            hours, minutes = map(int, time_str.split(':'))
            return 0 <= hours < 24 and 0 <= minutes < 60
        except ValueError:
            return False

    def is_in_cooldown(self, command: str, user_id: str, group_id: str) -> bool:
        """
        检查命令是否在冷却中

        :param command: 命令名称
        :param user_id: 用户 ID
        :param group_id: 群组 ID
        :return: 如果命令在冷却中返回 True，否则返回 False
        """
        current_time = time.time()
        last_use = self.cooldowns.get(command, {}).get(group_id, {}).get(user_id, 0)
        return current_time < last_use

    def set_cooldown(self, command: str, user_id: str, group_id: str, duration: int) -> None:
        """
        设置命令的冷却时间

        :param command: 命令名称
        :param user_id: 用户 ID
        :param group_id: 群组 ID
        :param duration: 冷却时间（秒）
        """
        if command not in self.cooldowns:
            self.cooldowns[command] = {}
        if group_id not in self.cooldowns[command]:
            self.cooldowns[command][group_id] = {}
        self.cooldowns[command][group_id][user_id] = time.time() + duration

    def get_cooldown_time(self, command: str, user_id: str, group_id: str) -> float:
        """
        获取命令的剩余冷却时间

        :param command: 命令名称
        :param user_id: 用户 ID
        :param group_id: 群组 ID
        :return: 剩余冷却时间（秒）
        """
        last_use = self.cooldowns.get(command, {}).get(group_id, {}).get(user_id, 0)
        return max(0, last_use - time.time())

# 创建 Utils 实例
utils = Utils()