import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import os
import sv_ttk  # Sun Valley主题库
import sys
from tkinter import font as tkfont  # 导入字体模块
import tksvg # 导入 tksvg 库


class YTDLPGUI:
    def __init__(self, root):
        self.root = root
        root.title("Dlp Downloader")
        root.minsize(650, 350)  # 增加最小窗口尺寸以适应更美观的布局
        
        # 设置应用程序字体
        self.default_font = tkfont.nametofont("TkDefaultFont")
        self.default_font.configure(size=10)  # 调整默认字体大小

        # 配置样式以尝试移除 Combobox 选择高亮
        style = ttk.Style()
        try:
            # 获取当前主题下 Combobox 的背景和前景颜色
            bg_color = style.lookup('TCombobox', 'fieldbackground')
            fg_color = style.lookup('TCombobox', 'foreground')
            
            # 配置 Combobox 下拉列表的选中样式
            # 注意: 'Combobox.Listbox' 是 Tkinter 内部名称，可能因主题或版本而异
            # 如果此配置无效，可能需要进一步研究 sv_ttk 的特定样式配置方法
            style.map('TCombobox', 
                      selectbackground=[('readonly', bg_color)], 
                      selectforeground=[('readonly', fg_color)])
            # 尝试直接配置 Listbox 部件样式 (作为备用方案)
            style.configure('Combobox.Listbox', selectbackground=bg_color, selectforeground=fg_color)
            
        except tk.TclError as e:
            print(f"警告: 配置 Combobox 样式失败，可能无法移除选择高亮: {e}")
        
        # 创建主框架，添加内边距
        self.main_frame = ttk.Frame(root, padding="20 15 20 15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题框架
        self.title_frame = ttk.Frame(self.main_frame)
        self.title_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 创建输入框架
        self.input_frame = ttk.LabelFrame(self.main_frame, text="输入信息", padding="15 10")
        self.input_frame.pack(fill=tk.X, pady=(0, 15))
        
        # URL 输入
        self.url_frame = ttk.Frame(self.input_frame)
        self.url_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.url_label = ttk.Label(self.url_frame, text="🎥 视频 URL:", width=12)
        self.url_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.url_entry = ttk.Entry(self.url_frame)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 输出目录输入
        self.dir_frame = ttk.Frame(self.input_frame)
        self.dir_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.output_dir_label = ttk.Label(self.dir_frame, text="📁 保存目录:", width=12)
        self.output_dir_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.output_dir_entry = ttk.Entry(self.dir_frame)
        self.output_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.button_frame = ttk.Frame(self.dir_frame)
        self.button_frame.pack(side=tk.RIGHT)
        
        self.browse_button = ttk.Button(self.button_frame, text="浏览", command=self.browse_output_dir, width=8)
        self.browse_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.open_dir_button = ttk.Button(self.button_frame, text="打开目录", command=self.open_output_dir, width=8)
        self.open_dir_button.pack(side=tk.LEFT)
        
        # 下载选项框架
        self.options_frame = ttk.LabelFrame(self.main_frame, text="下载选项", padding="15 10")
        self.options_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 选项内容框架
        self.options_content = ttk.Frame(self.options_frame)
        self.options_content.pack(fill=tk.X)
        
        # 合并选项
        self.merge_var = tk.BooleanVar(value=True)
        self.merge_checkbox = ttk.Checkbutton(self.options_content, text="合并视频和音频", variable=self.merge_var)
        self.merge_checkbox.pack(side=tk.LEFT, padx=(0, 30))
        
        # 格式选择
        self.format_frame = ttk.Frame(self.options_content)
        self.format_frame.pack(side=tk.LEFT)
        
        self.format_label = ttk.Label(self.format_frame, text="格式:")
        self.format_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.format_var = tk.StringVar(value="mp4")
        self.format_combobox = ttk.Combobox(self.format_frame,
                                          textvariable=self.format_var,
                                          values=["mp4", "mov", "avi"],
                                          state="readonly",
                                          width=8)
        self.format_combobox.pack(side=tk.LEFT)
        
        # 下载按钮
        self.download_button = ttk.Button(self.main_frame, text="⬇️ 下载视频", style="Accent.TButton", 
                                         command=self.start_download)
        self.download_button.pack(fill=tk.X, pady=(0, 15), ipady=5)  # 增加按钮高度
        
        # 进度框架
        self.progress_frame = ttk.LabelFrame(self.main_frame, text="下载进度", padding="15 10")
        self.progress_frame.pack(fill=tk.X, pady=(0, 15)) # 修改：移除 expand=True，设置 fill=tk.X
        
        # 进度条
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient="horizontal", 
                                          mode="determinate", style="success.Horizontal.TProgressbar")
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # 状态标签
        self.status_frame = ttk.Frame(self.progress_frame)
        self.status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_label = ttk.Label(self.status_frame, text="", anchor="w")
        self.status_label.pack(fill=tk.X)
        
        # 添加页脚框架 (用于放置主题按钮)
        self.footer_frame = ttk.Frame(self.main_frame)
        self.footer_frame.pack(fill=tk.X, pady=(10, 0))

        # 加载 SVG 图标
        self.icon_path = os.path.join(os.path.dirname(__file__), "assets")
        self.light_icon = tksvg.SvgImage(file=os.path.join(self.icon_path, "moon.svg"), scaletowidth=16)
        self.dark_icon = tksvg.SvgImage(file=os.path.join(self.icon_path, "sun.svg"), scaletowidth=16)

        # 主题切换按钮 (移动到页脚)
        self.theme_button = ttk.Button(self.footer_frame, command=self.toggle_theme, width=3)
        # 将主题切换按钮放置在页脚右侧
        self.theme_button.pack(side=tk.RIGHT)
        self.update_theme_button_icon() # 初始化按钮图标


    def browse_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, directory)

    def start_download(self):
        url = self.url_entry.get()
        output_dir = self.output_dir_entry.get()

        if not url:
            messagebox.showwarning("警告", "请输入视频 URL")
            return

        if not output_dir:
            messagebox.showwarning("警告", "请选择保存目录")
            return

        # Reset progress bar and status
        self.progress_bar["value"] = 0
        self.update_status("开始下载...")

        # Run download in a separate thread
        self.download_thread = threading.Thread(target=self.run_download, args=(url, output_dir))
        self.download_thread.start()

    def run_download(self, url, output_dir):
        # Assuming yt-dlp.exe and ffmpeg.exe are in the bin directory relative to the script
        yt_dlp_path = os.path.join(os.path.dirname(__file__), "bin", "yt-dlp.exe")
        ffmpeg_path = os.path.join(os.path.dirname(__file__), "bin", "ffmpeg.exe")

        if not os.path.exists(yt_dlp_path):
             self.update_status(f"错误: 找不到 yt-dlp.exe，请确保它位于 {yt_dlp_path}")
             return

        command = [yt_dlp_path, "--newline", "-o", os.path.join(output_dir, "%(title)s.%(ext)s"), "--format", "bestvideo+bestaudio", url]

        # Add format option if specified
        if self.format_var.get() != "mp4":
            command.extend(["--merge-output-format", self.format_var.get()])

        if self.merge_var.get():
            if not os.path.exists(ffmpeg_path):
                self.update_status(f"错误: 找不到 ffmpeg.exe，请确保它位于 {ffmpeg_path} 以进行合并")
                return
            # Use yt-dlp's built-in merge functionality, respecting the selected format
            command.extend(["-f", "bestvideo+bestaudio", "--merge-output-format", self.format_var.get(), "--ffmpeg-location", ffmpeg_path])

        try:
            # Windows-specific setup to hide console window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            process = subprocess.Popen(command,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     text=True,
                                     bufsize=1,
                                     universal_newlines=True,
                                     startupinfo=startupinfo)
            for line in process.stdout:
                self.parse_and_update_progress(line)
            process.wait()
            if process.returncode == 0:
                self.update_status("下载完成！")
            else:
                self.update_status(f"下载失败，错误码: {process.returncode}")
        except Exception as e:
            self.update_status(f"执行命令时发生错误: {e}")

    def parse_and_update_progress(self, line):
        # Example yt-dlp progress line:
        # [download] 10.1% of ~12.34MiB at 567.89KiB/s ETA 00:15
        if "[download]" in line and "% of" in line:
            try:
                parts = line.split()
                percentage_str = parts[1].replace('%', '')
                percentage = float(percentage_str)
                
                # 更新进度条
                self.progress_bar["value"] = percentage
                
                # 提取下载速度和剩余时间信息（如果存在）
                speed = "未知速度"
                eta = "未知时间"
                
                for i, part in enumerate(parts):
                    if part == "at" and i+1 < len(parts):
                        speed = parts[i+1]
                    if part == "ETA" and i+1 < len(parts):
                        eta = parts[i+1]
                
                # 格式化状态信息，使其更易读
                status_text = f"下载进度: {percentage:.1f}% | 速度: {speed} | 剩余时间: {eta}"
                self.update_status(status_text)
                
                # 根据进度更新进度条颜色
                if percentage < 30:
                    self.progress_bar.configure(style="Horizontal.TProgressbar")
                elif percentage < 70:
                    self.progress_bar.configure(style="info.Horizontal.TProgressbar")
                else:
                    self.progress_bar.configure(style="success.Horizontal.TProgressbar")
                    
            except (ValueError, IndexError):
                # 如果解析失败，直接显示原始行
                self.update_status(line.strip())
        else:
            # 显示其他相关消息
            self.update_status(line.strip())


    def open_output_dir(self):
        output_dir = self.output_dir_entry.get()
        if output_dir and os.path.exists(output_dir):
            try:
                # Use os.startfile on Windows to open the directory
                os.startfile(output_dir)
            except Exception as e:
                messagebox.showerror("错误", f"无法打开目录: {e}")
        elif output_dir:
            messagebox.showwarning("警告", "指定的目录不存在。")
        else:
            messagebox.showwarning("警告", "请先选择保存目录。")

    def update_status(self, text):
        # 更新状态标签并立即刷新界面
        self.status_label.config(text=text)
        # 如果是下载完成消息，添加绿色文本效果
        if "下载完成" in text:
            self.status_label.config(foreground="green")
        # 如果是错误消息，添加红色文本效果
        elif "错误" in text or "失败" in text:
            self.status_label.config(foreground="red")
        # 其他情况使用默认颜色
        else:
            self.status_label.config(foreground="")
        self.root.update_idletasks() # 立即更新GUI

    def update_theme_button_icon(self):
        """根据当前主题更新按钮图标"""
        # 修改：亮色模式显示太阳，暗色模式显示月亮
        if sv_ttk.get_theme() == "dark":
            self.theme_button.config(image=self.light_icon) # 暗色模式显示月亮 (light_icon)
        else:
            self.theme_button.config(image=self.dark_icon) # 亮色模式显示太阳 (dark_icon)

    def toggle_theme(self):
        """切换浅色/深色主题并更新按钮图标"""
        current_theme = sv_ttk.get_theme()
        
        # 切换主题
        if current_theme == "dark":
            sv_ttk.set_theme("light")
            self.update_status("已切换到浅色主题")
        else:
            sv_ttk.set_theme("dark")
            self.update_status("已切换到深色主题")
            
        self.update_theme_button_icon() # 更新按钮图标


if __name__ == "__main__":
    root = tk.Tk()
    
    # 设置窗口图标
    icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
    if os.path.exists(icon_path):
        try:
            root.iconbitmap(icon_path)
        except:
            pass
    
    # 设置窗口居中
    window_width = 700
    window_height = 420  # 减小窗口高度以消除底部多余空白
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    # 应用Sun Valley深色主题 (初始设置为暗色)
    sv_ttk.set_theme("light")
    
    app = YTDLPGUI(root)
    
    # 设置初始主题按钮文本
    if sv_ttk.get_theme() == "dark":
        app.theme_button.config(text="☀️")
    else:
        app.theme_button.config(text="🌙")
    
    # 设置焦点到URL输入框
    app.url_entry.focus_set()
    
    root.mainloop()