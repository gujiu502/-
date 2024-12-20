import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
import json
import pyperclip  # 导入 pyperclip 库，用于操作剪贴板

CONFIG_FILE = "config.txt"
APPS_FILE = "apps.json"

class AppManager:
    def __init__(self):
        self.apps = []
        self.load_apps()

    def load_apps(self):
        """从文件加载应用程序配置"""
        if os.path.exists(APPS_FILE):
            with open(APPS_FILE, "r") as file:
                self.apps = json.load(file)

    def save_apps(self):
        """保存应用程序配置到文件"""
        with open(APPS_FILE, "w") as file:
            json.dump(self.apps, file)

    def add_app(self, app_name, script_path, work_dir, use_cmd, create_console):
        """添加新的应用程序到配置中"""
        self.apps.append((app_name, script_path, work_dir, use_cmd, create_console))
        self.save_apps()

    def remove_app(self, app_name):
        """从配置中删除应用程序"""
        self.apps = [app for app in self.apps if app[0] != app_name]
        self.save_apps()

    def run_application(self, script_path, work_dir, app_name, use_cmd=False, create_console=False):
        """启动应用程序"""
        try:
            if use_cmd:
                args = ["cmd.exe", "/c", script_path]
                flags = subprocess.CREATE_NEW_CONSOLE if create_console else 0
            else:
                args = [script_path]
                flags = 0

            subprocess.Popen(args, cwd=work_dir, creationflags=flags)
            return f"{app_name} 已启动！", "green"
        except FileNotFoundError:
            return f"文件未找到：{script_path}", "red"
        except Exception as e:
            return f"运行 {app_name} 时出错：{e}", "red"


