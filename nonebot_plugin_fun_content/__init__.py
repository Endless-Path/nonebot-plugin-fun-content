import httpx
import string
from nonebot import logger, on_command
from nonebot.adapters.onebot.v11 import MessageSegment, Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot import get_driver
from nonebot.plugin import PluginMetadata

# 插件元数据定义
__plugin_meta__ = PluginMetadata(
    name="趣味内容插件",
    description="从多个 API 获取趣味内容，如一言、土味情话、舔狗日记等。",
    usage="""
    使用方法:
    - 一言: 获取一句话的灵感，使用命令 `一言` 或 `一句`。
    - 土味情话: 获取土味情话，使用命令 `土味情话`、`情话` 或 `土味`。
    - 舔狗日记: 获取舔狗日记，使用命令 `舔狗日记`、`dog` 或 `舔狗`。
    - 人间凑数: 获取人间凑数内容，使用命令 `人间凑数` 或 `我在人间凑数的日子`。
    - 微博热搜: 获取微博热搜，使用命令 `微博热搜`、`热搜` 或 `微博`。
    - 爱情公寓: 获取爱情公寓语录，使用命令 `爱情公寓`、`爱情语录` 或 `爱公寓`。
    - 随机白丝: 获取随机白丝内容，使用命令 `随机白丝`、`白丝` 或 `随机图`。
    - 宇宙CP文: 获取宇宙CP文，使用命令 `cp <角色1> <角色2>`。
    - 神回复: 获取神回复内容，使用命令 `神回复` 或 `神评`。
    """,
    type="application",
    homepage="https://github.com/yourusername/your-repo",
    supported_adapters={"~onebot.v11"},
)

# 获取超级用户列表
SUPERUSERS = get_driver().config.superusers

# 定义API URLs
API_URLS = {
    "hitokoto": "https://v2.api-m.com/api/yiyan?type=hitokoto",
    "twq": "https://jkapi.com/api/tuweiqinghua?type=json",
    "dog": "https://v2.api-m.com/api/dog",
    "renjian": "https://v2.api-m.com/api/renjian",
    "weibo_hot": "https://v2.api-m.com/api/weibohot",
    "aiqinggongyu": "https://v2.api-m.com/api/aiqinggongyu",
    "baisi": "https://v2.api-m.com/api/baisi",
    "cp": "https://www.hhlqilongzhu.cn/api/tu_lofter_cp.php",
    "shenhuifu": "https://v.api.aa1.cn/api/api-wenan-shenhuifu/index.php?aa1=json"
}

# 定义命令匹配器
commands = {
    "hitokoto": on_command("一言", aliases={"一句"}),
    "twq": on_command("土味情话", aliases={"情话", "土味"}),
    "dog": on_command("舔狗日记", aliases={"dog", "舔狗"}),
    "renjian": on_command("人间凑数", aliases={"我在人间凑数的日子"}),
    "weibo_hot": on_command("微博热搜", aliases={"热搜", "微博"}),
    "aiqinggongyu": on_command("爱情公寓", aliases={"爱情语录", "爱公寓"}),
    "baisi": on_command("随机白丝", aliases={"白丝", "随机图"}),
    "cp": on_command("cp", aliases={"宇宙cp"}),
    "shenhuifu": on_command("神回复", aliases={"神评"}),
}

