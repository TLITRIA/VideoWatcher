uv venv --python 3.14
uv pip install -r requirements.txt
准备浏览器当前版本对应的webdriver.exe并在Abspath.py中登记

# 下载
使用 yt-dlp --cookies-from-browser edge 需要关闭edge浏览器，这与项目中的设定冲突
所以需要使用--cookies参数读取cookies文件
yt-dlp --cookie 参数所要的文件暂时需要手动导出

# vscode插件
步骤 1：安装插件
打开 VSCode 扩展市场，搜索 Black Formatter 并安装。

步骤 2：设置为默认格式化工具
打开命令面板 Ctrl+Shift+P，搜索 Open User Settings (JSON)，添加：
{
    "editor.defaultFormatter": "ms-python.black-formatter"
}

步骤 3：配置行长度等参数
在 settings.json 中添加：
"black-formatter.args": ["--line-length", "120"],
"editor.formatOnSave": true
这样保存文件时会自动按 Black 规则格式化，并将单行限制为 120 字符。