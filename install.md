uv venv --python 3.14
uv pip install -r requirements.txt
准备浏览器当前版本对应的webdriver.exe并在Abspath.py中登记

# 下载
使用 yt-dlp --cookies-from-browser edge 需要关闭edge浏览器，这与项目中的设定冲突
所以需要使用--cookies参数读取cookies文件
yt-dlp --cookie 参数所要的文件暂时需要手动导出

# vscode插件
