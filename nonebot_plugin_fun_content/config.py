from pathlib import Path
from typing import Dict, List

from nonebot import get_driver
from pydantic import BaseModel, Field

class Config(BaseModel):
    # 数据库配置
    fun_content_db_path: Path = Field(
        default=Path(__file__).parent / "data/fun_content.db",
        env="FUN_CONTENT_DB_PATH"
    )

    # API URLs配置
    fun_content_api_urls: Dict[str, str] = Field(
    default={
        "weibo_hot": "https://v2.api-m.com/api/weibohot",
        "douyin_hot": "https://api.vvhan.com/api/hotlist/douyinHot",
        "cp": "https://www.hhlqilongzhu.cn/api/tu_lofter_cp.php",
    },
    env="FUN_CONTENT_API_URLS",
)

    # 功能冷却时间配置（秒）
    fun_content_cooldowns: Dict[str, int] = Field(
        default={
            "hitokoto": 20,
            "twq": 20,
            "dog": 20,
            "renjian": 20,
            "weibo_hot": 20,
            "douyin_hot": 20,
            "aiqinggongyu": 20,
            "beauty_pic": 20,
            "cp": 20,
            "shenhuifu": 20,
            "joke": 20,
        },
        env="FUN_CONTENT_COOLDOWNS"
    )

    # 持久化数据存储路径
    persistent_data_file: Path = Field(
        default=Path("config") / "persistent_data.json",
        env="PERSISTENT_DATA_FILE"
    )

    # 可用命令列表
    COMMANDS: List[str] = [
        "hitokoto", "twq", "dog", "renjian", "weibo_hot", "douyin_hot",
        "aiqinggongyu", "beauty_pic", "cp", "shenhuifu", "joke"
    ]

    # 本地数据库支持的功能列表
    DATABASE_SUPPORTED_COMMANDS: List[str] = [
        "hitokoto", "twq", "dog", "aiqinggongyu", "renjian",
        "shenhuifu", "joke", "beauty_pic"
    ]

    class Config:
        extra = "ignore"

driver = get_driver()
global_config = driver.config
plugin_config = Config.parse_obj(global_config)