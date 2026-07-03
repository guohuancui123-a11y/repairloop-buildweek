# Social Exposure Posts

## X / Twitter - concise

I built a tiny open-source tool that starts from the crash, not the prompt.

Run broken Python code → it reads the real error → applies a small local fix → reruns to verify.

No API key.
No cloud.
No source upload.
Dry-run by default.

GitHub:
https://github.com/guohuancui123-a11y/lobster-ai-system

#Python #OpenSource #DevTools #Debugging

## X / Twitter - demo focused

BROKEN CODE → CRASH → FIX → RETRY → SUCCESS

Lobster is a local-first repair loop for Python runtime errors.

It does not guess from a prompt.
It runs the failing command, reads the real traceback, applies a small safe fix, and verifies by rerunning.

GitHub:
https://github.com/guohuancui123-a11y/lobster-ai-system

## Xiaohongshu title

坏掉的 Python 代码，真的可以自动修好吗？

## Xiaohongshu body

最近做了一个本地优先的 Python 自动修复工具：Lobster AI System。

它不是让 AI 猜代码怎么改，而是从真实运行错误开始：

坏代码 → 运行崩溃 → 读取报错 → 应用小修复 → 重新运行验证

我觉得这个方向有意思的地方是：它不追求一上来生成一大段新代码，而是盯着第一个真实报错，做一个小修复，然后立刻复跑验证。

目前特点：

- 不需要 API Key
- 不需要云端模型
- 不上传你的代码
- 默认 dry-run，不会一上来乱改文件
- 本地规则引擎可以运行
- 修复后会重新执行原命令验证

现在 v0.1.1 支持一些常见 Python 运行问题：

- 缺依赖
- 缺文件
- 少冒号语法错误
- Flask / Werkzeug 兼容问题
- SQLite 数据目录 / 表缺失问题

项目已开源：
https://github.com/guohuancui123-a11y/lobster-ai-system

如果你经常被 Python 报错折磨，可以看看这个思路。

#Python #开源项目 #程序员 #AI工具 #自动修复 #GitHub #编程工具
