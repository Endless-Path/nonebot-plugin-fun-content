from nonebot import get_driver
from nonebot.plugin import PluginMetadata
from .handlers import register_handlers

# 插件元数据，提供插件的基本信息
__plugin_meta__ = PluginMetadata(
    name="趣味内容插件",
    description="从多个 API 获取趣味内容，如一言、土味情话、舔狗日记等。",
    usage="""
    - 一言: 发送 "一言" 获取一句话的灵感。
    - 土味情话: 发送 "土味情话"、"情话" 或 "土味" 获取土味情话。
    - 舔狗日记: 发送 "舔狗日记"、"dog" 或 "舔狗" 获取舔狗日记。
    - 人间凑数: 发送 "人间凑数" 获取人间凑数内容。
    - 微博热搜: 发送 "微博热搜"、"微博" 获取微博热搜。
    - 爱情公寓: 发送 "爱情公寓" 获取爱情公寓语录。
    - 随机白丝: 发送 "随机白丝"、"白丝" 获取随机白丝内容。
    - 宇宙CP文: 发送 "cp 角色1 角色2" 获取宇宙CP文。
    - 神回复: 发送 "神回复" 或 "神评" 获取神回复内容。
    """,
    type="application",
    homepage="https://github.com/chsiyu/nonebot-plugin-fun-content",
    supported_adapters={"~onebot.v11"},
)

# 注册所有命令处理器
register_handlers()
