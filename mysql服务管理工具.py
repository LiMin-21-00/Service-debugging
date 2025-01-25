import os
import shutil
import subprocess
import sys
import argparse

"""
MySQL数据库服务管理工具，需要系统管理员权限
当前版本为: 1.1.2.0
版本规则为:
    第一位:核心结构更新,
    第二位:使用体验更新,
    第三位:合并新增功能,
    第四位:报告漏洞修复
"""


def MySQL数据库服务管理工具():
    MYSQL_HOME = r"C:\Program Files\MySQL\MySQL Server 8.3"
    MYSQL_HOME_HPP = "Service_Name.hpp"
    serverManager = MySqlServiceManager(MYSQL_HOME, MYSQL_HOME_HPP)
    print("""\n
    ---------|———————-—————|---------
    ---+++---| MySQL数据库服务管理工具 |---+++---
    ---------|——————-——————|---------\n
    可用功能：
        ·查询服务 ·创建服务 ·删除服务 ·初始化服务 ·启动/停止服务
    """)
    while True:
        x = input('<·')
        if x == "查询服务":
            serverManager.Inquire()
        elif x == "创建服务":
            serverManager.create()
        elif x == "删除服务":
            serverManager.delete()
        elif x == "初始化服务":
            serverManager.initialize()
        elif x == "启动服务":
            serverManager.commandPrompt(True)
        elif x == "停止服务":
            serverManager.commandPrompt(False)
        elif x == "exit" or x == "quit":
            break
        else:
            print("输入错误")
            print("可用功能：\n  ·查询服务 ·创建服务 ·删除服务 ·初始化服务 ·启动/停止服务")


class MySqlServiceManager:
    def __init__(self, Home, ServiceTable):
        self.content_list = None
        self.BIN_MYSQLD = Home + r"\bin\mysqld.exe"
        self.MYSQL_HOME_DATA = os.path.join(Home, "data")
        self.MYSQL_SERVICE_TABLE = os.path.join(Home, ServiceTable)

        # 确保服务表文件被创建
        with open(self.MYSQL_SERVICE_TABLE, 'a', encoding='utf-8'):
            pass

    def Inquire(self, bool=True):  # 查询服务
        # 尝试打开表文件并读取内容
        with open(self.MYSQL_SERVICE_TABLE, 'r', encoding='utf-8') as file:
            # 读取文件内容并按换行符分割成列表
            self.content_list = list(filter(None, (line.strip() for line in file)))
        if not bool:
            return
        # 如果列表为空，则返回提示信息
        if not self.content_list:
            print("MySqlService中还未安装任何服务")
        else:
            print(f"在MySqlService中，已安装{len(self.content_list)}个服务")
            a = 1
            for i in self.content_list:
                print(f"{a}. {i}")
                a += 1

    def create(self):  # 创建服务
        self.Inquire(False)
        serviceName = input("新服务名：")
        if serviceName in self.content_list:
            print(f"创建失败，原因是 {serviceName} 服务以存在")
            return
        subprocess.run([self.BIN_MYSQLD, "--install", serviceName])
        # 存储已创建的MySQL服务信息
        with open(self.MYSQL_SERVICE_TABLE, 'a', encoding='utf-8') as file:
            file.write(serviceName + '\n')

    def delete(self):  # 删除服务
        self.Inquire(False)
        serviceName = input("将被移除的服务名：")
        if not (serviceName in self.content_list):
            print(f"删除失败，原因是 {serviceName} 服务不存在")
            return
        subprocess.run([self.BIN_MYSQLD, "--remove", serviceName])
        self.content_list.remove(serviceName)
        # 存储新的MySQL服务信息
        with open(self.MYSQL_SERVICE_TABLE, 'w', encoding='utf-8') as file:
            for i in self.content_list:
                file.write(i + '\n')

    def initialize(self):  # 初始化服务
        if os.path.exists(self.MYSQL_HOME_DATA) and os.path.isdir(self.MYSQL_HOME_DATA):
            if input("mysql服务器中存在初始配置文件。\n需删除后才能初始化服务，是否删除（y/n）：") == 'y':
                try:
                    # 使用shutil.rmtree来删除初始配置文件夹及其所有内容
                    print("正在删除文件")
                    shutil.rmtree(self.MYSQL_HOME_DATA)

                except OSError as e:
                    print(f"删除 mysql服务器初始配置文件 时发生错误: {e.strerror}")
                    return
            else:
                return

        subprocess.run([self.BIN_MYSQLD, "--initialize-insecure"])
        print("————已完成服务器初始化————")

    @staticmethod
    def commandPrompt(x):
        serviceName = input(("即将启动的" if x else "即将停止的") + "服务名称：")
        subprocess.run([
            "net",
            "start" if x else "stop",
            serviceName
        ])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--o', type=int, default=-1)
    args = parser.parse_args()
    if not args.o == -1:
        MySQL数据库服务管理工具()
    else:
        """
        尝试以管理员权限重新启动当前脚本，已确认执行权限
        """
        script_path = sys.argv[0]
        python_exe = sys.executable
        cmd = f'Start-Process -FilePath "{python_exe}" -ArgumentList @("{script_path}", "--o", "0") -Verb runAs'
        # 尝试以管理员身份运行
        try:
            subprocess.Popen(['powershell', '-Command', cmd], shell=False)
            print("脚本已尝试以管理员权限重新启动，请确认UAC提示。")
        except Exception as e:
            print(f"无法以管理员权限重新启动脚本: {e}")
