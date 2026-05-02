---
title: Flower Image Classification
emoji: 🌸
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
---

# flower_web_flask

本项目是花卉分类桌面版项目复制出的本地 Flask Web 版，复用现有 ResNet18 模型权重和 `model/class_names_zh_en.json`，不需要重新训练模型。

## 依赖

当前项目需要：

```bat
pip install -r requirements.txt
```

如果已经能正常打开网页并完成预测，就不需要重复安装。

## 本地访问

双击项目根目录下的：

```text
start_flask.bat
```

启动后在浏览器访问：

```text
http://127.0.0.1:5000
```

也可以在命令行手动运行：

```bat
cd /d E:\MyProjects\flower_web_flask
python app.py
```

## 公网临时访问

公网访问需要两个窗口同时运行：

1. 先双击 `start_flask.bat`，启动本地 Flask 服务。
2. 再双击 `start_cloudflared.bat`，启动 Cloudflare 临时公网隧道。
3. 在第二个黑色窗口中找到生成的 `trycloudflare.com` 链接，用手机或其他设备访问这个链接。

`start_cloudflared.bat` 使用的 cloudflared 路径是：

```text
D:\Download\Edge\cloudflared.exe
```

注意：

- 两个黑色窗口都不能关闭。
- 关闭 Flask 窗口后，本地服务停止，公网链接无法继续预测。
- 关闭 cloudflared 窗口后，公网链接会立即失效。
- 下次重新运行 `start_cloudflared.bat` 会生成新的 `trycloudflare.com` 临时链接。

## 停止服务

在对应黑色窗口中按 `Ctrl+C`，确认终止后关闭窗口即可。
