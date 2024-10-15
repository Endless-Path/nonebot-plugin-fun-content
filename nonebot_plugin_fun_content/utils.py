import time
import json
import os
from typing import Dict, Any, List
from .config import plugin_config
import logging

logger = logging.getLogger(__name__)

class Utils:
    def __init__(self):
        self.cooldowns: Dict[str, Dict[str, Dict[str, float]]] = {}
        self.persistent_data = self._load_persistent_data()

    def _load_persistent_data(self) -> Dict[str, Any]:
        file_path = plugin_config.persistent_data_file
        default_data = {
            "开关": {},
            "定时": {}
        }
        
        if not os.path.exists(file_path):
            logger.info(f"Persistent data file not found. Creating new file at {file_path}")
            self._save_persistent_data(default_data)
            return default_data
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Successfully loaded persistent data from {file_path}")
            
            # 确保数据结构正确
            if "开关" not in data:
                data["开关"] = {}
            if "定时" not in data:
                data["定时"] = {}
            
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {file_path}: {str(e)}")
            return default_data
        except Exception as e:
            logger.error(f"Unexpected error loading data from {file_path}: {str(e)}")
            return default_data

    def _save_persistent_data(self, data: Dict[str, Any] = None):
        if data is None:
            data = self.persistent_data
        try:
            with open(plugin_config.persistent_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully saved persistent data to {plugin_config.persistent_data_file}")
        except Exception as e:
            logger.error(f"Error saving persistent data: {str(e)}")

    def get_group_config(self, group_id: str) -> Dict[str, Any]:
        if group_id not in self.persistent_data["开关"]:
            self.persistent_data["开关"][group_id] = {cmd: True for cmd in plugin_config.COMMANDS}
        if group_id not in self.persistent_data["定时"]:
            self.persistent_data["定时"][group_id] = {}
        return {
            "开关": self.persistent_data["开关"][group_id],
            "定时": self.persistent_data["定时"][group_id]
        }

    def is_function_enabled(self, group_id: str, function: str) -> bool:
        return self.get_group_config(group_id)["开关"].get(function, True)

    def disable_function(self, group_id: str, function: str) -> None:
        self.persistent_data["开关"].setdefault(group_id, {})[function] = False
        self._save_persistent_data()

    def enable_function(self, group_id: str, function: str) -> None:
        self.persistent_data["开关"].setdefault(group_id, {})[function] = True
        self._save_persistent_data()

    def get_scheduled_tasks(self, group_id: str) -> Dict[str, List[str]]:
        return self.persistent_data["定时"].get(group_id, {})

    def add_scheduled_task(self, group_id: str, command: str, time: str) -> None:
        if group_id not in self.persistent_data["定时"]:
            self.persistent_data["定时"][group_id] = {}
        if command not in self.persistent_data["定时"][group_id]:
            self.persistent_data["定时"][group_id][command] = []
        if time not in self.persistent_data["定时"][group_id][command]:
            self.persistent_data["定时"][group_id][command].append(time)
            self._save_persistent_data()

    def remove_scheduled_task(self, group_id: str, command: str, time: str) -> bool:
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
        try:
            hours, minutes = map(int, time_str.split(':'))
            return 0 <= hours < 24 and 0 <= minutes < 60
        except ValueError:
            return False

    def is_in_cooldown(self, command: str, user_id: str, group_id: str) -> bool:
        current_time = time.time()
        last_use = self.cooldowns.get(command, {}).get(group_id, {}).get(user_id, 0)
        return current_time < last_use

    def set_cooldown(self, command: str, user_id: str, group_id: str, duration: int) -> None:
        if command not in self.cooldowns:
            self.cooldowns[command] = {}
        if group_id not in self.cooldowns[command]:
            self.cooldowns[command][group_id] = {}
        self.cooldowns[command][group_id][user_id] = time.time() + duration

    def get_cooldown_time(self, command: str, user_id: str, group_id: str) -> float:
        last_use = self.cooldowns.get(command, {}).get(group_id, {}).get(user_id, 0)
        return max(0, last_use - time.time())

utils = Utils()