async def fetch_data(url: str, params: dict = None) -> dict:
    """
    异步请求数据
    :param url: API的URL
    :param params: 请求参数字典
    :return: 返回JSON数据或错误信息
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"请求失败，状态码: {e.response.status_code}，URL: {url}")
        return {"error": "请求失败，请稍后再试喵~"}
    except Exception as e:
        logger.error(f"发生错误: {e}，URL: {url}")
        return {"error": "发生未知错误，请稍后再试喵~"}

async def handle_command(matcher: Matcher, command_key: str, params: dict = None):
    """
    处理命令，获取数据并返回
    :param matcher: 匹配器
    :param command_key: 命令对应的键
    :param params: 请求参数字典
    """
    data = await fetch_data(API_URLS[command_key], params=params)
    if isinstance(data, dict) and "error" in data:
        await matcher.send(data["error"])
        return

    msg = data.get("data", "没有获取到内容") if "data" in data else data
    await matcher.send(msg)

async def handle_no_arg_command(matcher: Matcher, command_key: str):
    """处理不带参数的命令"""
    await handle_command(matcher, command_key)

@commands["hitokoto"].handle()
async def hitokoto(matcher: Matcher, args: Message = CommandArg()):
    """一言命令处理"""
    if args:
        await matcher.send("请不要带参数喵~")
        return
    await handle_no_arg_command(matcher, "hitokoto")

@commands["twq"].handle()
async def twq(matcher: Matcher, args: Message = CommandArg()):
    """土味情话命令处理"""
    if args:
        await matcher.send("请不要带参数喵~")
        return
    await handle_no_arg_command(matcher, "twq")

@commands["dog"].handle()
async def lickdog_diary(matcher: Matcher, args: Message = CommandArg()):
    """舔狗日记命令处理"""
    if args:
        await matcher.send("请不要带参数喵~")
        return
    await handle_no_arg_command(matcher, "dog")

@commands["renjian"].handle()
async def renjian(matcher: Matcher, args: Message = CommandArg()):
    """人间凑数命令处理"""
    if args:
        await matcher.send("请不要带参数喵~")
        return
    await handle_no_arg_command(matcher, "renjian")

@commands["weibo_hot"].handle()
async def weibo_hot(matcher: Matcher, args: Message = CommandArg()):
    """微博热搜命令处理"""
    if args:
        await matcher.send("请不要带参数喵~")
        return

    data = await fetch_data(API_URLS["weibo_hot"])
    if isinstance(data, dict) and "error" in data:
        await matcher.send(data["error"])
        return

    if isinstance(data, dict) and data.get("code") == 200:
        hot_data = data.get("data", [])
        
        if hot_data:
            hot_msg = "当前微博热搜：\n"
            for item in hot_data[:10]:
                hot_msg += f"热搜排名: {item.get('index', '未知')}\n"
                hot_msg += f"热搜标题: {item.get('title', '没有标题')}\n"
                hot_msg += f"热搜热度: {item.get('hot', '未知')}\n"
                hot_msg += f"链接: {item.get('url', '没有链接')}\n\n"

            await matcher.send(hot_msg.strip())
        else:
            await matcher.send("没有获取到微博热搜内容喵~")
    else:
        await matcher.send("响应格式不正确，请稍后再试喵~")

@commands["aiqinggongyu"].handle()
async def aiqinggongyu(matcher: Matcher, args: Message = CommandArg()):
    """爱情公寓语录命令处理"""
    if args:
        await matcher.send("请不要带参数喵~")
        return
    await handle_no_arg_command(matcher, "aiqinggongyu")

@commands["baisi"].handle()
async def baisi(matcher: Matcher, args: Message = CommandArg()):
    """随机白丝命令处理"""
    if args:
        await matcher.send("请不要带参数喵~")
        return

    try:
        image_content = await get_baisi_image()
        await matcher.send(MessageSegment.image(image_content))
    except Exception as e:
        logger.error(f"发生错误: {e}")
        await matcher.send("获取随机白丝内容失败喵~")

async def get_baisi_image() -> str:
    """获取随机白丝图片内容"""
    async with httpx.AsyncClient() as client:
        headers = {
            'User-Agent': 'xiaoxiaoapi/1.0.0 (https://api-m.com)'
        }
        response = await client.get(API_URLS["baisi"], headers=headers)

        if response.status_code != 200:
            raise ValueError(f"随机白丝获取失败，错误码：{response.status_code}")

        data = response.json()
        
        if data.get("code") != 200:
            raise ValueError(f"请求失败，消息：{data.get('msg')}")

        image_url = data.get("data")
        if not image_url:
            raise ValueError("获取图片 URL 失败，返回数据不正确")

        return image_url

@commands["cp"].handle()
async def cp(matcher: Matcher, args: Message = CommandArg()):
    """宇宙CP文命令处理"""
    user_input = args.extract_plain_text().strip().lower()
    args_without_punctuation = user_input.translate(str.maketrans('', '', string.punctuation))

    if len(args_without_punctuation.split(' ')) < 2:
        await matcher.send('未匹配到参数！请提供两个角色的名称喵~')
        return

    options = [x for x in user_input.split(' ') if x.strip()]
    name1, name2 = options[0], options[1]
    url = f"{API_URLS['cp']}?n1={name1}&n2={name2}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '')

            if 'application/json' in content_type:
                data = response.json()
                if 'data' in data and data['data']:
                    image_url = data['data']
                    await matcher.send(MessageSegment.image(image_url))
                else:
                    await matcher.send("未获取到有效的 CP 文内容喵~")
            elif 'image/' in content_type:
                await matcher.send(MessageSegment.image(response.content))
            else:
                await matcher.send("返回内容格式不正确，请稍后再试喵~")
    
    except httpx.HTTPStatusError as e:
        logger.error(f"请求失败，状态码: {e.response.status_code}，URL: {url}")
        await matcher.send("请求失败，请稍后再试喵~")
    except Exception as e:
        logger.error(f"发生错误: {e}，URL: {url}")
        await matcher.send("发生未知错误，请稍后再试喵~")

@commands["shenhuifu"].handle()
async def shenhuifu(matcher: Matcher, args: Message = CommandArg()):
    """神回复命令处理"""
    if args:
        await matcher.send("请不要带参数喵~")
        return

    data = await fetch_data(API_URLS["shenhuifu"])
    if isinstance(data, dict) and "error" in data:
        await matcher.send(data["error"])
        return

    if isinstance(data, list) and len(data) > 0:
        shenhuifu_response = data[0].get("shenhuifu", "没有获取到神回复内容喵~")
        await matcher.send(shenhuifu_response)
    else:
        await matcher.send("没有获取到神回复内容喵~")

