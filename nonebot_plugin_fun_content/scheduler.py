from nonebot import require, get_bot
from nonebot.adapters.onebot.v11 import MessageSegment, Message
from typing import Dict, List, Union, Tuple
from .api import api
import logging
from io import BytesIO
import asyncio
import httpx
from pathlib import Path

# 导入 nonebot 的调度器
scheduler = require("nonebot_plugin_apscheduler").scheduler

# 设置日志记录器
logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self):
        """
        初始化 Scheduler 类
        创建一个空的任务字典来存储各个群组的定时任务
        """
        self.jobs: Dict[str, Dict[str, List[str]]] = {}  # {group_id: {command: [time1, time2, ...]}}

    def add_job(self, group_id: str, command: str, time: str):
        """
        添加一个新的定时任务

        :param group_id: 群组 ID
        :param command: 要执行的命令
        :param time: 任务执行时间（格式：HH:MM）
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
                scheduler.add_job(self.run_scheduled_task, 'cron', id=job_id,
                                  hour=hour, minute=minute, 
                                  args=[group_id, command])
                logger.info(f"Added new task: {command} at {time} for group {group_id}")
            else:
                logger.info(f"Task already exists: {command} at {time} for group {group_id}")
        except Exception as e:
            logger.error(f"Error adding job for group {group_id}, command {command}, time {time}: {str(e)}")

    def remove_job(self, group_id: str, command: str, time: str) -> bool:
        """
        移除一个定时任务

        :param group_id: 群组 ID
        :param command: 要移除的命令
        :param time: 任务执行时间
        :return: 如果成功移除返回 True，否则返回 False
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
        """
        获取指定群组的定时任务状态

        :param group_id: 群组 ID
        :return: 包含该群组所有定时任务的字典
        """
        return self.jobs.get(group_id, {})

    async def run_scheduled_task(self, group_id: str, command: str):
        """
        执行定时任务

        :param group_id: 群组 ID
        :param command: 要执行的命令
        """
        try:
            bot = get_bot()
            result = await self.execute_command(command)
            if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], Path):
                message, file_path = result
                await bot.send_group_msg(group_id=int(group_id), message=message)
                # 清理文件
                if file_path.exists():
                    file_path.unlink()
                if file_path.parent.exists() and not any(file_path.parent.iterdir()):
                    file_path.parent.rmdir()
            elif result:
                await bot.send_group_msg(group_id=int(group_id), message=result)
        except Exception as e:
            logger.error(f"Error in scheduled task: {e}", exc_info=True)

    async def execute_command(self, command: str) -> Union[Message, MessageSegment, Tuple[MessageSegment, Path], str]:
        """
        执行指定的命令

        :param command: 要执行的命令
        :return: 命令执行的结果，可能是消息、图片、音频文件或字符串
        """
        try:
            if command == "cp":
                image_data = await api.get_cp_content("")
                return MessageSegment.image(BytesIO(image_data))
            elif command == "beauty_pic":
                image_url = await api.get_beauty_pic()
                return MessageSegment.image(image_url)
            elif command == "lazy_sing":
                mp3_file = await api.get_lazy_song()
                result = MessageSegment.record(file=str(mp3_file))
                return result, mp3_file
            else:
                result = await api.get_content(command)
                return Message(result)
        except ValueError as e:
            logger.error(f"ValueError in {command} command: {str(e)}")
            return f"出错了：{str(e)}"
        except httpx.HTTPError as e:
            logger.error(f"HTTP error in {command} command: {str(e)}")
            return f"网络请求错误：{str(e)}"
        except asyncio.TimeoutError:
            logger.error(f"Timeout error in {command} command")
            return "请求超时，请稍后再试"
        except Exception as e:
            logger.error(f"Unexpected error in {command} command: {str(e)}", exc_info=True)
            return f"发生未知错误，请稍后再试"

    def clear_all_jobs(self):
        """
        清除所有定时任务
        """
        for group_id in list(self.jobs.keys()):
            for command in list(self.jobs[group_id].keys()):
                for time in list(self.jobs[group_id][command]):
                    self.remove_job(group_id, command, time)
        self.jobs.clear()
        logger.info("Cleared all scheduled jobs")

# 创建 Scheduler 实例
scheduler_instance = Scheduler()