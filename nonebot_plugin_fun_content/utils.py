import os
import json
import nonebot
import time
from typing import Dict, Any

class Utils:
    def __init__(self) -> None:
        # 初始化冷却时间目录，存储每个命令的用户冷却时间
        self.cooldown_dirs: Dict[str, Dict[str, Dict[str, float]]] = {cmd: {} for cmd in [
            "dog", "twq", "hitokoto", "renjian", "weibo_hot",
            "aiqinggongyu", "baisi", "cp", "shenhuifu"
        ]}

        # 从配置中获取默认冷却时间（秒），可通过配置文件进行调整
        config = nonebot.get_driver().config
        self.default_cooldowns = {
            cmd: getattr(config, f"{cmd}_cd", 20) for cmd in self.cooldown_dirs.keys()
        }

        # 加载群组数据
        self.groupdata = self.load_group_data()

    def load_group_data(self) -> Dict[str, Any]:
        """加载群组数据"""
        data_dir = "data/fun-content"
        group_data_file = os.path.join(data_dir, "groupdata.json")

        # 检查群组数据文件是否存在
        if os.path.exists(group_data_file):
            try:
                with open(group_data_file, "r", encoding="utf-8") as f:
                    return json.load(f)  # 这里可以根据需要返回特定群组的数据
            except (IOError, json.JSONDecodeError) as e:
                nonebot.logger.error(f"加载群组数据失败: {e}")
                return {}
        else:
            # 如果文件不存在，则创建相应的目录
            os.makedirs(data_dir, exist_ok=True)
            return {}

    def write_group_data(self, group_id: str) -> None:
        """写入特定群组的配置"""
        data_dir = "data/fun-content"
        group_data_file = os.path.join(data_dir, "groupdata.json")

        try:
            # 将当前群组数据写入文件
            # 可以根据群组 ID 创建一个结构来存储特定群组的数据
            with open(group_data_file, "w", encoding="utf-8") as f:
                json.dump(self.groupdata, f, indent=4)
        except IOError as e:
            nonebot.logger.error(f"写入群组数据失败: {e}")

    def is_in_cooldown(self, command: str, user_id: str, group_id: str) -> bool:
        """检查用户是否在冷却时间内"""
        current_time = time.time()
        if user_id in self.cooldown_dirs[command].get(group_id, {}):
            if current_time - self.cooldown_dirs[command][group_id][user_id] < self.default_cooldowns[command]:
                return True
        return False

    def set_cooldown(self, command: str, user_id: str, group_id: str) -> None:
        """设置用户的冷却时间"""
        if group_id not in self.cooldown_dirs[command]:
            self.cooldown_dirs[command][group_id] = {}
        self.cooldown_dirs[command][group_id][user_id] = time.time()
        nonebot.logger.info(f"设置 {user_id} 的命令 {command} 冷却时间在群组 {group_id} 中。")

    def get_cooldown_time(self, command: str, user_id: str, group_id: str) -> float:
        """获取用户的剩余冷却时间"""
        if user_id in self.cooldown_dirs[command].get(group_id, {}):
            return self.default_cooldowns[command] - (time.time() - self.cooldown_dirs[command][group_id][user_id])
        return 0.0

    def reset_cooldown(self, command: str, user_id: str, group_id: str) -> None:
        """重置用户的冷却时间"""
        if user_id in self.cooldown_dirs[command].get(group_id, {}):
            del self.cooldown_dirs[command][group_id][user_id]

    def clear_cooldowns(self) -> None:
        """清除所有用户的冷却时间"""
        for command in self.cooldown_dirs:
            self.cooldown_dirs[command].clear()

    def get_all_cooldowns(self) -> Dict[str, Dict[str, float]]:
        """获取所有指令的冷却状态"""
        return {command: {group_id: len(users) for group_id, users in user_data.items()} for command, user_data in self.cooldown_dirs.items()}

    def register_command(self, command: str) -> None:
        """动态注册命令，以便于扩展和维护"""
        if command not in self.cooldown_dirs:
            self.cooldown_dirs[command] = {}
            self.default_cooldowns[command] = 20  # 默认冷却时间20秒

# 创建 Utils 实例
utils = Utils()
