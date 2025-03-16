import tkinter as tk
from tkinter import messagebox
import random
from PIL import Image, ImageTk
from pygame import mixer
import os
import sys

class ChengYuGame:
    def __init__(self):
        self.current_level = 1
        self.score = 0
        self.grid_size = 6
        self.cells = {}
        self.selected_words = []
        self.selected_positions = []
        self.target_chengyu = []
        self.chengyu_database = []
        
        # 获取资源文件路径
        if getattr(sys, 'frozen', False):
            # 如果是打包后的可执行文件
            self.base_path = sys._MEIPASS
        else:
            # 如果是开发环境
            self.base_path = os.path.dirname(os.path.abspath(__file__))
        
        # 初始化音乐播放器
        mixer.init()
        self.music_files = ['Legends Never Die.mp3', '孤勇者.mp3', '天空之城.mp3'] # 音乐文件列表,不喜欢下载好MP3，改名字
        self.current_music_index = 0
        self.is_playing = False
        self.play_music()

        self.window = tk.Tk()
        self.window.title("成语填字游戏")
        self.window.geometry("600x700")
        self.window.configure(bg='#F5F5F5')
        
        bg_image = Image.open(os.path.join(self.base_path, 'OIG.jpg'))
        bg_image = bg_image.resize((600, 750), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(bg_image)
        
        bg_label = tk.Label(self.window, image=self.bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.init_ui()
        self.load_chengyu_database()
        self.start_game()
        self.window.mainloop()

    def init_ui(self):
        self.info_frame = tk.Frame(self.window, padx=10, pady=5)
        self.info_frame.pack(pady=15)

        self.level_label = tk.Label(self.info_frame, text=f"关卡 {self.current_level}", 
                                   font=("华文楷体", 24, "bold"), fg="#FF5722")
        self.level_label.pack(side=tk.LEFT, padx=20)
        
        self.score_label = tk.Label(self.info_frame, text=f"得分 {self.score}", 
                                   font=("华文楷体", 24, "bold"), fg="#FF5722")
        self.score_label.pack(side=tk.LEFT, padx=20)
        
        game_frame = tk.Frame(self.window, padx=10, pady=10)
        game_frame.pack(pady=20)
        
        self.canvas = tk.Canvas(game_frame, width=400, height=400, 
                               bg='#FFFFFF', highlightthickness=2,
                               highlightbackground='#2196F3')
        self.canvas.configure(bd=0)
        self.canvas.pack()
        
        self.selected_frame = tk.Frame(self.window, padx=10, pady=10, bg='#F5F5F5')
        self.selected_frame.pack(pady=10)
        self.selected_label = tk.Label(self.selected_frame, 
                                       text="已选：", 
                                       font=("华文楷体", 20, "bold"),
                                       fg="#2196F3",
                                       bg='#F5F5F5')
        self.selected_label.pack(side=tk.LEFT, padx=(0, 15))
        
        self.char_frames = []
        for i in range(4):
            frame = tk.Label(self.selected_frame, 
                           width=2, height=1,
                           relief='solid',
                           font=("华文楷体", 20, "bold"),
                           bg='#FFFFFF',
                           highlightthickness=1,
                           highlightbackground='#2196F3')
            frame.pack(side=tk.LEFT, padx=8)
            self.char_frames.append(frame)
            
        self.restart_button = tk.Button(self.selected_frame,
                                      text="重新开始",
                                      font=("华文楷体", 16, "bold"),
                                      fg="#FFFFFF",
                                      bg="#2196F3",
                                      command=self.restart_game,
                                      padx=10)
        self.restart_button.pack(side=tk.LEFT, padx=20)
        
        # 添加音乐控制按钮
        self.music_frame = tk.Frame(self.window, padx=10, pady=5, bg='#F5F5F5')
        self.music_frame.pack(pady=5)
        
        self.play_button = tk.Button(self.music_frame,
                                    text="播放/暂停",
                                    font=("华文楷体", 12, "bold"),
                                    fg="#FFFFFF",
                                    bg="#2196F3",
                                    command=self.toggle_music,
                                    padx=10)
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        self.next_button = tk.Button(self.music_frame,
                                    text="下一首",
                                    font=("华文楷体", 12, "bold"),
                                    fg="#FFFFFF",
                                    bg="#2196F3",
                                    command=self.next_music,
                                    padx=10)
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        # 添加目标成语列表框架
        self.target_frame = tk.Frame(self.window, padx=10, pady=5, bg='#F5F5F5')
        self.target_frame.pack(pady=10)
        self.target_label = tk.Label(self.target_frame, 
                                    text="目标成语：", 
                                    font=("华文楷体", 18, "bold"),
                                    fg="#2196F3",
                                    bg='#F5F5F5')
        self.target_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.target_display = tk.Label(self.target_frame, 
                                      text="", 
                                      font=("华文楷体", 16),
                                      fg="#333333",
                                      bg='#F5F5F5',
                                      wraplength=400,
                                      justify=tk.LEFT)
        self.target_display.pack(side=tk.LEFT)
        
        self.create_grid()

    def create_grid(self):
        cell_size = 60
        start_x, start_y = 20, 20
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x1, y1 = start_x + j * cell_size, start_y + i * cell_size
                x2, y2 = x1 + cell_size - 8, y1 + cell_size - 8
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, 
                                                  fill='#FFFFFF', outline='#2196F3', width=1)
                text = self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, 
                                              text='', font=("华文楷体", 20, "bold"), fill='#1E90FF')
                self.cells[(i, j)] = {'rect': rect, 'text': text, 'value': ''}
                self.canvas.tag_bind(rect, '<Button-1>', 
                                    lambda e, r=i, c=j: self.on_click_cell(r, c))
                self.canvas.tag_bind(text, '<Button-1>', 
                                    lambda e, r=i, c=j: self.on_click_cell(r, c))

    def load_chengyu_database(self):
        try:
            file_path = os.path.join(self.base_path, '成语库.txt')
            with open(file_path, 'r', encoding='utf-8') as f:
                self.chengyu_database = [line.strip() for line in f if len(line.strip()) == 4]
            if not self.chengyu_database:
                raise ValueError("成语数据库为空")
            random.shuffle(self.chengyu_database)
        except Exception as e:
            print(f"加载成语数据库出错: {e}，使用默认成语列表")
            self.chengyu_database = [
                "一举两得", "两全其美", "三心二意", "四面八方",
                "一帆风顺", "万无一失", "天长地久", "和气生财",
                "五湖四海", "千变万化", "心平气和", "守株待兔",
                "画蛇添足", "掩耳盗铃", "对牛弹琴", "滥竽充数"
            ]

    def start_game(self):
        if self.current_level > 6:
            messagebox.showinfo("恭喜", "恭喜你通关了！")
            self.current_level = 1
            self.score = 0
            self.level_label.config(text=f"关卡 {self.current_level}")
            self.score_label.config(text=f"得分 {self.score}")

        self.selected_words.clear()
        self.selected_positions.clear()
        self.update_selected_display()
        
        # 停止之前的计时器（如果有）
        if hasattr(self, 'timer_running') and self.timer_running:
            self.window.after_cancel(self.timer_running)
            self.timer_running = None
            
        # 移除现有的计时器标签（如果有）
        if hasattr(self, 'timer_label') and self.timer_label.winfo_exists():
            self.timer_label.destroy()
        
        # 根据关卡设置倒计时时间：第1关3分钟，之后每关增加1分钟
        self.time_remaining = (180 + (self.current_level - 1) * 60)  # 第1关3分钟，第2关4分钟，以此类推
        self.timer_label = tk.Label(self.info_frame, text=f"剩余时间: {self.time_remaining//60}:00", 
                                   font=("华文楷体", 24, "bold"), fg="#FF5722")
        self.timer_label.pack(side=tk.LEFT, padx=20)
        
        # 启动新的计时器
        self.start_timer()
        
        # 根据游戏说明调整关卡难度：每关成语数 = 2 + 当前关卡数（最多8个）
        chengyu_count = min(self.current_level + 2, 8)
        self.target_chengyu = random.sample(self.chengyu_database, chengyu_count)
        
        # 更新目标成语显示
        self.update_target_display()
        
        available_positions = [(i, j) for i in range(self.grid_size) 
                             for j in range(self.grid_size)]
        random.shuffle(available_positions)
        
        for pos in self.cells:
            self.cells[pos]['value'] = ''
            self.canvas.itemconfig(self.cells[pos]['text'], text='')
            self.canvas.itemconfig(self.cells[pos]['rect'], fill='white')
        
        for chengyu in self.target_chengyu:
            for char in chengyu:
                if available_positions:
                    row, col = available_positions.pop()
                    self.cells[(row, col)]['value'] = char
                    self.canvas.itemconfig(self.cells[(row, col)]['text'], 
                                         text=char, fill='#1E90FF')

    def update_target_display(self):
        # 更新目标成语显示，只显示每个成语的第一个字
        target_text = "、".join([chengyu[0] for chengyu in self.target_chengyu])
        self.target_display.config(text=target_text)

    def update_selected_display(self):
        for i in range(4):
            if i < len(self.selected_words):
                self.char_frames[i].config(text=self.selected_words[i], bg='#90CAF9')
            else:
                self.char_frames[i].config(text='', bg='white')

    def on_click_cell(self, row, col):
        cell = self.cells.get((row, col))
        if not cell or not cell['value']:
            return

        if (row, col) in self.selected_positions:
            # 取消选择
            idx = self.selected_positions.index((row, col))
            self.selected_positions.pop(idx)
            self.selected_words.pop(idx)
            self.canvas.itemconfig(cell['rect'], fill='white')
            self.canvas.itemconfig(cell['text'], fill='#1E90FF')  # 保持文字颜色一致
        else:
            # 新选择
            if len(self.selected_words) < 4:
                self.selected_words.append(cell['value'])
                self.selected_positions.append((row, col))
                self.canvas.itemconfig(cell['rect'], fill='#90CAF9')
                self.canvas.itemconfig(cell['text'], fill='#1E90FF')  # 保持文字颜色一致

        self.update_selected_display()
        if len(self.selected_words) == 4:
            self.check_chengyu()

    def check_chengyu(self):
        selected_chengyu = ''.join(self.selected_words)
        if selected_chengyu in self.target_chengyu:
            self.score += 10
            self.score_label.config(text=f"得分 {self.score}")
            
            # 清除已匹配成语的格子
            for row, col in self.selected_positions:
                self.canvas.itemconfig(self.cells[(row, col)]['rect'], fill='white')
                self.canvas.itemconfig(self.cells[(row, col)]['text'], text='')
                self.cells[(row, col)]['value'] = ''
            
            # 清空已选择的字符
            self.selected_words.clear()
            self.selected_positions.clear()
            self.update_selected_display()
                
            # 从目标成语列表中移除
            self.target_chengyu.remove(selected_chengyu)
            self.update_target_display()
            
            # 检查是否完成所有成语
            if not self.target_chengyu:
                self.current_level += 1
                self.level_label.config(text=f"关卡 {self.current_level}")
                if self.current_level <= 6:
                    messagebox.showinfo("恭喜", f"完成第{self.current_level - 1}关！")
                self.start_game()
        else:
            messagebox.showinfo("提示", "选择的成语不正确，请重试！")
            
            # 重置选择状态和颜色
            for row, col in self.selected_positions:
                self.canvas.itemconfig(self.cells[(row, col)]['rect'], fill='white')
                self.canvas.itemconfig(self.cells[(row, col)]['text'], fill='#1E90FF')
            
            self.selected_words.clear()
            self.selected_positions.clear()
            self.update_selected_display()

    def restart_game(self):
        # 停止当前计时器
        if self.timer_running:
            self.window.after_cancel(self.timer_running)
            self.timer_running = None
            
        # 移除现有的计时器标签
        if hasattr(self, 'timer_label') and self.timer_label.winfo_exists():
            self.timer_label.destroy()
            
        self.current_level = 1
        self.score = 0
        self.level_label.config(text=f"关卡 {self.current_level}")
        self.score_label.config(text=f"得分 {self.score}")
        self.start_game()

    def play_music(self):
        try:
            music_path = os.path.join(self.base_path, self.music_files[self.current_music_index])
            mixer.music.load(music_path)
            mixer.music.play()
            self.is_playing = True
        except Exception as e:
            print(f"音乐播放错误: {e}")
    
    def toggle_music(self):
        if self.is_playing:
            mixer.music.pause()
            self.is_playing = False
        else:
            mixer.music.unpause()
            self.is_playing = True
    
    def next_music(self):
        self.current_music_index = (self.current_music_index + 1) % len(self.music_files)
        self.play_music()

    def update_timer_display(self):
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        self.timer_label.config(text=f"剩余时间: {minutes}:{seconds:02d}")

    def start_timer(self):
        if self.time_remaining > 0:
            self.update_timer_display()
            self.time_remaining -= 1
            self.timer_running = self.window.after(1000, self.start_timer)
        else:
            messagebox.showinfo("提示", "时间到！游戏结束")
            self.restart_game()

if __name__ == "__main__":
    ChengYuGame()
