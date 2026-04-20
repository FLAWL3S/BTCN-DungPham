import tkinter as tk

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Calculator")

# Biến lưu biểu thức
expression = ""

# Hàm cập nhật biểu thức
def press(num):
    global expression
    expression += str(num)
    equation.set(expression)

# Hàm tính toán
def equalpress():
    global expression
    try:
        total = str(eval(expression))
        equation.set(total)
        expression = total
    except:
        equation.set("error")
        expression = ""

# Hàm xóa
def clear():
    global expression
    expression = ""
    equation.set("")

# Biến hiển thị
equation = tk.StringVar()

# Ô hiển thị
entry = tk.Entry(root, textvariable=equation, font=('Arial', 20), bd=10, insertwidth=2, width=14, borderwidth=4)
entry.grid(row=0, column=0, columnspan=4)

# Tạo các nút
buttons = [
    ('7',1,0), ('8',1,1), ('9',1,2), ('/',1,3),
    ('4',2,0), ('5',2,1), ('6',2,2), ('*',2,3),
    ('1',3,0), ('2',3,1), ('3',3,2), ('-',3,3),
    ('0',4,0), ('.',4,1), ('=',4,2), ('+',4,3),
]

for (text, row, col) in buttons:
    if text == "=":
        tk.Button(root, text=text, padx=20, pady=20, command=equalpress).grid(row=row, column=col)
    else:
        tk.Button(root, text=text, padx=20, pady=20, command=lambda t=text: press(t)).grid(row=row, column=col)

# Nút clear
tk.Button(root, text='C', padx=20, pady=20, command=clear).grid(row=5, column=0, columnspan=4)

root.mainloop()