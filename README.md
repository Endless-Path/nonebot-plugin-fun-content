<p align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://user-images.githubusercontent.com/44545625/209862575-acdc9feb-3c76-471d-ad89-cc78927e5875.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
</p>

<div align="center">

# nonebot-plugin-fun-content

_✨趣味内容插件✨_

</div>

<p align="center">
  <a href="https://raw.githubusercontent.com/kexue-z/nonebot-plugin-setu-now/master/LICENSE">
    <img src="https://img.shields.io/github/license/kexue-z/nonebot-plugin-setu-now.svg" alt="license">
  </a>
  <a href="https://pypi.org/project/nonebot-plugin-setu-now/">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-fun-content" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">
</p>


## 📖 介绍
>本人并非计算机类的专业，水平有限，如有问题或建议请直接发issue，我会尽量解决

本插件主要用于从多个 API 获取趣味内容，如一言、土味情话、舔狗日记等。

## 💿 如何安装
<details open>
<summary>使用 nb-cli 安装</summary>
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

## 🎉 指令列表
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| 一言 | 所有人 | 否 | 群聊 | 获取一句话的灵感 |
| 土味情话 | 所有人 | 否 | 群聊 | 获取一条土味情话 |
| 舔狗日记 | 所有人 | 否 | 群聊 | 获取一篇舔狗日记 |
| 人间凑数 | 所有人 | 否 | 群聊 | 获取人间凑数内容 |
| 微博热搜 | 所有人 | 否 | 群聊 | 获取当前微博热搜内容 |
| 爱情公寓 | 所有人 | 否 | 群聊 | 获取爱情公寓语录 |
| 随机白丝 | 所有人 | 否 | 群聊 | 获取随机白丝内容 |
| cp 角色1 角色2 | 所有人 | 否 | 群聊 | 获取宇宙CP文 |
| 神回复 | 所有人 | 否 | 群聊 | 获取神回复内容 |

## 将来可能支持的功能
- [ ] 指令频率限制
- [ ] 分群禁用
- [ ] 分功能分群禁用
- [ ] 加入定时计划
- [ ] API调用优化
- [ ] ......

## 💡鸣谢
- [Nonebot](https://github.com/nonebot/nonebot2): 本项目的基础，非常好用的聊天机器人框架。
- [夏柔API](https://api.aa1.cn/author/1):API接口来源

## ⚠️ 注意事项
本插件目前仅支持 nonebot2 + onebot.v11 的使用方式, 一切非此二者结合的使用方式造成的问题请自行探索解决, 或者使用其他插件。