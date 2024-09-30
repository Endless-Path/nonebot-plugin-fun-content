from pydantic import BaseModel, HttpUrl, Field
from typing import Dict
import json

class Config(BaseModel):
    fun_content_api_urls: Dict[str, HttpUrl] = Field(
        default={
            "hitokoto": "https://v2.api-m.com/api/yiyan?type=hitokoto",
            "twq": "https://jkapi.com/api/tuweiqinghua?type=json",
            "dog": "https://v2.api-m.com/api/dog",
            "renjian": "https://v2.api-m.com/api/renjian",
            "weibo_hot": "https://v2.api-m.com/api/weibohot",
            "aiqinggongyu": "https://v2.api-m.com/api/aiqinggongyu",
            "baisi": "https://v2.api-m.com/api/baisi",
            "cp": "https://www.hhlqilongzhu.cn/api/tu_lofter_cp.php",
            "shenhuifu": "https://v.api.aa1.cn/api/api-wenan-shenhuifu/index.php?aa1=json"
        },
        env="FUN_CONTENT_API_URLS"
    )

    fun_content_cooldowns: Dict[str, int] = Field(
        default={
            "hitokoto": 20,
            "twq": 20,
            "dog": 20,
            "renjian": 20,
            "weibo_hot": 20,
            "aiqinggongyu": 20,
            "baisi": 20,
            "cp": 20,
            "shenhuifu": 20
        },
        env="FUN_CONTENT_COOLDOWNS"
    )

config = Config()