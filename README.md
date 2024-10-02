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

本插件主要用于从多个 API 获取趣味内容，如一言、土味情话、舔狗日记等。

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
	"hitokoto": 10, 
	"twq": 20,  
	"dog": 20,  
	"renjian": 20,
	"weibo_hot": 20, 
	"aiqinggongyu": 20, 
	"baisi": 20, 
	"cp": 20, 
	"shenhuifu": 20,
	"joke": 20
}
'
#禁用功能文件路径配置（默认在插件目录下，可不配置）
#Linux
DISABLED_FUNCTIONS_FILE="/home/user/bot/data/disabled_functions.json"
#Windows
DISABLED_FUNCTIONS_FILE="C:/Users/YourUsername/Documents/bot/data/disabled_functions.json"

```

## 🎉 指令列表
> 你可能需要在env里配置指令响应头 " / "，取决于你的command_start设置

| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| 一言 | 所有人 | 否 | 群聊 | 获取一句话的灵感 |
| 土味情话/情话/土味 | 所有人 | 否 | 群聊 | 获取一条土味情话 |
| 舔狗日记/舔狗/dog | 所有人 | 否 | 群聊 | 获取一篇舔狗日记 |
| 人间凑数 | 所有人 | 否 | 群聊 | 获取我在人间凑数的日子内容 |
| 微博热搜/微博 | 所有人 | 否 | 群聊 | 获取当前微博热搜内容 |
| 爱情公寓 | 所有人 | 否 | 群聊 | 获取爱情公寓语录 |
| 随机白丝/白丝 | 所有人 | 否 | 群聊 | 获取随机白丝内容 |
| 宇宙cp/cp 角色1 角色2 | 所有人 | 否 | 群聊 | 获取宇宙CP文 |
| 神回复/神评 | 所有人 | 否 | 群聊 | 获取神回复内容 |
|讲个笑话/笑话|所有人|否|群聊|获取一个笑话内容|

## 管理命令（仅限超级用户、群主、管理员）
|指令|说明|
|:-----:|:----:|
|关闭 [功能名]| 在当前群禁用指定功能|
|开启 [功能名]| 在当前群启用指定功能|
|功能状态| 查看当前群组的功能禁用状态|

## 将来可能支持的功能
- [x] 增加CD限制
- [x] 增加指令开关
- [ ] 增加图片发送
- [ ] 加入定时计划
- [x] 整合更多的API
- [ ] 优化屎山代码
- [ ] ......

## 💡鸣谢
- [Nonebot](https://github.com/nonebot/nonebot2): 本项目的基础，非常好用的聊天机器人框架。
- [夏柔API](https://api.aa1.cn/author/1):API接口来源

## ⚠️ 注意事项
本插件目前仅支持 nonebot2 + onebot.v11 的使用方式, 一切非此二者结合的使用方式造成的问题请自行探索解决, 或者使用其他插件。
