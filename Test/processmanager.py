'''
ProcessManager启动的位置要注意，在__name__ == '__main__'下启动
'''
# TODO 假如有一列表的任务，如何按照managerworker的数目分配
# TODO 应用中有什么问题？
# 似乎开辟线程后全局变量也会变，单例类也会再创建一个新的对象
