# -*- coding: utf-8 -*-
from maya import mel
try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

class KeywordHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(KeywordHighlighter, self).__init__(parent)
        self.keywords = {
            # rgb(10, 255, 98)
            'green': [(QColor(10, 255, 98), [
                'and', 'as', 'assert', 'break', 'class', 'continue', 'def',
                'del', 'elif', 'else', 'except', 'finally', 'for',
                'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
                'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'false','true', 
                'try', 'while', 'with', 'yield','proc', 'string', 'int', 'float', 'list', 'dict', 'tuple', 'set', 'bool',
                'vector', 'matrix', 'source','print', 'range', 'len', 'abs', 'max', 'min', 'sum', 'round', 'ceil', 'floor', 'sqrt', 'pow', 'log', 'exp', 'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2', 'degrees', 'radians', 'pi', 'e', 'tau', 'inf', 'nan'
            ])],
            # rgb(59, 193, 255)
            'blue': [(QColor(59, 193, 255), ['None', 'True', 'False'])]
        }

        self.defined_variables = set()
        self.defined_functions = set()
        self.defined_modules = set()

    def highlightBlock(self, text):
        # Highlight keywords
        for color, keyword_groups in self.keywords.items():
            for color, keywords in keyword_groups:
                keyword_format = QTextCharFormat()
                keyword_format.setForeground(color)
                #keyword_format.setFontWeight(QFont.Bold)
                for keyword in keywords:
                    expression = QRegularExpression(r'\b' + keyword + r'\b')
                    match_iterator = expression.globalMatch(text)
                    while match_iterator.hasNext():
                        match = match_iterator.next()
                        self.setFormat(match.capturedStart(), match.capturedLength(), keyword_format)

        # Highlight variable definitions (including for loop variables)
        variable_def_format = QTextCharFormat()
        variable_def_format.setForeground(QColor(214, 140, 208)) # rgb(214, 140, 208)
        variable_def_expressions = [
            QRegularExpression(r'\b(\w+)\s*(?==)'),  # Variable assignment
            QRegularExpression(r'\bfor\s+(\w+)\s+in\b')  # For loop variable
        ]
        for expression in variable_def_expressions:
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(1), match.capturedLength(1), variable_def_format)
                self.defined_variables.add(match.captured(1))
        
        # 获取 from 和 import 的模块名，添加到 defined_modules 中
        module_def_format = QTextCharFormat()
        module_def_format.setForeground(QColor(80, 239, 209)) # rgb(80, 239, 209)
        module_def_expressions = [
            QRegularExpression(r'\bfrom\s+(\w+)\s+import\b'),  # from xxx import xxx
            QRegularExpression(r'\bimport\s+(\w+)\b')  # import xxx
        ]
        for expression in module_def_expressions:
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.defined_modules.add(match.captured(1))

        # Highlight module usages
        module_usage_format = QTextCharFormat()
        module_usage_format.setForeground(QColor(80, 239, 209)) # rgb(80, 239, 209)
        for module in self.defined_modules:
            expression = QRegularExpression(r'\b' + module + r'\b')
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), module_usage_format)

        # Highlight class definitions
        class_def_format = QTextCharFormat()
        class_def_format.setForeground(QColor(80, 239, 209)) # rgb(80, 239, 209)
        class_def_expression = QRegularExpression(r'\bclass\s+(\w+)\b')
        class_def_match_iterator = class_def_expression.globalMatch(text)
        while class_def_match_iterator.hasNext():
            match = class_def_match_iterator.next()
            self.setFormat(match.capturedStart(1), match.capturedLength(1), class_def_format)

        # Highlight function definitions
        function_def_format = QTextCharFormat()
        function_def_format.setForeground(QColor(86, 244, 255)) # rgb(86, 244, 255)
        function_def_expression = QRegularExpression(r'\bdef\s+(\w+)\s*\(')
        function_def_match_iterator = function_def_expression.globalMatch(text)
        while function_def_match_iterator.hasNext():
            match = function_def_match_iterator.next()
            self.setFormat(match.capturedStart(1), match.capturedLength(1), function_def_format)
            self.defined_functions.add(match.captured(1))

        # Highlight function calls
        function_call_format = QTextCharFormat()
        function_call_format.setForeground(QColor(86, 244, 255)) # rgb(86, 244, 255)
        function_call_expression = QRegularExpression(r'\b(\w+)\s*\(')
        function_call_match_iterator = function_call_expression.globalMatch(text)
        while function_call_match_iterator.hasNext():
            match = function_call_match_iterator.next()
            if match.captured(1) in self.defined_functions:
                self.setFormat(match.capturedStart(1), match.capturedLength(1), function_call_format)

        # 高亮 MEL 内置函数
        mel_builtin_function_format = QTextCharFormat()
        mel_builtin_function_format.setForeground(QColor(86, 244, 255)) # rgb(86, 244, 255)
        # 获取所有单词
        mel_builtin_function_expression = QRegularExpression(r'\b(\w+)\b')
        mel_builtin_function_match_iterator = mel_builtin_function_expression.globalMatch(text)
        while mel_builtin_function_match_iterator.hasNext():
            match = mel_builtin_function_match_iterator.next()
            evalWord = 'whatIs "' + match.captured(1) + '"'
            if 'Command' in mel.eval(evalWord) or 'Mel procedure found' in mel.eval(evalWord) or 'Script found' in mel.eval(evalWord): # whatIs "xxx"  返回 Command 则说明是内置函数
                # 排除掉 self.keywords['green'] 中的关键字
                if match.captured(1) not in self.keywords['green'][0][1]:
                    self.setFormat(match.capturedStart(1), match.capturedLength(1), mel_builtin_function_format)

        # Highlight MEL function definitions
        mel_function_def_format = QTextCharFormat()
        mel_function_def_format.setForeground(QColor(86, 244, 255)) # rgb(86, 244, 255)
        # 获取所有的函数 以 proc + 空格 开头，以 () 结尾 中的所有内容
        mel_function_def_expression = QRegularExpression(r'proc\s(.+)*\(')
        mel_function_def_match_iterator = mel_function_def_expression.globalMatch(text)
        while mel_function_def_match_iterator.hasNext():
            match = mel_function_def_match_iterator.next()
            # 如果 match.captured(1) 中有string float int string[] float[] int[] 加 空格 则说明有自定义函数类型的关键字需要排除掉这些关键字只高亮函数名
            if 'string ' in match.captured(1) or 'float ' in match.captured(1) or 'int ' in match.captured(1) or 'string[] ' in match.captured(1) or 'float[] ' in match.captured(1) or 'int[] ' in match.captured(1):
                # 获取函数名
                mel_function_name = match.captured(1).split(' ')[-1]
                mel_function_type = match.captured(1).split(' ')[0]
                # 从 len(mel_function_type) + 1 开始到 mel_function_name 结束
                self.defined_functions.add(mel_function_name)
                self.setFormat(match.capturedStart(1) + len(mel_function_type) + 1, len(mel_function_name), mel_function_def_format)
            else:
                # 获取函数名
                mel_function_name = match.captured(1)
                self.defined_functions.add(mel_function_name)
                self.setFormat(match.capturedStart(1), len(mel_function_name), mel_function_def_format)


        # Highlight variable usages
        variable_usage_format = QTextCharFormat()
        variable_usage_format.setForeground(QColor(214, 140, 208)) # rgb(214, 140, 208)
        variable_usage_expression = QRegularExpression(r'\b(\w+)\b')
        variable_usage_match_iterator = variable_usage_expression.globalMatch(text)
        while variable_usage_match_iterator.hasNext():
            match = variable_usage_match_iterator.next()
            if match.captured(1) in self.defined_variables:
                self.setFormat(match.capturedStart(1), match.capturedLength(1), variable_usage_format)

        # Highlight MEL variable usages
        mel_variable_usage_format = QTextCharFormat()
        mel_variable_usage_format.setForeground(QColor(214, 140, 208)) # rgb(214, 140, 208)
        # 获取所有的变量 以 $ 开头
        mel_variable_usage_expression = QRegularExpression(r'\$[a-zA-Z_]\w*')
        mel_variable_usage_match_iterator = mel_variable_usage_expression.globalMatch(text)
        while mel_variable_usage_match_iterator.hasNext():
            match = mel_variable_usage_match_iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), mel_variable_usage_format)

        # Highlight strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(255, 247, 10)) # rgb(255, 247, 10)
        string_expression = QRegularExpression(r'".*?"|\'[^\']*\'')
        string_match_iterator = string_expression.globalMatch(text)
        while string_match_iterator.hasNext():
            match = string_match_iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), string_format)

        # Highlight comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(255, 80, 51)) # rgb(255, 80, 51)
        comment_expression = QRegularExpression(r'#.*|//.*')
        comment_match_iterator = comment_expression.globalMatch(text)
        while comment_match_iterator.hasNext():
            match = comment_match_iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), comment_format)
