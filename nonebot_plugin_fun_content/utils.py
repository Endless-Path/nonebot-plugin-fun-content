import time
from typing import Dict
from .config import Config
from nonebot import get_driver

# 获取全局配置
global_config = get_driver().config
# 解析插件特定配置
config = Config.parse_obj(global_config)

class Utils:
    """
    工具类，主要用于管理命令冷却时间
    """
    def __init__(self):
        self.cooldowns: Dict[str, Dict[str, Dict[str, float]]] = {}

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
        cooldown_time = config.fun_content_cooldowns.get(command, 0)
        return current_time - last_use < cooldown_time

    def set_cooldown(self, command: str, user_id: str, group_id: str) -> None:
        """
        设置用户的冷却时间
        :param command: 命令名称
        :param user_id: 用户 ID
        :param group_id: 群组 ID
        """
        if command not in self.cooldowns:
            self.cooldowns[command] = {}
        if group_id not in self.cooldowns[command]:
            self.cooldowns[command][group_id] = {}
        self.cooldowns[command][group_id][user_id] = time.time()

    def get_cooldown_time(self, command: str, user_id: str, group_id: str) -> float:
        """
        获取用户的剩余冷却时间
        :param command: 命令名称
        :param user_id: 用户 ID
        :param group_id: 群组 ID
        :return: 剩余冷却时间（秒）
        """
        last_use = self.cooldowns.get(command, {}).get(group_id, {}).get(user_id, 0)
        return max(0, config.fun_content_cooldowns[command] - (time.time() - last_use))
    
utils = Utils()     #定义了Utils对象    