import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import sys
import webbrowser

class JsonViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("نمایشگر اطلاعات کاربران")
        self.root.geometry("1080x700")
        
        # متغیر برای نگهداری داده‌ها
        self.data_list = []
        self.filtered_data = []
        self.current_page = 0
        self.page_size = 100

        # --- فریم بالا (جستجو و بارگذاری) ---
        top_frame = tk.Frame(root, pady=10, padx=10)
        top_frame.pack(fill="x")

        # دکمه باز کردن فایل
        self.btn_open = tk.Button(top_frame, text="📂 باز کردن فایل JSON", command=self.load_file, bg="#e1e1e1")
        self.btn_open.pack(side="right", padx=5)

        # باکس جستجو
        tk.Label(top_frame, text="جستجو (نام کاربری):").pack(side="left")
        self.entry_search = tk.Entry(top_frame, width=30)
        self.entry_search.pack(side="left", padx=5)
        self.entry_search.bind("<KeyRelease>", self.filter_data) # جستجوی لحظه‌ای

        # --- فریم آمار ---
        stats_frame = tk.Frame(root, bg="#f0f0f0", pady=5)
        stats_frame.pack(fill="x")
        
        self.lbl_stats = tk.Label(stats_frame, text="لطفا یک فایل JSON بارگذاری کنید.", bg="#f0f0f0", font=("Arial", 10, "bold"))
        self.lbl_stats.pack()

        # --- فریم جدول ---
        table_frame = tk.Frame(root, padx=10, pady=10)
        table_frame.pack(fill="both", expand=True)

        # تعریف ستون‌ها
        columns = ("id", "username", "name", "followers", "account based", "tweets", "bot", "date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        # تنظیم سرستون‌ها
        self.tree.heading("id", text="#")
        self.tree.heading("username", text="نام کاربری")
        self.tree.heading("name", text="نام نمایشی")
        self.tree.heading("followers", text="فالوورها")
        self.tree.heading("account based", text="مکان")
        self.tree.heading("tweets", text="توییت‌ها")
        self.tree.heading("bot", text="ربات؟")
        self.tree.heading("date", text="تاریخ عضویت")

        # تنظیم عرض ستون‌ها
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("username", width=150)
        self.tree.column("name", width=150)
        self.tree.column("followers", width=80)
        self.tree.column("account based", width=100)
        self.tree.column("tweets", width=80)
        self.tree.column("bot", width=40)
        self.tree.column("date", width=150)

        # اسکرول بار برای جدول
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.open_link)

        # --- صفحه‌بندی---
        pagination_frame = tk.Frame(root, pady=5)
        pagination_frame.pack(fill="x", side="bottom")

        self.btn_prev = tk.Button(pagination_frame, text="< قبلی", command=lambda: self.change_page(-1))
        self.btn_prev.pack(side="left", padx=20)

        self.lbl_page = tk.Label(pagination_frame, text="صفحه 0 از 0")
        self.lbl_page.pack(side="left", expand=True)

        self.btn_next = tk.Button(pagination_frame, text="بعدی >", command=lambda: self.change_page(1))
        self.btn_next.pack(side="right", padx=20)

        # تلاش برای بارگذاری خودکار اگر فایل کنار برنامه باشد
        self.auto_load_default()

    def auto_load_default(self):
        # پیدا کردن مسیر فایل اجرایی یا اسکریپت
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        default_path = os.path.join(base_path, "IR-Network.json")
        
        if os.path.exists(default_path):
            self.process_json(default_path)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            self.process_json(file_path)

    def process_json(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.data_list = json.load(f)
            
            self.filtered_data = self.data_list
            self.current_page = 0
            self.update_table()
            self.update_stats(self.data_list)
        except Exception as e:
            messagebox.showerror("خطا", f"فایل خوانده نشد!\n{str(e)}")

    def update_stats(self, data):
        total = len(data)
        bots = sum(1 for x in data if x.get('bot') == True)
        self.lbl_stats.config(text=f"تعداد کل کاربران: {total}  |  تعداد ربات‌ها: {bots}")

    def change_page(self, direction):
        total_pages = (len(self.filtered_data) + self.page_size - 1) // self.page_size
        new_page = self.current_page + direction
        
        # بررسی اینکه از محدوده خارج نشود
        if 0 <= new_page < total_pages:
            self.current_page = new_page
            self.update_table()

    def open_link(self, event):
        # تشخیص اینکه روی کدام ستون کلیک شده
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            col = self.tree.identify_column(event.x)
            
            
            if col == '#2':
                item_id = self.tree.identify_row(event.y)
                if item_id:
                    # گرفتن نام کاربری از ردیف انتخاب شده
                    username = self.tree.item(item_id)['values'][1]
                    if username:
                        webbrowser.open(f"https://x.com/{username}")

    def update_table(self):
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.filtered_data:
            self.lbl_page.config(text="موردی یافت نشد")
            return

        
        start_index = self.current_page * self.page_size
        end_index = start_index + self.page_size
        
        
        page_data = self.filtered_data[start_index:end_index]
        
        
        for i, item in enumerate(page_data):
            row_number = start_index + i + 1  
            
            is_bot = "بله" if item.get('bot') else "خیر"
            
            self.tree.insert("", "end", values=(
                row_number,                       # ستون ۱: شماره
                item.get('username', ''),         # ستون ۲: یوزرنیم
                item.get('name', ''),             # ستون ۳: نام
                item.get('follower_count', 0),    # ستون ۴: فالوور
                item.get('account_based_in', ''), # ستون ۵: مکان
                item.get('number_of_tweets', 0),  # ستون ۶: توییت
                is_bot,                           # ستون ۷: ربات
                item.get('creation_date', '')     # ستون ۸: تاریخ
            ))
            
       
        total_items = len(self.filtered_data)
        total_pages = (total_items + self.page_size - 1) // self.page_size
        if total_pages == 0: total_pages = 1
        
        self.lbl_page.config(text=f"صفحه {self.current_page + 1} از {total_pages} (مجموع رکوردها: {total_items})")

    def filter_data(self, event):
        query = self.entry_search.get().lower()
        
        if not query:
            self.filtered_data = self.data_list
        else:
            self.filtered_data = [x for x in self.data_list if query in str(x.get('username', '')).lower()]
        
        self.current_page = 0 
        self.update_table()

if __name__ == "__main__":
    root = tk.Tk()
    app = JsonViewerApp(root)
    root.mainloop()