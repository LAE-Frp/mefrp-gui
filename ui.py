from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import dialog
import os
import requests
import json
import re


class Ui_MainWindow(object):
    def set_token(self):
        with open("token.txt", 'w', encoding="utf-8") as f:
            f.write(self.token.toPlainText())
        self.show_dialog = dialog.ShowInfoDialog("设置成功!")
        self.show_dialog.show_dialog()

    def listOfTunnel(self):
        if not os.path.exists("token.txt"):
            self.show_dialog = dialog.ShowInfoDialog("您尚未设置Token!")
            self.show_dialog.show_dialog()
            return
        with open("token.txt", 'r', encoding="utf-8") as f:
            self.token_data = f.read()
        self.token_data = self.token_data.strip()
        self.token_data = self.token_data.replace("\n", "")
        self.headers = {
            'authority': 'api.lae.yistars.net',
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'authorization': f'Bearer {self.token_data}',
            'origin': 'https://panel.mefrp.com',
            'referer': 'https://panel.mefrp.com/',
            'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        }

        self.response = requests.get('https://api.lae.yistars.net/api/modules/frp/hosts', headers=self.headers)
        self.response.encoding = self.response.apparent_encoding
        if self.response.status_code != 200:
            self.show_dialog = dialog.ShowInfoDialog("请求失败! 请检查网络连接!")
            self.show_dialog.show_dialog()
            return
        self.tunnels = json.loads(self.response.text)
        for i in range(len(self.tunnels["data"])):
            self.chooseTunnel.addItem(self.tunnels["data"][i]["name"])

    def start_tunnel(self):
        if not os.path.exists("token.txt"):
            self.show_dialog = dialog.ShowInfoDialog("您尚未设置Token!")
            self.show_dialog.show_dialog()
            return
        if self.chooseTunnel.currentText() == "" or self.chooseTunnel.currentText() == None:
            self.show_dialog = dialog.ShowInfoDialog("您尚未选择隧道!")
            self.show_dialog.show_dialog()
            return
        if not os.path.exists("frpc.exe"):
            self.show_dialog = dialog.ShowInfoDialog("frpc.exe文件缺失, 请重新下载启动器!")
            self.show_dialog.show_dialog()
            return
        with open("token.txt", 'r', encoding="utf-8") as f:
            self.token_data = f.read()
        self.token_data = self.token_data.strip()
        self.token_data = self.token_data.replace("\n", "")
        self.headers = {
            'authority': 'api.lae.yistars.net',
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'authorization': f'Bearer {self.token_data}',
            'origin': 'https://panel.mefrp.com',
            'referer': 'https://panel.mefrp.com/',
            'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        }
        self.response = requests.get('https://api.lae.yistars.net/api/modules/frp/hosts', headers=self.headers)
        if self.response.status_code != 200:
            self.show_dialog = dialog.ShowInfoDialog("请求失败! 请检查网络连接!")
            self.show_dialog.show_dialog()
            return
        self.response.encoding = self.response.apparent_encoding
        self.tunnels = json.loads(self.response.text)
        print(self.tunnels)
        self.regular = re.compile(r'.*?"id":(\d+),"name":"{}".*?'.format(self.chooseTunnel.currentText()))
        try:
            self.tunnelId = re.findall(self.regular, self.response.text)[0]
        except IndexError:
            pass
        self.headers_more = {
            'authority': 'api.lae.yistars.net',
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'authorization': f'Bearer {self.token_data}',
            'origin': 'https://panel.mefrp.com',
            'referer': 'https://panel.mefrp.com/',
            'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        }
        try:
            self.response = requests.get(f'https://api.lae.yistars.net/api/modules/frp/hosts/{self.tunnelId}', headers=self.headers_more)
        except AttributeError:
            self.show_dialog = dialog.ShowInfoDialog("暂不支持中文隧道哦~\n请尝试删除隧道+创建新非中文隧道\n并重启软件！\n或手动启动Frp！")
            self.show_dialog.show_dialog()
            return
        self.response.encoding = self.response.apparent_encoding
        if self.response.status_code != 200:
            self.show_dialog = dialog.ShowInfoDialog("请求失败! 请检查网络连接!")
            self.show_dialog.show_dialog()
            return
        self.more_info_json = json.loads(self.response.text)
        self.ini_config = self.more_info_json["data"]["config"]["server"] + "\n\n" + self.more_info_json["data"]["config"]["client"]
        with open("frpc.ini", 'w', encoding="utf-8") as f:
            f.write(self.ini_config)
        self.baseLog = r"""   __  __ ___   ___         
  /  \/  / __/ / __/ _ ___ 
 / /\// / _/  / _/ '_/ '_\
/_/  /_/___/ /_//_/ / .__/
                   /_/   
                   
ME Frp 服务即将启动
弹出框出现 start proxy success 即为隧道启动成功，否则隧道尚未启动。


"""
        self.outputLog.setText(self.baseLog)
        self.startTunnel.setDisabled(True)
        self.stopTunnel.setDisabled(False)
        self.restartTunnel.setDisabled(False)
        os.system("start run.bat")

    def stop_tunnel(self):
        self.startTunnel.setDisabled(False)
        self.stopTunnel.setDisabled(True)
        self.restartTunnel.setDisabled(True)
        os.system("taskkill /f /IM frpc.exe")
        self.outputLog.clear()

    def restart_tunnel(self):
        os.system("taskkill /f /IM frpc.exe")
        os.system("start run.bat")
        self.outputLog.clear()
        self.log = self.baseLog + "隧道已重启"
        self.outputLog.setText(self.log)

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(620, 440)
        MainWindow.setWindowTitle(u"Mirror Edge Frp \u5ba2\u6237\u7aef - V1.0.2 Released")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(10, 10, 601, 411))
        self.Token_Settings = QWidget()
        self.Token_Settings.setObjectName(u"Token_Settings")
        self.setToken = QPushButton(self.Token_Settings)
        self.setToken.setObjectName(u"setToken")
        self.setToken.setGeometry(QRect(150, 250, 281, 23))
        self.setToken.setText(u"\u8bbe\u7f6eToken")
        self.token = QTextEdit(self.Token_Settings)
        self.token.setObjectName(u"token")
        self.token.setGeometry(QRect(150, 110, 281, 131))
        self.token.setPlaceholderText(
            u"\u7b2c\u4e00\u6b21\u4f7f\u7528\u8bf7\u5230auth.laecloud.com, \u70b9\u51fb\"\u83b7\u53d6\u65b0\u7684Token\"\u6309\u94ae, \u5c06Token\u590d\u5236\u5230\u8fd9\u91cc, \u7136\u540e\u70b9\u51fb\"\u8bbe\u7f6eToken\"\u6309\u94ae")
        self.label = QLabel(self.Token_Settings)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(150, 70, 291, 21))
        font = QFont()
        font.setFamily(u"SimSun-ExtB")
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setText(u"Token (\u53ea\u6709\u914d\u7f6e\u5b8cToken\u624d\u80fd\u6b63\u5e38\u4f7f\u7528)")
        self.tabWidget.addTab(self.Token_Settings, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Token_Settings), u"Token\u8bbe\u7f6e")
        self.tunnel = QWidget()
        self.tunnel.setObjectName(u"tunnel")
        self.chooseTunnel = QComboBox(self.tunnel)
        self.chooseTunnel.setObjectName(u"chooseTunnel")
        self.chooseTunnel.setGeometry(QRect(70, 20, 231, 22))
        self.chooseTunnel.setCurrentText(u"")
        self.chooseTunnel.setPlaceholderText(u"--\u8bf7\u9009\u62e9--")
        self.startTunnel = QPushButton(self.tunnel)
        self.startTunnel.setObjectName(u"startTunnel")
        self.startTunnel.setGeometry(QRect(310, 20, 75, 21))
        self.startTunnel.setText(u"\u542f\u52a8\u96a7\u9053")
        self.stopTunnel = QPushButton(self.tunnel)
        self.stopTunnel.setObjectName(u"stopTunnel")
        self.stopTunnel.setGeometry(QRect(400, 20, 75, 21))
        self.stopTunnel.setText(u"\u505c\u6b62\u96a7\u9053")
        self.restartTunnel = QPushButton(self.tunnel)
        self.restartTunnel.setObjectName(u"restartTunnel")
        self.restartTunnel.setGeometry(QRect(490, 20, 75, 21))
        self.restartTunnel.setText(u"\u91cd\u542f\u96a7\u9053")
        self.label_2 = QLabel(self.tunnel)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 20, 54, 21))
        self.label_2.setText(u"\u9009\u62e9\u96a7\u9053")
        self.outputLog = QTextEdit(self.tunnel)
        self.outputLog.setObjectName(u"outputLog")
        self.outputLog.setGeometry(QRect(10, 100, 571, 281))
        self.outputLog.setFocusPolicy(Qt.NoFocus)
        self.outputLog.setReadOnly(True)
        self.label_3 = QLabel(self.tunnel)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 70, 101, 21))
        self.label_3.setText(u"\u65e5\u5fd7")
        self.tabWidget.addTab(self.tunnel, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tunnel), u"\u96a7\u9053")
        self.about = QWidget()
        self.about.setObjectName(u"about")
        self.label_4 = QLabel(self.about)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(0, 60, 601, 51))
        font1 = QFont()
        font1.setFamily(u"Segoe UI")
        font1.setPointSize(16)
        self.label_4.setFont(font1)
        self.label_4.setText(u"Copyright \u00a9 kingc, All rights reserved.")
        self.label_4.setAlignment(Qt.AlignCenter)
        self.label_5 = QLabel(self.about)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(0, 110, 601, 51))
        self.label_5.setFont(font1)
        self.label_5.setText(u"Copyright \u00a9 ME Frp 2022.")
        self.label_5.setAlignment(Qt.AlignCenter)
        self.label_6 = QLabel(self.about)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(0, 240, 601, 51))
        font2 = QFont()
        font2.setFamily(u"Comic Sans MS")
        font2.setPointSize(16)
        self.label_6.setFont(font2)
        self.label_6.setText(u"Designed By Qt Designer")
        self.label_6.setAlignment(Qt.AlignCenter)
        self.label_7 = QLabel(self.about)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(0, 280, 601, 51))
        self.label_7.setFont(font2)
        self.label_7.setText(u"This program uses Qt version 5.15.4")
        self.label_7.setAlignment(Qt.AlignCenter)
        self.tabWidget.addTab(self.about, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.about), u"\u5173\u4e8e")
        MainWindow.setCentralWidget(self.centralwidget)

        self.tabWidget.setCurrentIndex(0)
        self.listOfTunnel()

        self.setToken.clicked.connect(self.set_token)
        self.startTunnel.clicked.connect(self.start_tunnel)
        self.stopTunnel.clicked.connect(self.stop_tunnel)
        self.restartTunnel.clicked.connect(self.restart_tunnel)
        self.stopTunnel.setDisabled(True)
        self.restartTunnel.setDisabled(True)

        QMetaObject.connectSlotsByName(MainWindow)
