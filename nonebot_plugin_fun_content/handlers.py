from io import BytesIO
from typing import TypedDict

from nonebot import on_command, logger, get_bot
from nonebot.adapters.onebot.v11 import (
    MessageSegment, Message, MessageEvent, GroupMessageEvent
)
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER

from .utils import utils
from .api import api
from .config import plugin_config
from .scheduler import scheduler_instance as scheduler
from .response_handler import response_handler


class CommandConfig(TypedDict):
    """命令配置的类型定义
    Attributes:
        aliases: 命令别名元组，包含(主别名, [其他别名列表])
        allow_args: 是否允许命令带参数
    """
    aliases: tuple[str, list[str]]  # (主别名, [其他别名列表])
    allow_args: bool  # 是否允许命令带参数

# 定义命令及其别名配置
COMMANDS: dict[str, CommandConfig] = {
    "hitokoto": {"aliases": ("一言", []), "allow_args": False},
    "twq": {"aliases": ("土味情话", ["情话", "土味"]), "allow_args": False},
    "dog": {"aliases": ("舔狗日记", ["dog", "舔狗"]), "allow_args": False},
    "renjian": {"aliases": ("人间凑数", []), "allow_args": False},
    "weibo_hot": {"aliases": ("微博热搜", ["微博"]), "allow_args": False},
    "douyin_hot": {"aliases": ("抖音热搜", ["抖音"]), "allow_args": False},
    "aiqinggongyu": {"aliases": ("爱情公寓", []), "allow_args": False},
    "beauty_pic": {"aliases": ("随机美女", ["美女"]), "allow_args": False},
    "cp": {"aliases": ("cp", ["宇宙cp"]), "allow_args": True},
    "shenhuifu": {"aliases": ("神回复", ["神评"]), "allow_args": False},
    "joke": {"aliases": ("讲个笑话", ["笑话"]), "allow_args": False},
}


def register_handlers():
    """注册所有的命令处理器
    - 包括普通功能命令、管理命令和定时任务命令
    """
    # 注册普通功能命令
    for cmd, info in COMMANDS.items():
        main_alias, other_aliases = info["aliases"]
        matcher = on_command(main_alias, aliases=set(other_aliases), priority=5)
        matcher.handle()(handle_command(cmd))

    # 注册管理命令 - 群组功能开关控制
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

    # 注册定时任务相关命令
    set_schedule_cmd = on_command("设置",
                                  permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
                                  priority=1, block=True)
    schedule_status_cmd = on_command("定时任务状态",
                                     permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
                                     priority=1, block=True)
    disable_schedule_cmd = on_command("定时任务禁用",
                                      permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
                                      priority=1, block=True)

    set_schedule_cmd.handle()(handle_set_schedule)
    schedule_status_cmd.handle()(handle_schedule_status)
    disable_schedule_cmd.handle()(handle_disable_schedule)


def is_strict_command_match(command: str, user_input: str) -> bool:
    """严格匹配指令
    - 检查用户输入是否完全匹配命令别名
    - 区分是否允许带参数的命令匹配规则
    """
    main_alias, other_aliases = COMMANDS[command]["aliases"]
    all_aliases = [main_alias] + other_aliases
    allow_args = COMMANDS[command]["allow_args"]

    if allow_args:
        return any(user_input.strip().lower().startswith(alias.lower()) for alias in all_aliases)
    else:
        return any(user_input.strip().lower() == alias.lower() for alias in all_aliases)


