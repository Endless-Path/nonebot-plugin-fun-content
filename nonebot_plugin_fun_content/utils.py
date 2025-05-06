import time
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import plugin_config

# 设置日志记录器
logger = logging.getLogger(__name__)


class Utils:
    # 提取硬编码字符串为类属性
    SWITCH_KEY = "开关"
    SCHEDULED_KEY = "定时"

    def __init__(self):
        self.cooldowns: Dict[str, Dict[str, Dict[str, float]]] = {}
        self.persistent_data_file = Path(plugin_config.persistent_data_file)
        self.default_data: Dict[str, Dict[str, Any]] = {
            self.SWITCH_KEY: {},
            self.SCHEDULED_KEY: {}
        }
        self.persistent_data = self._load_persistent_data()

    def _ensure_file_exists(self) -> None:
        """
        确保持久化数据文件存在，如果不存在则创建。
        """
        if not self.persistent_data_file.exists():
            logger.info(f"Persistent data file not found. Creating new file at {self.persistent_data_file}")
            self._save_persistent_data(self.default_data)

    def _load_persistent_data(self) -> Dict[str, Any]:
        """
        加载持久化数据。
        如果文件不存在或解析出错，返回默认数据。

        :return: 包含持久化数据的字典
        """
        self._ensure_file_exists()
        try:
            data = json.loads(self.persistent_data_file.read_text(encoding='utf-8'))
            logger.info(f"Successfully loaded persistent data from {self.persistent_data_file}")
            data.setdefault(self.SWITCH_KEY, {})
            data.setdefault(self.SCHEDULED_KEY, {})
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {self.persistent_data_file}: {str(e)}")
        except FileNotFoundError:
            logger.error(f"File {self.persistent_data_file} not found.")
        except Exception as e:
            logger.error(f"Unexpected error loading data: {str(e)}")
        return self.default_data

    def _save_persistent_data(self, data: Optional[Dict[str, Any]] = None) -> None:
        """
        保存持久化数据到文件。

        :param data: 要保存的数据，默认为 self.persistent_data
        """
        data_to_save = data if data is not None else self.persistent_data
        try:
            self._ensure_directory_exists()
            self.persistent_data_file.write_text(json.dumps(data_to_save, indent=2, ensure_ascii=False), encoding='utf-8')
            logger.info(f"Successfully saved persistent data to {self.persistent_data_file}")
        except (PermissionError, TypeError, ValueError) as e:
            logger.error(f"Failed to save data: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error while saving: {str(e)}")

    def _ensure_directory_exists(self) -> None:
        """
        确保持久化数据文件所在目录存在。
        """
        self.persistent_data_file.parent.mkdir(parents=True, exist_ok=True)

    def _get_group_sub_data(self, key: str, group_id: str) -> Dict[str, Any]:
        """
        获取指定群组在特定键下的数据，如果不存在则初始化。

        :param key: 数据键，如 "开关" 或 "定时"
        :param group_id: 群组 ID
        :return: 包含群组特定数据的字典
        """
        if key == self.SWITCH_KEY:
            self.persistent_data[key].setdefault(group_id, {cmd: True for cmd in plugin_config.COMMANDS})
        else:
            self.persistent_data[key].setdefault(group_id, {})
        return self.persistent_data[key][group_id]

    def get_group_config(self, group_id: str) -> Dict[str, Any]:
        """
        获取指定群组的配置。

        :param group_id: 群组 ID
        :return: 包含群组配置的字典，包含 "开关" 和 "定时" 信息
        """
        return {
            self.SWITCH_KEY: self._get_group_sub_data(self.SWITCH_KEY, group_id),
            self.SCHEDULED_KEY: self._get_group_sub_data(self.SCHEDULED_KEY, group_id)
        }

    def is_function_enabled(self, group_id: str, function: str) -> bool:
        """
        检查指定群组中的功能是否启用。

        :param group_id: 群组 ID
        :param function: 功能名称
        :return: 如果功能启用则返回 True，否则返回 False
        """
        return self._get_group_sub_data(self.SWITCH_KEY, group_id).get(function, True)

    def disable_function(self, group_id: str, function: str) -> None:
        """
        禁用指定群组中的功能。

        :param group_id: 群组 ID
        :param function: 要禁用的功能名称
        """
        self._get_group_sub_data(self.SWITCH_KEY, group_id)[function] = False
        self._save_persistent_data()

    def enable_function(self, group_id: str, function: str) -> None:
        """
        启用指定群组中的功能。

        :param group_id: 群组 ID
        :param function: 要启用的功能名称
        """
        self._get_group_sub_data(self.SWITCH_KEY, group_id)[function] = True
        self._save_persistent_data()

    def get_scheduled_tasks(self, group_id: str) -> Dict[str, List[str]]:
        """
        获取指定群组的定时任务。

        :param group_id: 群组 ID
        :return: 包含该群组定时任务的字典
        """
        return self._get_group_sub_data(self.SCHEDULED_KEY, group_id)

    def add_scheduled_task(self, group_id: str, command: str, time_str: str) -> None:
        """
        添加定时任务。

        :param group_id: 群组 ID
        :param command: 要执行的命令
        :param time_str: 执行时间
        """
        self._get_group_sub_data(self.SCHEDULED_KEY, group_id).setdefault(command, []).append(time_str)
        self._save_persistent_data()

    def remove_scheduled_task(self, group_id: str, command: str, time_str: str) -> bool:
        """
        移除定时任务。

        :param group_id: 群组 ID
        :param command: 要移除的命令
        :param time_str: 执行时间
        :return: 如果成功移除返回 True，否则返回 False
        """
        tasks = self._get_group_sub_data(self.SCHEDULED_KEY, group_id).get(command, [])
        if time_str in tasks:
            tasks.remove(time_str)
            if not tasks:
                del self.persistent_data[self.SCHEDULED_KEY][group_id][command]
            if not self.persistent_data[self.SCHEDULED_KEY][group_id]:
                del self.persistent_data[self.SCHEDULED_KEY][group_id]
            self._save_persistent_data()
            return True
        return False

    def is_valid_time_format(self, time_str: str) -> bool:
        """
        检查时间格式是否有效。

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
        检查命令是否在冷却中。

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
        设置命令的冷却时间。

        :param command: 命令名称
        :param user_id: 用户 ID
        :param group_id: 群组 ID
        :param duration: 冷却时间（秒）
        """
        self.cooldowns.setdefault(command, {}).setdefault(group_id, {})[user_id] = time.time() + duration

    def get_cooldown_time(self, command: str, user_id: str, group_id: str) -> float:
        """
        获取命令的剩余冷却时间。

        :param command: 命令名称
        :param user_id: 用户 ID
        :param group_id: 群组 ID
        :return: 剩余冷却时间（秒）
        """
        last_use = self.cooldowns.get(command, {}).get(group_id, {}).get(user_id, 0)
        return max(0, last_use - time.time())


# 创建 Utils 实例
utils = Utils()