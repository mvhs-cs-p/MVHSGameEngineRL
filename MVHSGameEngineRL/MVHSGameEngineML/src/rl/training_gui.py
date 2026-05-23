import threading
import tkinter as tk
import time
from math import floor
from pathlib import Path
from tkinter import ttk, filedialog
import matplotlib

from .training_file_store import TrainingFileStore
from ..rl import AgentTrainer

from ..utilities import Logger
from MVHSGameEngineML.src.core.config import TrainingStatus

matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class TrainingGUI:
    def __init__(self, rl_game_config):
        self.root = tk.Tk()
        self.root.title("MVHS Game Engine ML Training Dashboard")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)
        self.config = rl_game_config
        self.rl_environment = self.config["rl_environment"]
        self.policy = self.config["policy_network"]
        self.training_thread = None

        self.status_label = None

        # Stats
        self.episode_stat = None
        self.average_reward = None
        self.success_rate = None
        self.training_start_time = None
        self.last_status_episode_count = 0

        self.status_window_interval = 50
        self.next_status_window_update = self.status_window_interval
        self.status_data = []

        # configs

        self.episodes_entry_config = None
        self.episodes_entry_config_var = None

        self.learning_rate_entry_config = None
        self.learning_rate_entry_config_var = None

        self.exploration_bonus_entry_config = None
        self.exploration_bonus_entry_config_var = None

        self.gamma_entry_config = None
        self.gamma_entry_config_var = None


        # Display Stats
        self.stats_interval_var = None
        self.short_avg_reward_window_var = None
        self.long_avg_reward_window_var = None

        self.loaded_policy_file = None

        # --- MVHS Colors: silver dominant, green accent ---
        self.colors = {
            "bg_dark": "#1c1c1c",
            "bg_panel": "#262626",
            "bg_input": "#333333",
            "text": "#e8e8e8",
            "text_dim": "#999999",
            "accent": "#2d5a27",
            "training_status": "#19ff19",
            "accent_light": "#3a7a32",
            "accent_text": "#5aad52",
            "silver_bright": "#f0f0f0",
            "silver": "#c0c0c0",
            "silver_dim": "#808080",
            "success": "#5aad52",
            "warning": "#d4a844",
            "error": "#c9544a",
            "border": "#3a3a3a",
            "graph_bg": "#1a1a1a",
            "graph_line": "#c0c0c0",
            "graph_avg": "#5aad52",
        }

        self.root.configure(bg=self.colors["bg_dark"])
        self._setup_styles()
        self._build_layout()

        self.agent_trainer = None


    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Panel.TFrame", background=self.colors["bg_panel"])
        style.configure("Dashboard.TLabel",
                         background=self.colors["bg_panel"],
                         foreground=self.colors["text"],
                         font=("Segoe UI", 10))
        style.configure("GameNameLabel.TLabel",
                        background=self.colors["bg_panel"],
                        foreground=self.colors["text"],
                        font=("Segoe UI", 12, "bold"))
        style.configure("Header.TLabel",
                         background=self.colors["bg_panel"],
                         foreground=self.colors["silver_bright"],
                         font=("Segoe UI", 12, "bold"))
        style.configure("Title.TLabel",
                         background=self.colors["bg_dark"],
                         foreground=self.colors["silver_bright"],
                         font=("Segoe UI", 16, "bold"))
        style.configure("Stat.TLabel",
                         background=self.colors["bg_panel"],
                         foreground=self.colors["silver_bright"],
                         font=("Segoe UI Semibold", 14))
        style.configure("StatLabel.TLabel",
                         background=self.colors["bg_panel"],
                         foreground=self.colors["text_dim"],
                         font=("Segoe UI", 9))
        style.configure("Status.TLabel",
                         background=self.colors["bg_dark"],
                         foreground=self.colors["text_dim"],
                         font=("Segoe UI", 9))

    def _build_layout(self):
        # ==================== TOP BAR ====================
        top_bar = tk.Frame(self.root, bg=self.colors["bg_dark"], height=50)
        top_bar.pack(fill="x", padx=15, pady=(10, 5))
        top_bar.pack_propagate(False)

        # Title with subtle green bar
        accent_mark = tk.Frame(top_bar, bg=self.colors["accent"], width=4, height=28)
        accent_mark.pack(side="left", padx=(0, 8))
        accent_mark.pack_propagate(False)

        title_label = ttk.Label(top_bar, text="RL Training Dashboard", style="Title.TLabel")
        title_label.pack(side="left")

        self.load_save_status_label = tk.Label(top_bar, text="", font=("Segoe UI", 16),
            bg=self.colors["bg_dark"], fg=self.colors["accent_text"])
        self.load_save_status_label.pack(side="left", padx=(100, 0))

        self.status_label = ttk.Label(top_bar, text="Status: Idle", style="Status.TLabel")
        self.status_label.pack(side="right", padx=10)

        # ==================== MAIN CONTENT ====================
        main_frame = tk.Frame(self.root, bg=self.colors["bg_dark"])
        main_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # Left column
        left_col = tk.Frame(main_frame, bg=self.colors["bg_dark"], width=280)
        left_col.pack(side="left", fill="y", padx=(0, 10))
        left_col.pack_propagate(False)

        # Right column
        right_col = tk.Frame(main_frame, bg=self.colors["bg_dark"])
        right_col.pack(side="left", fill="both", expand=True)

        self._build_game_selection_panel(left_col)
        self._build_training_config_panel(left_col)
        self._build_display_config_panel(left_col)
        self._build_control_buttons(left_col)

        self._build_graph_panel(right_col)
        self._build_stats_panel(right_col)


    # ==================== LEFT COLUMN ====================

    def _build_game_selection_panel(self, parent):
        panel = self._create_panel(parent, "Game Selection")
        row = tk.Frame(panel, bg=self.colors["bg_panel"])
        row.pack(fill="x", padx=10, pady=(0, 8))
        ttk.Label(row, text=self.config["game_name"], style="GameNameLabel.TLabel").pack(side="left")


    def _build_training_config_panel(self, parent):
        panel = self._create_panel(parent, "Training Config")

        # Episodes
        row = tk.Frame(panel, bg=self.colors["bg_panel"])
        row.pack(fill="x", padx=10, pady=2)
        ttk.Label(row, text="Episodes:", style="Dashboard.TLabel").pack(side="left")
        self.episodes_entry_config_var = tk.StringVar(value=self.config["default_training_episodes"])
        self.episodes_entry_config = tk.Entry(row, textvariable=self.episodes_entry_config_var, width=10,
                    bg=self.colors["bg_input"], fg=self.colors["text"], insertbackground=self.colors["silver"], relief="flat",
                    font=("Segoe UI", 10), selectbackground=self.colors["silver_dim"], selectforeground=self.colors["text"])
        self.episodes_entry_config.pack(side="right", ipady=2)

        # Learning Rate
        row = tk.Frame(panel, bg=self.colors["bg_panel"])
        row.pack(fill="x", padx=10, pady=2)
        ttk.Label(row, text="Learning Rate:", style="Dashboard.TLabel").pack(side="left")
        self.learning_rate_entry_config_var = tk.StringVar(value=self.config["default_learning_rate"])
        self.learning_rate_entry_config = tk.Entry(row, textvariable=self.learning_rate_entry_config_var, width=10,
                    bg=self.colors["bg_input"], fg=self.colors["text"], insertbackground=self.colors["silver"], relief="flat",
                    font=("Segoe UI", 10), selectbackground=self.colors["silver_dim"], selectforeground=self.colors["text"])
        self.learning_rate_entry_config.pack(side="right", ipady=2)

        # Exploration Bonus Rate
        row = tk.Frame(panel, bg=self.colors["bg_panel"])
        row.pack(fill="x", padx=10, pady=2)
        ttk.Label(row, text="Exploration Bonus Rate:", style="Dashboard.TLabel").pack(side="left")
        self.exploration_bonus_entry_config_var = tk.StringVar(value=self.config["default_exploration_bonus"])
        self.exploration_bonus_entry_config = tk.Entry(row, textvariable=self.exploration_bonus_entry_config_var, width=10,
                    bg=self.colors["bg_input"], fg=self.colors["text"], insertbackground=self.colors["silver"], relief="flat",
                    font=("Segoe UI", 10), selectbackground=self.colors["silver_dim"], selectforeground=self.colors["text"])
        self.exploration_bonus_entry_config.pack(side="right", ipady=2)

        # Gamma
        row = tk.Frame(panel, bg=self.colors["bg_panel"])
        row.pack(fill="x", padx=10, pady=2)
        ttk.Label(row, text="Gamma:", style="Dashboard.TLabel").pack(side="left")
        self.gamma_entry_config_var = tk.StringVar(value=self.config["default_gamma"])
        self.gamma_entry_config = tk.Entry(row, textvariable=self.gamma_entry_config_var, width=10,
                    bg=self.colors["bg_input"], fg=self.colors["text"], insertbackground=self.colors["silver"], relief="flat",
                    font=("Segoe UI", 10), selectbackground=self.colors["silver_dim"], selectforeground=self.colors["text"])
        self.gamma_entry_config.pack(side="right", ipady=2)


        # Restore defaults button
        tk.Button(panel, text="Restore Defaults",
                  bg=self.colors["bg_input"], fg=self.colors["silver"], relief="raised", font=("Segoe UI", 9), cursor="hand2",
                  activebackground=self.colors["border"], activeforeground=self.colors["text"],command=self._restore_training_defaults
                  ).pack(anchor="e", padx=10, pady=(4, 8))

        tk.Frame(panel, bg=self.colors["bg_panel"], height=5).pack()


    def _build_display_config_panel(self, parent):
        panel = self._create_panel(parent, "Display Config")

        # Short Average Window
        row = tk.Frame(panel, bg=self.colors["bg_panel"])
        row.pack(fill="x", padx=10, pady=2)
        ttk.Label(row, text="Short Avg Reward Window:", style="Dashboard.TLabel").pack(side="left")
        self.short_avg_reward_window_var = tk.StringVar(value="50")
        self.short_avg_window_entry = tk.Entry(row, textvariable=self.short_avg_reward_window_var, width=10,
                        bg=self.colors["bg_input"], fg=self.colors["text"], insertbackground=self.colors["silver"], relief="flat",
                        font=("Segoe UI", 10), selectbackground=self.colors["silver_dim"], selectforeground=self.colors["text"])
        self.short_avg_window_entry.pack(side="right", ipady=2)

        # Long Average Window
        row = tk.Frame(panel, bg=self.colors["bg_panel"])
        row.pack(fill="x", padx=10, pady=2)
        ttk.Label(row, text="Long Avg Reward Window:", style="Dashboard.TLabel").pack(side="left")
        self.long_avg_reward_window_var = tk.StringVar(value="200")
        self.long_avg_window_entry = tk.Entry(row, textvariable=self.long_avg_reward_window_var, width=10,
                        bg=self.colors["bg_input"], fg=self.colors["text"], insertbackground=self.colors["silver"], relief="flat",
                        font=("Segoe UI", 10), selectbackground=self.colors["silver_dim"], selectforeground=self.colors["text"])
        self.long_avg_window_entry.pack(side="right", ipady=2)

        # Stats Interval
        row = tk.Frame(panel, bg=self.colors["bg_panel"])
        row.pack(fill="x", padx=10, pady=2)
        ttk.Label(row, text="Stats Interval:", style="Dashboard.TLabel").pack(side="left")
        self.stats_interval_var = tk.StringVar(value="100")
        self.stats_interval_entry = tk.Entry(row, textvariable=self.stats_interval_var, width=10,
                        bg=self.colors["bg_input"], fg=self.colors["text"], insertbackground=self.colors["silver"], relief="flat",
                        font=("Segoe UI", 10), selectbackground=self.colors["silver_dim"], selectforeground=self.colors["text"])
        self.stats_interval_entry.pack(side="right", ipady=2)


        # Restore defaults
        tk.Button(panel, text="Restore Defaults",
                        bg=self.colors["bg_input"], fg=self.colors["silver"], relief="flat", font=("Segoe UI", 9), cursor="hand2",
                        activebackground=self.colors["border"], activeforeground=self.colors["text"], command=self._restore_display_defaults
                  ).pack(anchor="e", padx=10, pady=(4, 8))

        tk.Frame(panel, bg=self.colors["bg_panel"], height=5).pack()

    def _build_control_buttons(self, parent):
        panel = tk.Frame(parent, bg=self.colors["bg_dark"])
        panel.pack(fill="x", pady=(10, 0))
        btn_style = {"relief": tk.FLAT, "font": ("Segoe UI Semibold", 11),
                     "cursor": "hand2", "height": 1, "bd": 0}

        self.train_btn = tk.Button(panel, text="Train",
            bg=self.colors["accent"], fg=self.colors["silver_bright"],
            activebackground=self.colors["accent_light"], activeforeground="#ffffff",
            command=self._on_train_clicked, **btn_style)
        self.train_btn.pack(fill="x", pady=(0, 5))

        self.stop_btn = tk.Button(panel, text="Stop & Save",
            bg=self.colors["warning"], fg="#1c1c1c",
            activebackground="#c99a4e", activeforeground="#1c1c1c",
            command=self._on_stop_clicked, state="disabled", **btn_style)
        self.stop_btn.pack(fill="x", pady=(0, 5))

        self.load_policy_btn = tk.Button(panel, text="Load Policy",
            bg=self.colors["silver"], fg="#1c1c1c",
            activebackground="#c99a4e", activeforeground="#1c1c1c",
            command=self._on_load_policy_clicked, **btn_style)
        self.load_policy_btn.pack(fill="x", pady=(0, 5))




    # ==================== RIGHT COLUMN ====================

    def _build_graph_panel(self, parent):
        panel_frame = tk.Frame(parent, bg=self.colors["bg_panel"], bd=0,
            highlightthickness=1, highlightbackground=self.colors["border"])
        panel_frame.pack(fill="both", expand=True, pady=(0, 10))
        # panel_frame.pack(fill="x", pady=(0, 10))

        header = tk.Frame(panel_frame, bg=self.colors["bg_panel"])
        header.pack(fill="x", padx=12, pady=(8, 0))

        # Small green accent mark before header
        tk.Frame(header, bg=self.colors["accent"], width=3, height=16).pack(side="left", padx=(0, 6))
        ttk.Label(header, text="Reward Over Episodes", style="Header.TLabel").pack(side="left")

        self.fig = Figure(figsize=(6, 3.5), dpi=100, facecolor=self.colors["graph_bg"])
        self.ax = self.fig.add_subplot(111)
        self._style_graph()
        self.canvas = FigureCanvasTkAgg(self.fig, master=panel_frame)
        self.canvas.get_tk_widget().configure(bg=self.colors["graph_bg"], highlightthickness=0)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=(4, 8))

    def _style_graph(self):
        self.ax.set_facecolor(self.colors["graph_bg"])
        self.ax.tick_params(colors=self.colors["text_dim"], labelsize=8)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["bottom"].set_color(self.colors["border"])
        self.ax.spines["left"].set_color(self.colors["border"])
        self.ax.set_xlabel("Episode", color=self.colors["text_dim"], fontsize=9)
        self.ax.set_ylabel("Reward", color=self.colors["text_dim"], fontsize=9)
        self.ax.grid(True, alpha=0.1, color=self.colors["silver_dim"])
        self.fig.tight_layout(pad=2.0)

    def _build_stats_panel(self, parent):
        panel_frame = tk.Frame(parent, bg=self.colors["bg_panel"], bd=0,
            highlightthickness=1, highlightbackground=self.colors["border"])
        panel_frame.pack(fill="x")

        header = tk.Frame(panel_frame, bg=self.colors["bg_panel"])
        header.pack(fill="x", padx=12, pady=(8, 0))

        tk.Frame(header, bg=self.colors["accent"], width=3, height=16).pack(side="left", padx=(0, 6))
        ttk.Label(header, text="Training Statistics", style="Header.TLabel").pack(side="left")

        # --- Summary stats ---
        summary_frame = tk.Frame(panel_frame, bg=self.colors["bg_panel"])
        summary_frame.pack(fill="x", padx=12, pady=(8, 4))

        # Episode
        box = tk.Frame(summary_frame, bg=self.colors["bg_panel"])
        box.pack(side="left", expand=True, fill="x", padx=5)
        self.episode_stat = ttk.Label(box, text="0 / 0", style="Stat.TLabel")
        self.episode_stat.pack()
        ttk.Label(box, text="Episode", style="StatLabel.TLabel").pack()

        # Elapsed
        box = tk.Frame(summary_frame, bg=self.colors["bg_panel"])
        box.pack(side="left", expand=True, fill="x", padx=5)
        self.elapsed_stat = ttk.Label(box, text="00:00", style="Stat.TLabel")
        self.elapsed_stat.pack()
        ttk.Label(box, text="Elapsed Time", style="StatLabel.TLabel").pack()

        # Estimated
        box = tk.Frame(summary_frame, bg=self.colors["bg_panel"])
        box.pack(side="left", expand=True, fill="x", padx=5)
        self.estimated_stat = ttk.Label(box, text="00:00", style="Stat.TLabel")
        self.estimated_stat.pack()
        ttk.Label(box, text="Estimated Remaining Time", style="StatLabel.TLabel").pack()


        # --- Interval table ---
        table_frame = tk.Frame(panel_frame, bg=self.colors["bg_panel"])
        table_frame.pack(fill="x", padx=12, pady=(8, 10))

        columns = ("Ep Range", "Avg Reward", "Avg Steps", "Success", "Timeout", "Game Over")
        self.stats_tree = ttk.Treeview(table_frame, columns=columns, show="headings",
            height=5, style="Dashboard.Treeview")

        style = ttk.Style()
        style.configure("Dashboard.Treeview",
            background=self.colors["bg_input"],
            foreground=self.colors["text"],
            fieldbackground=self.colors["bg_input"],
            font=("Segoe UI", 9),
            rowheight=22)
        style.configure("Dashboard.Treeview.Heading",
            background=self.colors["bg_panel"],
            foreground=self.colors["silver"],
            font=("Segoe UI Semibold", 9))
        style.map("Dashboard.Treeview",
            background=[("selected", self.colors["border"])])

        for col in columns:
            self.stats_tree.heading(col, text=col)
            self.stats_tree.column(col, width=100, anchor="center")
        self.stats_tree.column("Ep Range", width=120)
        self.stats_tree.pack(fill="x")


    def _create_panel(self, parent, title):
        panel_frame = tk.Frame(parent, bg=self.colors["bg_panel"], bd=0,
            highlightthickness=1, highlightbackground=self.colors["border"])
        panel_frame.pack(fill="x", pady=(0, 8))

        header = tk.Frame(panel_frame, bg=self.colors["bg_panel"])
        header.pack(fill="x", padx=10, pady=(8, 4))

        # Small green accent mark
        tk.Frame(header, bg=self.colors["accent"], width=3, height=14).pack(side="left", padx=(0, 6))
        ttk.Label(header, text=title, style="Header.TLabel").pack(side="left")

        return panel_frame


    def _restore_training_defaults(self):
        self.episodes_entry_config_var.set(self.config["default_training_episodes"])
        self.learning_rate_entry_config_var.set(self.config["default_learning_rate"])
        self.exploration_bonus_entry_config_var.set(self.config["default_exploration_bonus"])
        self.gamma_entry_config_var.set(self.config["default_gamma"])


    def _restore_display_defaults(self):
        self.short_avg_reward_window_var.set("50")
        self.long_avg_reward_window_var.set("200")
        self.stats_interval_var.set("100")


    def _on_train_clicked(self):
        self.train_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal", text="Stop & Save")

        # disable config entries
        self.episodes_entry_config.configure(state="disabled")
        self.learning_rate_entry_config.configure(state="disabled")
        self.exploration_bonus_entry_config.configure(state="disabled")
        self.gamma_entry_config.configure(state="disabled")

        self.training_start_time = time.time()
        self.start_training()


    def _on_train_start_failed(self):
        self.train_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

        self.episodes_entry_config.configure(state="normal")
        self.learning_rate_entry_config.configure(state="normal")
        self.exploration_bonus_entry_config.configure(state="normal")
        self.gamma_entry_config.configure(state="normal")


    def _on_stop_clicked(self):
        self.stop_btn.configure(text="Stopping...", state="disabled")
        self.set_status("Stopping after current episode...")
        if self.agent_trainer is not None:
            self.agent_trainer.should_stop = True

    def _on_load_policy_clicked(self):
        filepath = filedialog.askopenfilename(title="Select Policy File",
                                              initialdir=self.config["policy_dir"],
                                              filetypes=[("PyTorch Model", "*.pt *.pth"), ("All Files", "*.*")])
        if filepath:
            self.load_save_status_label.configure(text=f"Loaded Policy: {Path(filepath).name}")
            self.load_policy(filepath)


    def load_policy(self, file_path):
        self.loaded_policy_file = TrainingFileStore.load_training(file_path)

        # For not all of this is displayed to ide console
        print(f"Policy loaded: {Path(file_path).name}")
        if "best_average_reward" in self.loaded_policy_file and "best_average_reward_episode" in self.loaded_policy_file:
            print("Best Policy Saved:")
            print(f"Best average reward: {self.loaded_policy_file["best_average_reward"]}")
            print(f"Best average reward episode: {self.loaded_policy_file["best_average_reward_episode"]}")
        print(self.loaded_policy_file["config_notes"])
        self.train_btn.configure(text="Continue Training")

        self.policy.load_state_dict(self.loaded_policy_file["policy_state_dict"])


    def get_training_config(self):
        episodes = self.episodes_entry_config.get()
        try:
            episodes = floor(int(episodes))
            if episodes < 1:
                raise ValueError("Must be positive")
        except ValueError:
            Logger.log_error(self, "Episodes Rate Config Value Error: Value must be a positive number")
            self._on_train_start_failed()
            episodes = None

        learning_rate = self.learning_rate_entry_config.get()
        try:
            learning_rate = float(learning_rate)
            if learning_rate < 0:
                raise ValueError("Must be positive")
        except ValueError:
            Logger.log_error(self, "Learning Rate Config Value Error: Value must be a positive number")
            self._on_train_start_failed()
            learning_rate = None

        exploration_bonus = self.exploration_bonus_entry_config.get()
        try:
            exploration_bonus = float(exploration_bonus)
            if exploration_bonus < 0:
                raise ValueError("Must be positive")
        except ValueError:
            Logger.log_error(self, "Exploration Bonus Config Value Error: Value must be a positive number")
            self._on_train_start_failed()
            exploration_bonus = None

        gamma = self.gamma_entry_config.get()
        try:
            gamma = float(gamma)
            if gamma < 0:
                raise ValueError("Must be positive")
        except ValueError:
            Logger.log_error(self, "Gamma Config Value Error: Value must be a positive number")
            self._on_train_start_failed()
            gamma = None

        return {
            "episodes": episodes,
            "learning_rate": learning_rate,
            "exploration_bonus": exploration_bonus,
            "gamma": gamma,
        }



    def start_training(self):

        optimizer_state_dict = None
        if self.loaded_policy_file is not None:
            optimizer_state_dict = self.loaded_policy_file["optimizer_state_dict"]

        training_configs = self.get_training_config()
        for key, value in training_configs.items():
            if value is None:
                Logger.log_error(self, f"Unable to start training, invalid {key}.")
                return

        agent_trainer_config = {
            "policy": self.policy,
            "learning_rate": training_configs["learning_rate"],
            "exploration_bonus" : training_configs["exploration_bonus"],
            "gamma": training_configs["gamma"],
            "environment": self.rl_environment,
            "episodes": training_configs["episodes"],
            "optimizer_state_dict": optimizer_state_dict
        }
        self.agent_trainer = AgentTrainer(agent_trainer_config)
        self.training_thread = threading.Thread(target=self.agent_trainer.start_training)
        self.training_thread.start()
        self.status_label.configure(text="Status: Training", foreground=self.colors["training_status"])
        self._poll_training()


    def _poll_training(self):

        if self.agent_trainer is None:
            return

        training_stats = self.agent_trainer.training_stats
        self._update_training_gui_displays(training_stats)
        if self.agent_trainer.is_training:
            self.root.after(500, self._poll_training)
        else:
            self.status_label.configure(text="Status: Saving", foreground=self.colors["training_status"])
            policy_save_time = TrainingFileStore.save_training(self.config["policy_dir"], self.agent_trainer, self.config["config_notes"])
            self.status_label.configure(text="Status: Idle", style="Status.TLabel")
            self.training_thread.join()
            self.training_thread = None
            self.load_save_status_label.configure(text=f"Training Complete - Policy Save time: {policy_save_time}")
            self.on_training_complete()


    def _update_training_gui_displays(self, training_stats):

        self._update_graph(training_stats)
        self._update_stats_data(training_stats)
        self.update_progress(
            training_stats["last_training_episode"],
            training_stats["training_episodes"],
            training_stats["elapsed_training_time"],
            training_stats["estimated_remaining_training_time"]
        )


    def _update_stats_data(self, training_stats):

        stats_interval = 100
        try:
            stats_interval = int(self.stats_interval_var.get())
            if stats_interval <= 0:
                raise ValueError("Must be positive")
        except ValueError:
            Logger.log_warning(self, "Update Stats Data Config Value Error: Value must be a positive number, set to default value - 100")

        episode_end_status = training_stats["episode_end_status"]
        episode_rewards = training_stats["episode_rewards"]
        episode_steps = training_stats["episode_steps"]

        rows = []
        total_episodes = len(episode_end_status)

        # Snap with multiples of window size
        status_interval_start = max(0, (total_episodes // stats_interval) - 4) * stats_interval
        for i in range(status_interval_start, total_episodes, stats_interval):
            status_chunk = episode_end_status[i:i + stats_interval]
            rewards_chunk = episode_rewards[i:i + stats_interval]
            steps_chunk = episode_steps[i:i + stats_interval]

            if status_chunk is not None:

                success_rate = status_chunk.count(TrainingStatus.SUCCESS) / len(status_chunk) * 100
                timeout_rate = status_chunk.count(TrainingStatus.TIMEOUT) / len(status_chunk) * 100
                game_over_rate = status_chunk.count(TrainingStatus.GAME_OVER) / len(status_chunk) * 100
                average_rewards = sum(rewards_chunk) / len(rewards_chunk)
                average_steps = sum(steps_chunk) / len(steps_chunk)

                rows.append((
                    f"{i + 1} - {i + len(status_chunk)}",
                    f"{average_rewards:.1f}",
                    f"{average_steps:.1f}",
                    f"{success_rate:.0f}%",
                    f"{timeout_rate:.0f}%",
                    f"{game_over_rate:.0f}%",
                ))

        self.update_stats(rows)


    # ==================== UPDATE METHODS ====================

    def _update_graph(self, training_stats, moving_avg=None):
        self.ax.clear()
        self._style_graph()
        episode_rewards = training_stats["episode_rewards"]
        if episode_rewards:

            reward = list(episode_rewards)
            episodes = list(range(1, len(reward) + 1))

            short_average_window = 50
            try:
                short_average_window = int(self.short_avg_reward_window_var.get())
                if short_average_window <= 0:
                    raise ValueError("Must be positive")
            except ValueError:
                Logger.log_warning(self,"Update Graph: Short Average Reward Value must be a positive number, set to default value - 50")

            short_avg = []
            for i in range(len(reward)):
                window = reward[max(0, i - short_average_window):i + 1]
                short_avg.append(sum(window) / len(window))


            long_average_window = 200
            try:
                long_average_window = int(self.long_avg_reward_window_var.get())
                if long_average_window <= 0:
                    raise ValueError("Must be positive")
            except ValueError:
                Logger.log_warning(self,"Update Graph: Long Average Reward Value must be a positive number, set to default value - 200")


            long_avg = []
            for i in range(len(reward)):
                window = reward[max(0, i - long_average_window):i + 1]
                long_avg.append(sum(window) / len(window))

            # Down sample episode rewards, keeps only 500 points max on the graph
            step = max(1, len(reward) // 500)
            sampled_episodes = episodes[::step]
            sampled_short = short_avg[::step]
            sampled_long = long_avg[::step]

            self.ax.plot(sampled_episodes, sampled_short,
                color=self.colors["graph_line"], alpha=0.3, linewidth=0.8, label=f"Short Avg ({short_average_window} ep)")

            self.ax.plot(sampled_episodes, sampled_long,
                color=self.colors["graph_avg"], linewidth=2, label=f"Long Avg ({long_average_window} ep)")

            if training_stats["best_average_reward"] > float("-inf"):
                self.ax.scatter(training_stats["best_average_reward_episode"], training_stats["best_average_reward"],
                                color='r', label="Best Average Reward")

            self.ax.legend(loc="upper left", fontsize=8,
                facecolor=self.colors["bg_panel"], edgecolor=self.colors["border"],
                labelcolor=self.colors["text_dim"])
        self.canvas.draw_idle()


    def update_stats(self, interval_rows):
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)
        for row in interval_rows:
            self.stats_tree.insert("", tk.END, values=row)


    def update_progress(self, current_episode, total_episodes, elapsed_seconds, estimated_seconds_left):
        self.episode_stat.configure(text=f"{current_episode} / {total_episodes}")
        elapsed_minutes = int(elapsed_seconds // 60)
        elapsed_seconds = int(elapsed_seconds % 60)
        self.elapsed_stat.configure(text=f"{elapsed_minutes:02d}:{elapsed_seconds:02d}")
        estimated_minutes_left = int(estimated_seconds_left // 60)
        estimated_seconds_left = int(estimated_seconds_left % 60)
        self.estimated_stat.config(text=f"{estimated_minutes_left:02d}:{estimated_seconds_left:02d}")


    def set_status(self, text):
        self.status_label.configure(text=f"Status: {text}")


    def on_training_complete(self):
        self.train_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled", text="Stop & Save")
        self.episodes_entry_config.configure(state="normal")
        self.learning_rate_entry_config.configure(state="normal")
        self.exploration_bonus_entry_config.configure(state="normal")
        self.gamma_entry_config.configure(state="normal")
        self.set_status("Idle")


    def run(self):
        self.root.mainloop()


