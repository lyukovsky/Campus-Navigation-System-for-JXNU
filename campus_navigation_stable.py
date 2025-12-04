import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from PIL import Image
import matplotlib.image as mpimg
import os
import pandas as pd


# 项目地址：https://github.com/lyukovsky/Campus-Navigation-System-for-JXNU


class CampusNavigation:
    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("校园导航系统")
        self.root.geometry("1200x800")

        # 设置中文字体
        plt.rcParams["font.family"] = ["SimHei"]
        plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

        # 标记是否正在放置新景点
        self.placing_new_node = False
        self.new_node_name = ""
        self.new_node_intro = ""

        # 背景图片相关设置
        self.background_image = None
        self.background_path = "campus.jpg"
        self.use_background = True
        self.target_width = 1609
        self.target_height = 1287

        # ===== 新增：撤回/重做功能相关 =====
        self.undo_stack = []  # 撤回栈：存储历史状态快照
        self.redo_stack = []  # 重做栈：存储被撤回的状态快照

        # ===== 新增：导入功能相关 =====
        self.imported_node_path = ""  # 记录选中的node.csv路径
        self.imported_edge_path = ""  # 记录选中的edge.csv路径

        # 尝试加载并处理背景图片
        self._load_and_process_background()

        # 创建主界面
        self._create_main_interface()

        # 创建无向图
        self.G = nx.Graph()

        # 校园景点及其坐标
        self.locations = {}
        try:
            df = pd.read_csv("node.csv")
            for index, row in df.iterrows():
                self.locations[row['name']] = (row['x'], row['y'])
        except FileNotFoundError:
            print(f"文件 {'node.csv'} 未找到。")

        # 景点之间的路径及距离
        self.paths = []  # 先初始化为空列表

        try:
            df = pd.read_csv("edge.csv")
            for index, row in df.iterrows():
                # 假设edge.csv有列：start, end, length 或类似的列名
                # 根据实际情况调整列名
                start_node = row['x']
                end_node = row['y']
                length = row['length']
                self.paths.append((start_node, end_node, length))
        except FileNotFoundError:
            print(f"文件 {'edge.csv'} 未找到，使用默认路径数据。")
            # 如果edge.csv不存在，使用默认路径数据（与原来硬编码的数据一致）
            self.paths = [
                ("青蓝门", "望城门", 300),
                ("青蓝门", "洁琼楼", 250),
                ("正大门", "正大坊", 100),
                ("正大门", "校址纪念碑", 150),
                ("望城门", "长胜门", 400),
                ("望城门", "洁琼楼", 200),
                ("长胜门", "惟义楼", 350),
                ("惟义楼", "图书馆", 250),
                ("惟义楼", "静湖", 200),
                ("名达楼", "静湖", 250),
                ("名达楼", "校址纪念碑", 150),
                ("方荫楼", "校址纪念碑", 300),
                ("方荫楼", "鹅湖湾", 250),
                ("先骕楼", "图书馆", 250),
                ("先骕楼", "方荫楼", 350),
                ("先骕楼", "静湖", 300),
                ("正大坊", "青蓝门", 450),
                ("静湖", "校址纪念碑", 200),
                ("鹅湖湾", "先骕楼", 400),
                ("洁琼楼", "名达楼", 300),
                # 推荐路线1新增节点间的路径（假设存在）
                ("图书馆", "静湖", 200),
                ("静湖", "校址纪念碑", 200),
                ("校址纪念碑", "方荫楼", 300),
                ("方荫楼", "音乐艺术广场", 150),
                ("音乐艺术广场", "鹅湖湾", 200),
                ("鹅湖湾", "白鹿会馆", 250),
                ("白鹿会馆", "正大坊", 300),
                # 推荐路线2新增节点间的路径（假设存在）
                ("正大坊", "升旗台", 150),
                ("升旗台", "校址纪念碑", 200),
                ("校址纪念碑", "静湖", 250),
                ("图书馆", "二食堂", 150),
                ("二食堂", "风雨球场", 200),
                ("风雨球场", "长胜门", 250)
            ]
        except Exception as e:
            print(f"读取edge.csv文件时出错: {str(e)}，使用默认路径数据。")
            # 如果读取出现其他错误，也使用默认路径数据
            self.paths = [
                ("青蓝门", "望城门", 300),
                ("青蓝门", "洁琼楼", 250),
                ("正大门", "正大坊", 100),
                ("正大门", "校址纪念碑", 150),
                ("望城门", "长胜门", 400),
                ("望城门", "洁琼楼", 200),
                ("长胜门", "惟义楼", 350),
                ("惟义楼", "图书馆", 250),
                ("惟义楼", "静湖", 200),
                ("名达楼", "静湖", 250),
                ("名达楼", "校址纪念碑", 150),
                ("方荫楼", "校址纪念碑", 300),
                ("方荫楼", "鹅湖湾", 250),
                ("先骕楼", "图书馆", 250),
                ("先骕楼", "方荫楼", 350),
                ("先骕楼", "静湖", 300),
                ("正大坊", "青蓝门", 450),
                ("静湖", "校址纪念碑", 200),
                ("鹅湖湾", "先骕楼", 400),
                ("洁琼楼", "名达楼", 300),
                # 推荐路线1新增节点间的路径（假设存在）
                ("图书馆", "静湖", 200),
                ("静湖", "校址纪念碑", 200),
                ("校址纪念碑", "方荫楼", 300),
                ("方荫楼", "音乐艺术广场", 150),
                ("音乐艺术广场", "鹅湖湾", 200),
                ("鹅湖湾", "白鹿会馆", 250),
                ("白鹿会馆", "正大坊", 300),
                # 推荐路线2新增节点间的路径（假设存在）
                ("正大坊", "升旗台", 150),
                ("升旗台", "校址纪念碑", 200),
                ("校址纪念碑", "静湖", 250),
                ("图书馆", "二食堂", 150),
                ("二食堂", "风雨球场", 200),
                ("风雨球场", "长胜门", 250)
            ]

        # 景点介绍
        self.introductions = {}  # 先初始化为空字典

        try:
            df = pd.read_csv("node.csv")
            for index, row in df.iterrows():
                name = row['name']
                self.locations[name] = (row['x'], row['y'])  # 确保 location 也加载了
                # 尝试从 'introduction' 列获取介绍，如果没有则尝试 'desc'
                if 'introduction' in row:
                    self.introductions[name] = row['introduction']
                elif 'desc' in row:
                    self.introductions[name] = row['desc']
                else:
                    # 如果 csv 里没有介绍列，给一个默认值，避免后续报错
                    self.introductions[name] = "暂无介绍信息"
        except FileNotFoundError:
            print(f"警告：未找到 node.csv 文件，无法加载景点介绍。")
            # 如果 node.csv 不存在，给所有已知景点一个默认介绍
            for name in self.locations.keys():
                self.introductions[name] = "暂无介绍信息（node.csv 未找到）"
            # 为推荐路线中的新节点添加默认介绍
            additional_nodes = ["音乐艺术广场", "白鹿会馆", "升旗台", "校址纪念碑", "二食堂", "风雨球场"]
            for node in additional_nodes:
                if node not in self.introductions:
                    self.introductions[node] = "推荐路线景点，暂无详细介绍"

        # 添加节点和边到图中
        self._initialize_graph()

        # 存储最短路径和选择的点
        self.shortest_path = []
        self.recommended_path = []  # 新增：存储推荐路线
        self.start_node = None
        self.end_node = None
        self.selected_nodes = []
        self.selected_edge = None

        # 首次启动时保存初始状态
        self.save_state()

        # 创建Matplotlib图形
        self.dpi = 100
        self.fig, self.ax = plt.subplots(
            figsize=(self.target_width / self.dpi, self.target_height / self.dpi),
            dpi=self.dpi
        )
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.display_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # 添加工具栏
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.display_frame)
        self.toolbar.update()

        # 添加控制按钮
        self._add_buttons()

        # 绘制初始图形
        self.draw_graph()

        # 连接点击事件
        self.canvas.mpl_connect('button_press_event', self.on_click)

    # ===== 新增：撤回/重做核心方法 =====
    def save_state(self):
        """保存当前地图状态到撤回栈"""
        state = {
            "locations": self.locations.copy(),  # 节点坐标
            "paths": self.paths.copy(),  # 路径信息
            "introductions": self.introductions.copy(),  # 景点介绍
            "G": nx.Graph(self.G)  # 图结构（深拷贝）
        }
        # 限制撤回栈最大长度（避免内存溢出）
        if len(self.undo_stack) > 20:
            self.undo_stack.pop(0)
        self.undo_stack.append(state)
        # 每次保存新状态，清空重做栈（重做仅针对最近撤回的操作）
        self.redo_stack.clear()

    def restore_state(self, state):
        """从快照恢复地图状态"""
        self.locations = state["locations"].copy()
        self.paths = state["paths"].copy()
        self.introductions = state["introductions"].copy()
        self.G = nx.Graph(state["G"])  # 深拷贝恢复图
        # 重置选中状态，重新绘制地图
        self.selected_nodes = []
        self.selected_edge = None
        self.shortest_path = []
        self.recommended_path = []
        self.draw_graph()

    def undo(self):
        """撤回操作"""
        if len(self.undo_stack) <= 1:  # 至少保留初始状态
            messagebox.showinfo("提示", "已无可撤回的操作！")
            return
        # 弹出最后一个状态（当前状态），存入重做栈
        current_state = self.undo_stack.pop()
        self.redo_stack.append(current_state)
        # 恢复到上一个历史状态
        last_state = self.undo_stack[-1]
        self.restore_state(last_state)
        messagebox.showinfo("提示", "已撤回上一步操作")

    def redo(self):
        """重做操作"""
        if not self.redo_stack:
            messagebox.showinfo("提示", "已无可重做的操作！")
            return
        # 弹出重做栈最后一个状态，存入撤回栈
        redo_state = self.redo_stack.pop()
        self.undo_stack.append(redo_state)
        # 恢复到重做状态
        self.restore_state(redo_state)
        messagebox.showinfo("提示", "已重做上一步操作")

    # ===== 新增：保存/导入核心方法 =====
    def save_data(self):
        """保存节点/路径到新CSV文件"""
        try:
            # 1. 保存节点文件 node_new.csv
            node_data = []
            for name, (x, y) in self.locations.items():
                node_data.append({
                    "name": name,
                    "x": x,
                    "y": y,
                    "introduction": self.introductions.get(name, "暂无介绍")
                })
            node_df = pd.DataFrame(node_data)
            node_df.to_csv("node_new.csv", index=False, encoding="utf-8-sig")

            # 2. 保存路径文件 edge_new.csv
            edge_data = []
            for u, v, weight in self.paths:
                edge_data.append({
                    "x": u,  # 保持与原有edge.csv列名一致（start节点）
                    "y": v,  # end节点
                    "length": weight
                })
            edge_df = pd.DataFrame(edge_data)
            edge_df.to_csv("edge_new.csv", index=False, encoding="utf-8-sig")

            messagebox.showinfo("成功", "数据已保存！\n节点文件：node_new.csv\n路径文件：edge_new.csv")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")

    def select_node_file(self):
        """选择节点CSV文件"""
        file_path = filedialog.askopenfilename(
            title="选择节点文件（node.csv）",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        if file_path:
            self.imported_node_path = file_path

    def select_edge_file(self):
        """选择路径CSV文件"""
        file_path = filedialog.askopenfilename(
            title="选择路径文件（edge.csv）",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        if file_path:
            self.imported_edge_path = file_path

    def do_import(self, is_override):
        """执行导入逻辑"""
        if not self.imported_node_path or not self.imported_edge_path:
            messagebox.showwarning("提示", "请先选择节点文件和路径文件！")
            return

        try:
            # 1. 读取导入的节点数据
            import_node_df = pd.read_csv(self.imported_node_path, encoding="utf-8-sig")
            new_locations = {}
            new_introductions = {}
            for _, row in import_node_df.iterrows():
                name = row["name"]
                x = row["x"]
                y = row["y"]
                intro = row.get("introduction", row.get("desc", "暂无介绍"))
                new_locations[name] = (x, y)
                new_introductions[name] = intro

            # 2. 读取导入的路径数据
            import_edge_df = pd.read_csv(self.imported_edge_path, encoding="utf-8-sig")
            new_paths = []
            for _, row in import_edge_df.iterrows():
                u = row["x"]  # 保持与原有列名一致
                v = row["y"]
                length = row["length"]
                new_paths.append((u, v, length))

            # 3. 处理导入逻辑（覆盖/合并）
            if is_override:
                # 覆盖模式：清空原有数据
                self.locations = new_locations
                self.introductions = new_introductions
                self.paths = new_paths
            else:
                # 合并模式：保留原有数据，新增导入数据（去重）
                # 合并节点（新节点覆盖同名旧节点）
                self.locations.update(new_locations)
                self.introductions.update(new_introductions)
                # 合并路径（避免重复边）
                existing_edges = set()
                for u, v, _ in self.paths:
                    # 无向边，统一存储为 (小, 大) 避免重复
                    key = (u, v) if u < v else (v, u)
                    existing_edges.add(key)
                # 添加新路径（去重）
                for u, v, length in new_paths:
                    key = (u, v) if u < v else (v, u)
                    if key not in existing_edges:
                        self.paths.append((u, v, length))
                        existing_edges.add(key)

            # 4. 重新初始化图并刷新
            self.G.clear()
            self._initialize_graph()
            self.reset()
            self.save_state()  # 导入后保存状态（支持撤回）
            messagebox.showinfo("成功", f"导入完成！\n新增节点：{len(new_locations)}个\n新增路径：{len(new_paths)}条")

        except Exception as e:
            messagebox.showerror("错误", f"导入失败：{str(e)}")

    def open_import_window(self):
        """打开导入窗口"""
        # 重置导入路径
        self.imported_node_path = ""
        self.imported_edge_path = ""

        # 创建导入窗口
        import_win = tk.Toplevel(self.root)
        import_win.title("导入数据")
        import_win.geometry("400x300")
        import_win.transient(self.root)
        import_win.grab_set()

        # 节点文件选择
        ttk.Label(import_win, text="节点文件（node.csv）：").pack(anchor=tk.W, padx=20, pady=10)
        node_frame = ttk.Frame(import_win)
        node_frame.pack(fill=tk.X, padx=20, pady=5)
        node_label = ttk.Label(node_frame, text="未选择")
        node_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(node_frame, text="选择文件",
                   command=lambda: [self.select_node_file(),
                                    node_label.config(
                                        text=self.imported_node_path.split("/")[
                                            -1] if self.imported_node_path else "未选择"
                                    )]).pack(side=tk.RIGHT)

        # 路径文件选择
        ttk.Label(import_win, text="路径文件（edge.csv）：").pack(anchor=tk.W, padx=20, pady=10)
        edge_frame = ttk.Frame(import_win)
        edge_frame.pack(fill=tk.X, padx=20, pady=5)
        edge_label = ttk.Label(edge_frame, text="未选择")
        edge_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(edge_frame, text="选择文件",
                   command=lambda: [self.select_edge_file(),
                                    edge_label.config(
                                        text=self.imported_edge_path.split("/")[
                                            -1] if self.imported_edge_path else "未选择"
                                    )]).pack(side=tk.RIGHT)

        # 覆盖性导入选项
        override_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(import_win, text="覆盖性导入（清空原有数据）",
                        variable=override_var).pack(anchor=tk.W, padx=20, pady=20)

        # 确认导入按钮
        ttk.Button(import_win, text="导入",
                   command=lambda: [self.do_import(override_var.get()), import_win.destroy()]).pack(side=tk.RIGHT,
                                                                                                    padx=20, pady=10)
        ttk.Button(import_win, text="取消", command=import_win.destroy).pack(side=tk.RIGHT, padx=10, pady=10)

    def _load_and_process_background(self):
        """加载并处理背景图片"""
        try:
            if not os.path.exists(self.background_path):
                messagebox.showerror("错误",
                                     f"未找到背景图片: {self.background_path}\n请确保图片在程序目录下的campus文件夹中")
                self.use_background = False
                return

            with Image.open(self.background_path) as img:
                resized_img = img.resize((self.target_width, self.target_height), Image.LANCZOS)
                self.background_image = np.array(resized_img)

            messagebox.showinfo("成功", f"背景图片加载成功，已调整为{self.target_width}x{self.target_height}像素")

        except Exception as e:
            messagebox.showerror("错误", f"加载背景图片失败: {str(e)}")
            self.use_background = False

    def _create_main_interface(self):
        """创建主界面布局"""
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.control_frame = ttk.LabelFrame(self.paned_window, text="功能面板")
        self.paned_window.add(self.control_frame, weight=1)

        self.display_frame = ttk.LabelFrame(self.paned_window, text="校园地图")
        self.paned_window.add(self.display_frame, weight=3)

    def _initialize_graph(self):
        """初始化图形数据"""
        for node, pos in self.locations.items():
            self.G.add_node(node, pos=pos)

        # 为推荐路线中的新节点添加默认位置（如果不存在）
        default_positions = {
            "音乐艺术广场": (800, 500),
            "白鹿会馆": (900, 600),
            "升旗台": (400, 300),
            "校址纪念碑": (500, 400),
            "二食堂": (700, 600),
            "风雨球场": (800, 700)
        }
        for node, pos in default_positions.items():
            if node not in self.locations:
                self.locations[node] = pos
                self.G.add_node(node, pos=pos)

        for u, v, weight in self.paths:
            self.G.add_edge(u, v, weight=weight)

    def _add_buttons(self):
        """添加功能按钮"""
        # 导航功能区
        nav_frame = ttk.LabelFrame(self.control_frame, text="导航功能")
        nav_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(nav_frame, text="计算最短路径", command=self.calculate_shortest_path).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(nav_frame, text="重置选择", command=self.reset).pack(fill=tk.X, padx=5, pady=2)

        # ===== 新增：撤回/重做按钮 =====
        undo_redo_frame = ttk.Frame(nav_frame)
        undo_redo_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(undo_redo_frame, text="撤回", command=self.undo).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(undo_redo_frame, text="重做", command=self.redo).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        # ===== 新增：保存/导入按钮 =====
        save_import_frame = ttk.Frame(nav_frame)
        save_import_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(save_import_frame, text="保存数据", command=self.save_data).pack(side=tk.LEFT, fill=tk.X,
                                                                                    expand=True, padx=2)
        ttk.Button(save_import_frame, text="导入数据", command=self.open_import_window).pack(side=tk.RIGHT, fill=tk.X,
                                                                                             expand=True, padx=2)

        # 景点管理区
        node_frame = ttk.LabelFrame(self.control_frame, text="景点管理")
        node_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(node_frame, text="新增景点", command=self.prepare_add_node).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(node_frame, text="修改景点信息", command=self.edit_node).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(node_frame, text="删除景点", command=self.delete_node).pack(fill=tk.X, padx=5, pady=2)

        # 路径管理区
        edge_frame = ttk.LabelFrame(self.control_frame, text="路径管理")
        edge_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(edge_frame, text="新增路径", command=self.add_edge).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(edge_frame, text="修改路径信息", command=self.edit_edge).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(edge_frame, text="删除路径", command=self.delete_edge).pack(fill=tk.X, padx=5, pady=2)

        # 推荐路线区 - 新增
        self.recommend_frame = ttk.LabelFrame(self.control_frame, text="推荐路线")
        self.recommend_frame.pack(fill=tk.X, padx=5, pady=5)

        # 推荐路线按钮和扩展框
        self.recommend_expanded = False
        self.recommend_details = ttk.Frame(self.recommend_frame)

        def toggle_recommend():
            self.recommend_expanded = not self.recommend_expanded
            if self.recommend_expanded:
                self.recommend_details.pack(fill=tk.X, padx=5, pady=5)
            else:
                self.recommend_details.pack_forget()

        ttk.Button(self.recommend_frame, text="推荐路线", command=toggle_recommend).pack(fill=tk.X, padx=5, pady=2)

        # 推荐路线1和路线2按钮
        ttk.Button(self.recommend_details, text="路线1", command=lambda: self.show_recommended_route(1)).pack(fill=tk.X,
                                                                                                              padx=5,
                                                                                                              pady=2)
        ttk.Button(self.recommend_details, text="路线2", command=lambda: self.show_recommended_route(2)).pack(fill=tk.X,
                                                                                                              padx=5,
                                                                                                              pady=2)

        # 信息显示区
        info_frame = ttk.LabelFrame(self.control_frame, text="信息")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.info_text = tk.Text(info_frame, height=8, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.info_text.insert(tk.END,
                              "操作说明:\n- 单击节点选择起点(浅绿色)和终点(浅橙色)\n- 双击节点查看介绍\n- 选择两个节点可创建路径\n- 新增景点后在地图上点击放置位置\n- 项目地址：https://github.com/lyukovsky/Campus-Navigation-System-for-JXNU")
        self.info_text.config(state=tk.DISABLED)

    def draw_graph(self):
        self.ax.clear()

        # 绘制背景图片（如有）
        if self.use_background and self.background_image is not None:
            self.ax.imshow(
                self.background_image,
                extent=[0, self.target_width, self.target_height, 0],
                aspect='auto',
                alpha=0.9
            )

        pos = nx.get_node_attributes(self.G, 'pos')

        # 绘制所有边（灰色）
        nx.draw_networkx_edges(self.G, pos, ax=self.ax, edge_color='#666666', width=1.5, alpha=0.6)

        # 高亮选中的边
        if self.selected_edge:
            nx.draw_networkx_edges(self.G, pos, edgelist=[self.selected_edge], ax=self.ax,
                                   edge_color='#9370DB', width=3, alpha=0.8)

        # 高亮最短路径的边（橙色）
        if self.shortest_path:
            path_edges = list(zip(self.shortest_path[:-1], self.shortest_path[1:]))
            nx.draw_networkx_edges(self.G, pos, edgelist=path_edges, ax=self.ax,
                                   edge_color='#FF4500', width=2.5, alpha=0.9)

        # 高亮推荐路线的边（紫色）
        if self.recommended_path:
            path_edges = list(zip(self.recommended_path[:-1], self.recommended_path[1:]))
            nx.draw_networkx_edges(self.G, pos, edgelist=path_edges, ax=self.ax,
                                   edge_color='#FF4500', width=3, alpha=0.9)

        # 绘制普通节点（浅色）
        all_nodes = set(self.locations.keys())
        unselected_nodes = all_nodes - set(self.selected_nodes)

        nx.draw_networkx_nodes(self.G, pos, nodelist=list(unselected_nodes),
                               ax=self.ax, node_size=300, node_color='#E0F7FA',
                               edgecolors='#26A69A', linewidths=1, alpha=0.6)

        # 起点（浅绿色）、终点（浅橙色）节点
        if self.selected_nodes:
            nx.draw_networkx_nodes(self.G, pos, nodelist=[self.selected_nodes[0]],
                                   ax=self.ax, node_size=400, node_color='#E8F5E9',
                                   edgecolors='#43A047', linewidths=1.2, alpha=0.7)
            if len(self.selected_nodes) > 1:
                nx.draw_networkx_nodes(self.G, pos, nodelist=[self.selected_nodes[1]],
                                       ax=self.ax, node_size=400, node_color='#FFF3E0',
                                       edgecolors='#FB8C00', linewidths=1.2, alpha=0.7)

        # 绘制节点标签
        nx.draw_networkx_labels(self.G, pos, ax=self.ax, font_size=9,
                                font_family="SimHei", font_weight='bold',
                                bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=1.5))

        # 显示最短路径权重
        if self.shortest_path:
            path_edges = list(zip(self.shortest_path[:-1], self.shortest_path[1:]))
            path_edge_labels = {}
            for u, v in path_edges:
                weight = self.G.edges[u, v].get('weight', 'N/A')
                path_edge_labels[(u, v)] = f"{weight}m"

            if path_edge_labels:
                nx.draw_networkx_edge_labels(
                    self.G, pos, edge_labels=path_edge_labels,
                    ax=self.ax, font_size=8, font_family="SimHei",
                    bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=1)
                )

        # 显示推荐路线权重
        if self.recommended_path:
            path_edges = list(zip(self.recommended_path[:-1], self.recommended_path[1:]))
            path_edge_labels = {}
            for u, v in path_edges:
                weight = self.G.edges[u, v].get('weight', 'N/A')
                path_edge_labels[(u, v)] = f"{weight}m"

            if path_edge_labels:
                nx.draw_networkx_edge_labels(
                    self.G, pos, edge_labels=path_edge_labels,
                    ax=self.ax, font_size=8, font_family="SimHei",
                    bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=1)
                )

        # 设置坐标轴等
        self.ax.set_xlim(0, self.target_width)
        self.ax.set_ylim(self.target_height, 0)
        self.ax.set_title("校园导航系统" if not self.placing_new_node else f"请在地图上点击放置: {self.new_node_name}",
                          fontsize=14, fontweight='bold', pad=10)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.tick_params(axis='both', which='major', labelsize=9)

        self.canvas.draw()

    def _place_new_node(self, x, y):
        """在指定像素坐标放置新景点"""
        self.locations[self.new_node_name] = (x, y)
        self.introductions[self.new_node_name] = self.new_node_intro
        self.G.add_node(self.new_node_name, pos=(x, y))

        self.placing_new_node = False
        self.selected_nodes = [self.new_node_name]
        self.draw_graph()
        self.save_state()  # 新增：保存状态
        messagebox.showinfo("成功", f"已新增景点: {self.new_node_name} (坐标: {int(x)}, {int(y)})")

    def calculate_shortest_path(self):
        if len(self.selected_nodes) < 2:
            self.show_message("提示", "请先选择起点和终点!")
            return

        self.start_node = self.selected_nodes[0]
        self.end_node = self.selected_nodes[1]

        if self.start_node == self.end_node:
            self.show_message("提示", "起点和终点不能相同!")
            return

        try:
            self.shortest_path = nx.dijkstra_path(self.G, self.start_node, self.end_node, weight='weight')
            path_length = nx.dijkstra_path_length(self.G, self.start_node, self.end_node, weight='weight')
            self.recommended_path = []  # 清除推荐路线
            self.draw_graph()
            path_str = " -> ".join(self.shortest_path)
            self.show_message("最短路径结果",
                              f"从 {self.start_node} 到 {self.end_node}\n路径: {path_str}\n总距离: {path_length}米")
        except nx.NetworkXNoPath:
            self.show_message("提示", f"从 {self.start_node} 到 {self.end_node} 没有可用路径!")

    # 新增：显示推荐路线
    def show_recommended_route(self, route_num):
        # 定义推荐路线
        if route_num == 1:
            route = ["青蓝门", "实验大楼", "名达楼", "惟义楼", "图书馆", "静湖", "校址纪念碑",
                     "方荫楼", "音乐艺术广场", "鹅湖湾", "白鹿会馆", "正大坊", "青蓝门"]
            route_name = "推荐路线1"
        else:
            route = ["正大门", "正大坊", "升旗台", "校址纪念碑", "静湖",
                     "图书馆", "二食堂", "风雨球场", "长胜门"]
            route_name = "推荐路线2"

        # 计算路线总长度
        total_length = 0
        valid_route = True
        for i in range(len(route) - 1):
            u = route[i]
            v = route[i + 1]
            if not self.G.has_edge(u, v):
                valid_route = False
                messagebox.showerror("错误", f"路线中不存在 {u} 到 {v} 的路径")
                break
            total_length += self.G.edges[u, v]['weight']

        if valid_route:
            self.recommended_path = route
            self.shortest_path = []  # 清除最短路径
            self.selected_nodes = []  # 清除选中节点
            self.draw_graph()
            path_str = " -> ".join(route)
            self.show_message(route_name, f"推荐路线:\n{path_str}\n总距离: {total_length}米")

    def reset(self):
        self.selected_nodes = []
        self.selected_edge = None
        self.shortest_path = []
        self.recommended_path = []  # 重置推荐路线
        self.placing_new_node = False
        self.draw_graph()

    def show_message(self, title, message):
        msg_window = tk.Toplevel(self.root)
        msg_window.title(title)
        msg_window.geometry("300x200")
        msg_window.transient(self.root)
        msg_window.grab_set()

        msg_window.update_idletasks()
        width = msg_window.winfo_width()
        height = msg_window.winfo_height()
        x = (self.root.winfo_width() // 2) - (width // 2) + self.root.winfo_x()
        y = (self.root.winfo_height() // 2) - (height // 2) + self.root.winfo_y()
        msg_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        ttk.Label(msg_window, text=message, wraplength=250, padding=20).pack(expand=True)
        ttk.Button(msg_window, text="确定", command=msg_window.destroy).pack(pady=10)

    def on_click(self, event):
        if event.inaxes != self.ax:
            return

        # 如果正在放置新节点
        if self.placing_new_node:
            self._place_new_node(event.xdata, event.ydata)
            return

        pos = nx.get_node_attributes(self.G, 'pos')
        clicked_node = None

        # 处理节点点击
        for node, (x, y) in pos.items():
            if np.sqrt((x - event.xdata) ** 2 + (y - event.ydata) ** 2) < 15:
                clicked_node = node
                break

        if clicked_node:
            # 节点点击逻辑（保持不变）
            if event.dblclick:  # 双击节点：显示介绍
                self.show_message(clicked_node, self.introductions.get(clicked_node, "无介绍信息"))
            else:  # 单击节点：选为起点或终点
                if clicked_node in self.selected_nodes:
                    self.selected_nodes.remove(clicked_node)
                else:
                    if len(self.selected_nodes) < 2:
                        self.selected_nodes.append(clicked_node)
                    else:
                        self.selected_nodes.pop()
                        self.selected_nodes.append(clicked_node)
            self.draw_graph()
            return  # 节点点击优先，避免同时触发边

        else:
            # ===== 核心修改：补充单击选中边的逻辑 =====
            if event.dblclick:
                # 双击边：查看边信息
                self._handle_double_click_on_edge(event)
            else:
                # 单击边：选中该边（新增）
                self._select_edge(event)  # 调用边选中方法
                # 若未选中任何边，清空选中边状态
                if not self.selected_edge:
                    self.selected_edge = None
                self.draw_graph()

    def _handle_double_click_on_edge(self, event):
        pos = nx.get_node_attributes(self.G, 'pos')
        min_dist = float('inf')
        selected_edge = None
        edge_u = edge_v = None

        # 遍历所有边，判断鼠标位置是否双击在边上
        for u, v, d in self.G.edges(data=True):
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            dist = self._point_to_line_distance(event.xdata, event.ydata, x1, y1, x2, y2)
            if dist < 10:  # 双击检测范围，可调整
                if dist < min_dist:
                    min_dist = dist
                    selected_edge = (u, v)
                    edge_u, edge_v = u, v

        if selected_edge:
            u, v = selected_edge
            weight = self.G.edges[u, v].get('weight', '未知')
            self.show_message(f"边信息：{u} — {v}",
                              f"{u} 到 {v}\n长度: {weight}米")

    def _select_edge(self, event):
        pos = nx.get_node_attributes(self.G, 'pos')
        min_dist = float('inf')
        selected = None

        for u, v in self.G.edges():
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            dist = self._point_to_line_distance(event.xdata, event.ydata, x1, y1, x2, y2)
            # 调整检测范围：8→10，更容易选中边
            if dist < 10 and dist < min_dist:
                min_dist = dist
                selected = (u, v)

        if selected:
            self.selected_nodes = []  # 选中边时清空节点选中状态
            self.selected_edge = selected
        else:
            self.selected_edge = None  # 未选中边则清空

    def _point_to_line_distance(self, x, y, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1

        if dx == 0 and dy == 0:
            return np.hypot(x - x1, y - y1)

        t = ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)
        t = max(0, min(1, t))

        proj_x = x1 + t * dx
        proj_y = y1 + t * dy

        return np.hypot(x - proj_x, y - proj_y)

    def prepare_add_node(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("新增景点")
        dialog.geometry("300x300")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="景点名称:").pack(anchor=tk.W, padx=10, pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(dialog, text="景点介绍:").pack(anchor=tk.W, padx=10, pady=5)
        intro_text = tk.Text(dialog, height=6, wrap=tk.WORD)
        intro_text.pack(fill=tk.X, padx=10, pady=5)

        def confirm_info():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("错误", "景点名称不能为空")
                return

            if name in self.locations:
                messagebox.showerror("错误", "该景点已存在")
                return

            self.new_node_name = name
            self.new_node_intro = intro_text.get("1.0", tk.END).strip()
            self.placing_new_node = True
            dialog.destroy()
            self.draw_graph()

        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="下一步", command=confirm_info).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)

    def edit_node(self):
        if not self.selected_nodes or len(self.selected_nodes) != 1:
            self.show_message("提示", "请先选择一个景点")
            return

        node = self.selected_nodes[0]
        current_pos = self.locations[node]
        current_intro = self.introductions.get(node, "")

        dialog = tk.Toplevel(self.root)
        dialog.title(f"修改景点: {node}")
        dialog.geometry("300x300")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="景点名称:").pack(anchor=tk.W, padx=10, pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.pack(fill=tk.X, padx=10, pady=5)
        name_entry.insert(0, node)

        ttk.Label(dialog, text="当前坐标:").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Label(dialog, text=f"X: {int(current_pos[0])}, Y: {int(current_pos[1])}").pack(anchor=tk.W, padx=10)
        ttk.Label(dialog, text="(点击地图可直接调整位置)").pack(anchor=tk.W, padx=10, pady=5)

        ttk.Label(dialog, text="景点介绍:").pack(anchor=tk.W, padx=10, pady=5)
        intro_text = tk.Text(dialog, height=4, wrap=tk.WORD)
        intro_text.pack(fill=tk.X, padx=10, pady=5)
        intro_text.insert("1.0", current_intro)

        def update_node():
            new_name = name_entry.get().strip()
            if not new_name:
                messagebox.showerror("错误", "景点名称不能为空")
                return

            if new_name != node and new_name in self.locations:
                messagebox.showerror("错误", "该景点名称已存在")
                return

            if new_name != node:
                self.locations[new_name] = self.locations.pop(node)
                self.introductions[new_name] = self.introductions.pop(node)
                self.G = nx.relabel_nodes(self.G, {node: new_name})
                self.selected_nodes = [new_name]

            self.introductions[new_name] = intro_text.get("1.0", tk.END).strip()
            self.draw_graph()
            self.save_state()  # 新增：保存状态
            dialog.destroy()
            messagebox.showinfo("成功", f"已更新景点: {new_name}")

        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="保存", command=update_node).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)

    def delete_node(self):
        if not self.selected_nodes or len(self.selected_nodes) != 1:
            self.show_message("提示", "请先选择一个景点")
            return

        node = self.selected_nodes[0]

        if not messagebox.askyesno("确认", f"确定要删除景点 '{node}' 吗?\n相关路径也将被删除"):
            return

        del self.locations[node]
        if node in self.introductions:
            del self.introductions[node]

        self.G.remove_node(node)
        self.reset()
        self.save_state()  # 新增：保存状态
        messagebox.showinfo("成功", f"已删除景点: {node}")

    def add_edge(self):
        if len(self.selected_nodes) != 2:
            self.show_message("提示", "请先选择两个景点来创建路径")
            return

        u, v = self.selected_nodes

        if self.G.has_edge(u, v):
            self.show_message("提示", f"{u} 和 {v} 之间已存在路径")
            return

        try:
            distance = simpledialog.askfloat("路径长度", f"请输入{u}到{v}的距离(米):",
                                             minvalue=1, parent=self.root)
            if distance is None:
                return
        except ValueError:
            self.show_message("错误", "请输入有效的数字")
            return

        self.paths.append((u, v, distance))
        self.G.add_edge(u, v, weight=distance)
        self.draw_graph()
        self.save_state()  # 新增：保存状态
        self.show_message("成功", f"已添加{u}到{v}的路径，长度: {distance}米")

    def edit_edge(self):
        if not self.selected_edge:
            self.show_message("提示", "请先选择一条路径")
            return

        u, v = self.selected_edge
        current_weight = self.G.edges[u, v]['weight']

        try:
            new_distance = simpledialog.askfloat("修改路径长度",
                                                 f"请输入{u}到{v}的新距离(米):",
                                                 minvalue=1,
                                                 initialvalue=current_weight,
                                                 parent=self.root)
            if new_distance is None:
                return
        except ValueError:
            self.show_message("错误", "请输入有效的数字")
            return

        self.G.edges[u, v]['weight'] = new_distance

        for i, (a, b, w) in enumerate(self.paths):
            if (a == u and b == v) or (a == v and b == u):
                self.paths[i] = (u, v, new_distance)
                break

        self.draw_graph()
        self.save_state()  # 新增：保存状态
        self.show_message("成功", f"已更新{u}到{v}的路径长度为: {new_distance}米")

    def delete_edge(self):
        if not self.selected_edge:
            self.show_message("提示", "请先选择一条路径")
            return

        u, v = self.selected_edge

        if not messagebox.askyesno("确认", f"确定要删除{u}到{v}的路径吗?"):
            return

        self.G.remove_edge(u, v)

        for i, (a, b, w) in enumerate(self.paths):
            if (a == u and b == v) or (a == v and b == u):
                del self.paths[i]
                break

        self.reset()
        self.save_state()  # 新增：保存状态
        self.show_message("成功", f"已删除{u}到{v}的路径")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = CampusNavigation()
    app.run()
