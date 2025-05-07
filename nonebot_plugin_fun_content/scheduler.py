from io import BytesIO
from typing import Dict, List, Union, Optional, Tuple

from nonebot import require, get_bot, logger
from nonebot.adapters.onebot.v11 import MessageSegment, Message

from .api import api
from .database import db_manager
from .response_handler import response_handler

# 导入 nonebot 的调度器
scheduler = require("nonebot_plugin_apscheduler").scheduler


class Scheduler:
    def __init__(self):
        """初始化 Scheduler 类"""
        self.jobs: Dict[str, Dict[str, List[str]]] = {}  # {group_id: {command: [time1, time2, ...]}}

    def add_job(self, group_id: str, command: str, time: str):
        """添加定时任务

        Args:
            group_id (str): 群组ID
            command (str): 要执行的命令
            time (str): 任务执行时间（格式：HH:MM）
        """
        try:
            if not isinstance(time, str):
                logger.error(f"Invalid time format for group {group_id}, command {command}: {time}")
                return

            hour, minute = time.split(':')
            if not hour.isdigit() or not minute.isdigit():
                logger.error(f"Invalid time format for group {group_id}, command {command}: {time}")
                return

            hour = int(hour)
            minute = int(minute)
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                logger.error(f"Invalid time values for group {group_id}, command {command}: {time}")
                return

            if group_id not in self.jobs:
                self.jobs[group_id] = {}
            if command not in self.jobs[group_id]:
                self.jobs[group_id][command] = []

            if time not in self.jobs[group_id][command]:
                self.jobs[group_id][command].append(time)
                job_id = f"{group_id}_{command}_{time}"
                scheduler.add_job(
                    self.run_scheduled_task,
                    'cron',
                    id=job_id,
                    hour=hour,
                    minute=minute,
                    args=[group_id, command]
                )
                logger.info(f"Added new task: {command} at {time} for group {group_id}")
            else:
                logger.info(f"Task already exists: {command} at {time} for group {group_id}")
        except Exception as e:
            logger.error(f"Error adding job for group {group_id}, command {command}, time {time}: {str(e)}")

    def remove_job(self, group_id: str, command: str, time: str) -> bool:
        """移除定时任务

        Args:
            group_id (str): 群组ID
            command (str): 要移除的命令
            time (str): 任务执行时间

        Returns:
            bool: 如果成功移除返回True，否则返回False
        """
        if (group_id in self.jobs and 
            command in self.jobs[group_id] and 
            time in self.jobs[group_id][command]):
            self.jobs[group_id][command].remove(time)
            if not self.jobs[group_id][command]:
                del self.jobs[group_id][command]
            if not self.jobs[group_id]:
                del self.jobs[group_id]
            job_id = f"{group_id}_{command}_{time}"
            scheduler.remove_job(job_id)
            logger.info(f"Removed task: {command} at {time} for group {group_id}")
            return True
        logger.info(f"Task not found for removal: {command} at {time} for group {group_id}")
        return False

    def get_schedule_status(self, group_id: str) -> Dict[str, List[str]]:
        """获取指定群组的定时任务状态

        Args:
            group_id (str): 群组ID

        Returns:
            Dict[str, List[str]]: 包含该群组所有定时任务的字典
        """
        return self.jobs.get(group_id, {})

    async def run_scheduled_task(self, group_id: str, command: str):
        """执行定时任务

        Args:
            group_id (str): 群组ID
            command (str): 要执行的命令
        """
        try:
            bot = get_bot()
            result = await self.execute_command(command)

            if isinstance(result, tuple):
                # 处理返回多个消息的情况
                for msg in result:
                    if msg:
                        await bot.send_group_msg(group_id=int(group_id), message=msg)
            elif result:
                await bot.send_group_msg(group_id=int(group_id), message=result)

        except Exception as e:
            error_msg = response_handler.format_error(e, command)
            logger.error(f"Error in scheduled task: {e}", exc_info=True)
            try:
                bot = get_bot()
                await bot.send_group_msg(group_id=int(group_id), message=error_msg)
            except Exception as send_error:
                logger.error(f"Failed to send error message to group: {send_error}")

    async def execute_command(self, command: str) -> Optional[Union[Message, MessageSegment, Tuple[Message, ...], str]]:
        """执行指定的命令

        Args:
            command (str): 要执行的命令

        Returns:
            Optional[Union[Message, MessageSegment, Tuple[Message, ...], str]]: 命令执行的结果
        """
        try:
            if command == "beauty_pic":
                # 优先从数据库获取
                image_url = await db_manager.get_random_beauty_pic()
                if not image_url:
                    image_url = await api.get_beauty_pic()
                return MessageSegment.image(image_url)

            elif command == "cp":
                # CP命令需要默认角色名
                image_data = await api.get_cp_content("默认CP 默认CP2")
                return MessageSegment.image(BytesIO(image_data))

            elif command in ["hitokoto", "twq", "dog", "aiqinggongyu", "renjian", "joke", "shenhuifu"]:
                # 优先从数据库获取
                if command == "shenhuifu":
                    result = await db_manager.get_random_shenhuifu()
                    if result:
                        return Message(f"问：{result['question']}\n答：{result['answer']}")
                else:
                    result = await db_manager.get_random_content(command)
                    if result:
                        return Message(result)

                # 如果数据库获取失败，使用API
                result = await api.get_content(command)
                return Message(result)

            elif command in ["weibo_hot", "douyin_hot"]:
                result = await api.get_content(command)
                return Message(result)

            else:
                result = await api.get_content(command)
                return Message(result)

        except Exception as e:
            logger.error(f"Error executing command {command}: {e}")
            raise

    def clear_all_jobs(self):
        """清除所有定时任务"""
        for group_id in list(self.jobs.keys()):
            for command in list(self.jobs[group_id].keys()):
                for time in list(self.jobs[group_id][command]):
                    self.remove_job(group_id, command, time)
        self.jobs.clear()
        logger.info("Cleared all scheduled jobs")

# 创建 Scheduler 实例
scheduler_instance = Scheduler()