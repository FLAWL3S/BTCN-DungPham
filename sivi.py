import sqlite3
import customtkinter as ctk
from tkinter import ttk, messagebox
from PIL import Image #pillow
import os
# --- KHỞI TẠO DATABASE ---
def init_db():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT,
            major TEXT,
            gpa DOUBLE
        )
    ''')
    conn.commit()
    conn.close()
    

# --- GIAO DIỆN CHÍNH ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Quản lý cơ sở dữ liệu sinh viên")
        self.geometry("900x500")
        ctk.set_appearance_mode("System")
        
        # Biến lưu trữ dữ liệu nhập
        self.entry_id = ctk.StringVar()
        self.entry_name = ctk.StringVar()
        self.entry_major = ctk.StringVar()
        self.entry_gpa = ctk.StringVar()
        self.search_var = ctk.StringVar()

        self.setup_ui()
        self.load_data()
        self.bg_label = None
        self.bg_image = None

    def setup_ui(self):
        # --- KHUNG NHẬP LIỆU ---
        input_frame = ctk.CTkFrame(self,fg_color="transparent")
        input_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(input_frame, text="Mã SV:").grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkEntry(input_frame, textvariable=self.entry_id).grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="Họ Tên:").grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkEntry(input_frame, textvariable=self.entry_name).grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="Ngành:").grid(row=0, column=4, padx=5, pady=5)
        ctk.CTkEntry(input_frame, textvariable=self.entry_major).grid(row=0, column=5, padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="GPA").grid(row=0,column=6,padx=5,pady=5)
        ctk.CTkEntry(input_frame, textvariable=self.entry_gpa).grid(row=0,column=7,padx=6,pady=5)
        #Secret button
        btn_framesecret=ctk.CTkFrame(self,fg_color="transparent")
        btn_framesecret.pack(pady=10,padx=10,anchor="e")
        ctk.CTkButton(btn_framesecret,text="SUPER SECRET SETTING",width=50,height=50,command=self.toggle_mod,fg_color="#E67E22",hover_color="#D35400").pack(side="left",padx=5)
        # --- KHUNG CHỨC NĂNG ---
        btn_frame = ctk.CTkFrame(self,fg_color="transparent")
        btn_frame.pack(pady=5, padx=10, fill="x")

        ctk.CTkButton(btn_frame, text="Thêm", command=self.add_record).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame,text="Cập nhật",command=self.update_rec).pack(side="left",padx=5)
        ctk.CTkButton(btn_frame, text="Xóa", command=self.delete_record, fg_color="#D32F2F", hover_color="#B71C1C").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame,text="Xóa Tất Cả",command=self.delete_all,fg_color="#D32F2F", hover_color="#B71C1C").pack(side="left",padx=5)

        # Thanh tìm kiếm
        ctk.CTkEntry(btn_frame, textvariable=self.search_var, placeholder_text="Nhập gpa...").pack(side="left", padx=(30, 5), fill="x", expand=True)
        ctk.CTkButton(btn_frame, text="Lọc theo gpa <", command=self.filter_data).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Làm mới", command=self.load_data).pack(side="left", padx=5)

        # --- KHUNG BẢNG DỮ LIỆU (TREEVIEW) ---
        table_frame = ctk.CTkFrame(self,fg_color="transparent")
        table_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Cấu hình style cho Treeview để hợp với nền tối/sáng
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=25, fieldbackground="#2b2b2b")
        style.map('Treeview', background=[('selected', '#1f538d')])

        self.tree = ttk.Treeview(table_frame, columns=("ID", "Name", "Major","GPA"), show="headings")
        self.tree.heading("ID", text="Mã Sinh Viên")
        self.tree.heading("Name", text="Họ và Tên")
        self.tree.heading("Major", text="Ngành Học")
        self.tree.heading("GPA",text="GPA")

        self.tree.column("ID", width=100, anchor="center")
        self.tree.column("Name", width=250, anchor="w")
        self.tree.column("Major", width=200, anchor="center")
        self.tree.column("GPA",width=100,anchor="center")

        self.tree.pack(fill="both", expand=True)
        # Lắng nghe sự kiện click chuột trái vào một dòng trên bảng
        self.tree.bind("<ButtonRelease-1>", self.select_record)

    # --- CÁC HÀM XỬ LÝ DATABASE ---
    def execute_query(self, query, parameters=()):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute(query, parameters)
        conn.commit()
        result = cursor.fetchall()
        conn.close()
        return result

    def load_data(self):
        # Xóa dữ liệu cũ trên bảng
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Lấy dữ liệu mới từ DB
        rows = self.execute_query("SELECT * FROM students")
        for row in rows:
            self.tree.insert("", "end", values=row)

    def add_record(self):
        sv_id = self.entry_id.get()
        name = self.entry_name.get()
        major = self.entry_major.get()
        gpa_tx=self.entry_gpa.get()

        if not sv_id or not name or not gpa_tx:
            messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return
        try:
            GPA = float(gpa_tx)
        except ValueError:
            messagebox.showerror("Lỗi", "Cột Điểm bắt buộc phải là số!")
            return
        try:
            self.execute_query("INSERT INTO students VALUES (?, ?, ?, ?)", (sv_id, name, major,GPA))
            self.load_data()
            
            # Xóa trắng ô nhập liệu sau khi thêm
            self.entry_id.set("")
            self.entry_name.set("")
            self.entry_major.set("")
            self.entry_gpa.set("")
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Mã SV này đã tồn tại!")

    def select_record(self, event):
        # 1. Xóa sạch các ô nhập liệu cũ trước khi điền dữ liệu mới
        self.entry_id.set("")
        self.entry_name.set("")
        self.entry_major.set("")
        self.entry_gpa.set("")

        # 2. Lấy ID ẩn của dòng đang được bôi đen (chọn) trên bảng
        selected_row = self.tree.focus()
        if not selected_row:
            return

        # 3. Lấy toàn bộ giá trị của dòng đó và đẩy ngược lên các biến nhập liệu
        values = self.tree.item(selected_row, "values")
        if values:
            self.entry_id.set(values[0])     # Mã SV
            self.entry_name.set(values[1])   # Họ tên
            self.entry_major.set(values[2])  # Ngành
            self.entry_gpa.set(values[3])    # GPA
    def update_rec(self):
        # Lấy dữ liệu hiện tại đang nằm trên các ô nhập
        sv_id = self.entry_id.get()
        new_name = self.entry_name.get()
        new_major = self.entry_major.get()
        new_gpa = self.entry_gpa.get()

        # Kiểm tra xem người dùng đã chọn SV nào chưa
        if not sv_id:
            from tkinter import messagebox
            messagebox.showwarning("Cảnh báo", "Vui lòng click chọn một sinh viên trên bảng để cập nhật!")
            return

        # Cập nhật vào Cơ sở dữ liệu
        query = "UPDATE students SET name=?, major=?, gpa=? WHERE id=?"
        
        try:
            self.execute_query(query, (new_name, new_major, float(new_gpa), sv_id))
            
            # Làm mới bảng và hiện thông báo
            self.load_data()
            from tkinter import messagebox
            messagebox.showinfo("Thành công", f"Đã cập nhật thông tin sinh viên {sv_id}!")
            
            # Xóa trắng form để nhập người khác
            self.entry_id.set("")
            self.entry_name.set("")
            self.entry_major.set("")
            self.entry_gpa.set("")
            
        except ValueError:
            from tkinter import messagebox
            messagebox.showerror("Lỗi", "GPA phải là một số!")
    def delete_record(self): #xóa dữ liệu được chọn
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Lỗi", "Vui lòng chọn một dòng để xóa!")
            return
        
        # Lấy ID của dòng được chọn
        item = self.tree.item(selected_item)
        sv_id = item['values'][0]

        self.execute_query("DELETE FROM students WHERE id=?", (sv_id,))
        self.load_data()

    def delete_all(self): #xóa dữ liệu hiển thị
        visible_items=self.tree.get_children()
        confirm = messagebox.askyesno("Xác nhận", f"Bạn có muốn xóa {len(visible_items)} sivi khỏi Database không?")
        if confirm:
            for item in visible_items:
                sv_id=self.tree.item(item)["values"][0]
                self.execute_query("DELETE FROM students WHERE id=?",(sv_id,))
            self.load_data()
            messagebox.showinfo("Thông báo","Đã xóa thành công!")

    def filter_data(self):
        search_text = self.search_var.get()
        #xóa dữ liệu cũ
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        # Lọc sv có gpa nhỏ hơn
        query = "SELECT * FROM students WHERE gpa < ?"
        rows = self.execute_query(query, (float(search_text),))
        #hiển thị kết quả
        for row in rows:
            self.tree.insert("", "end", values=row)
    def toggle_mod(self):
        if self.bg_label is None:
            try:
                from PIL import Image
                current_dir=os.path.dirname(os.path.abspath(__file__))
                image_path=os.path.join(current_dir,"background.png")
                self.bg_image=ctk.CTkImage(Image.open(image_path),size=(900,500))
                self.bg_label=ctk.CTkLabel(self,text="",image=self.bg_image)
                self.bg_label.place(x=0,y=0,relwidth=1,relheight=0.3)
                self.bg_label.lower()
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Lỗi",f"Không tìm thấy file background,{e}")
        else:
            self.bg_label.destroy()
            self.bg_label=None

if __name__ == "__main__":
    init_db()
    app = App()
    app.mainloop()