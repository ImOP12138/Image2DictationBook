# src/generateWord.py
import requests
from docx import Document
from docx.enum.text import WD_UNDERLINE, WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Cm
import os
import re

# API配置
API_URL = "https://v2.xxapi.cn/api/englishwords"
HEADERS = {
    'User-Agent': 'xiaoxiaoapi/1.0.0 (https://xxapi.cn)'
}


def read_words_from_file(filename='word.txt'):
    """读取txt中的单词"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f.readlines() if line.strip()]
        return words
    except FileNotFoundError:
        print(f"❌ 文件 {filename} 不存在")
        return []
    except Exception as e:
        print(f"❌ 读取文件失败：{e}")
        return []


def get_word_details(word):
    """调用小小API获取单词详细信息"""
    try:
        response = requests.get(f"{API_URL}?word={word}", headers=HEADERS)
        data = response.json()

        if data["code"] == 200:
            translations = data["data"]["translations"]
            result = []

            for trans in translations:
                pos = trans["pos"]
                tran_cn = trans["tran_cn"].strip()
                result.append(f"{pos}. {tran_cn}")

            # 返回格式化后的字符串
            return "\n".join(result)

        else:
            return "未找到释义"
    except Exception as e:
        return f"请求失败：{e}"


def create_word_doc(words_with_details, output_filename='单词听写本（带词意）.docx'):
    """创建带词意的听写本word"""
    try:
        doc = Document()

        # 设置双栏布局
        section = doc.sections[0]
        sect_pr = section._sectPr

        cols = OxmlElement('w:cols')
        cols.set(qn('w:num'), '2')  # 设置两栏
        cols.set(qn('w:space'), '720')  # 栏间距（单位 twip）

        # 清除旧的分栏设置
        for child in list(sect_pr):
            if child.tag == qn('w:cols'):
                sect_pr.remove(child)

        sect_pr.append(cols)

        # 添加表格
        table = doc.add_table(rows=0, cols=2)

        # 设置第一列宽度
        for row in table.rows:
            row.cells[0].width = 12800  # 单位：缇（twip）

        # 填充数据
        for word, detail in words_with_details:
            row = table.add_row()
            cells = row.cells  # 获取当前行的单元格
            cells[0].text = word
            cells[1].text = ''

            paragraph = cells[1].paragraphs[0]
            paragraph.paragraph_format.space_after = Pt(0)  # 行距紧凑
            lines = detail.split('\n')
            for i, line in enumerate(lines):
                run = paragraph.add_run(line.strip())
                run.bold = False  # 强制不加粗
                run.font.name = '宋体'  # 设置中文字体
                run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')  # 兼容中文字体
                run.font.size = Pt(9)  # 设置字号

                if i < len(lines) - 1:
                    run.add_break()  # 换行

            # 最后一行也统一设置
            run.underline = WD_UNDERLINE.SINGLE

            # 设置新增行的第一列宽度
            cells[0].width = 12800

        doc.save(output_filename)
        print(f"✅ 已保存为 {os.path.abspath(output_filename)}")
        return True

    except Exception as e:
        print(f"❌ 生成带词意文档失败：{e}")
        return False


def create_blank_word_doc(words_with_details, output_filename='单词听写本（无词意）.docx'):
    """创建不带词意的听写本word（供默写）"""
    try:
        doc = Document()

        # 设置双栏布局
        section = doc.sections[0]
        sect_pr = section._sectPr

        cols = OxmlElement('w:cols')
        cols.set(qn('w:num'), '2')  # 设置两栏
        cols.set(qn('w:space'), '720')  # 栏间距（单位 twip）

        # 清除旧的分栏设置
        for child in list(sect_pr):
            if child.tag == qn('w:cols'):
                sect_pr.remove(child)

        sect_pr.append(cols)

        # 添加表格（不带初始行）
        table = doc.add_table(rows=0, cols=2)

        # 填充数据
        for word, detail in words_with_details:
            row = table.add_row()
            cells = row.cells
            cells[0].text = word
            cells[1].text = ''

            paragraph = cells[1].paragraphs[0]
            paragraph.paragraph_format.space_after = Pt(0)

            # 提取词性部分（n., v., adj. 等）
            lines = detail.split('\n')
            for i, line in enumerate(lines):
                match = re.match(r'^([a-zA-Z]+\.).*', line.strip())
                if match:
                    pos = match.group(1)
                    run = paragraph.add_run(pos)
                    run.font.name = '宋体'
                    run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
                    run.font.size = Pt(9)
                    if i < len(lines) - 1:
                        run.add_break()  # 每个词性占一行

            # 设置第一列宽度
            cells[0].width = 12800

        doc.save(output_filename)
        print(f"✅ 已保存为 {os.path.abspath(output_filename)}")
        return True

    except Exception as e:
        print(f"❌ 生成无词意文档失败：{e}")
        return False


def generate_dictation_books(input_file='word.txt'):
    """生成听写本的主函数"""
    try:
        # 读取单词
        words = read_words_from_file(input_file)
        if not words:
            return False, "没有找到单词数据"

        # 获取每个单词的详细信息
        words_with_details = []
        for word in words:
            meaning = get_word_details(word)
            words_with_details.append((word, meaning))

        # 生成Word文档
        success1 = create_word_doc(words_with_details, '单词听写本（带词意）.docx')

        # 生成不带词意的 Word 文档（供默写）
        success2 = create_blank_word_doc(words_with_details, '单词听写本（无词意）.docx')

        if success1 and success2:
            return True, "听写本生成成功！已创建两个文件：单词听写本（带词意）.docx 和 单词听写本（无词意）.docx"
        else:
            return False, "部分文件生成失败"

    except Exception as e:
        return False, f"生成听写本失败：{str(e)}"