from nonebot import get_driver
from nonebot.plugin import PluginMetadata
from .handlers import register_handlers
from .config import plugin_config
from .scheduler import scheduler_instance
from .utils import utils
import logging

__plugin_meta__ = PluginMetadata(
    name="趣味内容插件",
    description="从多个 API 获取趣味内容，如一言、土味情话、舔狗日记等。",
    usage="""
    - 一言: 发送 "一言" 获取一句话的灵感。
    - 土味情话: 发送 "土味情话"、"情话" 或 "土味" 获取土味情话。
    - 舔狗日记: 发送 "舔狗日记"、"dog" 或 "舔狗" 获取舔狗日记。
    - 网抑云: 发送 "网抑云" 获取网易云音乐热评。
    - 人间凑数: 发送 "人间凑数" 获取人间凑数内容。
    - 微博热搜: 发送 "微博热搜"、"微博" 获取微博热搜。
    - 抖音热搜: 发送 "抖音热搜" 或 "抖音" 获取抖音热搜榜。
    - 爱情公寓: 发送 "爱情公寓" 获取爱情公寓语录。
    - 随机美女: 发送 "随机美女" 或 "美女" 获取随机美女图片。
    - 宇宙CP文: 发送 "cp 角色1 角色2" 获取宇宙CP文。
    - 神回复: 发送 "神回复" 或 "神评" 获取神回复内容。
    - 讲个笑话: 发送 "讲个笑话" 或 "笑话" 获取一个笑话。
    - 懒洋洋唱歌: 发送 "懒洋洋唱歌"、"懒洋洋" 或 "唱歌" 获取一段随机歌曲。

    管理命令（仅限超级用户、群主、管理员）：
    - 关闭 [功能名]: 在当前群禁用指定功能
    - 开启 [功能名]: 在当前群启用指定功能
    - 功能状态: 查看当前群组的功能禁用状态
    - [功能名]设置 [时间]: 设置定时任务，如 "一言设置 08:00"
    - 定时任务状态: 查看当前群组的定时任务
    - 定时任务禁用 [功能名] [时间]: 禁用指定的定时任务
    """,
    type="application",
    homepage="https://github.com/Endless-Path/nonebot-plugin-fun-content",
    supported_adapters={"~onebot.v11"},
)

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s]: %(message)s'))
logger.addHandler(handler)

# 获取驱动以访问全局配置
driver = get_driver()

initialization_completed = False

@driver.on_startup
async def plugin_init():
    logger.info("趣味内容插件正在初始化...")
    
    # 初始化定时任务
    for group_id, group_tasks in utils.persistent_data["定时"].items():
        for command, times in group_tasks.items():
            for time in times:
                try:
                    scheduler_instance.add_job(group_id, command, time)
                except Exception as e:
                    logger.error(f"Error adding job for group {group_id}, command {command}, time {time}: {str(e)}")
    
    logger.info("趣味内容插件初始化完成")

@driver.on_shutdown
async def plugin_shutdown():
    logger.info("趣味内容插件正在关闭...")
    
    # 更新定时任务数据
    utils.persistent_data["定时"] = {
        group_id: {
            command: times for command, times in group_tasks.items() if times
        } for group_id, group_tasks in scheduler_instance.jobs.items()
    }
    
    # 移除空的群组数据
    utils.persistent_data["定时"] = {
        group_id: group_tasks for group_id, group_tasks in utils.persistent_data["定时"].items() if group_tasks
    }
    
    utils._save_persistent_data()
    
    logger.info("趣味内容插件已关闭")
    
# 注册处理程序
register_handlers()

# 可以在这里添加全局错误处理
@driver.on_bot_connect
async def handle_connect(bot):
    logger.info(f"Bot {bot.self_id} 已连接")

@driver.on_bot_disconnect
async def handle_disconnect(bot):
    logger.info(f"Bot {bot.self_id} 已断开连接")