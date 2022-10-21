from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import dialog
import os
import requests
import json
import re
import webbrowser


class Ui_MainWindow(object):
    def set_token(self):
        if self.token.toPlainText() == "":
            self.show_dialog = dialog.ShowInfoDialog("Token不能为空!")
            self.show_dialog.show_dialog()
            return
        with open("token.txt", 'w', encoding="utf-8") as f:
            f.write(self.token.toPlainText())
        self.show_dialog = dialog.ShowInfoDialog("设置成功! 请重启软件!")
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
            'authorization': f'Bearer {self.token_data}',
        }

        self.response = requests.get('https://api.lae.yistars.net/api/modules/frp/hosts', headers=self.headers)
        self.response.encoding = self.response.apparent_encoding
        if self.response.status_code != 200:
            self.show_dialog = dialog.ShowInfoDialog("请求失败! 请检查网络连接!")
            self.show_dialog.show_dialog()
            return
        self.tunnels = json.loads(self.response.text)
        self.chooseTunnel.clear()
        for i in range(len(self.tunnels["data"])):
            self.chooseTunnel.addItem(self.tunnels["data"][i]["name"])

    def start_tunnel(self):
        if not os.path.exists("token.txt"):
            self.show_dialog = dialog.ShowInfoDialog("您尚未设置Token!")
            self.show_dialog.show_dialog()
            return
        if self.chooseTunnel.currentText() == "":
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
            'authorization': f'Bearer {self.token_data}',
        }

        self.response = requests.get('https://api.lae.yistars.net/api/modules/frp/hosts', headers=self.headers)
        if self.response.status_code != 200:
            self.show_dialog = dialog.ShowInfoDialog("请求失败! 请检查网络连接!")
            self.show_dialog.show_dialog()
            return
        self.response.encoding = self.response.apparent_encoding
        self.tunnels = json.loads(self.response.text)
        self.regular = re.compile(r'.*?"id":(\d+),"name":"{}".*?'.format(self.chooseTunnel.currentText()))
        self.tunnelId = re.findall(self.regular, self.response.text)[0]
        self.headers_more = {
            'authorization': f'Bearer {self.token_data}',
        }
        self.response = requests.get(f'https://api.lae.yistars.net/api/modules/frp/hosts/{self.tunnelId}', headers=self.headers_more)
        self.response.encoding = self.response.apparent_encoding
        if self.response.status_code != 200:
            self.show_dialog = dialog.ShowInfoDialog("请求失败! 请检查网络连接!")
            self.show_dialog.show_dialog()
            return
        self.more_info_json = json.loads(self.response.text)
        self.ini_config = self.more_info_json["data"]["config"]["server"] + "\n\n" + self.more_info_json["data"]["config"]["client"]
        try:
            with open(f"temp/{self.more_info_json['data']['name']}.ini", 'w', encoding="utf-8") as f:
                f.write(self.ini_config)
        except FileNotFoundError:
            os.mkdir("temp")
            with open(f"temp/{self.more_info_json['data']['name']}.ini", 'w', encoding="utf-8") as f:
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
        self.stopTunnel.setDisabled(False)
        os.system(f"start run.bat {self.more_info_json['data']['name']}")

    def stop_tunnel(self):
        self.stopTunnel.setDisabled(True)
        os.system("taskkill /f /IM frpc.exe")
        self.outputLog.clear()

    def openTokenWebsite(self):
        webbrowser.open("https://auth.laecloud.com/")

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(620, 440)
        MainWindow.setWindowTitle(u"Mirror Edge Frp \u5ba2\u6237\u7aef - V1.3 Released")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(10, 10, 601, 421))
        self.Token_Settings = QWidget()
        self.Token_Settings.setObjectName(u"Token_Settings")
        self.setToken = QPushButton(self.Token_Settings)
        self.setToken.setObjectName(u"setToken")
        self.setToken.setGeometry(QRect(150, 250, 281, 23))
        self.setToken.setText(u"\u8bbe\u7f6eToken")
        self.token = QTextEdit(self.Token_Settings)
        self.token.setObjectName(u"token")
        self.token.setGeometry(QRect(150, 120, 281, 121))
        self.token.setPlaceholderText(u"\u7b2c\u4e00\u6b21\u4f7f\u7528\u8bf7\u5230auth.laecloud.com, \u70b9\u51fb\"\u83b7\u53d6\u65b0\u7684Token\"\u6309\u94ae, \u5c06Token\u590d\u5236\u5230\u8fd9\u91cc, \u7136\u540e\u70b9\u51fb\"\u8bbe\u7f6eToken\"\u6309\u94ae")
        self.label = QLabel(self.Token_Settings)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(150, 50, 291, 21))
        font = QFont()
        font.setFamily(u"SimSun-ExtB")
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setText(u"Token (\u53ea\u6709\u914d\u7f6e\u5b8cToken\u624d\u80fd\u6b63\u5e38\u4f7f\u7528)")
        self.openWebsite = QPushButton(self.Token_Settings)
        self.openWebsite.setObjectName(u"openWebsite")
        self.openWebsite.setGeometry(QRect(204, 80, 151, 23))
        self.openWebsite.setCursor(QCursor(Qt.PointingHandCursor))
        self.openWebsite.setFocusPolicy(Qt.NoFocus)
        self.openWebsite.setStyleSheet(u"")
        self.openWebsite.setText(u"\u6253\u5f00auth.laecloud.com")
        self.tabWidget.addTab(self.Token_Settings, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Token_Settings), u"Token\u8bbe\u7f6e")
        self.tunnelStart = QWidget()
        self.tunnelStart.setObjectName(u"tunnelStart")
        self.chooseTunnel = QComboBox(self.tunnelStart)
        self.chooseTunnel.setObjectName(u"chooseTunnel")
        self.chooseTunnel.setGeometry(QRect(70, 20, 291, 22))
        self.chooseTunnel.setCurrentText(u"")
        self.chooseTunnel.setPlaceholderText(u"--\u8bf7\u9009\u62e9--")
        self.startTunnel = QPushButton(self.tunnelStart)
        self.startTunnel.setObjectName(u"startTunnel")
        self.startTunnel.setGeometry(QRect(10, 90, 81, 31))
        self.startTunnel.setText(u"\u542f\u52a8\u96a7\u9053")
        self.stopTunnel = QPushButton(self.tunnelStart)
        self.stopTunnel.setObjectName(u"stopTunnel")
        self.stopTunnel.setGeometry(QRect(100, 90, 101, 31))
        self.stopTunnel.setText(u"\u505c\u6b62\u6240\u6709\u96a7\u9053")
        self.label_2 = QLabel(self.tunnelStart)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 20, 54, 21))
        self.label_2.setText(u"\u9009\u62e9\u96a7\u9053")
        self.outputLog = QTextEdit(self.tunnelStart)
        self.outputLog.setObjectName(u"outputLog")
        self.outputLog.setGeometry(QRect(10, 170, 571, 211))
        self.outputLog.setFocusPolicy(Qt.NoFocus)
        self.outputLog.setReadOnly(True)
        self.label_3 = QLabel(self.tunnelStart)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 140, 31, 21))
        self.label_3.setText(u"\u65e5\u5fd7")
        self.label_8 = QLabel(self.tunnelStart)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(10, 60, 41, 21))
        self.label_8.setText(u"\u64cd\u4f5c\u533a")
        self.refreshTunnel = QPushButton(self.tunnelStart)
        self.refreshTunnel.setObjectName(u"refreshTunnel")
        self.refreshTunnel.setGeometry(QRect(500, 90, 81, 31))
        self.refreshTunnel.setText(u"\u5237\u65b0\u96a7\u9053")
        self.tabWidget.addTab(self.tunnelStart, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tunnelStart), u"\u542f\u52a8\u96a7\u9053")
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

        # 自定义代码部分
        self.listOfTunnel()

        # 按钮点击事件绑定
        self.setToken.clicked.connect(self.set_token)
        self.startTunnel.clicked.connect(self.start_tunnel)
        self.stopTunnel.clicked.connect(self.stop_tunnel)
        self.openWebsite.clicked.connect(self.openTokenWebsite)
        self.refreshTunnel.clicked.connect(self.listOfTunnel)
        # 设置禁用停止/重启隧道按钮
        self.stopTunnel.setDisabled(True)

        # 如果有token.txt文件直接切换到隧道板块
        if os.path.exists("token.txt"):
            self.tabWidget.setCurrentIndex(1)

        # StyleSheet部分
        self.openWebsite.setStyleSheet("""
        border: none;
        color: #0d6efd;
        text-decoration: underline;
        """)
        QMetaObject.connectSlotsByName(MainWindow)
