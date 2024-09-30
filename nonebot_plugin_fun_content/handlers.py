from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment, Message, MessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from .utils import Utils
from .api import API
from .config import config

# 初始化工具类和 API 类
utils = Utils()
api = API()  

def register_handlers():
    """
    注册所有命令处理器
    """
    commands = {
        "hitokoto": on_command("一言"),
        "twq": on_command("土味情话", aliases={"情话", "土味"}),
        "dog": on_command("舔狗日记", aliases={"dog", "舔狗"}),
        "renjian": on_command("人间凑数"),
        "weibo_hot": on_command("微博热搜", aliases={"微博"}),
        "aiqinggongyu": on_command("爱情公寓"),
        "baisi": on_command("随机白丝", aliases={"白丝"}),
        "cp": on_command("cp", aliases={"宇宙cp"}),
        "shenhuifu": on_command("神回复", aliases={"神评"}),
    }

    for cmd, matcher in commands.items():
        matcher.handle()(handle_command(cmd))

def handle_command(command: str):
    """
    通用命令处理函数
    :param command: 命令名称
    :return: 异步处理函数
    """
    async def handler(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
        # 检查参数（除了 cp 命令外，其他命令不应该有参数）
        if args and command != "cp":
            await matcher.send("请不要带参数喵~")
            return

        group_id = str(event.group_id)
        user_id = str(event.user_id)

        # 检查冷却时间
        if utils.is_in_cooldown(command, user_id, group_id):
            remaining_cd = utils.get_cooldown_time(command, user_id, group_id)
            await matcher.send(f"指令冷却中，请等待 {int(remaining_cd)} 秒再试喵~")
            return

        try:
            # 处理不同的命令
            if command == "cp":
                url = await api.get_cp_content(args.extract_plain_text().strip())
                await matcher.send(MessageSegment.image(url))
                utils.set_cooldown(command, user_id, group_id)
                return
            elif command == "baisi":
                image_url = await api.get_baisi_image()
                await matcher.send(MessageSegment.image(image_url))
                utils.set_cooldown(command, user_id, group_id)
                return
            else:
                result = await api.get_content(command)

            await matcher.send(result)
            utils.set_cooldown(command, user_id, group_id)
        except ValueError as e:
            await matcher.send(str(e))
        except Exception as e:
            await matcher.send("发生未知错误，请稍后再试喵~")

    return handler