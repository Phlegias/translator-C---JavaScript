class Node:
    def __init__(self, type, children=None, value=None):
        self.type = type
        self.children = children if children is not None else []
        self.value = value

    def __repr__(self):
        return f"Node({self.type}, {self.value}, {self.children})"

    def print_tree(self, level=0):
        indent = "  " * level
        output = f"{indent}Node({self.type}, {self.value})\n"
        for child in self.children:
            output += child.print_tree(level + 1)
        return output

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0

    def eat(self, token_type, value=None):
        if self.current_token_index < len(self.tokens):
            token = self.tokens[self.current_token_index]
            if token.type == token_type and (value is None or token.value == value):
                self.current_token_index += 1
            else:
                raise SyntaxError(f"Ожидался токен {token_type} '{value}', но найден {token.type} '{token.value}'")
        else:
            raise SyntaxError("Неожиданный конец ввода")

    def next_token(self):
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        else:
            return None

    def next_token_type(self):
        token = self.next_token()
        return token.type if token else None

    def next_token_value(self):
        token = self.next_token()
        return token.value if token else None

    def parse(self):
        try:
            return self.program()
        except SyntaxError as e:
            raise SyntaxError(f"Синтаксическая ошибка: {e}")
            return None

    def program(self):
        nodes = []
        while self.current_token_index < len(self.tokens):
            if self.next_token_value() == 'using':
                nodes.append(self.lib_import())
            else:
                nodes.append(self.namespace_declaration())
        return Node("Program", nodes)

    def lib_import(self):
        self.eat('KEYWORD', 'using')
        lib_name_parts = []
        while True:
            lib_name_parts.append(self.next_token_value())
            self.eat('ID')
            if self.next_token_value() == '.':
                self.eat('OP', '.')
            else:
                break
        lib_name = '.'.join(lib_name_parts)
        self.eat('DELIM', ';')
        return Node("LibraryImport", value=lib_name)

    def namespace_declaration(self):
        self.eat('KEYWORD', 'namespace')
        namespace_name = self.next_token_value()
        self.eat('ID')
        self.eat('DELIM', '{')

        class_nodes = []
        while self.next_token_value() != '}':
            class_nodes.append(self.class_declaration())
        self.eat('DELIM', '}')
        return Node("Namespace", children=class_nodes, value=namespace_name)

    def class_declaration(self):
        modifiers = []
        while self.next_token_type() == 'KEYWORD' and self.next_token_value() in {'public', 'private', 'protected', 'static'}:
            modifiers.append(self.next_token_value())
            self.eat('KEYWORD')
        self.eat('TYPE', 'class')
        class_name = self.next_token_value()
        self.eat('ID')
        self.eat('DELIM', '{')

        method_nodes = []
        while self.next_token_value() != '}':
            method_nodes.append(self.method_declaration())

        self.eat('DELIM', '}')
        return Node("Class", children=method_nodes, value={"name": class_name, "modifiers": modifiers})

    def method_declaration(self):
        modifiers = []
        while self.next_token_type() == 'KEYWORD' and self.next_token_value() in {'public', 'private', 'protected', 'static'}:
            modifiers.append(self.next_token_value())
            self.eat('KEYWORD')
        return_type = self.next_token_value()
        self.eat('TYPE')
        method_name = self.next_token_value()
        self.eat('ID')
        self.eat('DELIM', '(')
        parameters = self.method_parameters()
        self.eat('DELIM', ')')
        self.eat('DELIM', '{')

        statement_list = self.statement_list()

        self.eat('DELIM', '}')
        return Node("Method", children=statement_list, value={"name": method_name, "modifiers": modifiers, "parameters": parameters, "return_type": return_type})

    def method_parameters(self):
        params = []
        if self.next_token_value() != ')':
            while True:
                param_type = self.next_token_value()
                self.eat('TYPE')
                param_name = self.next_token_value()
                self.eat('ID')
                params.append(param_name)
                if self.next_token_value() == ',':
                    self.eat('DELIM', ',')
                else:
                    break
        return params

    def statement_list(self):
        statements = []
        while self.next_token_value() != '}':
            statements.append(self.statement())
        return statements

    def statement(self):
        if self.next_token_type() == 'OUTPUT':
            return self.output()
        elif self.next_token_type() == 'TYPE':
            return self.variable_declaration()
        elif self.next_token_type() == 'ID':
            if self.tokens[self.current_token_index + 1].type == 'OP':
                next_op = self.tokens[self.current_token_index + 1].value
                if next_op in {'=', '+=', '-=', '*=', '/=', '%='}:
                    if next_op == '=':
                        return self.assignment_statement()
                    else:
                        return self.compound_assignment()
                elif next_op == '.':
                    return self.method_call()
                else:
                    return self.expression_statement()
            elif self.tokens[self.current_token_index + 1].value == '(':
                    return self.method_call()
            else:
                return self.expression_statement()
        elif self.next_token_value() == 'return':
            return self.return_statement()
        elif self.next_token_value() in {'if', 'while', 'do', 'for'}:
            return self.control_statement()
        else:
            raise SyntaxError(f"Неожиданное начало оператора: {self.next_token_value()}")

    def output(self):
        self.eat('OUTPUT')
        self.eat('DELIM', '(')
        value = self.expression()
        self.eat('DELIM', ')')
        self.eat('DELIM', ';')
        return Node("Output", children=[value] if value else [])


    def variable_declaration(self):
        var_type = self.next_token_value()
        self.eat('TYPE')
        var_name = self.next_token_value()
        self.eat('ID')
        value = None
        if self.next_token_value() == '=':
            self.eat('OP', '=')
            value = self.expression()
        self.eat('DELIM', ';')
        return Node("VariableDeclaration", value={"type": var_type, "name": var_name}, children=[value] if value else [])

    def assignment_statement(self):
        var_name = self.next_token_value()
        self.eat('ID')
        self.eat('OP', '=')
        value = self.expression()
        self.eat('DELIM', ';')
        return Node("Assignment", value={"variable": var_name}, children=[value])

    def compound_assignment(self):
        var_name = self.next_token_value()
        self.eat('ID')
        operator = self.next_token_value()
        self.eat('OP')
        value = self.expression()
        self.eat('DELIM', ';')
        return Node("CompoundAssignment", value={"variable": var_name, "operator": operator}, children=[value])

    def expression_statement(self):
        expr = self.expression()
        self.eat('DELIM', ';')
        return Node("ExpressionStatement", children=[expr])

    def expression(self):
        return self.logical_or()

    def logical_or(self):
        node = self.logical_and()
        while self.next_token_value() == '||':
            op = self.next_token_value()
            self.eat('OP', '||')
            right = self.logical_and()
            node = Node("BinaryOperation", value=op, children=[node, right])
        return node

    def logical_and(self):
        node = self.equality()
        while self.next_token_value() == '&&':
            op = self.next_token_value()
            self.eat('OP', '&&')
            right = self.equality()
            node = Node("BinaryOperation", value=op, children=[node, right])
        return node

    def equality(self):
        node = self.relational()
        while self.next_token_value() in {'==', '!='}:
            op = self.next_token_value()
            self.eat('OP')
            right = self.relational()
            node = Node("BinaryOperation", value=op, children=[node, right])
        return node

    def relational(self):
        node = self.additive()
        while self.next_token_value() in {'<', '>', '<=', '>='}:
            op = self.next_token_value()
            self.eat('OP')
            right = self.additive()
            node = Node("BinaryOperation", value=op, children=[node, right])
        return node

    def additive(self):
        node = self.multiplicative()
        while self.next_token_value() in {'+', '-'}:
            op = self.next_token_value()
            self.eat('OP')
            right = self.multiplicative()
            node = Node("BinaryOperation", value=op, children=[node, right])
        return node

    def multiplicative(self):
        node = self.unary()
        while self.next_token_value() in {'*', '/', '%'}:
            op = self.next_token_value()
            self.eat('OP')
            right = self.unary()
            node = Node("BinaryOperation", value=op, children=[node, right])
        return node

    def unary(self):
        if self.next_token_value() in {'-', '!', '++', '--'}:
            op = self.next_token_value()
            self.eat('OP')
            operand = self.unary()
            return Node("UnaryOperation", value=op, children=[operand])
        else:
            return self.primary()

    def primary(self):
        token = self.next_token()
        if token.type == 'NUMBER':
            self.eat('NUMBER')
            return Node("Number", value=token.value)
        elif token.type == 'STRING':
            self.eat('STRING')
            return Node("String", value=token.value)
        elif token.type == 'ID':
            self.eat('ID')
            return Node("Variable", value=token.value)
        elif token.type == 'KEYWORD' and token.value in {'true', 'false'}:
            self.eat('KEYWORD')
            return Node("Boolean", value=token.value)
        elif token.type == 'DELIM' and token.value == '(':
            self.eat('DELIM', '(')
            expr = self.expression()
            self.eat('DELIM', ')')
            return expr
        else:
            raise SyntaxError(f"Неожиданный токен: {token.type} '{token.value}'")

    def return_statement(self):
        self.eat('KEYWORD', 'return')
        if self.next_token_value() != ';':
            expr = self.expression()
        else:
            expr = None
        self.eat('DELIM', ';')
        return Node("Return", children=[expr] if expr else [])

    def control_statement(self):
        if self.next_token_value() == 'if':
            return self.if_statement()
        elif self.next_token_value() == 'while':
            return self.while_statement()
        elif self.next_token_value() == 'do':
            return self.do_while_statement()
        else:
            raise SyntaxError(f"Неизвестная управляющая конструкция: {self.next_token_value()}")

    def if_statement(self):
        self.eat('KEYWORD', 'if')
        self.eat('DELIM', '(')
        condition = self.expression()
        self.eat('DELIM', ')')
        self.eat('DELIM', '{')
        then_branch = self.statement_list()
        self.eat('DELIM', '}')
        else_branch = None
        if self.next_token_value() == 'else':
            self.eat('KEYWORD', 'else')
            if self.next_token_value() == 'if':
                else_branch = self.statement_list()
            else:
                self.eat('DELIM', '{')
                else_branch = self.statement_list()
                self.eat('DELIM', '}')
        return Node("If", children=[condition, Node("Block", children=then_branch)] + ([Node("ElseBlock", children=else_branch)] if else_branch else []))

    def while_statement(self):
        self.eat('KEYWORD', 'while')
        self.eat('DELIM', '(')
        condition = self.expression()
        self.eat('DELIM', ')')
        self.eat('DELIM', '{')
        body = self.statement_list()
        self.eat('DELIM', '}')
        return Node("While", children=[condition, Node("Block", children=body)])

    def do_while_statement(self):
        self.eat('KEYWORD', 'do')
        self.eat('DELIM', '{')
        body = self.statement_list()
        self.eat('DELIM', '}')
        self.eat('KEYWORD', 'while')
        self.eat('DELIM', '(')
        condition = self.expression()
        self.eat('DELIM', ')')
        self.eat('DELIM', ';')
        return Node("DoWhile", children=[Node("Block", children=body), condition])

    def method_call(self):
        method_name = self.next_token_value()
        self.eat('ID')
        while self.next_token_value() != '(':
            self.eat('OP')
            method_name += '.'
            method_name += self.next_token_value()
            self.eat('ID')
        self.eat('DELIM', '(')
        args = []
        if self.next_token_value() != ')':
            while True:
                args.append(self.expression())
                if self.next_token_value() == ',':
                    self.eat('DELIM', ',')
                else:
                    break
        self.eat('DELIM', ')')
        self.eat('DELIM', ';')
        return Node("MethodCall", value=method_name, children=args)
