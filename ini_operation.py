import configparser
import os.path

import dialog

cp = configparser.ConfigParser()


def writeToIni():
    with open("config.ini", 'w', encoding="UTF-8") as f:
        cp.write(f)


def init():
    if not os.path.exists("config.ini"):
        show_dialog = dialog.ShowInfoDialog("您尚未设置Token!")
        show_dialog.show_dialog()
    else:
        cp.read("config.ini")


def setToken(token):
    sections = cp.sections()
    if "auth" not in sections:
        cp.add_section("auth")
    cp.set("auth", "token", token)
    writeToIni()


def readToken():
    return cp.get("auth", "token")
