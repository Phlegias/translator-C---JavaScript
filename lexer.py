import re

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, '{self.value}')"


class Lexer:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.current_position = 0
        self.keywords = {'public', 'private', 'static', 'return', 'if', 'else', 'do', 'while', 'for', 'using', 'namespace', 'true', 'false'}
        self.types = {'class', 'int', 'float', 'double', 'string', 'char', 'bool', 'void'}

        # Определение токенов и их регулярных выражений
        self.token_specification = [
            ('OUTPUT', r'Console.WriteLine|Console.Write'),
            ('NUMBER', r'\d+(\.\d+)?(f)?'),            # Числа (целые и с плавающей точкой)
            ('STRING', r'"(\\.|[^"\\])*"'),        # Строки с поддержкой escape-последовательностей
            ('CHAR', r"'(\\.|[^'\\])'"),           # Символы с поддержкой escape-последовательностей
            ('ID', r'[A-Za-z_][A-Za-z0-9_]*'),     # Идентификаторы и ключевые слова
            ('OP', r'(\+=|-=|\*=|/=|%=|==|!=|<=|>=|&&|\|\||[+\-*/%<>=!&|\.])'),    # Операторы, включая точку
            ('DELIM', r'[;,\(\)\{\}]'),            # Разделители
            ('SKIP', r'[ \t]+'),                   # Пробелы и табуляции
            ('COMMENT', r'//.*|/\*[\s\S]*?\*/'),   # Комментарии
            ('NEWLINE', r'\n'),                    # Новая строка
            ('MISMATCH', r'.'),                    # Любой другой символ
        ]

    def tokenize(self):
        while self.current_position < len(self.code):
            match = None
            for token_type, pattern in self.token_specification:
                regex = re.compile(pattern)
                match = regex.match(self.code, self.current_position)
                if match:
                    value = match.group(0)
                    if token_type == 'ID':
                        if value in self.keywords:
                            self.tokens.append(Token('KEYWORD', value))
                        elif value in self.types:
                            self.tokens.append(Token('TYPE', value))
                        else:
                            self.tokens.append(Token('ID', value))
                    elif token_type == 'NEWLINE':
                        pass  # Игнорируем новые строки
                    elif token_type != 'SKIP' and token_type != 'COMMENT':  # Пропускаем пробелы и комментарии
                        self.tokens.append(Token(token_type, value))
                    break
            if match:
                self.current_position = match.end(0)  # Переход к следующему символу
            else:
                raise ValueError(f"Неожиданный символ: {self.code[self.current_position]}")
        return self.tokens
