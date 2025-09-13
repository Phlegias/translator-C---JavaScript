from tkinter import *
import sys
import argparse
from lexer import Lexer
from parser import Parser
from generator import CodeGenerator

def onChangeText(var, index, mode):
    code = sv.get()

    if text1.compare("end-1c", "==", "1.0"):   
        label3['text'] = 'Ожидание ввода...'
        return

    errorMessage = 'ОК'
    js_code = ''

    lexer = Lexer(code)
    try:
        tokens = lexer.tokenize()
    except ValueError as e:
        errorMessage = f"Лексическая ошибка: {e}"
    except Exception as e:
        errorMessage = e

    text2.delete(1.0, END)
    label3['text'] = errorMessage
    if (errorMessage != 'ОК'): return

    parser_obj = Parser(tokens)
    try:
        ast = parser_obj.parse()
        if ast is None:
            errorMessage = "Синтаксический анализ завершился с ошибками."
    except Exception as e:
        errorMessage = e

    text2.delete(1.0, END)
    label3['text'] = errorMessage
    if (errorMessage != 'ОК'): return

    generator = CodeGenerator()
    try:
        js_code = generator.generate(ast)
    except Exception as e:
        errorMessage = e

    text2.delete(1.0, END)
    label3['text'] = errorMessage
    if (errorMessage != 'ОК'): return

    text2.insert(END, js_code)

def typingText(event):
    sv.set(text1.get(1.0, END))

def pasteText():
    text1.delete(1.0, END)
    text1.insert(END, root.clipboard_get())
    sv.set(root.clipboard_get())

def copyText():
    root.clipboard_clear()
    root.clipboard_append(text2.get(1.0, END))

root = Tk()

sv = StringVar()
sv.trace_add('write', onChangeText)

label1 = Label(text="C#")
label1.grid(row=0, column=0, sticky=W, padx=10, pady=4)

button1 = Button(text='Paste', width=10, command=pasteText)
button1.grid(row=0, column=1, sticky=E, padx=2)

text1 = Text(width=60, height=30)
text1.bind('<KeyRelease>', typingText)
text1.grid(row=1, column=0, columnspan=2, padx=2)

label2 = Label(text="JavaScript")
label2.grid(row=0, column=2, sticky=W, padx=10, pady=4)

button2 = Button(text='Copy', width=10, command=copyText)
button2.grid(row=0, column=3, sticky=E, padx=2)

text2 = Text(width=60, height=30)
text2.grid(row=1, column=2, columnspan=2, padx=2)

label3 = Label(text='Ожидание ввода...')
label3.grid(row=2, column=0, columnspan=4, sticky=W, pady=4)

root.mainloop()
