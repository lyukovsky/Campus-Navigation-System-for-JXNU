import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from PIL import Image
import matplotlib.image as mpimg
import os
import pandas as pd


class CampusNavigation:
    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("校园导航系统")
        self.root.geometry("1200x800")

        # 设置中文字体
        plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
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
            print(f"文件 {"node.csv"} 未找到。")

        # 景点之间的路径及距离
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
            ("洁琼楼", "名达楼", 300)
        ]

        # 景点介绍
        self.introductions = {
            "青蓝门": "校园主要入口之一，连接校内与外部主干道，交通便利。",
            "正大门": "学校正门，气势恢宏，是学校的标志性入口。",
            "望城门": "位于校园西侧，靠近教学区，方便学生进出。",
            "长胜门": "靠近运动区的侧门，周边有多个体育场馆。",
            "惟义楼": "主要教学楼之一，设有多个多媒体教室和实验室。",
            "名达楼": "综合性教学楼，以文科类教学为主。",
            "方荫楼": "理工科教学与实验楼，配备先进的实验设备。",
            "先骕楼": "科研大楼，多个重点实验室所在地。",
            "图书馆": "学校文献信息中心，藏书丰富，学习氛围浓厚。",
            "静湖": "校园内的人工湖，风景优美，是休闲散步的好去处。",
            "校址纪念碑": "纪念学校建校地址的标志性建筑。",
            "正大坊": "校内标志性牌坊，具有深厚的文化底蕴。",
            "洁琼楼": "女生宿舍楼，环境整洁，设施完善。",
            "鹅湖湾": "校园内的自然景观区，生态环境良好。"
        }

        # 添加节点和边到图中
        self._initialize_graph()

        # 存储最短路径和选择的点
        self.shortest_path = []
        self.start_node = None
        self.end_node = None
        self.selected_nodes = []
        self.selected_edge = None

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

        for u, v, weight in self.paths:
            self.G.add_edge(u, v, weight=weight)

    def _add_buttons(self):
        """添加功能按钮"""
        # 导航功能区
        nav_frame = ttk.LabelFrame(self.control_frame, text="导航功能")
        nav_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(nav_frame, text="计算最短路径", command=self.calculate_shortest_path).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(nav_frame, text="重置选择", command=self.reset).pack(fill=tk.X, padx=5, pady=2)

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

        # 信息显示区
        info_frame = ttk.LabelFrame(self.control_frame, text="信息")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.info_text = tk.Text(info_frame, height=8, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.info_text.insert(tk.END,
                              "操作说明:\n- 单击节点选择起点(浅绿色)和终点(浅橙色)\n- 双击节点查看介绍\n- 选择两个节点可创建路径\n- 新增景点后在地图上点击放置位置")
        self.info_text.config(state=tk.DISABLED)

    def draw_graph(self):
        """绘制校园地图，使用浅色、透明、较小的节点"""
        self.ax.clear()

        # 绘制背景图片
        if self.use_background and self.background_image is not None:
            self.ax.imshow(
                self.background_image,
                extent=[0, self.target_width, self.target_height, 0],
                aspect='auto',
                alpha=0.9
            )

        # 获取节点位置
        pos = nx.get_node_attributes(self.G, 'pos')

        # 绘制所有边
        nx.draw_networkx_edges(self.G, pos, ax=self.ax, edge_color='#666666', width=1.5, alpha=0.6)

        # 高亮显示选中的边
        if self.selected_edge:
            nx.draw_networkx_edges(self.G, pos, edgelist=[self.selected_edge], ax=self.ax,
                                   edge_color='#9370DB', width=3, alpha=0.8)

        # 绘制最短路径
        if self.shortest_path:
            path_edges = list(zip(self.shortest_path[:-1], self.shortest_path[1:]))
            nx.draw_networkx_edges(self.G, pos, edgelist=path_edges, ax=self.ax,
                                   edge_color='#FF4500', width=2.5, alpha=0.9)

        # 绘制普通节点 - 浅色、透明、较小
        all_nodes = set(self.locations.keys())
        unselected_nodes = all_nodes - set(self.selected_nodes)

        nx.draw_networkx_nodes(self.G, pos, nodelist=list(unselected_nodes),
                               ax=self.ax, node_size=300,  # 较小的节点尺寸
                               node_color='#E0F7FA',  # 浅青色
                               edgecolors='#26A69A',  # 边框颜色
                               linewidths=1,
                               alpha=0.6)  # 较高的透明度

        # 绘制选中的起点节点（浅绿色、稍大）
        if self.selected_nodes:
            nx.draw_networkx_nodes(self.G, pos, nodelist=[self.selected_nodes[0]],
                                   ax=self.ax, node_size=400,  # 比普通节点稍大
                                   node_color='#E8F5E9',  # 浅绿色
                                   edgecolors='#43A047',  # 深绿色边框
                                   linewidths=1.2,
                                   alpha=0.7)  # 稍高的透明度

        # 绘制选中的终点节点（浅橙色、稍大）
        if len(self.selected_nodes) > 1:
            nx.draw_networkx_nodes(self.G, pos, nodelist=[self.selected_nodes[1]],
                                   ax=self.ax, node_size=400,  # 比普通节点稍大
                                   node_color='#FFF3E0',  # 浅橙色
                                   edgecolors='#FB8C00',  # 深橙色边框
                                   linewidths=1.2,
                                   alpha=0.7)  # 稍高的透明度

        # 绘制节点标签
        nx.draw_networkx_labels(self.G, pos, ax=self.ax, font_size=9,
                                font_family="SimHei", font_weight='bold',
                                bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=1.5))

        # 绘制边的权重
        edge_labels = {(u, v): f"{d['weight']}m" for u, v, d in self.G.edges(data=True)}
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, ax=self.ax,
                                     font_size=8, font_family="SimHei",
                                     bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=1))

        # 固定坐标轴范围
        self.ax.set_xlim(0, self.target_width)
        self.ax.set_ylim(self.target_height, 0)

        # 设置标题
        if self.placing_new_node:
            self.ax.set_title(f"请在地图上点击放置: {self.new_node_name}",
                              fontsize=14, fontweight='bold', pad=10)
        else:
            self.ax.set_title("校园导航系统", fontsize=14, fontweight='bold', pad=10)

        # 美化坐标轴
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
            self.draw_graph()
            path_str = " -> ".join(self.shortest_path)
            self.show_message("最短路径结果",
                              f"从 {self.start_node} 到 {self.end_node}\n路径: {path_str}\n总距离: {path_length}米")
        except nx.NetworkXNoPath:
            self.show_message("提示", f"从 {self.start_node} 到 {self.end_node} 没有可用路径!")

    def reset(self):
        self.selected_nodes = []
        self.selected_edge = None
        self.shortest_path = []
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

        if self.placing_new_node:
            self._place_new_node(event.xdata, event.ydata)
            return

        pos = nx.get_node_attributes(self.G, 'pos')
        clicked_node = None

        # 调整点击检测范围，因为节点变小了
        for node, (x, y) in pos.items():
            if np.sqrt((x - event.xdata) ** 2 + (y - event.ydata) ** 2) < 15:  # 保持较大的点击范围
                clicked_node = node
                break

        if clicked_node:
            if event.dblclick:
                self.show_message(clicked_node, self.introductions.get(clicked_node, "无介绍信息"))
            else:
                self.selected_edge = None
                if clicked_node in self.selected_nodes:
                    self.selected_nodes.remove(clicked_node)
                else:
                    if len(self.selected_nodes) < 2:
                        self.selected_nodes.append(clicked_node)
                    else:
                        self.selected_nodes.pop()
                        self.selected_nodes.append(clicked_node)
            self.draw_graph()
        else:
            self._select_edge(event)

    def _select_edge(self, event):
        pos = nx.get_node_attributes(self.G, 'pos')
        min_dist = float('inf')
        selected = None

        for u, v in self.G.edges():
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            dist = self._point_to_line_distance(event.xdata, event.ydata, x1, y1, x2, y2)
            if dist < 8 and dist < min_dist:
                min_dist = dist
                selected = (u, v)

        if selected:
            self.selected_nodes = []
            self.selected_edge = selected
            self.draw_graph()

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
        self.show_message("成功", f"已删除{u}到{v}的路径")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = CampusNavigation()
    app.run()
