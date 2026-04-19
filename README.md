<div align=center>
  <img src="logo.png" alt="" width="128">
</div>

<h2 align="center">
External Knowledge Base Retrieval
</h2>

<h2 align="center">
Astrbot Plugin
</h2>
<h2 align="center">
Astrbot 插件 - 外部知识库检索
</h2>

<div align="center">
💖 一款可以让 AstrBot Bot 自由访问外部知识库的插件，使用 Python 编写 😎
</div>
<div align="center">
由 POINTER 用 ❤️ 制作
</div>

<div align="center">

[中文 README](README.md) | [English README](README_en.md)

</div>

<div align=center>

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/)
[![Ask Zread](https://img.shields.io/badge/Ask_Zread-_.svg?style=flat&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff)](https://zread.ai/)
[![Ask Code Wiki](https://img.shields.io/badge/-Ask_Code_Wiki-0e182e?style=flat&logo=googlegemini&logoColor=6192f7&labelColor=000000)](https://codewiki.google/)

</div>

> [!NOTE]
> 本插件正在开发中......
>
> 本插件暂未上架 AstrBot 插件市场
>
> 本插件因为还在开发中，所以版本号可能会保持不变

## 主要功能

让 AstrBot Bot 自由访问外部知识库，并且提供3种决策方案供用户选择

## 更新路线图

- [x] 加入查询知识库的决策层

## 安装

AstrBot Web UI - 插件 - 右下角"+"号 - 从链接安装

## 使用

按 AstrBot Web UI 中本插件设置的引导使用

也可以查看下面 `## 插件配置` 获取详细信息

## 支持的外部知识库

[Dify](https://dify.ai/)（推荐）

[Flowise](https://flowiseai.com/)

[RAGFlow](https://ragflow.io/)（未经过完善测试）

## 插件配置

### 决策模式

L1: 总是发送知识库查询并把匹配到的内容注入提示词

L2: 通过关键词判断是否执行 `L1`

L3: 调用大模型进行意图识别（推荐使用输出速度快的模型以保证整体的回复速度）

### 默认提示词

#### L2

请问,解释,文档,是什么,介绍,怎么,如何,帮我,可以,帮

#### L3

你是一个意图识别引擎。
用户语境:
{history}
用户当前输入: {user_msg}
判断用户上述输入是否是在提问查资料并需要通过外部知识库或文档检索进一步的背景知识。如果需要检索额外资料，回答YES，否则如果只是日常聊天或不需要检索资料，回答NO。只输出YES或NO。

#### 查询重写

根据以下对话历史，将用户的最新输入重写为独立的搜索查询词。核心任务是：解决指代不明，将代词(他,那个等)替换为具体提及的实体；如果不需要重写，直接输出用户输入内容。只输出重写后的内容，不要作答或解释。

对话历史:
{history}

用户最新的需重写输入: {user_msg}

#### 知识库检索结果注入

请参考以下背景知识来回答用户的问题（如果背景知识与问题无关可以忽略）：
{context_str}

请结合以上背景知识回答问题。

### 知识库 API 基地址

#### 官方云服务

Dify: https://api.dify.ai/v1

RAGFlow: N/A (仅支持本地部署)

Flowise: https://cloud.flowiseai.com/api/v1

#### 本地部署（包括 Docker 部署）

请修改 API 端点（API 基地址）为你的可访问地址，比如 `http://127.0.0.1:3000/api/v1`

## 感谢

[Dependencies](https://github.com/jin6yang/astrbot_plugin_external_knowledgebase/network/dependencies)

[AstrBotDevs/AstrBot✨](https://github.com/AstrBotDevs/AstrBot)

## 开发支持

- [AstrBot Repo](https://github.com/AstrBotDevs/AstrBot)
- [AstrBot Plugin Development Docs (Chinese)](https://docs.astrbot.app/dev/star/plugin-new.html)
- [AstrBot Plugin Development Docs (English)](https://docs.astrbot.app/en/dev/star/plugin-new.html)

## 许可证

![](agplv3-155x51.png)
