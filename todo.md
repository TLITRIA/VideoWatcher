##### https://doc.qt.io/qtforpython-6.8/

# TODO:
videowatch 寻找程序中临时布置的代码，并分轻重缓急处理：
    InfoWidget内部问题：
        1-isblocked属性 程序更新和用户操作更新时不可
        2-isdeleted属性 控件未能按时销毁
        3-im 同步所有infowidget更新
    focus 防止mywebwidget连接到已关闭的标签页
    BackWebDriver 为了适配后台运行的需求，似乎没必要，反正新进程的单例与主进程无关
    self.dbw 触发函数创建的界面无法保存

- dialog新增一个排除表记录排除原因的功能 todo
- 评论区和简介中的url链接提取 todo
- 每个控件添加一个测试脚本 todo
- 如何适配油管？是在已有控件上修改，还是重新写一个控件？ todo
- dbViewWidget添加，编辑数据库中的信息 todo
- entry、playlistWidget添加自动前往默认收藏夹的功能 done
- infowidget设置初始化 noneed
- 在biliParse、biliAccess中不区分前台还是后台webdriver，而在调用的时候区分。删除BackWebDriver done
- playlist自己设置读取的数量 todo
- 将路径在abspath.py中统一处理 todo
- 访问bilibili页面出现404怎么处理？ todo

# Done
- 添加了dbwidget，可以查看数据库中的信息
- entrywidget添加默认收藏夹、数据库查看功能

# FATAL ERROR
滚轮交互tag框时会导致tag异常添加，原因未知 todo

CHECK:
- 隐私信息
B站个人id
用户路径、用户名称



