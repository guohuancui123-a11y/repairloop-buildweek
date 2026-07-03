# 小红书发布文案

## 标题

坏掉的 Python 代码，真的可以自动修好吗？

## 正文

最近做了一个本地优先的 Python 自动修复工具：**Lobster AI System**。

它的思路不是让 AI 直接“猜代码怎么改”，而是从真实运行错误开始：

```text
坏代码 → 运行崩溃 → 读取报错 → 应用小修复 → 重新运行验证
```

简单说，就是让工具盯着真实错误，一步一步把程序修到能跑。

它目前的特点：

- 不需要 API Key
- 不需要云端模型
- 不上传你的代码
- 默认 dry-run，不会一上来乱改文件
- 本地规则引擎就能运行
- 修复后会重新执行原命令验证

现在 v0.1 支持一些常见 Python 运行问题：

- 缺依赖：`ModuleNotFoundError`
- 缺文件：`FileNotFoundError`
- 少冒号：`SyntaxError: expected ':'`
- Flask / Werkzeug 版本兼容问题
- SQLite 数据目录 / 表缺失问题

这个方向我觉得挺有意思：

**不是生成一堆新代码，而是从真实报错出发，把坏掉的程序一步步修好。**

项目已开源：
https://github.com/guohuancui123-a11y/lobster-ai-system

如果你经常被 Python 报错折磨，可以看看这个思路。

#Python #开源项目 #程序员 #AI工具 #自动修复 #GitHub #编程工具 #独立开发

## 视频素材

E:\GitHub\lobster-ai-system\docs\assets\lobster-demo-vertical-clean.mp4
