<p align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://user-images.githubusercontent.com/44545625/209862575-acdc9feb-3c76-471d-ad89-cc78927e5875.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
</p>

<div align="center">

# nonebot-plugin-fun-content

_✨趣味内容插件✨_

</div>

<p align="center">
  <a href="https://pypi.org/project/nonebot-plugin-fun-content/">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-fun-content" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">
</p>


## 📖 介绍
>本人并非计算机类的专业，水平有限，如有问题或建议请直接发issue，我会尽量解决

本插件主要用于从多个 API 获取趣味内容，如一言、土味情话、舔狗日记等。现在还支持定时发送功能！

## 💿 如何安装
<details open>
<summary>使用 nb-cli 安装（推荐）</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-fun-content

</details>

<details open>
<summary>使用 pip 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

> 如果你启用了 **虚拟环境** 且 **nonebot没有加载本插件** 则需进入虚拟环境（Windows在命令行输入`.venv\Scripts\activate`,Linux使用`source .venv/bin/activate`）再输入下方命令，使用`deactivate`退出虚拟环境

    pip install nonebot-plugin-fun-content

然后打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_fun_content"]

</details>

## 配置

在bot目录对应的.env.*文件（一般为`.env.prod`）中添加
```dotenv
#命令冷却时间配置（单位：秒,默认为20，可不配置）
FUN_CONTENT_COOLDOWNS='
{
	"hitokoto": 20, 
	"twq": 20,  
	"dog": 20, 
	"wangyiyun": 20, 
	"renjian": 20,
	"weibo_hot": 20, 
	"douyin_hot": 20,
	"aiqinggongyu": 20, 
	"beauty_pic": 20, 
	"cp": 20, 
	"shenhuifu": 20,
	"joke": 20,
	"lazy_sing": 60
}
'
#开关和定时任务配置文件路径配置（默认在插件目录下，可不配置）
#Linux
PERSISTENT_DATA_FILE="/home/user/bot/data/persistent_data.json"
#Windows
PERSISTENT_DATA_FILE="C:/Users/YourUsername/Documents/bot/data/persistent_data.json"
```

<details open>
<summary>persistent_data.json格式示例</summary>

```json
{
  "开关": {
    "3324569": {
      "hitokoto": true,
      "twq": true,
      "dog": true,
      "wangyiyun": true,
      "renjian": true,
      "weibo_hot": true,
      "douyin_hot": true,
      "aiqinggongyu": true,
      "beauty_pic": true,
      "cp": true,
      "shenhuifu": true,
      "joke": true,
      "lazy_sing": true
    },
    "7644494": {
      "hitokoto": true,
      "twq": true,
      "dog": true,
      "wangyiyun": true,
      "renjian": true,
      "weibo_hot": true,
      "douyin_hot": true,
      "aiqinggongyu": true,
      "beauty_pic": true,
      "cp": true,
      "shenhuifu": true,
      "joke": true,
      "lazy_sing": true
    }
  },
  "定时": {
    "群号1": {
      "lazy_sing": [
        "14:25",
        "13:38"
      ],
      "hitokoto": [
        "13:38",
        "15:56"
      ]
    },
    "群号2": {
      "hitokoto": [
        "13:38",
        "15:56"
      ]
    }
  }
}
```

</details>

## 🎉 指令列表
> 你可能需要在env里配置指令响应头 " / "，取决于你的command_start设置

| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| 一言 | 所有人 | 否 | 群聊/私聊 | 获取一句话的灵感 |
| 土味情话/情话/土味 | 所有人 | 否 | 群聊/私聊 | 获取一条土味情话 |
| 舔狗日记/舔狗/dog | 所有人 | 否 | 群聊/私聊 | 获取一篇舔狗日记 |
| 网抑云 | 所有人 | 否 | 群聊/私聊 | 获取网易云音乐热评 |
| 人间凑数 | 所有人 | 否 | 群聊/私聊 | 获取我在人间凑数的日子内容 |
| 微博热搜/微博 | 所有人 | 否 | 群聊/私聊 | 获取当前微博热搜内容 |
| 抖音热搜/抖音 | 所有人 | 否 | 群聊/私聊 | 获取当前抖音热搜内容 |
| 爱情公寓 | 所有人 | 否 | 群聊/私聊 | 获取爱情公寓语录 |
| 随机美女/美女 | 所有人 | 否 | 群聊/私聊 | 获取随机白丝内容 |
| 宇宙cp/cp 角色1 角色2 | 所有人 | 否 | 群聊/私聊 | 获取宇宙CP文 |
| 神回复/神评 | 所有人 | 否 | 群聊/私聊 | 获取神回复内容 |
| 讲个笑话/笑话 | 所有人 | 否 | 群聊/私聊 | 获取一个笑话内容 |
| 懒洋洋唱歌/唱歌/懒洋洋 | 所有人 | 否 | 群聊/私聊 | 获取AI懒洋洋唱歌语音 |
>！！！注意懒洋洋唱歌功能需要下载ffmpeg并正确配置到环境变量中


## 管理员命令（仅限超级用户、群主、管理员）
| 指令 | 范围 | 说明 | 示例 |
|:-----|:-----|:-----|:-----|
| 关闭 [功能名] | 群聊 | 在当前群禁用指定功能 | 关闭 一言 |
| 开启 [功能名] | 群聊 | 在当前群启用指定功能 | 开启 土味情话 |
| 功能状态 | 群聊 | 查看当前群组的功能禁用状态 | 功能状态 |
| 设置+[功能指令] [HH:MM] | 群聊 | 添加定时任务 | 设置一言 08:00 |
| 定时任务状态 | 群聊 | 查看当前群组的所有定时任务 | 定时任务状态 |
| 定时任务禁用 [功能指令] [时间] | 群聊 | 删除指定命令在指定时间的定时任务 | 定时任务禁用 一言 08:00 |

## 将来可能支持的功能
- [x] 增加CD限制
- [x] 增加指令开关
- [x] 加入定时计划
- [x] 整合更多的API
- [ ] 优化屎山代码
- [ ] ......

## 💡鸣谢
- [Nonebot](https://github.com/nonebot/nonebot2): 本项目的基础，非常好用的聊天机器人框架。
- [夏柔API](https://api.aa1.cn/author/1):API接口来源

## ⚠️ 注意事项
本插件目前仅支持 nonebot2 + onebot.v11 的使用方式, 一切非此二者结合的使用方式造成的问题请自行探索解决, 或者使用其他插件。