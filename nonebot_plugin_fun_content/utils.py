import time
import json
import os
from typing import Dict, Set
from .config import plugin_config
from nonebot import get_driver

class Utils:
    """
    工具类，用于管理命令冷却时间和功能启用/禁用状态
    """
    def __init__(self):
        self.cooldowns: Dict[str, Dict[str, Dict[str, float]]] = {}
        self.disabled_functions: Dict[str, Set[str]] = self._load_disabled_functions()

    def _load_disabled_functions(self) -> Dict[str, Set[str]]:
        """
        从 JSON 文件加载禁用的功能
        如果文件不存在，则创建一个空文件
        """
        file_path = plugin_config.disabled_functions_file
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump({}, f)
            return {}

        with open(file_path, 'r') as f:
            data = json.load(f)
            # 将 JSON 中的列表转换为集合
            return {k: set(v) for k, v in data.items()}

    def _save_disabled_functions(self):
        """
        将禁用的功能保存到 JSON 文件
        """
        # 将集合转换为列表，因为 JSON 不能序列化集合
        data = {k: list(v) for k, v in self.disabled_functions.items()}
        with open(plugin_config.disabled_functions_file, 'w') as f:
            json.dump(data, f)

    def is_in_cooldown(self, command: str, user_id: str, group_id: str) -> bool:
        """
        检查用户是否在冷却时间内
        :param command: 命令名称
        :param user_id: 用户 ID
        :param group_id: 群组 ID
        :return: 是否在冷却时间内
        """
        current_time = time.time()
        last_use = self.cooldowns.get(command, {}).get(group_id, {}).get(user_id, 0)
        return current_time < last_use

    def set_cooldown(self, command: str, user_id: str, group_id: str, duration: int) -> None:
        """
        设置用户的冷却时间
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
        获取用户的剩余冷却时间
        :param command: 命令名称
        :param user_id: 用户 ID
        :param group_id: 群组 ID
        :return: 剩余冷却时间（秒）
        """
        last_use = self.cooldowns.get(command, {}).get(group_id, {}).get(user_id, 0)
        return max(0, last_use - time.time())

    def disable_function(self, group_id: str, function: str) -> None:
        """
        禁用某个群的某个功能
        :param group_id: 群组 ID
        :param function: 功能名称
        """
        if group_id not in self.disabled_functions:
            self.disabled_functions[group_id] = set()
        self.disabled_functions[group_id].add(function)
        self._save_disabled_functions()

    def enable_function(self, group_id: str, function: str) -> None:
        """
        启用某个群的某个功能
        :param group_id: 群组 ID
        :param function: 功能名称
        """
        if group_id in self.disabled_functions:
            self.disabled_functions[group_id].discard(function)
            self._save_disabled_functions()

    def is_function_enabled(self, group_id: str, function: str) -> bool:
        """
        检查某个群的某个功能是否启用
        :param group_id: 群组 ID
        :param function: 功能名称
        :return: 功能是否启用
        """
        return function not in self.disabled_functions.get(group_id, set())

# 创建 Utils 实例
utils = Utils()