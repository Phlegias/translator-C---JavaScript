from parser import Parser

indent = 2

class CodeGenerator:
    mainFlag = False
    nameMainClass = ''

    def generate(self, node):
        try:
            code = self.pre_order(node)
            return code
        except Exception as e:
            raise Exception(f"Ошибка при генерации кода: {e}")
            return ''

    def pre_order(self, node, depth=0):
        code = self.visit(node, depth)
        # code += self.visit(self.mainNode, 0)
        if self.mainFlag:
            code += f'\n{self.nameMainClass}Main()'
        return code

    def visit(self, node, depth):
        method_name = f'visit_{node.type}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node, depth)

    def generic_visit(self, node, depth):
        raise Exception(f'Нет visit_{node.type} метода')


    def visit_Output(self, node, depth):
        code = f'{depth * " "}console.log({self.visit(node.children[0], depth)})'
        return code

    def visit_Program(self, node, depth):
        code = '\n'.join(self.visit(child, depth) for child in node.children)
        return code

    def visit_LibraryImport(self, node, depth):
        return f'// Imported library: {node.value}'

    def visit_Namespace(self, node, depth):
        code = '\n'.join(self.visit(child, depth) for child in node.children)
        return code

    def visit_Class(self, node, depth):
        name = node.value['name']
        isChanged = self.mainFlag
        code = f'class {name} {{'
        for child in node.children:
            code += f'\n{self.visit(child, depth + indent)}'
        code += f'\n}}'

        if self.mainFlag != isChanged:
            self.nameMainClass += f'{name}.'
        
        return code

    def visit_Method(self, node, depth):
        name = node.value['name']

        if (name == "Main"):
            self.mainFlag = True

        parameters = ', '.join(node.value['parameters'])
        code = f'{depth * " "}function {name}({parameters}) {{'
        for child in node.children:
            code += f'\n{self.visit(child, depth + indent)}'
        code += f'\n{depth * " "}}}'
        return code

    def visit_VariableDeclaration(self, node, depth):
        name = node.value['name']
        value = self.visit(node.children[0], depth) if node.children else ''
        return f'{depth * " "}let {name} = {value};'

    def visit_Assignment(self, node, depth):
        variable = node.value['variable']
        value = self.visit(node.children[0], depth)
        return f'{depth * " "}{variable} = {value};'

    def visit_CompoundAssignment(self, node, depth):
        variable = node.value["variable"]
        operator = node.value["operator"]
        value = self.visit(node.children[0], depth)
        return f'{depth * " "}{variable} {operator} {value};'

    def visit_BinaryOperation(self, node, depth):
        left = self.visit(node.children[0], depth)
        right = self.visit(node.children[1], depth)
        operator = node.value
        return f'({left} {operator} {right})'

    def visit_UnaryOperation(self, node, depth):
        operand = self.visit(node.children[0], depth)
        operator = node.value
        return f'{operator}{operand}'

    def visit_Variable(self, node, depth):
        return node.value

    def visit_Number(self, node, depth):
        return node.value

    def visit_String(self, node, depth):
        return node.value

    def visit_Boolean(self, node, depth):
        return node.value

    def visit_If(self, node, depth):
        condition = self.visit(node.children[0], depth)
        then_branch = self.visit(node.children[1], depth)
        if len(node.children) > 2:
            else_branch = self.visit(node.children[2], depth)
            return f'{depth * " "}if ({condition}) {{\n{then_branch}\n{depth * " "}}} else {{\n{else_branch}\n{depth * " "}}}'
        else:
            return f'{depth * " "}if ({condition}) {{\n{then_branch}\n{depth * " "}}}'

    def visit_Block(self, node, depth):
        code = ''
        for child in node.children:
            code += f'{self.visit(child, depth + indent)}\n'
        return code.rstrip()

    def visit_ElseBlock(self, node, depth):
        return self.visit_Block(node, depth)

    def visit_Return(self, node, depth):
        if node.children:
            value = self.visit(node.children[0], depth)
            return f'{depth * " "}return {value};'
        else:
            return f'{depth * " "}return;'

    def visit_DoWhile(self, node, depth):
        body = self.visit(node.children[0], depth + indent)
        condition = self.visit(node.children[1], depth)
        return f'{depth * " "}do {{\n{body}\n{depth * " "}}} while ({condition});'

    def visit_While(self, node, depth):
        condition = self.visit(node.children[0], depth)
        body = self.visit(node.children[1], depth + indent)
        return f'{depth * " "}while ({condition}) {{\n{body}\n{depth * " "}}}'

    def visit_MethodCall(self, node, depth):
        method_name = node.value
        arguments = ', '.join(self.visit(arg, depth) for arg in node.children)
        return f'{depth * " "}{method_name}({arguments});'

    def visit_ExpressionStatement(self, node, depth):
        expr = self.visit(node.children[0], depth)
        return f'{depth * " "}{expr};'
