import json
import os
import random
import re
import webbrowser

import requests
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import dialog


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

    def randomTunnelName(self):
        self.chars = []
        for i in range(65, 91):
            self.chars.append(chr(i))
        for i in range(97, 123):
            self.chars.append(chr(i))
        self.gen_tunnel_name_list = []
        for i in range(10):
            self.gen_tunnel_name_list.append(random.choice(self.chars))
        self.gen_tunnel_name = ""
        for i in range(10):
            self.gen_tunnel_name = self.gen_tunnel_name + self.gen_tunnel_name_list[i]
        return self.gen_tunnel_name

    def clear_cache(self):
        try:
            self.allIniFile = os.listdir("temp")
        except FileNotFoundError:
            self.show_dialog = dialog.ShowInfoDialog("无缓存配置可清理!")
            self.show_dialog.show_dialog()
            return
        os.chdir("temp")
        for i in range(len(self.allIniFile)):
            os.remove(self.allIniFile[i])
        os.chdir("..")
        os.rmdir("temp")
        self.show_dialog = dialog.ShowInfoDialog("清理成功!")
        self.show_dialog.show_dialog()

    def getPersonalInfo(self):
        if not os.path.exists("token.txt"):
            self.show_dialog = dialog.ShowInfoDialog("您尚未设置Token!")
            self.show_dialog.show_dialog()
            # 特殊需求return false
            return False
        with open("token.txt", 'r', encoding="utf-8") as f:
            self.token_data = f.read()
        self.token_data = self.token_data.strip()
        self.token_data = self.token_data.replace("\n", "")
        self.headers = {
            'authorization': f'Bearer {self.token_data}',
        }
        self.response = requests.get("https://api.laecloud.com/api/users", headers=self.headers)
        self.response.encoding = self.response.apparent_encoding
        if self.response.status_code != 200:
            self.show_dialog = dialog.ShowInfoDialog(
                f"向后端接口发送请求时发生错误:\n\n{self.response.status_code}: {self.tunnels['data']}")
            self.show_dialog.show_dialog()
            return
        try:
            self.personal_info = json.loads(self.response.text)
        except json.decoder.JSONDecodeError:
            self.show_dialog = dialog.ShowInfoDialog(
                f"对后端接口返回JSON数据解码时发生错误:\n\n{self.response.status_code}: {self.response.text}")
            self.show_dialog.show_dialog()
            return
        self.return_data = []
        self.return_data.append(self.personal_info["data"]["name"])
        self.return_data.append(str(self.personal_info["data"]["id"]))
        self.return_data.append(str(self.personal_info["data"]["balance"]))
        self.return_data.append(self.personal_info["data"]["email"])
        return self.return_data

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

        self.response = requests.get('https://api.laecloud.com/api/modules/frp/hosts', headers=self.headers)
        self.response.encoding = self.response.apparent_encoding
        try:
            self.tunnels = json.loads(self.response.text)
        except json.decoder.JSONDecodeError:
            self.show_dialog = dialog.ShowInfoDialog(
                f"对后端接口返回JSON数据解码时发生错误:\n\n{self.response.status_code}: {self.response.text}")
            self.show_dialog.show_dialog()
            return
        if self.response.status_code != 200:
            self.show_dialog = dialog.ShowInfoDialog(
                f"向后端接口发送请求时发生错误:\n\n{self.response.status_code}: {self.tunnels['data']}")
            self.show_dialog.show_dialog()
            return
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

        self.response = requests.get('https://api.laecloud.com/api/modules/frp/hosts', headers=self.headers)
        self.response.encoding = self.response.apparent_encoding
        try:
            self.tunnels = json.loads(self.response.text)
        except json.decoder.JSONDecodeError:
            self.show_dialog = dialog.ShowInfoDialog(
                f"对后端接口返回JSON数据解码时发生错误:\n\n{self.response.status_code}: {self.response.text}")
            self.show_dialog.show_dialog()
            return
        if self.response.status_code != 200:
            self.show_dialog = dialog.ShowInfoDialog(
                f"向后端接口发送请求时发生错误:\n\n{self.response.status_code}: {self.tunnels['data']}")
            self.show_dialog.show_dialog()
            return
        self.regular = re.compile(r'.*?"id":(\d+),"name":"{}".*?'.format(self.chooseTunnel.currentText()))
        self.tunnelId = re.findall(self.regular, self.response.text)[0]
        self.headers_more = {
            'authorization': f'Bearer {self.token_data}',
        }
        self.response = requests.get(f'https://api.laecloud.com/api/modules/frp/hosts/{self.tunnelId}',
                                     headers=self.headers_more)
        self.response.encoding = self.response.apparent_encoding
        try:
            self.more_info_json = json.loads(self.response.text)
        except json.decoder.JSONDecodeError:
            self.show_dialog = dialog.ShowInfoDialog(
                f"对后端接口返回JSON数据解码时发生错误:\n\n{self.response.status_code}: {self.response.text}")
            self.show_dialog.show_dialog()
            return
        if self.response.status_code != 200:
            self.show_dialog = dialog.ShowInfoDialog(
                f"向后端接口发送请求时发生错误:\n\n{self.response.status_code}: {self.more_info_json['data']}")
            self.show_dialog.show_dialog()
            return
        self.ini_config = self.more_info_json["data"]["config"]["server"] + "\n\n" + \
                          self.more_info_json["data"]["config"]["client"]
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
        webbrowser.open("https://api.laecloud.com/")

    def openStatusWebsite(self):
        webbrowser.open("https://dash.laecloud.com/servers")

    def updateCreateTunnelPage(self):
        if self.protocol.currentText() == "HTTP":
            self.choose_server.clear()
            for i in range(len(self.servers["data"])):
                if self.servers["data"][i]["allow_http"] == 1 and self.servers["data"][i]["status"] == "up":
                    self.choose_server.addItem(self.servers["data"][i]["name"])
        elif self.protocol.currentText() == "HTTPS":
            self.choose_server.clear()
            for i in range(len(self.servers["data"])):
                if self.servers["data"][i]["allow_https"] == 1 and self.servers["data"][i]["status"] == "up":
                    self.choose_server.addItem(self.servers["data"][i]["name"])
        elif self.protocol.currentText() == "TCP":
            self.choose_server.clear()
            for i in range(len(self.servers["data"])):
                if self.servers["data"][i]["allow_tcp"] == 1 and self.servers["data"][i]["status"] == "up":
                    self.choose_server.addItem(self.servers["data"][i]["name"])
        elif self.protocol.currentText() == "UDP":
            self.choose_server.clear()
            for i in range(len(self.servers["data"])):
                if self.servers["data"][i]["allow_udp"] == 1 and self.servers["data"][i]["status"] == "up":
                    self.choose_server.addItem(self.servers["data"][i]["name"])
        self.label_12.setText(re.sub("[A-Z]+", self.protocol.currentText(), self.label_12.text()))
        if self.protocol.currentText() == "HTTP" or self.protocol.currentText() == "HTTPS":
            self.special_argument.setPlaceholderText("绑定域名")
        else:
            self.special_argument.setPlaceholderText("远程端口")

    def create_tunnel(self):
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
        if self.protocol.currentText() == "TCP" or self.protocol.currentText() == "UDP":
            self.json_data = {
                'name': self.tunnelName.text(),
                'protocol': 'tcp',
                'local_address': self.local_ip.text(),
                'remote_port': self.special_argument.text(),
                'custom_domain': None,
                'create_https': False,
                'create_cdn': False,
            }
            if self.protocol.currentText() == "UDP":
                self.json_data["protocol"] = "udp"
            for i in range(0, len(self.servers["data"])):
                if self.servers["data"][i]["name"] == self.choose_server.currentText():
                    self.json_data["server_id"] = self.servers["data"][i]["id"]
            self.response = requests.post('https://api.laecloud.com/api/modules/frp/hosts', headers=self.headers, json=self.json_data)
            self.response.encoding = self.response.apparent_encoding
            try:
                self.create_tunnel_json = json.loads(self.response.text)
            except json.decoder.JSONDecodeError:
                self.show_dialog = dialog.ShowInfoDialog(
                    f"对后端接口返回JSON数据解码时发生错误:\n\n{self.response.status_code}: {self.response.text}")
                self.show_dialog.show_dialog()
                return
            if self.response.status_code != 200:
                self.show_dialog = dialog.ShowInfoDialog(
                    f"向后端接口发送请求时发生错误:\n\n{self.response.status_code}: {self.create_tunnel_json}")
                self.show_dialog.show_dialog()
                return
            else:
                self.show_dialog = dialog.ShowInfoDialog("创建成功！")
                self.show_dialog.show_dialog()
                return
        else:
            self.json_data = {
                'name': self.tunnelName.text(),
                'protocol': 'http',
                'local_address': self.local_ip.text(),
                'remote_port': None,
                'custom_domain': self.special_argument.text(),
                'create_https': False,
                'create_cdn': False,
            }
            if self.protocol.currentText() == "HTTPS":
                self.json_data["protocol"] = "https"
            for i in range(0, len(self.servers["data"])):
                if self.servers["data"][i]["name"] == self.choose_server.currentText():
                    self.json_data["server_id"] = self.servers["data"][i]["id"]
            self.response = requests.post('https://api.laecloud.com/api/modules/frp/hosts', headers=self.headers,
                                          json=self.json_data)
            self.response.encoding = self.response.apparent_encoding
            try:
                self.create_tunnel_json = json.loads(self.response.text)
            except json.decoder.JSONDecodeError:
                self.show_dialog = dialog.ShowInfoDialog(
                    f"对后端接口返回JSON数据解码时发生错误:\n\n{self.response.status_code}: {self.response.text}")
                self.show_dialog.show_dialog()
                return
            if self.response.status_code != 200:
                self.show_dialog = dialog.ShowInfoDialog(
                    f"向后端接口发送请求时发生错误:\n\n{self.response.status_code}: {self.create_tunnel_json}")
                self.show_dialog.show_dialog()
                return
            else:
                self.show_dialog = dialog.ShowInfoDialog("创建成功！")
                self.show_dialog.show_dialog()
                return
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(620, 440)
        MainWindow.setWindowTitle(u"Mirror Edge Frp \u5ba2\u6237\u7aef - V1.6 Released")
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
        self.token.setPlaceholderText(
            u"\u7b2c\u4e00\u6b21\u4f7f\u7528\u8bf7\u5230api.laecloud.com, \u70b9\u51fb\"\u83b7\u53d6\u65b0\u7684Token\"\u6309\u94ae, \u5c06Token\u590d\u5236\u5230\u8fd9\u91cc, \u7136\u540e\u70b9\u51fb\"\u8bbe\u7f6eToken\"\u6309\u94ae")
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
        self.openWebsite.setText(u"\u6253\u5f00api.laecloud.com")
        self.tabWidget.addTab(self.Token_Settings, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Token_Settings), u"Token\u8bbe\u7f6e")
        self.personal_info = QWidget()
        self.personal_info.setObjectName(u"personal_info")
        self.info_table = QTableWidget(self.personal_info)
        if (self.info_table.columnCount() < 2):
            self.info_table.setColumnCount(2)
        if (self.info_table.rowCount() < 5):
            self.info_table.setRowCount(5)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setText(u"\u540d\u79f0");
        __qtablewidgetitem.setTextAlignment(Qt.AlignCenter);
        self.info_table.setItem(0, 0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        __qtablewidgetitem1.setText(u"\u503c");
        __qtablewidgetitem1.setTextAlignment(Qt.AlignCenter);
        self.info_table.setItem(0, 1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        __qtablewidgetitem2.setText(u"\u7528\u6237\u540d");
        __qtablewidgetitem2.setTextAlignment(Qt.AlignCenter);
        self.info_table.setItem(1, 0, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        __qtablewidgetitem3.setTextAlignment(Qt.AlignCenter);
        self.info_table.setItem(1, 1, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        __qtablewidgetitem4.setText(u"\u7528\u6237ID");
        __qtablewidgetitem4.setTextAlignment(Qt.AlignCenter);
        self.info_table.setItem(2, 0, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        __qtablewidgetitem5.setTextAlignment(Qt.AlignCenter);
        self.info_table.setItem(2, 1, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        __qtablewidgetitem6.setText(u"\u4f59\u989d");
        __qtablewidgetitem6.setTextAlignment(Qt.AlignCenter);
        self.info_table.setItem(3, 0, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        __qtablewidgetitem7.setTextAlignment(Qt.AlignCenter);
        self.info_table.setItem(3, 1, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        __qtablewidgetitem8.setText(u"\u90ae\u7bb1");
        __qtablewidgetitem8.setTextAlignment(Qt.AlignCenter);
        self.info_table.setItem(4, 0, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        __qtablewidgetitem9.setTextAlignment(Qt.AlignCenter);
        self.info_table.setItem(4, 1, __qtablewidgetitem9)
        self.info_table.setObjectName(u"info_table")
        self.info_table.setGeometry(QRect(10, 10, 571, 371))
        self.info_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.info_table.setRowCount(5)
        self.info_table.setColumnCount(2)
        self.info_table.horizontalHeader().setVisible(False)
        self.info_table.horizontalHeader().setDefaultSectionSize(290)
        self.info_table.verticalHeader().setVisible(False)
        self.info_table.verticalHeader().setDefaultSectionSize(40)
        self.tabWidget.addTab(self.personal_info, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.personal_info), u"\u4e2a\u4eba\u4fe1\u606f")
        self.tunnelStart = QWidget()
        self.tunnelStart.setObjectName(u"tunnelStart")
        self.chooseTunnel = QComboBox(self.tunnelStart)
        self.chooseTunnel.setObjectName(u"chooseTunnel")
        self.chooseTunnel.setGeometry(QRect(100, 20, 291, 22))
        self.chooseTunnel.setCurrentText(u"")
        self.chooseTunnel.setPlaceholderText(u"--\u8bf7\u9009\u62e9--")
        self.startTunnel = QPushButton(self.tunnelStart)
        self.startTunnel.setObjectName(u"startTunnel")
        self.startTunnel.setGeometry(QRect(10, 90, 91, 31))
        self.startTunnel.setText(u"\u542f\u52a8\u96a7\u9053")
        self.stopTunnel = QPushButton(self.tunnelStart)
        self.stopTunnel.setObjectName(u"stopTunnel")
        self.stopTunnel.setGeometry(QRect(110, 90, 111, 31))
        self.stopTunnel.setText(u"\u505c\u6b62\u6240\u6709\u96a7\u9053")
        self.label_2 = QLabel(self.tunnelStart)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 20, 81, 21))
        self.label_2.setText(u"\u9009\u62e9\u96a7\u9053")
        self.outputLog = QTextEdit(self.tunnelStart)
        self.outputLog.setObjectName(u"outputLog")
        self.outputLog.setGeometry(QRect(10, 170, 571, 211))
        self.outputLog.setFocusPolicy(Qt.NoFocus)
        self.outputLog.setReadOnly(True)
        self.label_3 = QLabel(self.tunnelStart)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 140, 41, 21))
        self.label_3.setText(u"\u65e5\u5fd7")
        self.label_8 = QLabel(self.tunnelStart)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(10, 60, 61, 21))
        self.label_8.setText(u"\u64cd\u4f5c\u533a")
        self.refreshTunnel = QPushButton(self.tunnelStart)
        self.refreshTunnel.setObjectName(u"refreshTunnel")
        self.refreshTunnel.setGeometry(QRect(490, 90, 91, 31))
        self.refreshTunnel.setText(u"\u5237\u65b0\u96a7\u9053")
        self.clearCache = QPushButton(self.tunnelStart)
        self.clearCache.setObjectName(u"clearCache")
        self.clearCache.setGeometry(QRect(370, 90, 111, 31))
        self.clearCache.setText(u"\u6e05\u9664\u914d\u7f6e\u6587\u4ef6\u7f13\u5b58")
        self.tabWidget.addTab(self.tunnelStart, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tunnelStart), u"\u542f\u52a8\u96a7\u9053")
        self.createTunnel = QWidget()
        self.createTunnel.setObjectName(u"createTunnel")
        self.label_9 = QLabel(self.createTunnel)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setGeometry(QRect(20, 80, 71, 31))
        self.label_9.setText(u"\u96a7\u9053\u540d\u79f0")
        self.tunnelName = QLineEdit(self.createTunnel)
        self.tunnelName.setObjectName(u"tunnelName")
        self.tunnelName.setGeometry(QRect(20, 110, 201, 21))
        self.label_10 = QLabel(self.createTunnel)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setGeometry(QRect(20, 150, 91, 31))
        self.label_10.setText(u"\u672c\u5730\u5730\u5740\u548c\u7aef\u53e3")
        self.local_ip = QLineEdit(self.createTunnel)
        self.local_ip.setObjectName(u"local_ip")
        self.local_ip.setGeometry(QRect(20, 180, 201, 21))
        self.local_ip.setText(u"127.0.0.1:80")
        self.label_11 = QLabel(self.createTunnel)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setGeometry(QRect(20, 220, 51, 31))
        self.label_11.setText(u"\u534f\u8bae")
        self.protocol = QComboBox(self.createTunnel)
        self.protocol.addItem(u"HTTP")
        self.protocol.addItem(u"HTTPS")
        self.protocol.addItem(u"TCP")
        self.protocol.addItem(u"UDP")
        self.protocol.setObjectName(u"protocol")
        self.protocol.setGeometry(QRect(20, 250, 121, 22))
        self.open_status_page = QPushButton(self.createTunnel)
        self.open_status_page.setObjectName(u"open_status_page")
        self.open_status_page.setGeometry(QRect(20, 30, 201, 31))
        self.open_status_page.setCursor(QCursor(Qt.PointingHandCursor))
        self.open_status_page.setText(u"\u6253\u5f00\u670d\u52a1\u5668\u72b6\u6001\u9875\u9762")
        self.label_12 = QLabel(self.createTunnel)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setGeometry(QRect(280, 80, 171, 31))
        self.label_12.setText(u"\u9009\u62e9\u652f\u6301HTTP\u534f\u8bae\u7684\u8282\u70b9")
        self.protocol_ok = QPushButton(self.createTunnel)
        self.protocol_ok.setObjectName(u"protocol_ok")
        self.protocol_ok.setGeometry(QRect(150, 250, 71, 23))
        self.protocol_ok.setText(u"\u786e\u5b9a")
        self.choose_server = QComboBox(self.createTunnel)
        self.choose_server.setObjectName(u"choose_server")
        self.choose_server.setGeometry(QRect(280, 110, 221, 22))
        self.label_13 = QLabel(self.createTunnel)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setGeometry(QRect(280, 150, 61, 31))
        self.label_13.setText(u"\u7279\u6b8a\u53c2\u6570")
        self.special_argument = QLineEdit(self.createTunnel)
        self.special_argument.setObjectName(u"special_argument")
        self.special_argument.setGeometry(QRect(280, 180, 221, 21))
        self.special_argument.setPlaceholderText(u"\u7ed1\u5b9a\u57df\u540d")
        self.create_tunnel_ok = QPushButton(self.createTunnel)
        self.create_tunnel_ok.setObjectName(u"create_tunnel_ok")
        self.create_tunnel_ok.setGeometry(QRect(280, 240, 221, 31))
        self.create_tunnel_ok.setText(u"\u786e\u5b9a")
        self.tabWidget.addTab(self.createTunnel, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.createTunnel), u"\u65b0\u5efa\u96a7\u9053")
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

        # StyleSheet部分
        self.openWebsite.setStyleSheet("""
        border: none;
        color: #0d6efd;
        text-decoration: underline;
        """)
        self.open_status_page.setStyleSheet("""
        border: none;
        color: #0d6efd;
        text-decoration: underline;
        """)

        QMetaObject.connectSlotsByName(MainWindow)

        # 自定义代码部分 / 逻辑代码部分
        self.listOfTunnel()

        # 按钮点击事件绑定
        self.setToken.clicked.connect(self.set_token)
        self.startTunnel.clicked.connect(self.start_tunnel)
        self.stopTunnel.clicked.connect(self.stop_tunnel)
        self.openWebsite.clicked.connect(self.openTokenWebsite)
        self.refreshTunnel.clicked.connect(self.listOfTunnel)
        self.open_status_page.clicked.connect(self.openStatusWebsite)
        self.protocol_ok.clicked.connect(self.updateCreateTunnelPage)
        self.create_tunnel_ok.clicked.connect(self.create_tunnel)
        self.clearCache.clicked.connect(self.clear_cache)
        # 设置禁用停止所有隧道按钮
        self.stopTunnel.setDisabled(True)
        # 设置新建隧道 隧道名称
        self.tunnelName.setText(self.randomTunnelName())
        # 获取用户信息并填入表中
        self.info = self.getPersonalInfo()
        if self.info != False:
            __qtablewidgetitem = QTableWidgetItem()
            __qtablewidgetitem.setText(self.info[0])
            __qtablewidgetitem.setTextAlignment(Qt.AlignCenter)
            self.info_table.setItem(1, 1, __qtablewidgetitem)
            __qtablewidgetitem2 = QTableWidgetItem()
            __qtablewidgetitem2.setText(self.info[1])
            __qtablewidgetitem2.setTextAlignment(Qt.AlignCenter)
            self.info_table.setItem(2, 1, __qtablewidgetitem2)
            __qtablewidgetitem3 = QTableWidgetItem()
            __qtablewidgetitem3.setText(self.info[2])
            __qtablewidgetitem3.setTextAlignment(Qt.AlignCenter)
            self.info_table.setItem(3, 1, __qtablewidgetitem3)
            __qtablewidgetitem4 = QTableWidgetItem()
            __qtablewidgetitem4.setText(self.info[3])
            __qtablewidgetitem4.setTextAlignment(Qt.AlignCenter)
            self.info_table.setItem(4, 1, __qtablewidgetitem4)
        # 获取服务器列表 供新建隧道板块使用
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
        self.response = requests.get('https://api.laecloud.com/api/modules/frp/servers', headers=self.headers)
        self.response.encoding = self.response.apparent_encoding
        try:
            self.servers = json.loads(self.response.text)
        except json.decoder.JSONDecodeError:
            self.show_dialog = dialog.ShowInfoDialog(
                f"对后端接口返回JSON数据解码时发生错误:\n\n{self.response.status_code}: {self.response.text}")
            self.show_dialog.show_dialog()
            return
        if self.response.status_code != 200:
            self.show_dialog = dialog.ShowInfoDialog(
                f"向后端接口发送请求时发生错误:\n\n{self.response.status_code}: {self.servers['data']}")
            self.show_dialog.show_dialog()
            return
        # 如果有token.txt文件直接切换到隧道板块
        if os.path.exists("token.txt"):
            self.tabWidget.setCurrentIndex(2)
