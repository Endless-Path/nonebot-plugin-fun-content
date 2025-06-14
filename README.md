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

本插件旨在提供多种趣味文案的发送功能，包括一言、土味情话、舔狗日记等内容。

- 支持自定义命令冷却时间（CD）配置
- 支持自定义群开关和定时任务配置文件路径
- 支持群主和管理员对指定功能进行启用或禁用
- 支持群主和管理员设置定时任务

## 💿 如何安装

<details open>
<summary>使用 nb-cli 安装（推荐）</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

```shell
nb plugin install nonebot-plugin-fun-content
```

</details>

<details>
<summary>使用 pip 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

> 如果你启用了 **虚拟环境** 且 **nonebot没有加载本插件** 则需进入虚拟环境（Windows在命令行输入`.venv\Scripts\activate`,Linux使用`source .venv/bin/activate`）再输入下方命令，使用`deactivate`退出虚拟环境

```shell
pip install nonebot-plugin-fun-content
```

然后打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

```shell
plugins = ["nonebot_plugin_fun_content"]
```

</details>

## 🔧 配置

在bot目录对应的.env.*文件（一般为`.env.prod`）中添加

```bash
#命令冷却时间配置（单位：秒,默认为20，可不配置）
FUN_CONTENT_COOLDOWNS='
{
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
  "joke": 20
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
      "renjian": true,
      "weibo_hot": true,
      "douyin_hot": true,
      "aiqinggongyu": true,
      "beauty_pic": true,
      "cp": true,
      "shenhuifu": true,
      "joke": true
    },
    "7644494": {
      "hitokoto": true,
      "twq": true,
      "dog": true,
      "renjian": true,
      "weibo_hot": true,
      "douyin_hot": true,
      "aiqinggongyu": true,
      "beauty_pic": true,
      "cp": true,
      "shenhuifu": true,
      "joke": true
    }
  },
  "定时": {
    "群号1": {
      "twq": [
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

## 🎉 使用

> ⚠️ 你可能需要在指令前加env里配置指令响应头 `/`，具体取决于你的 `command_start` 设置

### 基础命令

| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| 一言 | 所有人 | 否 | 群聊/私聊 | 获取一句话的灵感 |
| 土味情话/情话/土味 | 所有人 | 否 | 群聊/私聊 | 获取一条土味情话 |
| 舔狗日记/舔狗/dog | 所有人 | 否 | 群聊/私聊 | 获取一篇舔狗日记 |
| 人间凑数 | 所有人 | 否 | 群聊/私聊 | 获取我在人间凑数的日子内容 |
| 微博热搜/微博 | 所有人 | 否 | 群聊/私聊 | 获取当前微博热搜内容 |
| 抖音热搜/抖音 | 所有人 | 否 | 群聊/私聊 | 获取当前抖音热搜内容 |
| 爱情公寓 | 所有人 | 否 | 群聊/私聊 | 获取爱情公寓语录 |
| 随机美女/美女 | 所有人 | 否 | 群聊/私聊 | 获取随机白丝内容 |
| 宇宙cp/cp 角色1 角色2 | 所有人 | 否 | 群聊/私聊 | 获取宇宙CP文 |
| 神回复/神评 | 所有人 | 否 | 群聊/私聊 | 获取神回复内容 |
| 讲个笑话/笑话 | 所有人 | 否 | 群聊/私聊 | 获取一个笑话内容 |

> 宇宙cp支持通过@用户获取其昵称作为角色名
>⚠️ 角色名不能大于6个汉字，不支持 “cp 角色名 @用户” 或 “cp @用户 角色名”的形式

### 管理员命令（仅限超级用户、群主、管理员）

| 指令 | 范围 | 说明 | 示例 |
|:-----|:-----|:-----|:-----|
| 关闭 [功能名] | 群聊 | 在当前群禁用指定功能 | 关闭 一言 |
| 开启 [功能名] | 群聊 | 在当前群启用指定功能 | 开启 土味情话 |
| 功能状态 | 群聊 | 查看当前群组的功能禁用状态 | 功能状态 |
| 设置+[功能指令] [HH:MM] | 群聊 | 添加定时任务 | 设置一言 08:00 |
| 定时任务状态 | 群聊 | 查看当前群组的所有定时任务 | 定时任务状态 |
| 定时任务禁用 [功能指令] [时间] | 群聊 | 删除指定命令在指定时间的定时任务 | 定时任务禁用 一言 08:00 |

## 🚧 TODO

- [x] **增加命令冷却时间限制（CD）功能**
- [x] **支持指令启用/禁用开关**
- [x] **添加定时任务功能**
- [x] **修复 API 请求失败问题**（~~增加更多 API~~ 或使用数据库）
- [ ] **优化发送内容的排版格式，提升用户阅读体验**
- [ ] **优化数据库结构和内容，提高查询效率**
- [ ] **提供更具体的错误日志提示，便于问题排查**
- [ ] **重构代码以提升可读性和维护性**
- [ ] **更多功能待补充……**

## 💡鸣谢

- [Nonebot](https://github.com/nonebot/nonebot2): 本项目的基础，非常好用的聊天机器人框架。
- [夏柔API](https://api.aa1.cn/author/1): API接口来源

## ⚠️ 注意事项

本插件目前仅支持 nonebot2 + onebot.v11 的使用方式, 一切非此二者结合的使用方式造成的问题请自行探索解决, 或者使用其他插件。

## License

[MIT](./LICENSE)
