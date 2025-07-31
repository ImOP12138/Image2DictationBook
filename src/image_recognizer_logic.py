# src/image_recognizer_logic.py
import sys
import os
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from MainWindow import Ui_MainWindow
from image_analyzer import analyze_image, save_result_to_file
from generateWord import generate_dictation_books  # 导入新模块


class AnalysisThread(QThread):
    """分析线程，避免界面卡顿"""
    analysis_finished = pyqtSignal(str)  # 分析完成信号
    analysis_error = pyqtSignal(str)  # 分析错误信号

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path

    def run(self):
        try:
            result = analyze_image(self.image_path)
            self.analysis_finished.emit(result)
        except Exception as e:
            self.analysis_error.emit(str(e))


class GenerateWordThread(QThread):
    """生成Word文档线程"""
    generate_finished = pyqtSignal(bool, str)  # 生成完成信号 (成功/失败, 消息)

    def __init__(self, input_file='word.txt'):
        super().__init__()
        self.input_file = input_file

    def run(self):
        try:
            success, message = generate_dictation_books(self.input_file)
            self.generate_finished.emit(success, message)
        except Exception as e:
            self.generate_finished.emit(False, f"生成失败：{str(e)}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 初始化界面
        self.setup_connections()
        self.setup_ui()

        # 线程
        self.analysis_thread = None
        self.generate_thread = None
        self.last_result = ""  # 保存最后的分析结果

    def setup_connections(self):
        """连接信号和槽"""
        # 浏览按钮
        self.ui.buttonBrowse.clicked.connect(self.browse_image)

        # 分析按钮
        self.ui.buttonAnalyze.clicked.connect(self.analyze_image)

        # 生成听写本按钮
        self.ui.buttonGenerateWord.clicked.connect(self.generate_word_docs)

        # 路径输入框回车事件
        self.ui.lineEditImagePath.returnPressed.connect(self.analyze_image)

    def setup_ui(self):
        """设置界面初始状态"""
        self.setWindowTitle("图像文字识别工具")
        self.statusBar().showMessage("就绪")

        # 禁用分析按钮
        self.ui.buttonAnalyze.setEnabled(False)

    def browse_image(self):
        """浏览图片文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片文件", "",
            "图片文件 (*.jpg *.jpeg *.png);;所有文件 (*)"
        )

        if file_path:
            self.ui.lineEditImagePath.setText(file_path)
            self.ui.buttonAnalyze.setEnabled(True)
            self.statusBar().showMessage(f"已选择图片: {os.path.basename(file_path)}")

    def analyze_image(self):
        """分析图片"""
        image_path = self.ui.lineEditImagePath.text().strip()

        if not image_path:
            QMessageBox.warning(self, "警告", "请输入图片路径")
            return

        if not os.path.exists(image_path):
            QMessageBox.warning(self, "警告", "图片文件不存在")
            return

        # 禁用按钮，显示正在分析
        self.ui.buttonAnalyze.setEnabled(False)
        self.ui.buttonBrowse.setEnabled(False)
        self.ui.buttonGenerateWord.setEnabled(False)  # 生成按钮也禁用
        self.statusBar().showMessage("正在分析图片，请稍候...")

        # 启动分析线程
        self.analysis_thread = AnalysisThread(image_path)
        self.analysis_thread.analysis_finished.connect(self.on_analysis_finished)
        self.analysis_thread.analysis_error.connect(self.on_analysis_error)
        self.analysis_thread.finished.connect(self.on_thread_finished)
        self.analysis_thread.start()

    def on_analysis_finished(self, result):
        """分析完成"""
        self.ui.textEditResult.setPlainText(result)
        self.last_result = result  # 保存结果

        # 自动保存结果
        self.auto_save_result(result)

        self.statusBar().showMessage("分析完成，结果已自动保存")

    def auto_save_result(self, result):
        """自动保存结果到文件"""
        if result:
            try:
                if save_result_to_file(result, "word.txt"):
                    self.statusBar().showMessage("分析完成，结果已自动保存到 word.txt")
                    # 启用生成听写本按钮
                    self.ui.buttonGenerateWord.setEnabled(True)
                else:
                    self.statusBar().showMessage("分析完成，但保存文件失败")
            except Exception as e:
                self.statusBar().showMessage(f"分析完成，但保存失败：{str(e)}")
        else:
            self.statusBar().showMessage("分析完成，但没有识别到结果")

    def on_analysis_error(self, error):
        """分析出错"""
        QMessageBox.critical(self, "错误", f"分析失败：{error}")
        self.statusBar().showMessage("分析失败")

    def on_thread_finished(self):
        """线程结束"""
        self.ui.buttonAnalyze.setEnabled(True)
        self.ui.buttonBrowse.setEnabled(True)

    def generate_word_docs(self):
        """生成听写本Word文档"""
        # 检查word.txt文件是否存在
        if not os.path.exists("word.txt"):
            QMessageBox.warning(self, "警告", "未找到 word.txt 文件，请先进行图片分析")
            return

        # 禁用按钮，显示正在生成
        self.ui.buttonGenerateWord.setEnabled(False)
        self.ui.buttonAnalyze.setEnabled(False)
        self.ui.buttonBrowse.setEnabled(False)
        self.statusBar().showMessage("正在生成听写本，请稍候...")

        # 启动生成线程
        self.generate_thread = GenerateWordThread("word.txt")
        self.generate_thread.generate_finished.connect(self.on_generate_finished)
        self.generate_thread.finished.connect(self.on_generate_thread_finished)
        self.generate_thread.start()

    def on_generate_finished(self, success, message):
        """生成完成"""
        if success:
            QMessageBox.information(self, "成功", message)
            self.statusBar().showMessage("听写本生成完成")
        else:
            QMessageBox.critical(self, "错误", message)
            self.statusBar().showMessage("听写本生成失败")

    def on_generate_thread_finished(self):
        """生成线程结束"""
        self.ui.buttonGenerateWord.setEnabled(True)
        self.ui.buttonAnalyze.setEnabled(True)
        self.ui.buttonBrowse.setEnabled(True)