def handle_command(command: str):
    """返回命令处理函数闭包
    - 用于处理具体的功能命令逻辑
    - 包含冷却检查、权限控制和结果发送
    """
    async def handler(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
        user_input = event.get_plaintext().strip()

        # 严格匹配指令，避免模糊触发
        if not is_strict_command_match(command, user_input):
            await matcher.finish()

        # 检查群组功能权限
        if isinstance(event, GroupMessageEvent):
            group_id = str(event.group_id)
            if not utils.is_function_enabled(group_id, command):
                logger.info(f"Function {command} is disabled in group {group_id}")
                await matcher.finish(f"该功能在本群已被禁用")

        command_args = await _process_command_args(command, event, args)
        # 检查命令参数合法性
        if not COMMANDS[command]["allow_args"] and command_args:
            await matcher.finish()

        user_id = str(event.user_id)
        group_id = str(event.group_id) if isinstance(event, GroupMessageEvent) else "private"

        # 检查冷却时间，防止滥用
        cooldown = plugin_config.fun_content_cooldowns.get(command, 20)
        if utils.is_in_cooldown(command, user_id, group_id):
            remaining_cd = utils.get_cooldown_time(command, user_id, group_id)
            logger.info(f"Command {command} is in cooldown for user {user_id} in group {group_id}")
            await matcher.finish(f"指令冷却中，请等待 {int(remaining_cd)} 秒再试喵~")

        try:
            # 不同类型命令的处理逻辑
            if command == "cp":
                # 处理CP图片生成命令
                image_data = await api.get_cp_content(command_args)
                try:
                    await matcher.send(MessageSegment.image(BytesIO(image_data)))
                except Exception as e:
                    error_msg = response_handler.format_error(e, command)
                    logger.error(f"Failed to send image for CP command: {error_msg}")
                    await matcher.send("CP图片生成成功，但发送失败。请稍后再试。")

            elif command == "beauty_pic":
                # 处理随机美女图片命令
                try:
                    image_url = await api.get_content(command)
                    await matcher.send(MessageSegment.image(image_url))
                except Exception as e:
                    error_msg = response_handler.format_error(e, command)
                    logger.error(f"Failed to send beauty pic: {error_msg}")
                    await matcher.send("图片获取失败，请稍后再试。")

            else:
                # 处理文本类命令
                result = await api.get_content(command)
                await matcher.send(result)

            # 设置命令冷却时间
            utils.set_cooldown(command, user_id, group_id, cooldown)

        except Exception as e:
            error_msg = response_handler.format_error(e, command)
            logger.error(f"Error in command {command}: {error_msg}")
            await matcher.send(error_msg)

    return handler


async def handle_enable(matcher: Matcher, event: GroupMessageEvent, args: Message = CommandArg()):
    """处理启用功能的命令
    - 仅限管理员或超级用户使用
    - 启用指定群组的特定功能
    """
    function = args.extract_plain_text().strip()
    group_id = str(event.group_id)

    # 查找并启用对应功能
    for cmd, info in COMMANDS.items():
        main_alias, other_aliases = info["aliases"]
        if function == main_alias or function in other_aliases:
            utils.enable_function(group_id, cmd)
            await matcher.finish(f"{main_alias}已启用。")

    await matcher.finish(f"未找到名为 '{function}' 的功能。")


async def handle_disable(matcher: Matcher, event: GroupMessageEvent, args: Message = CommandArg()):
    """处理禁用功能的命令
    - 仅限管理员或超级用户使用
    - 禁用指定群组的特定功能
    """
    function = args.extract_plain_text().strip()
    group_id = str(event.group_id)

    # 查找并禁用对应功能
    for cmd, info in COMMANDS.items():
        main_alias, other_aliases = info["aliases"]
        if function == main_alias or function in other_aliases:
            utils.disable_function(group_id, cmd)
            await matcher.finish(f"{main_alias}已禁用。")

    await matcher.finish(f"未找到名为 '{function}' 的功能。")


async def handle_status(matcher: Matcher, event: GroupMessageEvent):
    """获取当前群组功能状态
    - 显示所有功能的启用/禁用状态
    """
    group_id = str(event.group_id)
    status_messages = []
    for cmd, info in COMMANDS.items():
        main_alias, _ = info["aliases"]
        status = "已启用" if utils.is_function_enabled(group_id, cmd) else "已禁用"
        status_messages.append(f"{main_alias}: {status}")

    await matcher.finish("\n".join(status_messages))


async def handle_set_schedule(matcher: Matcher, event: GroupMessageEvent, args: Message = CommandArg()):
    """处理设置定时任务的命令
    - 格式：设置 [功能指令] [时间]
    - 时间格式：HH:MM
    """
    group_id = str(event.group_id)
    command_args = args.extract_plain_text().strip().split()
    if len(command_args) == 2:
        function, time = command_args
        for cmd, info in COMMANDS.items():
            main_alias, other_aliases = info["aliases"]
            if function == main_alias or function in other_aliases:
                if utils.is_valid_time_format(time):
                    scheduler.add_job(group_id, cmd, time)
                    await matcher.finish(f"已设置 {main_alias} 在 {time} 定时触发。")
                else:
                    await matcher.finish("时间格式错误，请使用 HH:MM 格式。")
        await matcher.finish(f"未找到名为 '{function}' 的功能。")
    else:
        await matcher.finish("参数错误，请使用正确的格式：设置 [功能指令] [时间]")


async def handle_schedule_status(matcher: Matcher, event: GroupMessageEvent):
    """获取当前群组的定时任务状态
    - 显示所有已设置的定时任务
    """
    group_id = str(event.group_id)
    status = scheduler.get_schedule_status(group_id)
    if status:
        formatted_status = []
        for command, times in status.items():
            main_alias = next((info["aliases"][0] for cmd, info in COMMANDS.items() if cmd == command), command)
            for time in times:
                formatted_status.append(f"{main_alias} 在 {time} 触发")
        await matcher.finish("\n".join(formatted_status))
    else:
        await matcher.finish("当前群组没有设置定时任务。")


async def handle_disable_schedule(matcher: Matcher, event: GroupMessageEvent, args: Message = CommandArg()):
    """处理禁用定时任务的命令
    - 格式：定时任务禁用 [功能指令] [时间]
    - 时间格式：HH:MM
    """
    group_id = str(event.group_id)
    command_args = args.extract_plain_text().strip().split()
    if len(command_args) != 2:
        await matcher.finish("参数错误，请使用正确的格式：定时任务禁用 [功能指令] [时间]")

    function, time = command_args
    for cmd, info in COMMANDS.items():
        main_alias, other_aliases = info["aliases"]
        if function == main_alias or function in other_aliases:
            if utils.is_valid_time_format(time):
                if scheduler.remove_job(group_id, cmd, time):
                    await matcher.finish(f"已删除 {main_alias} 在 {time} 的定时任务。")
                else:
                    await matcher.finish(f"未找到 {main_alias} 在 {time} 的定时任务。")
            else:
                await matcher.finish("时间格式错误，请使用 HH:MM 格式。")

    await matcher.finish(f"未找到名为 '{function}' 的功能。")

async def _process_command_args(command, event, args: Message = CommandArg()):
    """处理命令参数，严格返回两个名称，且只允许纯文本或纯@用户"""
    if command != "cp":
        return args.extract_plain_text().strip()

    has_text = False  # 是否包含文本段
    has_at = False    # 是否包含@用户段
    names = []
    
    for seg in args:
        # 处理@用户段
        if seg.type == "at":
            qq = seg.data.get("qq")
            if not qq:
                continue

            try:
                if isinstance(event, GroupMessageEvent):
                    group_id = event.group_id
                    bot = get_bot()
                    member_info = await bot.get_group_member_info(group_id=group_id, user_id=qq)
                    name = member_info.get("card") or member_info.get("nickname", str(qq))
                else:
                    name = str(qq)

                names.append(name)
                has_at = True
            except Exception as e:
                logger.error(f"获取用户信息失败: {e}")
                names.append(str(qq))

        # 处理文本段
        elif seg.type == "text":
            text = seg.data.get("text", "").strip()
            if text:
                names.extend(text.split())
                has_text = True

    # 检查是否混用了文本和@用户
    if has_text and has_at:
        return ""  # 混用了文本和@用户，返回空字符串

    # 严格返回两个名称，否则返回空字符串
    return " ".join(names[:2]) if len(names) == 2 else ""