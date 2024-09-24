# _✨欢迎使用趣味内容插件✨_
本插件主要用于从多个 API 获取趣味内容，如一言、土味情话、舔狗日记等。

## 💿如何安装
<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-fun-content

</details>

<details open>
<summary>使用 pip 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

> 如果你启用了 **虚拟环境** 且 **nonebot没有加载本插件** 则需要进入.\.venv\Scripts目录下打开命令行,将pip.exe或者pip拖入命令行中再运行以下命令

    pip install nonebot-plugin-fun-content

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_template"]

</details>

## 🎉指令列表
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| 一言 | 所有人 | 否 | 群聊 | 获取一句话的灵感 |
| 土味情话 | 所有人 | 否 | 群聊 | 获取一条土味情话 |
| 舔狗日记 | 所有人 | 否 | 群聊 | 获取一篇舔狗日记 |
| 人间凑数 | 所有人 | 否 | 群聊 | 获取人间凑数内容 |
| 微博热搜 | 所有人 | 否 | 群聊 | 获取当前微博热搜内容 |
| 爱情公寓 | 所有人 | 否 | 群聊 | 获取爱情公寓语录 |
| 随机白丝 | 所有人 | 否 | 群聊 | 获取随机白丝内容 |
| cp <角色1> <角色2> | 所有人 | 否 | 群聊 | 获取宇宙CP文 |
| 神回复 | 所有人 | 否 | 群聊 | 获取神回复内容 |
