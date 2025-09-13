from lexer import Lexer
from parser111 import Parser
from parser111 import Node
from generator import CodeGenerator

code = """
using System;
using System.Generic;

namespace Hello { 
    public class World {
        public static void Main() {
            int x = 3;
            string y = "sgg";
            x += 5;
            z = y + 2;
            if (z != z) {
                return 0;
            }
        }

        private int NotMain() {
            do {
                return 0;
            } while (true);
        }
    }
}
"""

# Лексический анализ
lexer = Lexer(code)
tokens = lexer.tokenize()
i = 0
for token in tokens:
    print(i, token)
    i += 1

# Ситаксический анализ
parser = Parser(tokens)
result = parser.parse()
print(result)
print(type(result))
# Получаем текстовое представление дерева
tree_representation = result.print_tree()
print(tree_representation)


# генератор кода
generator = CodeGenerator()
js_code = generator.pre_order(result)
# print(js_code)