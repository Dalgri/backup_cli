import tkinter as tk
from tkinter import ttk
import threading
from tkinter import filedialog
import queue
from .services.backup_engine import BackupEngine

# ── Palette ──────────────────────────────────────────────────────────────────
BG        = "#0f0f0f"   # near-black canvas
PANEL     = "#161616"   # slightly lighter panel
BORDER    = "#2a2a2a"   # subtle divider
ACCENT    = "#00e5a0"   # sharp mint-green accent
ACCENT_DIM= "#00a370"   # dimmed accent for hover
TEXT      = "#e8e8e8"   # primary text
TEXT_DIM  = "#606060"   # muted labels
DANGER    = "#e05555"   # remove / error red
MONO      = ("Courier New", 9)
SANS      = ("Segoe UI", 9)
SANS_SM   = ("Segoe UI", 8)


class GUI:
    def __init__(self):
        self.log_queue = queue.Queue()
        self.backup = BackupEngine()
        self.setup_ui()
        self.update_backup_labels()
        self.show_inbox()
        self.running = True
        

    # ── Build UI ──────────────────────────────────────────────────────────────
    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title("Backup Utility")
        self.root.geometry("1080x980")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.root.protocol('WM_DELETE_WINDOW', self.on_close)

        self._apply_styles()

        # ── outer padding frame ───────────────────────────────────────────────
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True, padx=20, pady=20)

        # ── header bar ───────────────────────────────────────────────────────
        header = tk.Frame(outer, bg=BG)
        header.pack(fill="x", pady=(0, 14))

        tk.Label(
            header, text="BACKUP", font=("Courier New", 13, "bold"),
            fg=ACCENT, bg=BG
        ).pack(side="left")

        tk.Label(
            header, text="utility", font=("Segoe UI", 10),
            fg=TEXT_DIM, bg=BG
        ).pack(side="left", padx=(6, 0), pady=(2, 0))

        # thin accent line under header
        tk.Frame(outer, bg=BORDER, height=1).pack(fill="x", pady=(0, 16))

        # ── body: left panel + right panel ───────────────────────────────────
        body = tk.Frame(outer, bg=BG)
        body.pack(fill="both", expand=True)

        self._build_left(body)
        self._build_right(body)

    def _build_left(self, parent):
        left = tk.Frame(parent, bg=PANEL, bd=0, highlightthickness=1,
                        highlightbackground=BORDER)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))

        # list label
        tk.Label(
            left, text="SOURCE PATHS", font=("Courier New", 8),
            fg=TEXT_DIM, bg=PANEL, anchor="w"
        ).pack(fill="x", padx=12, pady=(10, 4))

        # listbox with custom scrollbar
        lb_frame = tk.Frame(left, bg=PANEL)
        lb_frame.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        scrollbar = tk.Scrollbar(lb_frame, bg=BORDER, troughcolor=PANEL,
                                 activebackground=ACCENT, bd=0, width=6)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(
            lb_frame,
            bg=BG, fg=TEXT,
            selectbackground=ACCENT, selectforeground=BG,
            font=MONO,
            bd=0, highlightthickness=0,
            activestyle="none",
            yscrollcommand=scrollbar.set,
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

        # thin separator
        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=12)

        # action buttons row
        btn_row = tk.Frame(left, bg=PANEL)
        btn_row.pack(fill="x", padx=12, pady=10)

        self.add_btn = self._flat_btn(btn_row, "+ Add path",
                                      self.add_to_refresh, accent=True)
        self.add_btn.pack(side="left", padx=(0, 6))

        self.rem_btn = self._flat_btn(btn_row, "− Remove",
                                      self.rem_path, danger=True)
        self.rem_btn.pack(side="left")

    def _build_right(self, parent):
        right = tk.Frame(parent, bg=PANEL, bd=0, highlightthickness=1,
                         highlightbackground=BORDER, width=300)
        right.pack(side="right", fill="both")
        right.pack_propagate(False)

        # log label
        tk.Label(
            right, text="LOG", font=("Courier New", 8),
            fg=TEXT_DIM, bg=PANEL, anchor="w"
        ).pack(fill="x", padx=12, pady=(10, 4))

        # log text box
        log_frame = tk.Frame(right, bg=PANEL)
        log_frame.pack(fill="both", expand=True, padx=12)

        log_scroll = tk.Scrollbar(log_frame, bg=BORDER, troughcolor=PANEL,
                                  activebackground=ACCENT, bd=0, width=6)
        log_scroll.pack(side="right", fill="y")

        self.log_box = tk.Text(
            log_frame,
            bg=BG, fg=TEXT_DIM,
            font=MONO,
            bd=0, highlightthickness=0,
            state="disabled",
            wrap="word",
            yscrollcommand=log_scroll.set,
            insertbackground=ACCENT,
        )
        self.log_box.pack(side="left", fill="both", expand=True)
        log_scroll.config(command=self.log_box.yview)

        # progress section
        prog_frame = tk.Frame(right, bg=PANEL)
        prog_frame.pack(fill="x", padx=12, pady=(8, 0))

        tk.Label(
            prog_frame, text="PROGRESS", font=("Courier New", 8),
            fg=TEXT_DIM, bg=PANEL, anchor="w"
        ).pack(fill="x")

        self.progress = ttk.Progressbar(
            prog_frame, length=276, mode="determinate",
            style="Accent.Horizontal.TProgressbar"
        )
        self.progress.pack(fill="x", pady=(4, 8))

        # thin separator
        tk.Frame(right, bg=BORDER, height=1).pack(fill="x", padx=12)

        # control buttons
        ctrl = tk.Frame(right, bg=PANEL)
        ctrl.pack(fill="x", padx=12, pady=10)

                # info section (backup paths)
        info_frame = tk.Frame(right, bg=PANEL)
        info_frame.pack(fill="x", padx=12, pady=(10, 0))

        tk.Frame(info_frame, bg=BORDER, height=1).pack(fill="x", pady=(0, 6))

        self.backup_label = tk.Label(
            info_frame,
            text="Backup: ",
            font=("Courier New", 8),
            fg=TEXT,
            bg=PANEL,
            anchor="w",
            justify="left",
            wraplength=260
        )
        self.backup_label.pack(fill="x")

        self.default_label = tk.Label(
            info_frame,
            text="Default: ",
            font=("Courier New", 8),
            fg=TEXT_DIM,
            bg=PANEL,
            anchor="w",
            justify="left",
            wraplength=260
        )
        self.default_label.pack(fill="x", pady=(2, 0))
        
        
        self.backup_btn = self._flat_btn(ctrl, "▶  Run backup",
                                         self.start_backup, accent=True, wide=True)
        self.backup_btn.pack(fill="x", pady=(0, 5))

        self.change_default_btn = self._flat_btn(
            ctrl, "⚙  Set default path",
            lambda: [self.add_default(), self.update_backup_labels()],
            wide=True
        )
        self.change_default_btn.pack(fill="x")
        
        self.change_backup_btn = self._flat_btn(
        ctrl, "📁  Change backup path",
        lambda: [self.mod_backup(), self.update_backup_labels()],
        wide=True
    )
        self.change_backup_btn.pack(fill="x", pady=(5, 0))

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _flat_btn(self, parent, label, command=None,
                  accent=False, danger=False, wide=False):
        """A flat, borderless button that fits the dark theme."""
        fg   = BG     if accent else (DANGER if danger else TEXT)
        bg   = ACCENT if accent else (PANEL  if danger else BORDER)
        hbg  = ACCENT_DIM if accent else (DANGER if danger else "#333333")
        hfg  = BG if accent else TEXT

        w = 20 if wide else None
        btn = tk.Button(
            parent, text=label, font=SANS_SM,
            fg=fg, bg=bg, activeforeground=hfg, activebackground=hbg,
            bd=0, padx=10, pady=5,
            cursor="hand2", command=command,
            relief="flat", width=w
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=hbg, fg=hfg))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg, fg=fg))
        return btn

    def _apply_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(
            "Accent.Horizontal.TProgressbar",
            troughcolor=BG,
            background=ACCENT,
            bordercolor=BG,
            lightcolor=ACCENT,
            darkcolor=ACCENT,
        )

    def _log(self, msg):
        self.log_box.config(state="normal")
        self.log_box.insert(tk.END, msg)
        self.log_box.see(tk.END)
        self.log_box.config(state="disabled")

    # ── Data / events ─────────────────────────────────────────────────────────
    
    def update_backup_labels(self):
        backup = self.backup.get_commands(2)
        default = self.backup.get_commands(3)
        
        self.backup_label.config(text=f'Backup: {backup}')
        self.default_label.config(text=f'Default: {default}')
    
    def show_inbox(self):
        for src in self.backup.get_commands(1):
            self.listbox.insert(tk.END, f"  {src}")

    def refresh(self):
        self.listbox.delete(0, tk.END)
        self.show_inbox()

    def add_to_refresh(self):
        path = filedialog.askdirectory()
        self.backup.get_commands(4, path)
        self.refresh()

    def mod_backup(self):
        add = filedialog.askdirectory()
        if not add:
            return
        self.backup.get_commands(6, add)
    
    def rem_path(self):
        select = self.listbox.curselection()
        if not select:
            self._log("Nothing selected to remove.\n")
            return
        idx = select[0]
        self.backup.get_commands(7, idx)
        self.refresh()

    def start_backup(self):
        self.progress["value"] = 0
        self.backup_btn.config(state='disabled')
        thread = threading.Thread(
            target=self.run_backup_thread,
            daemon=True
        )
        thread.start()
    
    def run_backup_thread(self):
        try:
            self.backup.cli_backup(self.log_queue)
        finally:
            self.log_queue.put('__DONE__')

    def add_default(self):
        add = filedialog.askdirectory()
        if not add:
            return
        self.backup.get_commands(5, add)
    
    def poll_queue(self):
        if not self.running:
            return
        try:
            while True:
                msg = self.log_queue.get_nowait()
                if msg == '__DONE__':
                    self.backup_btn.config(state='normal')
                elif isinstance(msg, dict):
                    self.progress["value"] = msg["progress"]
                else:
                    self._log(msg)
        except queue.Empty:
            pass
        if self.running:
            
            self.root.after(100, self.poll_queue)
    def on_close(self):
        self.running = False
        self.root.destroy()
    
    def run(self):
        self.root.after(100, self.poll_queue)
        self.root.mainloop()