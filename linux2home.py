#!/usr/bin/env python3
"""
Linux2Home - Win2Linux Migration Importer
Win2Linux Migrator ile oluşturulan paketi Linux'a yerleştiren araç
Gereksinim: pip install customtkinter psutil
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
import json
import shutil
import zipfile
import threading
import subprocess
import platform
from pathlib import Path
from datetime import datetime

# ── Tema ──────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

ACCENT   = "#22C55E"
ACCENT2  = "#16A34A"
BG_DARK  = "#0A1628"
BG_CARD  = "#0F2537"
BG_CARD2 = "#162d42"
TEXT     = "#F0FDF4"
MUTED    = "#94A3B8"
SUCCESS  = "#4ADE80"
WARNING  = "#FCD34D"
DANGER   = "#F87171"
LINUX    = "#F97316"

# ── Klasör haritası (Windows → Linux) ────────────────────────────────────────
FOLDER_MAP = {
    "Masaüstü":     str(Path.home() / "Desktop"),
    "Belgeler":     str(Path.home() / "Documents"),
    "İndirilenler": str(Path.home() / "Downloads"),
    "Müzik":        str(Path.home() / "Music"),
    "Resimler":     str(Path.home() / "Pictures"),
    "Videolar":     str(Path.home() / "Videos"),
}

# ── Paket yöneticisi komutları ────────────────────────────────────────────────
PKG_MANAGERS = {
    "apt":    "sudo apt install -y",
    "dnf":    "sudo dnf install -y",
    "pacman": "sudo pacman -S --noconfirm",
    "zypper": "sudo zypper install -y",
    "flatpak":"flatpak install -y flathub",
}

def detect_pkg_manager() -> str:
    for mgr in ["apt", "dnf", "pacman", "zypper"]:
        if shutil.which(mgr):
            return mgr
    return "apt"

# ─────────────────────────────────────────────────────────────────────────────
#  Ana uygulama
# ─────────────────────────────────────────────────────────────────────────────
class Linux2HomeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Linux2Home — Migration Importer")
        self.geometry("1100x720")
        self.minsize(900, 600)
        self.configure(fg_color=BG_DARK)

        self._pack_path    = tk.StringVar()
        self._pack_dir     = None   # Çözümlenen klasör yolu (Path)
        self._programs     = []     # programs.json içeriği
        self._folder_vars  : dict[str, tk.BooleanVar] = {}
        self._browser_vars : dict[str, tk.BooleanVar] = {}
        self._config_vars  : dict[str, tk.BooleanVar] = {}
        self._pkg_mgr      = detect_pkg_manager()

        self._build_ui()

    # ── UI İskeleti ──────────────────────────────────────────────────────────
    def _build_ui(self):
        sidebar = ctk.CTkFrame(self, width=220, fg_color=BG_CARD, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(pady=(28, 8), padx=16, fill="x")
        ctk.CTkLabel(logo_frame, text="🐧", font=("Monospace", 38)).pack()
        ctk.CTkLabel(logo_frame, text="Linux2Home", font=("Monospace", 16, "bold"),
                     text_color=SUCCESS).pack()
        ctk.CTkLabel(logo_frame, text="Migration Importer", font=("Monospace", 10),
                     text_color=MUTED).pack()

        ctk.CTkFrame(sidebar, height=1, fg_color="#1e3a2f").pack(fill="x", padx=16, pady=12)

        self._nav_btns: dict[str, ctk.CTkButton] = {}
        nav_items = [
            ("📦  Paket Seç",      self._show_select),
            ("📁  Dosyalar",       self._show_files),
            ("📋  Programlar",     self._show_programs),
            ("🌐  Browser Verileri",self._show_browser),
            ("⚙️  Konfigürasyon",  self._show_config),
            ("🚀  Kurulum",        self._show_install),
        ]
        for label, cmd in nav_items:
            btn = ctk.CTkButton(sidebar, text=label, anchor="w",
                                font=("Monospace", 12),
                                fg_color="transparent", hover_color="#0d3320",
                                text_color=MUTED, height=42,
                                command=cmd)
            btn.pack(fill="x", padx=10, pady=2)
            self._nav_btns[label] = btn

        # Paket durumu
        self._pack_status_lbl = ctk.CTkLabel(sidebar,
            text="⚠️ Paket yüklenmedi", font=("Monospace", 10),
            text_color=WARNING)
        self._pack_status_lbl.pack(side="bottom", pady=4)

        ctk.CTkLabel(sidebar,
            text=f"🐧 {platform.node()}\n{self._pkg_mgr} tespit edildi",
            font=("Monospace", 9), text_color="#475569").pack(side="bottom", pady=(0, 4))

        self._content = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        self._content.pack(side="left", fill="both", expand=True)
        ctk.CTkButton(
            sidebar, text="🐙  GitHub",
            font=("Segoe UI", 11),
            fg_color="transparent", hover_color="#1e3a5f",
            text_color=MUTED, height=32, cursor="hand2",
            command=lambda: __import__("webbrowser").open("https://github.com/AtillaTokmak")
        ).pack(side="bottom", fill="x", padx=10, pady=(0, 4))

        self._show_select()

    def _clear_content(self):
        for w in self._content.winfo_children():
            w.destroy()
        for btn in self._nav_btns.values():
            btn.configure(text_color=MUTED, fg_color="transparent")

    def _activate_nav(self, label: str):
        if label in self._nav_btns:
            self._nav_btns[label].configure(text_color=TEXT, fg_color="#0d3320")

    def _page_header(self, title: str, subtitle: str):
        hdr = ctk.CTkFrame(self._content, fg_color="transparent")
        hdr.pack(fill="x", padx=32, pady=(28, 4))
        ctk.CTkLabel(hdr, text=title, font=("Monospace", 22, "bold"),
                     text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(hdr, text=subtitle, font=("Monospace", 11),
                     text_color=MUTED).pack(anchor="w", pady=(2, 0))
        ctk.CTkFrame(self._content, height=1, fg_color="#1e3a2f").pack(
            fill="x", padx=32, pady=(12, 0))

    # ── Sayfa 0 · Paket Seç ──────────────────────────────────────────────────
    def _show_select(self):
        self._clear_content()
        self._activate_nav("📦  Paket Seç")
        self._page_header("Migration Paketini Seç",
                          "Win2Linux Migrator ile oluşturulan ZIP veya klasörü aç")

        main = ctk.CTkFrame(self._content, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=32, pady=20)

        # Sürükle-bırak benzeri büyük seçim kutusu
        drop_zone = ctk.CTkFrame(main, fg_color=BG_CARD, corner_radius=16,
                                  border_width=2, border_color="#1e3a2f")
        drop_zone.pack(fill="x", pady=(0, 20))

        inner = ctk.CTkFrame(drop_zone, fg_color="transparent")
        inner.pack(pady=30)
        ctk.CTkLabel(inner, text="📦", font=("Monospace", 48)).pack()
        ctk.CTkLabel(inner, text="Migration Paketini Yükle",
                     font=("Monospace", 16, "bold"), text_color=TEXT).pack(pady=(8, 4))
        ctk.CTkLabel(inner, text="Win2Linux Migrator'ın oluşturduğu W2L_*.zip dosyasını\nveya çıkarılmış klasörü seçin",
                     font=("Monospace", 11), text_color=MUTED, justify="center").pack()

        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(pady=16)
        ctk.CTkButton(btn_row, text="📂  ZIP Dosyası Seç",
                      command=self._select_zip,
                      fg_color=ACCENT, hover_color=ACCENT2,
                      font=("Monospace", 12, "bold"), height=42, width=180).pack(side="left", padx=6)
        ctk.CTkButton(btn_row, text="📁  Klasör Seç",
                      command=self._select_folder,
                      fg_color=BG_CARD2, hover_color="#1e3a2f",
                      text_color=TEXT, font=("Monospace", 12), height=42, width=150).pack(side="left", padx=6)

        # Seçili yol
        path_frame = ctk.CTkFrame(main, fg_color=BG_CARD, corner_radius=10)
        path_frame.pack(fill="x", pady=8)
        path_inner = ctk.CTkFrame(path_frame, fg_color="transparent")
        path_inner.pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(path_inner, text="Seçili Paket:", font=("Monospace", 11),
                     text_color=MUTED).pack(anchor="w")
        self._path_display = ctk.CTkLabel(path_inner, text="Henüz seçilmedi",
                                           font=("Monospace", 11), text_color=WARNING)
        self._path_display.pack(anchor="w", pady=(4, 0))

        # Paket içeriği özeti
        self._summary_frame = ctk.CTkFrame(main, fg_color=BG_CARD, corner_radius=10)
        self._summary_frame.pack(fill="x", pady=8)
        self._summary_inner = ctk.CTkFrame(self._summary_frame, fg_color="transparent")
        self._summary_inner.pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(self._summary_inner, text="Paket İçeriği",
                     font=("Monospace", 12, "bold"), text_color=TEXT).pack(anchor="w")
        self._summary_lbl = ctk.CTkLabel(self._summary_inner,
                                          text="Paket yüklendiğinde içerik buraya görünür.",
                                          font=("Monospace", 11), text_color=MUTED)
        self._summary_lbl.pack(anchor="w", pady=(4, 0))

        # Devam butonu
        self._continue_btn = ctk.CTkButton(main, text="Devam Et →",
                      command=self._show_files,
                      fg_color=ACCENT, hover_color=ACCENT2,
                      font=("Monospace", 13, "bold"), height=44,
                      state="disabled")
        self._continue_btn.pack(fill="x", pady=(12, 0))

    def _select_zip(self):
        path = filedialog.askopenfilename(
            title="Migration ZIP seç",
            filetypes=[("ZIP Dosyaları", "*.zip"), ("Tümü", "*.*")]
        )
        if not path:
            return
        self._pack_path.set(path)
        self._extract_zip(path)

    def _select_folder(self):
        path = filedialog.askdirectory(title="Migration klasörü seç")
        if not path:
            return
        self._pack_path.set(path)
        self._pack_dir = Path(path)
        self._load_package()

    def _extract_zip(self, zip_path: str):
        extract_to = Path(zip_path).parent / Path(zip_path).stem
        self._path_display.configure(text=f"⏳ ZIP çıkarılıyor...", text_color=WARNING)
        self.update()
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(extract_to)
            self._pack_dir = extract_to
            self._load_package()
        except Exception as e:
            messagebox.showerror("Hata", f"ZIP çıkarılamadı:\n{e}")

    def _load_package(self):
        if not self._pack_dir or not self._pack_dir.exists():
            return

        self._path_display.configure(
            text=str(self._pack_dir), text_color=SUCCESS)

        # programs.json
        prog_json = self._pack_dir / "programs.json"
        if prog_json.exists():
            try:
                with open(prog_json, "r", encoding="utf-8") as f:
                    self._programs = json.load(f)
            except:
                self._programs = []

        # Özet
        has_files   = (self._pack_dir / "files").exists()
        has_browser = (self._pack_dir / "browser").exists()
        has_config  = (self._pack_dir / "config").exists()
        has_progs   = len(self._programs) > 0

        parts = []
        if has_files:
            dirs = list((self._pack_dir / "files").iterdir())
            parts.append(f"📁 {len(dirs)} dosya klasörü")
        if has_progs:
            matched = sum(1 for p in self._programs if p.get("alt"))
            parts.append(f"📦 {len(self._programs)} program ({matched} Linux alternatifi)")
        if has_browser:
            browsers = list((self._pack_dir / "browser").iterdir())
            parts.append(f"🌐 {len(browsers)} tarayıcı verisi")
        if has_config:
            configs = list((self._pack_dir / "config").iterdir())
            parts.append(f"⚙️ {len(configs)} konfigürasyon")

        summary_text = "\n".join(f"  ✅ {p}" for p in parts) if parts else "⚠️ Paket içeriği bulunamadı"
        self._summary_lbl.configure(text=summary_text, text_color=SUCCESS if parts else WARNING)

        self._pack_status_lbl.configure(text="✅ Paket yüklendi", text_color=SUCCESS)
        self._continue_btn.configure(state="normal")

    # ── Sayfa 1 · Dosyalar ────────────────────────────────────────────────────
    def _show_files(self):
        self._clear_content()
        self._activate_nav("📁  Dosyalar")
        self._page_header("Dosyaları Yerleştir",
                          "Klasörleri Linux home dizinine kopyala")

        if not self._pack_dir:
            self._no_pack_warning()
            return

        files_dir = self._pack_dir / "files"
        if not files_dir.exists():
            ctk.CTkLabel(self._content,
                         text="⚠️ Bu pakette dosya klasörü bulunamadı.",
                         font=("Monospace", 13), text_color=WARNING).pack(pady=40)
            return

        scroll = ctk.CTkScrollableFrame(self._content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=32, pady=16)

        ctk.CTkLabel(scroll, text="Kopyalanacak Klasörler",
                     font=("Monospace", 13, "bold"), text_color=TEXT).pack(anchor="w", pady=(0, 10))

        self._folder_vars = {}
        grid = ctk.CTkFrame(scroll, fg_color="transparent")
        grid.pack(fill="x")
        grid.columnconfigure((0, 1), weight=1)

        folders = list(files_dir.iterdir()) if files_dir.exists() else []
        row = 0
        for i, src_folder in enumerate(sorted(folders)):
            if not src_folder.is_dir():
                continue
            col = i % 2
            if col == 0 and i > 0:
                row += 1

            name = src_folder.name
            # Hedef klasörü bul
            linux_dst = FOLDER_MAP.get(name, str(Path.home() / name))

            try:
                size = sum(f.stat().st_size for f in src_folder.rglob("*") if f.is_file())
                size_str = self._human(size)
                file_count = sum(1 for f in src_folder.rglob("*") if f.is_file())
            except:
                size_str = "?"
                file_count = 0

            card = ctk.CTkFrame(grid, fg_color=BG_CARD, corner_radius=10)
            card.grid(row=row, column=col, padx=6, pady=6, sticky="ew")

            var = tk.BooleanVar(value=True)
            self._folder_vars[name] = {"var": var, "src": src_folder, "dst": linux_dst}

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=14, pady=12)

            ctk.CTkCheckBox(inner, text=name, variable=var,
                            font=("Monospace", 12, "bold"),
                            text_color=TEXT, checkmark_color="white",
                            fg_color=ACCENT).pack(anchor="w")

            ctk.CTkLabel(inner, text=f"📂 Kaynak: {src_folder.name}",
                         font=("Monospace", 9), text_color=MUTED).pack(anchor="w", pady=(3, 0))
            ctk.CTkLabel(inner, text=f"🎯 Hedef: {linux_dst}",
                         font=("Monospace", 9), text_color=SUCCESS).pack(anchor="w")
            ctk.CTkLabel(inner, text=f"📊 {file_count} dosya · {size_str}",
                         font=("Monospace", 9), text_color=MUTED).pack(anchor="w")

            # Çakışma uyarısı
            if os.path.exists(linux_dst) and os.listdir(linux_dst):
                warn = ctk.CTkFrame(inner, fg_color="#2d1b00", corner_radius=6)
                warn.pack(fill="x", pady=(6, 0))
                ctk.CTkLabel(warn,
                             text="⚠️ Hedef klasör dolu — Üzerine yaz?",
                             font=("Monospace", 9), text_color=WARNING).pack(padx=8, pady=4)
                var_overwrite_key = f"overwrite_{name}"
                overwrite_var = tk.BooleanVar(value=False)
                self._folder_vars[var_overwrite_key] = {"var": overwrite_var}
                ctk.CTkCheckBox(warn, text="Evet, üzerine yaz",
                                variable=overwrite_var,
                                font=("Monospace", 9), text_color=WARNING,
                                fg_color=WARNING).pack(padx=8, pady=(0, 4))

    # ── Sayfa 2 · Programlar ──────────────────────────────────────────────────
    def _show_programs(self):
        self._clear_content()
        self._activate_nav("📋  Programlar")
        self._page_header("Program Alternatifleri",
                          "Windows programlarınız için Linux alternatifleri ve kurulum komutları")

        if not self._pack_dir:
            self._no_pack_warning()
            return

        if not self._programs:
            ctk.CTkLabel(self._content,
                         text="⚠️ Bu pakette program listesi bulunamadı.",
                         font=("Monospace", 13), text_color=WARNING).pack(pady=40)
            return

        scroll = ctk.CTkScrollableFrame(self._content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=32, pady=16)

        # İstatistikler
        matched = [p for p in self._programs if p.get("alt")]
        stats = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=10)
        stats.pack(fill="x", pady=(0, 16))
        stat_inner = ctk.CTkFrame(stats, fg_color="transparent")
        stat_inner.pack(fill="x", padx=16, pady=12)

        cols = ctk.CTkFrame(stat_inner, fg_color="transparent")
        cols.pack(fill="x")
        for val, label, color in [
            (str(len(self._programs)), "Toplam Program", TEXT),
            (str(len(matched)),        "Alternatif Bulundu", SUCCESS),
            (str(len(self._programs) - len(matched)), "Manuel Araştır", WARNING),
        ]:
            col = ctk.CTkFrame(cols, fg_color=BG_CARD2, corner_radius=8)
            col.pack(side="left", padx=4, ipadx=16, ipady=8)
            ctk.CTkLabel(col, text=val, font=("Monospace", 22, "bold"),
                         text_color=color).pack()
            ctk.CTkLabel(col, text=label, font=("Monospace", 9),
                         text_color=MUTED).pack()

        # Toplu kur butonu
        install_cmd = self._build_install_cmd([p for p in matched if p.get("alt")])
        if install_cmd:
            cmd_frame = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=10)
            cmd_frame.pack(fill="x", pady=(0, 12))
            cmd_inner = ctk.CTkFrame(cmd_frame, fg_color="transparent")
            cmd_inner.pack(fill="x", padx=16, pady=12)
            ctk.CTkLabel(cmd_inner, text="Toplu Kurulum Komutu",
                         font=("Monospace", 11, "bold"), text_color=TEXT).pack(anchor="w")
            cmd_box = ctk.CTkTextbox(cmd_inner, height=70,
                                      font=("Monospace", 10),
                                      fg_color=BG_DARK, text_color=SUCCESS)
            cmd_box.pack(fill="x", pady=(4, 0))
            cmd_box.insert("end", install_cmd)
            cmd_box.configure(state="disabled")
            ctk.CTkButton(cmd_inner, text="📋  Komutu Kopyala",
                          command=lambda c=install_cmd: self._copy_to_clipboard(c),
                          fg_color=BG_CARD2, hover_color=ACCENT,
                          text_color=TEXT, height=32).pack(anchor="w", pady=(6, 0))

        # Filtre
        filter_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 8))
        self._prog_filter = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(filter_frame,
                        text="Yalnızca Linux alternatifi olanları göster",
                        variable=self._prog_filter,
                        command=lambda: self._refresh_prog_list(prog_list_frame),
                        text_color=MUTED).pack(side="left")

        prog_list_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        prog_list_frame.pack(fill="x")
        self._refresh_prog_list(prog_list_frame)

    def _refresh_prog_list(self, container):
        for w in container.winfo_children():
            w.destroy()
        show_all = not self._prog_filter.get()
        for prog in self._programs:
            alt = prog.get("alt")
            if not show_all and not alt:
                continue
            card = ctk.CTkFrame(container, fg_color=BG_CARD, corner_radius=8)
            card.pack(fill="x", pady=2)
            card.columnconfigure(1, weight=1)

            icon = "✅" if alt else "❓"
            ctk.CTkLabel(card, text=icon, font=("Monospace", 14), width=36).grid(
                row=0, column=0, padx=10, pady=10)
            ctk.CTkLabel(card, text=prog["name"], font=("Monospace", 11),
                         text_color=TEXT, anchor="w").grid(
                row=0, column=1, sticky="w", pady=10)

            if alt:
                alt_name, alt_pkg, alt_desc = alt[0], alt[1], alt[2]
                alt_f = ctk.CTkFrame(card, fg_color="#0d2b0d", corner_radius=6)
                alt_f.grid(row=0, column=2, padx=10, pady=6)
                ctk.CTkLabel(alt_f, text=f"🐧 {alt_name}",
                             font=("Monospace", 10, "bold"),
                             text_color=SUCCESS).pack(padx=10, pady=(4, 0))
                ctk.CTkLabel(alt_f, text=f"$ {self._pkg_mgr} install {alt_pkg}",
                             font=("Monospace", 9), text_color=LINUX).pack(padx=10)
                ctk.CTkLabel(alt_f, text=alt_desc,
                             font=("Monospace", 8), text_color=MUTED).pack(padx=10, pady=(0, 4))

    def _build_install_cmd(self, matched_progs) -> str:
        pkgs = set()
        for p in matched_progs:
            alt = p.get("alt")
            if alt and len(alt) > 1:
                pkgs.add(alt[1])
        if not pkgs:
            return ""
        mgr_cmd = PKG_MANAGERS.get(self._pkg_mgr, "sudo apt install -y")
        return f"{mgr_cmd} {' '.join(sorted(pkgs))}"

    # ── Sayfa 3 · Browser ─────────────────────────────────────────────────────
    def _show_browser(self):
        self._clear_content()
        self._activate_nav("🌐  Browser Verileri")
        self._page_header("Browser Verilerini İçe Aktar",
                          "Yer imleri ve profil verilerini mevcut tarayıcıya aktar")

        if not self._pack_dir:
            self._no_pack_warning()
            return

        browser_dir = self._pack_dir / "browser"
        if not browser_dir.exists():
            ctk.CTkLabel(self._content,
                         text="⚠️ Bu pakette tarayıcı verisi bulunamadı.",
                         font=("Monospace", 13), text_color=WARNING).pack(pady=40)
            return

        scroll = ctk.CTkScrollableFrame(self._content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=32, pady=16)

        self._browser_vars = {}

        for browser_dir_entry in sorted(browser_dir.iterdir()):
            if not browser_dir_entry.is_dir():
                continue
            browser_name = browser_dir_entry.name

            # Linux'ta bu tarayıcının hedef yolu
            linux_paths = {
                "Chrome":  Path.home() / ".config" / "google-chrome",
                "Firefox": Path.home() / ".mozilla" / "firefox",
                "Edge":    Path.home() / ".config" / "microsoft-edge",
                "Brave":   Path.home() / ".config" / "BraveSoftware" / "Brave-Browser",
            }
            linux_target = linux_paths.get(browser_name, Path.home() / ".config" / browser_name.lower())

            icons = {"Chrome": "🔵", "Firefox": "🟠", "Edge": "🟣", "Brave": "🦁"}
            icon = icons.get(browser_name, "🌐")

            section = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=12)
            section.pack(fill="x", pady=8)

            hdr = ctk.CTkFrame(section, fg_color="transparent")
            hdr.pack(fill="x", padx=16, pady=(14, 4))
            ctk.CTkLabel(hdr, text=f"{icon} {browser_name}",
                         font=("Monospace", 14, "bold"), text_color=TEXT).pack(side="left")

            # Tarayıcı yüklü mü?
            installed = self._is_browser_installed(browser_name)
            status_text = "✅ Kurulu" if installed else "⚠️ Kurulu değil"
            status_color = SUCCESS if installed else WARNING
            ctk.CTkLabel(hdr, text=status_text,
                         font=("Monospace", 10), text_color=status_color).pack(side="right")

            # Profiller
            for profile_dir in browser_dir_entry.iterdir():
                if not profile_dir.is_dir():
                    continue

                row = ctk.CTkFrame(section, fg_color="transparent")
                row.pack(fill="x", padx=16, pady=4)

                key = f"{browser_name}::{profile_dir.name}"
                var = tk.BooleanVar(value=installed)
                self._browser_vars[key] = {
                    "var": var, "src": profile_dir,
                    "dst": linux_target / profile_dir.name,
                    "browser": browser_name
                }

                ctk.CTkCheckBox(row, text=profile_dir.name, variable=var,
                                text_color=TEXT, fg_color=ACCENT,
                                state="normal" if installed else "disabled").pack(side="left")

                try:
                    size = sum(f.stat().st_size for f in profile_dir.rglob("*") if f.is_file())
                    ctk.CTkLabel(row, text=self._human(size),
                                 font=("Monospace", 9), text_color=MUTED).pack(side="right")
                except:
                    pass

            # Hedef bilgisi
            info = ctk.CTkFrame(section, fg_color="transparent")
            info.pack(fill="x", padx=16, pady=(4, 14))
            ctk.CTkLabel(info, text=f"🎯 Hedef: {linux_target}",
                         font=("Monospace", 9), text_color=MUTED).pack(anchor="w")

            if not installed:
                ctk.CTkLabel(info,
                             text=f"💡 Kurmak için: {self._pkg_mgr} install {browser_name.lower()}",
                             font=("Monospace", 9), text_color=LINUX).pack(anchor="w")

    def _is_browser_installed(self, browser_name: str) -> bool:
        executables = {
            "Chrome":  ["google-chrome", "google-chrome-stable"],
            "Firefox": ["firefox"],
            "Edge":    ["microsoft-edge"],
            "Brave":   ["brave-browser", "brave"],
        }
        for exe in executables.get(browser_name, []):
            if shutil.which(exe):
                return True
        return False

    # ── Sayfa 4 · Config ──────────────────────────────────────────────────────
    def _show_config(self):
        self._clear_content()
        self._activate_nav("⚙️  Konfigürasyon")
        self._page_header("Konfigürasyonları Uygula",
                          "SSH, git ve diğer sistem ayarlarını yerleştir")

        if not self._pack_dir:
            self._no_pack_warning()
            return

        config_dir = self._pack_dir / "config"
        if not config_dir.exists():
            ctk.CTkLabel(self._content,
                         text="⚠️ Bu pakette konfigürasyon bulunamadı.",
                         font=("Monospace", 13), text_color=WARNING).pack(pady=40)
            return

        scroll = ctk.CTkScrollableFrame(self._content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=32, pady=16)

        self._config_vars = {}

        # Konfigürasyon öğeleri
        config_items = {
            ".ssh":        ("🔑 SSH Anahtarları",   str(Path.home() / ".ssh"),       "600"),
            "hosts":       ("📋 Hosts Dosyası",      "/etc/hosts",                    None),
            "env_vars.json":("🌍 Ortam Değişkenleri","~/.bashrc / ~/.zshrc'ye ekle",  None),
            ".gitconfig":  ("🔒 Git Konfigürasyonu", str(Path.home() / ".gitconfig"), None),
            "User":        ("💻 VSCode Ayarları",    str(Path.home() / ".config/Code/User"), None),
        }

        for item in config_dir.iterdir():
            label_info = config_items.get(item.name, (f"📄 {item.name}", str(Path.home() / item.name), None))
            title, linux_dst, permissions = label_info

            card = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=10)
            card.pack(fill="x", pady=6)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=16, pady=12)

            var = tk.BooleanVar(value=True)
            self._config_vars[item.name] = {
                "var": var, "src": item,
                "dst": linux_dst, "perms": permissions
            }

            row1 = ctk.CTkFrame(inner, fg_color="transparent")
            row1.pack(fill="x")
            ctk.CTkCheckBox(row1, text=title, variable=var,
                            font=("Monospace", 12, "bold"),
                            text_color=TEXT, fg_color=ACCENT).pack(side="left")

            ctk.CTkLabel(inner, text=f"🎯 Hedef: {linux_dst}",
                         font=("Monospace", 9), text_color=SUCCESS).pack(anchor="w", pady=(4, 0))

            if permissions:
                ctk.CTkLabel(inner, text=f"🔒 İzinler: chmod {permissions} uygulanacak",
                             font=("Monospace", 9), text_color=WARNING).pack(anchor="w")

            # Özel işlemler
            if item.name == "env_vars.json":
                ctk.CTkLabel(inner,
                             text="ℹ️ Değişkenler ~/.bashrc ve ~/.profile dosyasına eklenecek",
                             font=("Monospace", 9), text_color=MUTED).pack(anchor="w")
            elif item.name == "hosts":
                ctk.CTkLabel(inner,
                             text="⚠️ /etc/hosts yazımı için sudo gerekli",
                             font=("Monospace", 9), text_color=WARNING).pack(anchor="w")

    # ── Sayfa 5 · Kurulum ─────────────────────────────────────────────────────
    def _show_install(self):
        self._clear_content()
        self._activate_nav("🚀  Kurulum")
        self._page_header("Kurulum",
                          "Seçilen tüm öğeleri Linux sistemine yerleştir")

        if not self._pack_dir:
            self._no_pack_warning()
            return

        main = ctk.CTkFrame(self._content, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=32, pady=16)

        # Özet kutusu
        summary = ctk.CTkFrame(main, fg_color=BG_CARD, corner_radius=10)
        summary.pack(fill="x", pady=(0, 12))
        sum_inner = ctk.CTkFrame(summary, fg_color="transparent")
        sum_inner.pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(sum_inner, text="Kurulum Özeti",
                     font=("Monospace", 13, "bold"), text_color=TEXT).pack(anchor="w")

        folders_sel = sum(1 for v in self._folder_vars.values()
                          if isinstance(v, dict) and v.get("var") and v["var"].get()
                          and "src" in v)
        browser_sel = sum(1 for v in self._browser_vars.values()
                          if v.get("var") and v["var"].get())
        config_sel  = sum(1 for v in self._config_vars.values()
                          if v.get("var") and v["var"].get())
        progs_count = sum(1 for p in self._programs if p.get("alt"))

        for label, count, color in [
            (f"📁 {folders_sel} dosya klasörü kopyalanacak", folders_sel, TEXT),
            (f"📦 {progs_count} program için kurulum komutu hazır", progs_count, TEXT),
            (f"🌐 {browser_sel} tarayıcı profili içe aktarılacak", browser_sel, TEXT),
            (f"⚙️ {config_sel} konfigürasyon yerleştirilecek", config_sel, TEXT),
        ]:
            ctk.CTkLabel(sum_inner, text=label,
                         font=("Monospace", 11),
                         text_color=color if count > 0 else MUTED).pack(anchor="w")

        # Log
        self._log_box = ctk.CTkTextbox(main, height=220,
                                        font=("Monospace", 10),
                                        fg_color=BG_CARD, text_color=SUCCESS,
                                        corner_radius=10)
        self._log_box.pack(fill="x", pady=8)
        self._log_box.insert("end", "Kurulumu başlatmak için aşağıdaki butona tıkla...\n")
        self._log_box.configure(state="disabled")

        # İlerleme
        self._progress = ctk.CTkProgressBar(main, height=12, corner_radius=6,
                                             fg_color=BG_CARD, progress_color=ACCENT)
        self._progress.pack(fill="x")
        self._progress.set(0)

        # Buton
        self._install_btn = ctk.CTkButton(
            main, text="🚀  Kurulumu Başlat",
            command=self._start_install,
            fg_color=ACCENT, hover_color=ACCENT2,
            font=("Monospace", 14, "bold"), height=46)
        self._install_btn.pack(fill="x", pady=(12, 0))

    def _log(self, msg: str):
        self._log_box.configure(state="normal")
        self._log_box.insert("end", f"{msg}\n")
        self._log_box.see("end")
        self._log_box.configure(state="disabled")

    def _start_install(self):
        self._install_btn.configure(state="disabled", text="⏳  Kurulum yapılıyor...")
        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")
        self._log_box.configure(state="disabled")
        self._progress.set(0)
        threading.Thread(target=self._do_install, daemon=True).start()

    def _do_install(self):
        steps = []

        # 1. Dosya klasörleri
        for key, info in self._folder_vars.items():
            if not isinstance(info, dict) or "src" not in info:
                continue
            if info["var"].get():
                overwrite_key = f"overwrite_{key}"
                overwrite = False
                if overwrite_key in self._folder_vars:
                    ov = self._folder_vars[overwrite_key]
                    if isinstance(ov, dict) and ov.get("var"):
                        overwrite = ov["var"].get()
                steps.append(("folder", key, info["src"], info["dst"], overwrite))

        # 2. Browser verileri
        for key, info in self._browser_vars.items():
            if info["var"].get():
                steps.append(("browser", key, info["src"], info["dst"], True))

        # 3. Konfigürasyonlar
        for key, info in self._config_vars.items():
            if info["var"].get():
                steps.append(("config", key, info["src"], info["dst"], info.get("perms")))

        total = len(steps)
        if total == 0:
            self.after(0, lambda: self._log("⚠️ Hiçbir öğe seçilmedi!"))
            self.after(0, lambda: self._install_btn.configure(
                state="normal", text="🚀  Kurulumu Başlat"))
            return

        self.after(0, lambda: self._log(f"🚀 {total} öğe işlenecek...\n"))

        for i, step in enumerate(steps):
            kind    = step[0]
            name    = step[1]
            src     = step[2]
            dst     = step[3]
            extra   = step[4]

            self.after(0, lambda n=name: self._log(f"  → {n} işleniyor..."))

            try:
                if kind in ("folder", "browser"):
                    dst_path = Path(dst)
                    if os.path.isdir(src):
                        if dst_path.exists() and extra:  # overwrite
                            shutil.rmtree(dst_path, ignore_errors=True)
                        dst_path.mkdir(parents=True, exist_ok=True)
                        shutil.copytree(src, dst_path, dirs_exist_ok=True)
                    elif os.path.isfile(src):
                        dst_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, dst_path)
                    self.after(0, lambda n=name: self._log(f"    ✅ {n} kopyalandı"))

                elif kind == "config":
                    perms = extra
                    # env_vars özel işlem
                    if name == "env_vars.json" and os.path.isfile(src):
                        self._apply_env_vars(src)
                        self.after(0, lambda: self._log("    ✅ Ortam değişkenleri ~/.bashrc'ye eklendi"))
                    elif name == "hosts" and os.path.isfile(src):
                        self.after(0, lambda: self._log(
                            "    ℹ️ Hosts dosyası kopyalanamadı (sudo gerekli). Manuel:\n"
                            f"       sudo cp {src} /etc/hosts"))
                    else:
                        dst_path = Path(dst)
                        if os.path.isdir(src):
                            dst_path.mkdir(parents=True, exist_ok=True)
                            shutil.copytree(src, dst_path, dirs_exist_ok=True)
                        elif os.path.isfile(src):
                            dst_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(src, dst_path)

                        # İzin uygula
                        if perms:
                            subprocess.run(["chmod", "-R", perms, str(dst_path)],
                                           capture_output=True)
                        self.after(0, lambda n=name: self._log(f"    ✅ {n} yerleştirildi"))

            except Exception as e:
                self.after(0, lambda n=name, err=e: self._log(f"    ❌ {n}: {err}"))

            self.after(0, lambda v=(i + 1) / total: self._progress.set(v))

        # Kurulum komutu oluştur
        install_cmd = self._build_install_cmd(
            [p for p in self._programs if p.get("alt")])
        if install_cmd:
            self.after(0, lambda: self._log(
                f"\n📦 Programları kurmak için şu komutu terminalde çalıştır:\n{install_cmd}"))
            # install_cmd.sh dosyasına yaz
            script = Path.home() / "install_linux_apps.sh"
            try:
                with open(script, "w") as f:
                    f.write("#!/bin/bash\n")
                    f.write("# Win2Linux Migration - Program Kurulum Scripti\n")
                    f.write(f"# Oluşturulma: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                    f.write(install_cmd + "\n")
                os.chmod(script, 0o755)
                self.after(0, lambda p=script: self._log(f"✅ Kurulum scripti: {p}"))
            except Exception as e:
                pass

        self.after(0, lambda: self._log("\n🎉 Tüm işlemler tamamlandı!"))
        self.after(0, lambda: self._progress.set(1.0))
        self.after(0, lambda: self._install_btn.configure(
            state="normal", text="🚀  Kurulumu Başlat"))
        self.after(0, lambda: messagebox.showinfo(
            "Tamamlandı",
            "Migration başarıyla tamamlandı!\n\n"
            "~/install_linux_apps.sh dosyasını çalıştırarak\n"
            "Linux alternatiflerini kurabilirsin."))

    def _apply_env_vars(self, json_path):
        """Ortam değişkenlerini ~/.bashrc'ye ekle (mevcut olanları atla)."""
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                env_data = json.load(f)

            bashrc = Path.home() / ".bashrc"
            existing = bashrc.read_text(encoding="utf-8") if bashrc.exists() else ""

            # Sistem değişkenlerini filtrele
            skip = {"PATH", "HOME", "USER", "SHELL", "TERM", "DISPLAY",
                    "XDG_RUNTIME_DIR", "DBUS_SESSION_BUS_ADDRESS", "LOGNAME", "MAIL"}

            additions = ["\n# === Win2Linux Migration - Ortam Değişkenleri ==="]
            for key, value in env_data.items():
                if key in skip or key.startswith("_"):
                    continue
                if f'export {key}=' not in existing:
                    # Değeri bash-safe hale getir
                    safe_val = value.replace("\\", "/").replace('"', '\\"')
                    additions.append(f'export {key}="{safe_val}"')

            if len(additions) > 1:
                with open(bashrc, "a", encoding="utf-8") as f:
                    f.write("\n".join(additions) + "\n")
        except Exception as e:
            pass

    # ── Yardımcılar ───────────────────────────────────────────────────────────
    def _no_pack_warning(self):
        frame = ctk.CTkFrame(self._content, fg_color="transparent")
        frame.pack(expand=True)
        ctk.CTkLabel(frame, text="📦", font=("Monospace", 48)).pack()
        ctk.CTkLabel(frame, text="Önce bir migration paketi yükleyin",
                     font=("Monospace", 15), text_color=MUTED).pack(pady=8)
        ctk.CTkButton(frame, text="← Paket Seç",
                      command=self._show_select,
                      fg_color=ACCENT, hover_color=ACCENT2,
                      font=("Monospace", 12), height=38).pack()

    def _copy_to_clipboard(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Kopyalandı", "Komut panoya kopyalandı!")

    @staticmethod
    def _human(n: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if n < 1024:
                return f"{n:.1f} {unit}"
            n /= 1024
        return f"{n:.1f} TB"


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if platform.system() == "Windows":
        print("Bu uygulama Linux'ta çalıştırılmalıdır!")
        sys.exit(1)
    app = Linux2HomeApp()
    app.mainloop()