class AppUI:
    def __init__(self, root, app_manager):
        self.root = root
        self.app_manager = app_manager
        self.bg_photo = None
        self.bg_image = None
        self.create_widgets()

    def create_widgets(self):
        """创建主界面的UI组件"""
        # 主窗口配置
        self.root.title("助手")
        self.root.geometry("800x400")
        self.root.resizable(False, False)

        # 背景图片标签
        self.bg_label = tk.Label(self.root, bg="lightgray")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # 状态标签
        self.status_label = tk.Label(self.root, text="请选择应用程序", font=("Arial", 12), fg="blue", bg="white")
        self.status_label.pack(pady=10)

        # 动态生成按钮的容器
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(pady=20)

        # 更新按钮列表
        self.update_buttons()

        # 功能按钮布局
        function_frame = ttk.Frame(self.root)
        function_frame.pack(side=tk.BOTTOM, pady=10)

        change_bg_button = ttk.Button(function_frame, text="更换背景", command=self.change_background)
        change_bg_button.grid(row=0, column=0, padx=10)

        add_button = ttk.Button(function_frame, text="添加新按钮", command=self.add_new_button)
        add_button.grid(row=0, column=1, padx=10)

        delete_button = ttk.Button(function_frame, text="删除按钮", command=self.open_delete_window)
        delete_button.grid(row=0, column=2, padx=10)

        export_button = ttk.Button(function_frame, text="导出按钮配置", command=self.export_buttons_to_clipboard)
        export_button.grid(row=1, column=0, padx=10)

        import_button = ttk.Button(function_frame, text="从剪贴板导入配置", command=self.import_buttons_from_clipboard)
        import_button.grid(row=1, column=1, padx=10)

        # 加载背景配置
        self.load_config()

    def update_buttons(self):
        """根据应用程序列表动态更新按钮"""
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        for i, (name, path, work_dir, use_cmd, console) in enumerate(self.app_manager.apps):
            btn = ttk.Button(
                self.button_frame,
                text=name,
                command=lambda p=path, d=work_dir, n=name, u=use_cmd, c=console: self.run_application(p, d, n, u, c),
            )
            row = i // 2
            column = i % 2
            btn.grid(row=row, column=column, padx=20, pady=10, sticky="w")

    def update_status(self, message, color):
        """更新状态栏文本"""
        self.status_label.config(text=message, fg=color)

    def run_application(self, script_path, work_dir, app_name, use_cmd=False, create_console=False):
        """运行应用程序并更新状态"""
        message, color = self.app_manager.run_application(script_path, work_dir, app_name, use_cmd, create_console)
        self.update_status(message, color)

    def change_background(self):
        """更换背景图片"""
        file_path = filedialog.askopenfilename(
            title="选择背景图片",
            filetypes=[("图片文件", "*.png;*.jpg;*.jpeg"), ("所有文件", "*.*")]
        )
        if file_path:
            self.set_background(file_path)
            self.save_config(file_path)

    def set_background(self, image_path):
        """设置背景图片"""
        try:
            self.bg_image = Image.open(image_path).convert("RGBA")
            self.bg_image = self.bg_image.resize((800, 400))

            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.bg_label.config(image=self.bg_photo)
        except Exception as e:
            self.update_status(f"无法加载背景图片：{e}", "red")

    def save_config(self, image_path):
        """保存背景图片路径到配置文件"""
        with open(CONFIG_FILE, "w") as file:
            file.write(image_path)

    def load_config(self):
        """加载配置文件中的背景图片路径"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as file:
                image_path = file.read().strip()
                if os.path.exists(image_path):
                    self.set_background(image_path)

    def add_new_button(self):
        """弹出对话框，允许用户添加新按钮"""
        app_name = simpledialog.askstring("添加按钮", "请输入应用程序名称：")
        if not app_name:
            return
        script_path = filedialog.askopenfilename(title="选择应用程序或脚本")
        if not script_path:
            return
        work_dir = filedialog.askdirectory(title="选择工作目录")
        if not work_dir:
            return
        use_cmd = messagebox.askyesno("运行方式", "是否通过命令提示符运行？")
        create_console = messagebox.askyesno("新控制台", "是否创建新控制台？")

        self.app_manager.add_app(app_name, script_path, work_dir, use_cmd, create_console)
        self.update_buttons()

    def open_delete_window(self):
        """打开删除窗口"""
        delete_window = tk.Toplevel(self.root)
        delete_window.title("删除应用程序")
        delete_window.geometry("400x300")
        delete_window.resizable(False, False)

        bg_label = tk.Label(delete_window, bg="lightgray")
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        delete_frame = ttk.Frame(delete_window)
        delete_frame.pack(pady=20)

        for i, (name, _, _, _, _) in enumerate(self.app_manager.apps):
            btn = ttk.Button(
                delete_frame,
                text=f"删除 {name}",
                command=lambda n=name: self.delete_app(n, delete_window)
            )
            row = i // 2
            column = i % 2
            btn.grid(row=row, column=column, padx=20, pady=5, sticky="w")

    def delete_app(self, app_name, delete_window):
        """删除指定的应用程序"""
        if messagebox.askyesno("确认删除", f"确定要删除应用程序 {app_name} 吗？"):
            self.app_manager.remove_app(app_name)
            self.update_buttons()
            self.update_status(f"{app_name} 已删除", "red")
            delete_window.destroy()

    def export_buttons_to_clipboard(self):
        """将按钮配置导出到剪贴板"""
        app_data = json.dumps(self.app_manager.apps, ensure_ascii=False, indent=4)
        pyperclip.copy(app_data)
        self.update_status("按钮配置已导出到剪贴板", "green")

    def import_buttons_from_clipboard(self):
        """从剪贴板导入按钮配置"""
        clipboard_data = pyperclip.paste()
        try:
            new_apps = json.loads(clipboard_data)
            if isinstance(new_apps, list):
                self.app_manager.apps = new_apps
                self.app_manager.save_apps()
                self.update_buttons()
                self.update_status("按钮配置已从剪贴板导入", "green")
            else:
                self.update_status("剪贴板内容无效", "red")
        except json.JSONDecodeError:
            self.update_status("剪贴板内容无法解析", "red")


if __name__ == "__main__":
    root = tk.Tk()

    # 创建应用程序管理器
    app_manager = AppManager()

    # 创建UI
    app_ui = AppUI(root, app_manager)

    # 启动主循环
    root.mainloop()
