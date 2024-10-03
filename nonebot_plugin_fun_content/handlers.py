from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment, Message, MessageEvent, GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from .utils import utils
from .api import api
from .config import plugin_config
import logging
import httpx
from io import BytesIO
from typing import Dict, Tuple, List, Union
import os
import asyncio

# 设置日志记录
logger = logging.getLogger(__name__)

# 定义命令及其别名，以及是否允许参数
COMMANDS: Dict[str, Dict[str, Union[Tuple[str, List[str]], bool]]] = {
    "hitokoto": {"aliases": ("一言", []), "allow_args": False},
    "twq": {"aliases": ("土味情话", ["情话", "土味"]), "allow_args": False},
    "dog": {"aliases": ("舔狗日记", ["dog", "舔狗"]), "allow_args": False},
    "wangyiyun": {"aliases": ("网抑云", []), "allow_args": False}, 
    "renjian": {"aliases": ("人间凑数", []), "allow_args": False},
    "weibo_hot": {"aliases": ("微博热搜", ["微博"]), "allow_args": False},
    "douyin_hot": {"aliases": ("抖音热搜", ["抖音"]), "allow_args": False}, 
    "aiqinggongyu": {"aliases": ("爱情公寓", []), "allow_args": False},
    "beauty_pic": {"aliases": ("随机美女", ["美女"]), "allow_args": False},
    "cp": {"aliases": ("cp", ["宇宙cp"]), "allow_args": True},
    "shenhuifu": {"aliases": ("神回复", ["神评"]), "allow_args": False},
    "joke": {"aliases": ("讲个笑话", ["笑话"]), "allow_args": False},
    "lazy_sing": {"aliases": ("懒洋洋唱歌", ["懒洋洋", "唱歌"]), "allow_args": False},
}

def register_handlers():
    # 注册命令处理器
    for cmd, info in COMMANDS.items():
        main_alias, other_aliases = info["aliases"]
        matcher = on_command(main_alias, aliases=set(other_aliases), priority=5)
        matcher.handle()(handle_command(cmd))

    # 注册启用和禁用命令
    enable_cmd = on_command("开启", 
                            permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
                            priority=1, block=True)
    disable_cmd = on_command("关闭", 
                             permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
                             priority=1, block=True)
    status_cmd = on_command("功能状态", 
                            permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
                            priority=1, block=True)

    enable_cmd.handle()(handle_enable)
    disable_cmd.handle()(handle_disable)
    status_cmd.handle()(handle_status)

async def handle_enable(matcher: Matcher, event: GroupMessageEvent, args: Message = CommandArg()):
    """处理启用功能的命令"""
    function = args.extract_plain_text().strip()
    group_id = str(event.group_id)

    for cmd, info in COMMANDS.items():
        main_alias, other_aliases = info["aliases"]
        if function == main_alias or function in other_aliases:
            utils.enable_function(group_id, cmd)
            await matcher.finish(f"{main_alias}已启用。")
    
    await matcher.finish(f"未找到名为 '{function}' 的功能。")

async def handle_disable(matcher: Matcher, event: GroupMessageEvent, args: Message = CommandArg()):
    """处理禁用功能的命令"""
    function = args.extract_plain_text().strip()
    group_id = str(event.group_id)

    for cmd, info in COMMANDS.items():
        main_alias, other_aliases = info["aliases"]
        if function == main_alias or function in other_aliases:
            utils.disable_function(group_id, cmd)
            await matcher.finish(f"{main_alias}已禁用。")
    
    await matcher.finish(f"未找到名为 '{function}' 的功能。")

async def handle_status(matcher: Matcher, event: GroupMessageEvent):
    """获取当前群组功能状态"""
    group_id = str(event.group_id)
    status_messages = []
    for cmd, info in COMMANDS.items():
        main_alias, _ = info["aliases"]
        status = "已启用" if utils.is_function_enabled(group_id, cmd) else "已禁用"
        status_messages.append(f"{main_alias}: {status}")
    
    await matcher.finish("\n".join(status_messages))

def handle_command(command: str):
    """返回命令处理函数"""
    async def handler(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
        # 检查是否为群消息事件
        if isinstance(event, GroupMessageEvent):
            group_id = str(event.group_id)
            if not utils.is_function_enabled(group_id, command):
                logger.info(f"Function {command} is disabled in group {group_id}")
                await matcher.finish(f"该功能在本群已被禁用")

        # 检查命令是否允许参数
        if not COMMANDS[command]["allow_args"] and args.extract_plain_text().strip():
            # 如果命令不允许参数但用户提供了参数，直接结束处理而不发送任何消息
            await matcher.finish()

        user_id = str(event.user_id)
        group_id = str(event.group_id) if isinstance(event, GroupMessageEvent) else "private"

        # 检查冷却时间
        cooldown = plugin_config.fun_content_cooldowns.get(command, 20)
        if utils.is_in_cooldown(command, user_id, group_id):
            remaining_cd = utils.get_cooldown_time(command, user_id, group_id)
            logger.info(f"Command {command} is in cooldown for user {user_id} in group {group_id}")
            await matcher.finish(f"指令冷却中，请等待 {int(remaining_cd)} 秒再试喵~")

        try:
            # 根据命令类型调用相应的 API
            if command == "cp":
                image_data = await api.get_cp_content(args.extract_plain_text().strip())
                try:
                    await matcher.send(MessageSegment.image(BytesIO(image_data)))
                except Exception as e:
                    logger.error(f"Failed to send image for CP command: {e}")
                    await matcher.send("CP 图片生成成功，但发送失败。请稍后再试。")
            elif command == "beauty_pic":
                image_url = await api.get_beauty_pic()
                try:
                    await matcher.send(MessageSegment.image(image_url))
                except Exception as e:
                    logger.error(f"Failed to send image for beauty pic command: {e}")
                    await matcher.send(f"美女图片获取成功，但发送失败。请访问以下链接查看：{image_url}")
            elif command == "lazy_sing":
                await matcher.send("懒洋洋正在准备唱歌，请稍候...")
                mp3_filename = await api.get_lazy_song()
                try:
                    await matcher.send(MessageSegment.record(file=mp3_filename))
                    await matcher.send("懒洋洋唱完啦！")
                except Exception as e:
                    logger.error(f"Failed to send voice message for lazy sing command: {e}")
                    await matcher.send("懒洋洋唱歌时出了点小问题，请稍后再试。")
                finally:
                    if mp3_filename and os.path.exists(mp3_filename):
                        os.remove(mp3_filename)
            else:
                result = await api.get_content(command)
                await matcher.send(result)
            
            utils.set_cooldown(command, user_id, group_id, cooldown)
        except ValueError as e:
            logger.error(f"ValueError in {command} command: {str(e)}")
            await matcher.send(f"出错了：{str(e)}")
        except httpx.HTTPError as e:
            logger.error(f"HTTP error in {command} command: {str(e)}")
            await matcher.send(f"网络请求错误：{str(e)}")
        except asyncio.TimeoutError:
            logger.error(f"Timeout error in {command} command")
            await matcher.send("请求超时，请稍后再试")
        except Exception as e:
            logger.error(f"Unexpected error in {command} command: {str(e)}", exc_info=True)
            await matcher.send(f"发生未知错误，请稍后再试")

    return handler