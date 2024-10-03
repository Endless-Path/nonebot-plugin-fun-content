from pydantic import BaseModel, HttpUrl, Field
from typing import Dict, List, Union 
from pathlib import Path
from nonebot import get_driver

class Config(BaseModel):
    fun_content_api_urls: Dict[str, Union[HttpUrl, List[HttpUrl]]] = Field(
        default={
            "hitokoto": [
                "https://v2.api-m.com/api/yiyan?type=hitokoto",
                "https://uapis.cn/api/say",
                "https://tenapi.cn/v2/yiyan",
                "https://api.vvhan.com/api/ian/rand?type=json"
            ],
            "twq": "https://jkapi.com/api/tuweiqinghua?type=json",
            "dog": [
                "https://v2.api-m.com/api/dog",
                "https://api.52vmy.cn/api/wl/yan/tiangou",
                "https://api.xiaole.work/api/dog/dog.php?format=json"
            ],
            "wangyiyun": "https://v.api.aa1.cn/api/api-wenan-wangyiyunreping/index.php?aa1=json",
            "renjian": "https://v2.api-m.com/api/renjian",
            "weibo_hot": "https://v2.api-m.com/api/weibohot",
            "douyin_hot": "https://api.vvhan.com/api/hotlist/douyinHot",
            "aiqinggongyu": "https://v2.api-m.com/api/aiqinggongyu",
            "beauty_pic": [
                "https://v2.api-m.com/api/baisi",
                "https://v2.api-m.com/api/meinvpic",
                "https://v2.api-m.com/api/heisi",
                "https://api.52vmy.cn/api/img/tu/girl",
                "https://api.unmz.net/free/api/images/girl/getRandomGirlUrl?size=1"
            ],
            "cp": "https://www.hhlqilongzhu.cn/api/tu_lofter_cp.php",
            "shenhuifu": "https://v.api.aa1.cn/api/api-wenan-shenhuifu/index.php?aa1=json",
            "joke": "https://api.vvhan.com/api/text/joke?type=json",
            "lazy_sing": "https://api.treason.cn/API/nan.php"
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
            "beauty_pic": 20,
            "cp": 20,
            "shenhuifu": 20,
            "joke": 20,
            "lazy_sing": 60
        },
        env="FUN_CONTENT_COOLDOWNS"
    )

    # 新增配置项：禁用功能文件路径
    disabled_functions_file: Path = Field(
        default=Path(__file__).parent / "disabled_functions.json",
        env="DISABLED_FUNCTIONS_FILE"
    )

driver = get_driver()
global_config = driver.config
plugin_config = Config.parse_obj(global_config)