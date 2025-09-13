class Node:
    def __init__(self, type, children=None, value=None):
        self.type = type
        self.children = children if children is not None else []
        self.value = value

    def __repr__(self):
        return f"Node({self.type}, {self.value}, {self.children})"

    def print_tree(self, level=0):
        indent = "  " * level  # Создаем отступы для визуализации вложенности
        output = f"{indent}Node({self.type}, {self.value})\n"
        
        for child in self.children:
            output += child.print_tree(level + 1)  # Рекурсивно вызываем для дочерних узлов
        
        return output

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0

    def eat(self, token_type):
        token = self.tokens[self.current_token_index]
        if token.type == token_type:
            self.current_token_index += 1
        else:
            raise SyntaxError(f"Ожидался токен {token_type}, но найден {token.type}")

    def next_token(self):
        token = self.tokens[self.current_token_index]
        return token.type

    def next_token_value(self):
        token = self.tokens[self.current_token_index]
        return token.value

    def parse(self):
        return self.program()

    def program(self):
        nodes = []
        while self.current_token_index < len(self.tokens):
            if self.next_token_value() == 'using':
                nodes.append(self.lib_import())
            elif self.next_token_value() == '{':
                self.eat('DELIM')  # Открывающая скобка для блока
                nodes.append(self.statement_list())
                self.eat('DELIM')  # Закрывающая скобка для блока
            else:
                nodes.append(self.namespace_declaration())
        return Node("Program", nodes)


    def lib_import(self):
        self.eat('KEYWORD')  # using
        lib_name = self.tokens[self.current_token_index].value
        self.eat('ID')  # name
        while self.next_token() == 'OP':
            self.eat('OP')  # .
            lib_name += f".{self.tokens[self.current_token_index].value}"
            self.eat('ID')  # name
        self.eat('DELIM')  # ;
        return Node("LibraryImport", value=lib_name)

    def namespace_declaration(self):
        self.eat('KEYWORD')  # namespace
        namespace_name = self.tokens[self.current_token_index].value
        self.eat('ID')       # Имя
        self.eat('DELIM')    # {
        
        class_nodes = []
        while self.next_token() == 'KEYWORD':
            class_nodes.append(self.class_declaration())

        self.eat('DELIM')    # }
        return Node("Namespace", children=class_nodes, value=namespace_name)

    def class_declaration(self):
        modifiers = []
        while self.next_token() != 'TYPE':  # public static
            modifiers.append(self.tokens[self.current_token_index].value)
            self.eat('KEYWORD')
        self.eat('TYPE')  # class
        class_name = self.tokens[self.current_token_index].value
        self.eat('ID')  # Имя класса
        self.eat('DELIM')  # {
        
        method_nodes = []
        while self.next_token() == 'KEYWORD':
            method_nodes.append(self.method_declaration())

        self.eat('DELIM')  # }
        return Node("Class", children=method_nodes, value={"name": class_name, "modifiers": modifiers})

    def method_declaration(self):
        modifiers = []
        while self.next_token() != 'TYPE':  # public static
            modifiers.append(self.tokens[self.current_token_index].value)
            self.eat('KEYWORD')
        return_type = self.tokens[self.current_token_index].value  # Тип возвращаемого значения
        self.eat('TYPE')  # type
        method_name = self.tokens[self.current_token_index].value
        self.eat('ID')  # Имя метода
        self.eat('DELIM')  # (
        parameters = self.method_parameters()
        self.eat('DELIM')  # )
        self.eat('DELIM')  # {

        statement_list = self.statement_list()

        self.eat('DELIM')  # }
        return Node("Method", children=statement_list, value={"name": method_name, "modifiers": modifiers, "parameters": parameters, "return_type": return_type})

    def method_parameters(self):
        params = []
        if self.next_token() != 'DELIM':  # Если не закрывающая скобка
            params.append(self.tokens[self.current_token_index].value)
            self.eat('ID')
            while self.next_token() == 'DELIM' and self.next_token_value() == ',':
                self.eat('DELIM')  # запятая
                params.append(self.tokens[self.current_token_index].value)
                self.eat('ID')
        return params

    def statement_list(self):
        statements = []
        print(f"Starting statement list parsing at index {self.current_token_index}")  # Отладка
        while self.tokens[self.current_token_index].type != 'DELIM' or self.tokens[self.current_token_index].value != '}':
            statements.append(self.statement())
        print(f"Finished statement list at index {self.current_token_index}")  # Отладка
        return statements

    def statement(self):
        print(f"Processing statement at index {self.current_token_index}, token: {self.tokens[self.current_token_index]}")  # Отладка
        if self.tokens[self.current_token_index + 1].type == 'OP' and self.tokens[self.current_token_index + 1].value == '.':
            return self.method_call()  # Вызов метода
        elif self.next_token_value() == 'return':
            return self.return_statement()
        elif self.next_token_value() in {'if', 'while', 'for', 'do'}:
            return self.control_statement()
        elif self.next_token_value() in {'+=', '-=', '*=', '/=', '%='}:
            return self.compound_assignment()
        elif self.next_token_value() in {'++', '--', '!'}:
            return self.unary_operation()
        else:
            return self.variable_declaration()


    def return_statement(self):
        self.eat('KEYWORD')  # return
        expr = self.expression()
        self.eat('DELIM')  # ;
        return Node("Return", children=[expr])

    def control_statement(self):
        if self.next_token_value() == 'if':
            return self.if_statement()
        elif self.next_token_value() == 'else':
            return self.else_statement()
        elif self.next_token_value() == 'while':
            return self.while_statement()
        elif self.next_token_value() == 'for':
            return self.for_statement()
        elif self.next_token_value() == 'do':
            return self.do_while_statement()

    def if_statement(self):
        self.eat('KEYWORD')  # if
        self.eat('DELIM')  # (
        condition = self.expression()
        self.eat('DELIM')  # )
        self.eat('DELIM')  # {
        body = self.statement_list()
        self.eat('DELIM')  # }
        
        if self.next_token_value() == 'else':  # Проверяем наличие else
            else_clause = self.else_statement()
            return Node("If", children=[condition] + body + [else_clause])
        
        return Node("If", children=[condition] + body)

    def else_statement(self):
        self.eat('KEYWORD')  # else
        if self.next_token_value() == 'if':  # Проверка elif/else if
            return self.if_statement()
        self.eat('DELIM')  # {
        body = self.statement_list()
        self.eat('DELIM')  # }
        return Node("Else", children=body)

    def do_while_statement(self):
        self.eat('KEYWORD')  # do
        self.eat('DELIM')    # {
        body = self.statement_list()
        self.eat('DELIM')    # }
        self.eat('KEYWORD')  # while
        self.eat('DELIM')    # (
        condition = self.expression()
        self.eat('DELIM')    # )
        self.eat('DELIM')    # ;
        return Node("DoWhile", children=body + [condition])

    def while_statement(self):
        self.eat('KEYWORD')  # while
        self.eat('DELIM')  # (
        condition = self.expression()
        self.eat('DELIM')  # )
        self.eat('DELIM')  # {
        body = self.statement_list()
        self.eat('DELIM')  # }
        return Node("While", children=[condition] + body)

    def method_call(self):
        object_chain = []  # Список объектов в цепочке вызовов
        object_name = self.tokens[self.current_token_index].value
        object_chain.append(object_name)  # Сохраняем первый объект
        self.eat('ID')  # Имя объекта (например, Console)
        
        # Собираем всю цепочку объектов до метода
        while self.next_token() == 'OP' and self.tokens[self.current_token_index].value == '.':
            self.eat('OP')  # Точка (.)
            object_name = self.tokens[self.current_token_index].value
            object_chain.append(object_name)
            self.eat('ID')  # Следующий объект или метод

        method_name = object_chain.pop()  # Последний элемент - это метод
        self.eat('DELIM')  # Открывающая скобка (
        arguments = self.arguments()
        self.eat('DELIM')  # Закрывающая скобка )
        self.eat('DELIM')  # Точка с запятой (;)

        return Node("MethodCall", value={"object_chain": object_chain, "method": method_name}, children=arguments)


    def arguments(self):
        args = []
        if self.next_token() != 'DELIM':  # Если не закрывающая скобка
            args.append(self.expression())
            while self.next_token() == 'DELIM' and self.next_token_value() == ',':
                self.eat('DELIM')  # запятая
                args.append(self.expression())
        return args

    def variable_declaration(self):
        # Проверяем, может ли быть тип переменной
        if self.next_token() == 'TYPE':
            var_type = self.tokens[self.current_token_index].value
            self.eat('TYPE')  # Тип переменной
        else:
            var_type = 'auto'  # Присваиваем тип 'auto', если тип не указан явно

        var_name = self.tokens[self.current_token_index].value
        self.eat('ID')       # Имя переменной
        self.eat('OP')       # Оператор присваивания
        value = self.expression()
        self.eat('DELIM')    # Завершающий символ (точка с запятой)
        return Node("VariableDeclaration", value={"type": var_type, "name": var_name}, children=[value])

    def expression(self):
        print(f"Processing expression at index {self.current_token_index}")  # Отладка
        # Обработка унарного оператора перед числом/переменной
        if self.next_token() == 'OP' and self.tokens[self.current_token_index].value in {'-', '!', '++', '--'}:
            operator = self.tokens[self.current_token_index].value
            print(f"Unary operator: {operator} at index {self.current_token_index}")  # Отладка
            self.eat('OP')  # Унарный оператор
            right = self.term()
            return Node("UnaryOperation", value=operator, children=[right])
        else:
            left = self.term()
            # Обработка бинарных операторов
            while self.next_token() == 'OP' and self.tokens[self.current_token_index].value in {'+', '-', '&&', '||', '!=', '==', '<', '>', '<=', '>='}:
                operator = self.tokens[self.current_token_index].value
                print(f"Binary operator: {operator} at index {self.current_token_index}")  # Отладка
                self.eat('OP')
                right = self.term()
                left = Node("BinaryOperation", value=operator, children=[left, right])
            return left




    def compound_assignment(self):
        var_name = self.tokens[self.current_token_index].value
        self.eat('ID')  # Имя переменной
        operator = self.tokens[self.current_token_index].value
        self.eat('OP')  # Оператор типа +=, -=, *= и т.д.
        value = self.expression()  # Правое выражение
        self.eat('DELIM')  # ;
        return Node("CompoundAssignment", value={"variable": var_name, "operator": operator}, children=[value])


    def unary_operation(self):
        operator = self.tokens[self.current_token_index].value
        self.eat('OP')  # Унарный оператор типа -, !, ++, --

        if operator in {'++', '--'}:
            var_name = self.tokens[self.current_token_index].value
            self.eat('ID')  # Переменная
            return Node("UnaryOperation", value={"operator": operator, "variable": var_name})
        else:
            # Если унарный оператор применяется к числу или выражению
            value = self.term()
            return Node("UnaryOperation", value={"operator": operator, "value": value})


    def term(self):
        token = self.tokens[self.current_token_index]
        print(f"Processing term: {token} at index {self.current_token_index}")  # Отладка
        if token.type == 'NUMBER':
            self.eat('NUMBER')
            return Node("Number", value=token.value)
        elif token.type == 'STRING':
            self.eat('STRING')
            return Node("String", value=token.value)
        elif token.type == 'ID':
            value = token.value
            self.eat('ID')
            return Node("Variable", value=value)
        elif token.type == 'OP' and token.value in {'-', '!', '++', '--'}:
            operator = token.value
            self.eat('OP')  # Унарный оператор
            var_name = self.tokens[self.current_token_index].value
            self.eat('ID')  # Переменная после унарного оператора
            return Node("UnaryOperation", value={"operator": operator, "variable": var_name})
        else:
            raise SyntaxError(f"Неожиданный токен в выражении: {token.type}")
