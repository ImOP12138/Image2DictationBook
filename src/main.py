# src/main.py
import sys
import os
from PyQt5.QtWidgets import QApplication
from image_recognizer_logic import MainWindow


def main():
    # 设置应用程序属性
    app = QApplication(sys.argv)
    app.setApplicationName("图像文字识别工具")
    app.setApplicationVersion("1.0")

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    # 运行应用程序
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()