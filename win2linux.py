"""
Win2Linux Migrator — v2.1
Windows'tan Linux'a geçiş için kapsamlı GUI aracı
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
import winreg
import platform
from pathlib import Path
from datetime import datetime

# ── Tema ──────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ACCENT   = "#3B82F6"
ACCENT2  = "#6366F1"
BG_DARK  = "#0F172A"
BG_CARD  = "#1E293B"
BG_CARD2 = "#273549"
TEXT     = "#F1F5F9"
MUTED    = "#94A3B8"
SUCCESS  = "#22C55E"
WARNING  = "#F59E0B"
DANGER   = "#EF4444"

# ── Linux alternatifleri veritabanı ──────────────────────────────────────────
LINUX_ALTERNATIVES = {
    "microsoft office":   ("LibreOffice",         "libreoffice",          "Tam uyumlu ofis paketi"),
    "ms office":          ("LibreOffice",         "libreoffice",          "Tam uyumlu ofis paketi"),
    "word":               ("LibreOffice Writer",  "libreoffice-writer",   "Word belgelerini açar"),
    "excel":              ("LibreOffice Calc",     "libreoffice-calc",     "Excel dosyalarını açar"),
    "powerpoint":         ("LibreOffice Impress", "libreoffice-impress",  "Sunum uygulaması"),
    "onenote":            ("Obsidian / Joplin",   "obsidian",             "Markdown tabanlı not"),
    "outlook":            ("Thunderbird",         "thunderbird",          "E-posta istemcisi"),
    "publisher":          ("Scribus",             "scribus",              "Masaüstü yayıncılık"),
    "visio":              ("Dia / draw.io",       "dia",                  "Diyagram aracı"),
    "project":            ("ProjectLibre",        "projectlibre",         "Proje yönetimi"),
    "microsoft project":  ("ProjectLibre",        "projectlibre",         "Proje yönetimi"),
    "access":             ("LibreOffice Base",    "libreoffice-base",    "Veritabanı yönetimi"),
    "wps office":         ("WPS Office",          "wps-office",           "Linux sürümü mevcut"),
    "onlyoffice":         ("ONLYOFFICE",          "onlyoffice-desktopeditors","Linux sürümü mevcut"),
    "libreoffice":        ("LibreOffice",         "libreoffice",          "Zaten Linux'ta var!"),
    "google chrome":      ("Chromium / Firefox",  "chromium-browser",     "Açık kaynak tarayıcı"),
    "microsoft edge":     ("Firefox",             "firefox",              "Gizlilik odaklı tarayıcı"),
    "opera":              ("Vivaldi",             "vivaldi",              "Özelleştirilebilir tarayıcı"),
    "opera gx":           ("Vivaldi / Brave",     "vivaldi",              "Oyuncu odaklı tarayıcı"),
    "arc browser":        ("Zen Browser",         "zen-browser",          "Modern sekmeli deneyim"),
    "firefox":            ("Firefox",             "firefox",              "Zaten Linux'ta var!"),
    "zen browser":        ("Zen Browser",         "zen-browser",          "Linux sürümü mevcut"),
    "brave":              ("Brave",               "brave-browser",        "Linux sürümü mevcut"),
    "vivaldi":            ("Vivaldi",             "vivaldi",              "Linux sürümü mevcut"),
    "chromium":           ("Chromium",            "chromium-browser",     "Zaten Linux'ta var!"),
    "tor browser":        ("Tor Browser",         "torbrowser-launcher",  "Anonimlik tarayıcısı"),
    "waterfox":           ("Waterfox",            "waterfox",             "Firefox tabanlı tarayıcı"),
    "vlc":                ("VLC",                 "vlc",                  "Zaten Linux'ta var!"),
    "spotify":            ("Spotify",             "spotify",              "Linux sürümü mevcut"),
    "apple music":        ("Cider",               "cider",                "Apple Music istemcisi"),
    "itunes":             ("Rhythmbox",           "rhythmbox",            "Müzik çalar"),
    "windows media":      ("VLC",                 "vlc",                  "Evrensel medya oynatıcı"),
    "media player":       ("VLC / Celluloid",     "vlc",                  "Medya oynatıcı"),
    "foobar":             ("DeaDBeeF",            "deadbeef",             "Hafif müzik çalar"),
    "musicbee":           ("Rhythmbox / Clementine","rhythmbox",          "Müzik yöneticisi"),
    "potplayer":          ("VLC / mpv",           "mpv",                  "Video oynatıcı"),
    "mpc-hc":             ("mpv",                 "mpv",                  "Hafif video oynatıcı"),
    "plex":               ("Jellyfin",            "jellyfin",             "Medya sunucusu"),
    "jriver":             ("Strawberry",          "strawberry",           "Müzik koleksiyonu yöneticisi"),
    "audacity":           ("Audacity",            "audacity",             "Ses düzenleyici"),
    "ableton":            ("Bitwig Studio",       "bitwig-studio",        "Müzik prodüksiyonu"),
    "fl studio":          ("LMMS",                "lmms",                 "Beat yapım aracı"),
    "cubase":             ("Ardour",              "ardour",               "DAW alternatifi"),
    "reaper":             ("REAPER",              "reaper",               "Linux sürümü mevcut"),
    "mpv":                ("mpv",                 "mpv",                  "Zaten Linux'ta var!"),
    "kodi":               ("Kodi",                "kodi",                 "Zaten Linux'ta var!"),
    "obs studio":         ("OBS Studio",          "obs-studio",           "Zaten Linux'ta var!"),
    "obs":                ("OBS Studio",          "obs-studio",           "Zaten Linux'ta var!"),
    "bandicam":           ("OBS Studio",          "obs-studio",           "Ekran kayıt aracı"),
    "medal":              ("GPU Screen Recorder", "gpu-screen-recorder",  "Hafif oyun kayıt aracı"),
    "shadowplay":         ("GPU Screen Recorder", "gpu-screen-recorder",  "NVIDIA kayıt alternatifi"),
    "xsplit":             ("OBS Studio",          "obs-studio",           "Yayın yazılımı"),
    "streamlabs":         ("OBS Studio",          "obs-studio",           "Yayın yazılımı"),
    "camtasia":           ("Kdenlive / OBS",      "kdenlive",             "Video kayıt & düzenleme"),
    "adobe photoshop":    ("GIMP",                "gimp",                 "Güçlü görsel editör"),
    "photoshop":          ("GIMP",                "gimp",                 "Güçlü görsel editör"),
    "adobe illustrator":  ("Inkscape",            "inkscape",             "Vektör grafik editörü"),
    "illustrator":        ("Inkscape",            "inkscape",             "Vektör grafik editörü"),
    "adobe premiere":     ("DaVinci Resolve / Kdenlive","kdenlive",       "Video editörü"),
    "premiere":           ("Kdenlive",            "kdenlive",             "Video editörü"),
    "after effects":      ("Natron / Blender",    "natron",               "Efekt & kompozisyon"),
    "cinema 4d":          ("Blender",             "blender",              "3D modelleme"),
    "maya":               ("Blender",             "blender",              "3D animasyon"),
    "zbrush":             ("Blender Sculpt",      "blender",              "Dijital heykel"),
    "substance painter":  ("ArmorPaint",          "armorpaint",           "PBR texture boyama"),
    "paint tool sai":     ("Krita",               "krita",                "Dijital çizim"),
    "clip studio paint":  ("Krita",               "krita",                "Manga & çizim"),
    "paint.net":          ("Pinta",               "pinta",                "Basit görsel editör"),
    "adobe xd":           ("Penpot",              "penpot",               "UI/UX tasarım aracı"),
    "lightroom":          ("Darktable / RawTherapee","darktable",         "Fotoğraf düzenleme"),
    "adobe lightroom":    ("Darktable",           "darktable",            "RAW fotoğraf işleme"),
    "adobe acrobat":      ("Okular / Evince",     "okular",               "PDF okuyucu & editör"),
    "acrobat":            ("Okular",              "okular",               "PDF okuyucu"),
    "figma":              ("Figma",               "figma-linux",          "Linux sürümü mevcut"),
    "blender":            ("Blender",             "blender",              "Zaten Linux'ta var!"),
    "inkscape":           ("Inkscape",            "inkscape",             "Zaten Linux'ta var!"),
    "gimp":               ("GIMP",                "gimp",                 "Zaten Linux'ta var!"),
    "krita":              ("Krita",               "krita",                "Zaten Linux'ta var!"),
    "darktable":          ("Darktable",           "darktable",            "Zaten Linux'ta var!"),
    "visual studio code": ("VS Code",             "code",                 "Zaten Linux'ta var!"),
    "visual studio":      ("VS Code + JetBrains", "code",                 "IDE alternatifleri"),
    "rider":              ("JetBrains Rider",     "rider",                "C# IDE"),
    "android studio":     ("Android Studio",      "android-studio",       "Linux sürümü mevcut"),
    "netbeans":           ("Apache NetBeans",     "netbeans",             "Java IDE"),
    "notepad++":          ("Kate / Gedit",        "kate",                 "Güçlü metin editörü"),
    "sublime text":       ("Kate / Gedit",        "kate",                 "Metin editörü"),
    "atom":               ("VS Code",             "code",                 "Modern editör"),
    "intellij":           ("IntelliJ IDEA",       "intellij-idea-community","Linux sürümü mevcut"),
    "pycharm":            ("PyCharm",             "pycharm-community",    "Linux sürümü mevcut"),
    "webstorm":           ("WebStorm / VS Code",  "code",                 "JS/TS IDE"),
    "clion":              ("CLion / VS Code",     "code",                 "C++ IDE"),
    "eclipse":            ("Eclipse",             "eclipse",              "Zaten Linux'ta var!"),
    "arduino":            ("Arduino IDE",         "arduino",              "Linux sürümü mevcut"),
    "putty":              ("SSH (built-in)",      "openssh-client",       "Linux'ta yerleşik"),
    "winscp":             ("FileZilla / SFTP",    "filezilla",            "Dosya aktarımı"),
    "mobaxterm":          ("Terminator / Remmina","terminator",           "Terminal ve SSH"),
    "github desktop":     ("GitHub Desktop",      "github-desktop",       "Linux sürümü mevcut"),
    "gitkraken":          ("GitKraken",           "gitkraken",            "Git GUI istemcisi"),
    "sourcetree":         ("GitKraken / Git Cola","gitkraken",            "Git istemcisi"),
    "postman":            ("Postman",             "postman",              "Linux sürümü mevcut"),
    "insomnia":           ("Insomnia",            "insomnia",             "Linux sürümü mevcut"),
    "bruno":              ("Bruno",               "bruno",                "API test aracı"),
    "dbeaver":            ("DBeaver",             "dbeaver",              "Zaten Linux'ta var!"),
    "heidisql":           ("DBeaver / MySQL Workbench","dbeaver",         "Veritabanı yöneticisi"),
    "xampp":              ("LAMP Stack",          "apache2",              "Web sunucu paketi"),
    "wamp":               ("LAMP Stack",          "apache2",              "Apache + PHP + MariaDB"),
    "laragon":            ("LAMP / Docker",       "docker.io",            "Web geliştirme ortamı"),
    "docker desktop":     ("Docker",              "docker.io",            "Linux'ta yerel destek"),
    "git":                ("Git",                 "git",                  "Zaten Linux'ta var!"),
    "node.js":            ("Node.js",             "nodejs",               "Zaten Linux'ta var!"),
    "python":             ("Python",              "python3",              "Zaten Linux'ta var!"),
    "golang":             ("Go",                  "golang",               "Linux desteği mevcut"),
    "rust":               ("Rust",                "rustc",                "Linux desteği mevcut"),
    "wireshark":          ("Wireshark",           "wireshark",            "Zaten Linux'ta var!"),
    "virtualbox":         ("VirtualBox",          "virtualbox",           "Linux sürümü mevcut"),
    "vmware":             ("VirtualBox / QEMU",   "virtualbox",           "Sanallaştırma"),
    "hyper-v":            ("KVM / QEMU",          "qemu-kvm",             "Linux yerleşik VM"),
    "7-zip":              ("7-Zip / p7zip",       "p7zip-full",           "Arşiv aracı"),
    "winrar":             ("p7zip / Ark",         "p7zip-full",           "Arşiv aracı"),
    "peazip":             ("PeaZip",              "peazip",               "Arşiv yöneticisi"),
    "ccleaner":           ("BleachBit",           "bleachbit",            "Sistem temizleyici"),
    "everything":         ("fd / locate",         "fd-find",              "Terminal tabanlı arama"),
    "rainmeter":          ("Conky",               "conky",                "Masaüstü widget sistemi"),
    "wallpaper engine":   ("Komorebi / Hidamari", "komorebi",             "Animasyonlu duvar kağıdı"),
    "crystaldiskinfo":    ("GSmartControl",       "gsmartcontrol",        "Disk sağlığı izleyici"),
    "hwmonitor":          ("Psensor",             "psensor",              "Donanım izleme"),
    "cpu-z":              ("CPU-X",               "cpux",                 "CPU bilgisi"),
    "gpu-z":              ("GPU-Viewer / sensors","gpuinfo",              "GPU bilgisi"),
    "msi afterburner":    ("CoreCtrl / GreenWithEnvy","corectrl",         "GPU hız aşırtma"),
    "autohotkey":         ("AutoKey",             "autokey-gtk",          "Tuş makroları"),
    "process hacker":     ("htop / btop",         "btop",                 "Sistem süreç yöneticisi"),
    "task manager":       ("btop / System Monitor","btop",                "Sistem izleme"),
    "revo uninstaller":   ("Stacer",              "stacer",               "Uygulama kaldırıcı"),
    "rufus":              ("Ventoy",              "ventoy",               "USB boot aracı"),
    "balena etcher":      ("Etcher",              "balena-etcher",        "USB yazdırma aracı"),
    "ventoy":             ("Ventoy",              "ventoy",               "Çoklu ISO boot aracı"),
    "tailscale":          ("Tailscale",           "tailscale",            "Linux sürümü mevcut"),
    "syncthing":          ("Syncthing",           "syncthing",            "Dosya senkronizasyonu"),
    "teamviewer":         ("RustDesk / AnyDesk",  "rustdesk",             "Uzak masaüstü"),
    "anydesk":            ("AnyDesk",             "anydesk",              "Linux sürümü mevcut"),
    "rustdesk":           ("RustDesk",            "rustdesk",             "Zaten Linux'ta var!"),
    "parsec":             ("Sunshine + Moonlight","sunshine",             "Düşük gecikmeli yayın"),
    "openvpn":            ("OpenVPN",             "openvpn",              "VPN istemcisi"),
    "malwarebytes":       ("ClamAV / Maldet",     "clamav",               "Açık kaynak antivirüs"),
    "avast":              ("ClamAV",              "clamav",               "Açık kaynak antivirüs"),
    "bitdefender":        ("Bitdefender",         "bitdefender",          "Linux sürümü mevcut"),
    "windows defender":   ("ClamAV",              "clamav",               "Açık kaynak antivirüs"),
    "bitwarden":          ("Bitwarden",           "bitwarden",            "Zaten Linux'ta var!"),
    "keepass":            ("KeePassXC",           "keepassxc",            "Şifre yöneticisi"),
    "lastpass":           ("Bitwarden",           "bitwarden",            "Açık kaynak alternatif"),
    "authy":              ("Aegis / Authenticator","authenticator",        "2FA uygulaması"),
    "discord":            ("Discord",             "discord",              "Linux sürümü mevcut"),
    "slack":              ("Slack",               "slack-desktop",        "Linux sürümü mevcut"),
    "telegram":           ("Telegram",            "telegram-desktop",     "Zaten Linux'ta var!"),
    "zoom":               ("Zoom",                "zoom",                 "Linux sürümü mevcut"),
    "microsoft teams":    ("MS Teams",            "teams",                "Linux sürümü mevcut"),
    "skype":              ("Skype",               "skype",                "Linux sürümü mevcut"),
    "whatsapp":           ("WhatsApp Web / Signal","signal-desktop",      "Gizlilik odaklı alternatif"),
    "signal":             ("Signal",              "signal-desktop",       "Zaten Linux'ta var!"),
    "element":            ("Element",             "element-desktop",      "Matrix istemcisi"),
    "steam":              ("Steam",               "steam",                "Linux'ta çalışır"),
    "epic games":         ("Heroic Games Launcher","heroic",              "Epic & GOG alternatif launcher"),
    "gog galaxy":         ("Heroic Games Launcher","heroic",              "GOG kütüphanesi"),
    "battle.net":         ("Lutris",              "lutris",               "Blizzard oyunları için"),
    "minecraft launcher": ("Prism Launcher",      "prismlauncher",        "Minecraft launcher"),
    "curseforge":         ("Prism Launcher",      "prismlauncher",        "Minecraft mod yönetimi"),
    "riot vanguard":      ("— (Desteklenmiyor)",  "",                     "Kernel-level AC, Linux'ta çalışmaz"),
    "valorant":           ("— (Desteklenmiyor)",  "",                     "Vanguard yüzünden Linux'ta yok"),
    "roblox":             ("Sober (Flatpak)",     "sober",                "Native Linux Roblox istemcisi"),
    "osu!":               ("osu!lazer",           "osu-lazer",            "Linux sürümü mevcut"),
    "retroarch":          ("RetroArch",           "retroarch",            "Emülasyon platformu"),
    "yuzu":               ("Ryujinx",             "ryujinx",              "Switch emülasyonu"),
    "cemu":               ("Cemu",                "cemu",                 "Wii U emülatörü"),
    "solidworks":         ("FreeCAD / OpenSCAD",  "freecad",              "Açık kaynak CAD"),
    "autocad":            ("FreeCAD / LibreCAD",  "freecad",              "2D/3D CAD alternatifi"),
    "fusion 360":         ("FreeCAD",             "freecad",              "3D modelleme"),
    "catia":              ("FreeCAD",             "freecad",              "CAD alternatifi"),
    "matlab":             ("GNU Octave",          "octave",               "Matematiksel analiz"),
    "simulink":           ("Scilab / Xcos",       "scilab",               "Simülasyon aracı"),
    "labview":            ("OpenPLC / Python",    "python3",              "Otomasyon geliştirme"),
    "onedrive":           ("Nextcloud / rclone",  "nextcloud-desktop",    "Bulut depolama"),
    "dropbox":            ("Dropbox",             "dropbox",              "Linux sürümü mevcut"),
    "google drive":       ("rclone / Insync",     "rclone",               "Google Drive bağlantısı"),
    "mega":               ("MEGAsync",            "megasync",             "Bulut depolama"),
    "teracopy":           ("rsync / RapidCopy",   "rsync",                "Hızlı dosya kopyalama"),
    "filezilla":          ("FileZilla",           "filezilla",            "Zaten Linux'ta var!"),
    "winmerge":           ("Meld",                "meld",                 "Dosya karşılaştırma"),
    "qbittorrent":        ("qBittorrent",         "qbittorrent",          "Zaten Linux'ta var!"),
    "utorrent":           ("qBittorrent",         "qbittorrent",          "Açık kaynak alternatif"),
    "nordvpn":            ("NordVPN",             "nordvpn",              "Linux sürümü mevcut"),
    "expressvpn":         ("ProtonVPN",           "protonvpn",            "VPN alternatifi"),
    "protonvpn":          ("ProtonVPN",           "protonvpn",            "Linux sürümü mevcut"),
    "mullvad":            ("Mullvad VPN",         "mullvad-vpn",          "Linux sürümü mevcut"),
    "surfshark":          ("Surfshark",           "surfshark",            "Linux sürümü mevcut"),
    "microsoft .net":     (".NET SDK (Linux)",    "dotnet-sdk-8",         "Linux .NET desteği tam"),
    "microsoft asp.net":  ("ASP.NET Core (Linux)","dotnet-sdk-8",         "Linux web geliştirme"),
    "visual c++":         ("GCC / Clang",         "build-essential",      "Linux derleyici araçları"),
    "java runtime":       ("OpenJDK",             "openjdk-21-jdk",       "Java runtime alternatifi"),
    "directx":            ("Vulkan / DXVK",       "vulkan-tools",         "Grafik API desteği"),
    "samfw":              ("Heimdall",            "heimdall-flash",       "Samsung flash alternatifi"),
    "icloud":             ("iCloud Web",          "firefox",              "Tarayıcı üzerinden erişim"),
    "amazon kindle":      ("Calibre",             "calibre",              "E-kitap yöneticisi"),
    "calibre":            ("Calibre",             "calibre",              "Zaten Linux'ta var!"),
    "notion":             ("Notion",              "notion-app",           "Linux istemcisi mevcut"),
    "obsidian":           ("Obsidian",            "obsidian",             "Zaten Linux'ta var!"),
    "joplin":             ("Joplin",              "joplin",               "Zaten Linux'ta var!"),
    "anki":               ("Anki",                "anki",                 "Kart tabanlı öğrenme"),
    "draw.io":            ("draw.io",             "drawio",               "Diyagram oluşturucu"),
    "etcher":             ("balenaEtcher",        "balena-etcher",        "USB yazdırma aracı"),
}

# ── Atlanacak dosya/klasör kalıpları ─────────────────────────────────────────
_SKIP_PATTERNS = [
    "kinect for windows speech", "sdk arm64", "wpt redistributable",
    "wptx64", "winrt intellisense", "windows app certification",
    "universal crt", "clickonce bootstrapper", "kits configuration",
    "diagnoticshub", "icecap_collection", "launcher prerequisites",
    "setup 0.0", "${{",
]

# BUG FIX #2: .git ve diğer kilitli/gereksiz klasörler
SKIP_DIR_NAMES = {
    "Müziğim", "Resimlerim", "Videolarım",
    "My Music", "My Pictures", "My Videos",
    "Application Data", "Local Settings",
    ".git",          # Git object db — Error 5 verir, donduruyor
    ".hg",           # Mercurial
    ".svn",          # SVN
    "node_modules",  # Gereksiz dev bağımlılıkları
    "__pycache__",   # Python cache
    ".venv", "venv", # Python virtualenv
}

# BUG FIX #1: Döngü tespiti için normalize edilmiş yol karşılaştırması
def _is_subpath(child: Path, parent: Path) -> bool:
    """child, parent'ın içinde mi? (veya aynı yol mu?)"""
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _match_alternative(prog_name: str) -> tuple | None:
    pl = prog_name.lower().strip()
    if not pl or pl.startswith("${{"):
        return None
    for skip in _SKIP_PATTERNS:
        if skip in pl:
            return None
    for kw in sorted(LINUX_ALTERNATIVES.keys(), key=len, reverse=True):
        if kw in pl:
            return LINUX_ALTERNATIVES[kw]
    return None


DEFAULT_FOLDERS = {
    "Masaüstü":    os.path.expanduser("~/Desktop"),
    "Belgeler":    os.path.expanduser("~/Documents"),
    "İndirilenler":os.path.expanduser("~/Downloads"),
    "Müzik":       os.path.expanduser("~/Music"),
    "Resimler":    os.path.expanduser("~/Pictures"),
    "Videolar":    os.path.expanduser("~/Videos"),
}


# ─────────────────────────────────────────────────────────────────────────────
class Win2LinuxApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Win2Linux Migrator")
        self.geometry("1100x720")
        self.minsize(900, 600)
        self.configure(fg_color=BG_DARK)

        self._output_dir = tk.StringVar(value=str(Path.home() / "W2L_Migration"))
        self._prog_results: list[dict] = []
        self._folder_vars: dict[str, tk.BooleanVar] = {}
        self._custom_folders: list[str] = []

        self._build_ui()

    # ── UI İskeleti ──────────────────────────────────────────────────────────
    def _build_ui(self):
        sidebar = ctk.CTkFrame(self, width=220, fg_color=BG_CARD, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(pady=(28, 8), padx=16, fill="x")
        ctk.CTkLabel(logo_frame, text="🐧", font=("Segoe UI", 38)).pack()
        ctk.CTkLabel(logo_frame, text="Win2Linux", font=("Segoe UI", 18, "bold"),
                     text_color=TEXT).pack()
        ctk.CTkLabel(logo_frame, text="Migrator v2.1", font=("Segoe UI", 12),
                     text_color=MUTED).pack()

        ctk.CTkFrame(sidebar, height=1, fg_color="#334155").pack(fill="x", padx=16, pady=12)

        self._nav_btns: dict[str, ctk.CTkButton] = {}
        nav_items = [
            ("📁  Dosyalar",        self._show_files),
            ("📦  Programlar",      self._show_programs),
            ("🌐  Browser Verileri",self._show_browser),
            ("⚙️  Sistem Config",   self._show_config),
            ("🚀  Export",          self._show_export),
        ]
        for label, cmd in nav_items:
            btn = ctk.CTkButton(sidebar, text=label, anchor="w",
                                font=("Segoe UI", 13),
                                fg_color="transparent", hover_color="#1e3a5f",
                                text_color=MUTED, height=42, command=cmd)
            btn.pack(fill="x", padx=10, pady=2)
            self._nav_btns[label] = btn

        ctk.CTkLabel(sidebar, text=f"v2.1 · {platform.node()}",
                     font=("Segoe UI", 10), text_color="#475569").pack(side="bottom", pady=16)
        ctk.CTkButton(
            sidebar, text="🐙  GitHub",
            font=("Segoe UI", 11),
            fg_color="transparent", hover_color="#1e3a5f",
            text_color=MUTED, height=32, cursor="hand2",
            command=lambda: __import__("webbrowser").open("https://github.com/AtillaTokmak")
        ).pack(side="bottom", fill="x", padx=10, pady=(0, 4))

        self._content = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        self._content.pack(side="left", fill="both", expand=True)
        self._show_files()

    def _clear_content(self):
        for w in self._content.winfo_children():
            w.destroy()
        for btn in self._nav_btns.values():
            btn.configure(text_color=MUTED, fg_color="transparent")

    def _activate_nav(self, label: str):
        if label in self._nav_btns:
            self._nav_btns[label].configure(text_color=TEXT, fg_color="#1e3a5f")

    def _page_header(self, title: str, subtitle: str):
        hdr = ctk.CTkFrame(self._content, fg_color="transparent")
        hdr.pack(fill="x", padx=32, pady=(28, 4))
        ctk.CTkLabel(hdr, text=title, font=("Segoe UI", 24, "bold"),
                     text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(hdr, text=subtitle, font=("Segoe UI", 13),
                     text_color=MUTED).pack(anchor="w", pady=(2, 0))
        ctk.CTkFrame(self._content, height=1, fg_color="#1e3a5f").pack(
            fill="x", padx=32, pady=(12, 0))

    # ── Sayfa 1 · Dosyalar ────────────────────────────────────────────────────
    def _show_files(self):
        self._clear_content()
        self._activate_nav("📁  Dosyalar")
        self._page_header("Dosya Seçimi", "Linux'a taşımak istediğin klasörleri seç")

        scroll = ctk.CTkScrollableFrame(self._content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=32, pady=16)

        ctk.CTkLabel(scroll, text="Standart Klasörler",
                     font=("Segoe UI", 14, "bold"), text_color=TEXT).pack(anchor="w", pady=(0, 10))

        grid = ctk.CTkFrame(scroll, fg_color="transparent")
        grid.pack(fill="x")
        grid.columnconfigure((0, 1), weight=1)

        row = 0
        for i, (name, path) in enumerate(DEFAULT_FOLDERS.items()):
            col = i % 2
            if col == 0 and i > 0:
                row += 1
            card = ctk.CTkFrame(grid, fg_color=BG_CARD, corner_radius=10)
            card.grid(row=row, column=col, padx=6, pady=6, sticky="ew")

            exists = os.path.exists(path)
            size_str = ""
            if exists:
                try:
                    size = sum(f.stat().st_size for f in Path(path).rglob("*") if f.is_file())
                    size_str = f" · {self._human(size)}"
                except:
                    size_str = ""

            var = tk.BooleanVar(value=exists)
            self._folder_vars[name] = var

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=14, pady=12)
            ctk.CTkCheckBox(inner, text=name, variable=var,
                            font=("Segoe UI", 13, "bold"),
                            text_color=TEXT if exists else MUTED,
                            checkmark_color="white", fg_color=ACCENT).pack(anchor="w")
            ctk.CTkLabel(inner,
                         text=f"📂 {path}{size_str}" if exists else "⚠️ Klasör bulunamadı",
                         font=("Segoe UI", 10), text_color=MUTED,
                         wraplength=340).pack(anchor="w", pady=(3, 0))

        ctk.CTkLabel(scroll, text="Özel Klasörler",
                     font=("Segoe UI", 14, "bold"), text_color=TEXT).pack(anchor="w", pady=(22, 10))
        self._custom_list_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self._custom_list_frame.pack(fill="x")
        ctk.CTkButton(scroll, text="➕  Klasör Ekle", command=self._add_custom_folder,
                      fg_color=BG_CARD2, hover_color=ACCENT,
                      text_color=TEXT, height=38).pack(anchor="w", pady=(8, 0))

    def _add_custom_folder(self):
        path = filedialog.askdirectory(title="Klasör seç")
        if path:
            self._custom_folders.append(path)
            row = ctk.CTkFrame(self._custom_list_frame, fg_color=BG_CARD, corner_radius=8)
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=f"📁 {path}", font=("Segoe UI", 11),
                         text_color=TEXT).pack(side="left", padx=12, pady=8)
            ctk.CTkButton(row, text="✕", width=28, height=28,
                          fg_color=DANGER, hover_color="#b91c1c",
                          command=lambda r=row, p=path: self._remove_custom(r, p)).pack(
                side="right", padx=8)

    def _remove_custom(self, row_widget, path):
        if path in self._custom_folders:
            self._custom_folders.remove(path)
        row_widget.destroy()

    # ── Sayfa 2 · Programlar ──────────────────────────────────────────────────
    def _show_programs(self):
        self._clear_content()
        self._activate_nav("📦  Programlar")
        self._page_header("Kurulu Programlar",
                          "Windows uygulamalarını tara ve Linux alternatiflerini keşfet")

        btn_frame = ctk.CTkFrame(self._content, fg_color="transparent")
        btn_frame.pack(fill="x", padx=32, pady=12)
        self._scan_btn = ctk.CTkButton(
            btn_frame, text="🔍  Taramayı Başlat",
            command=self._scan_programs,
            fg_color=ACCENT, hover_color="#2563EB",
            font=("Segoe UI", 13, "bold"), height=40)
        self._scan_btn.pack(side="left")
        self._prog_status = ctk.CTkLabel(btn_frame, text="",
                                          font=("Segoe UI", 12), text_color=MUTED)
        self._prog_status.pack(side="left", padx=16)

        self._prog_scroll = ctk.CTkScrollableFrame(self._content, fg_color="transparent")
        self._prog_scroll.pack(fill="both", expand=True, padx=32, pady=8)
        if self._prog_results:
            self._render_program_list()

    def _scan_programs(self):
        self._scan_btn.configure(state="disabled", text="⏳  Taranıyor...")
        self._prog_status.configure(text="Kayıt defteri okunuyor...")
        self._prog_results = []
        threading.Thread(target=self._do_scan, daemon=True).start()

    def _do_scan(self):
        results = []
        reg_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
        ]
        for reg_path in reg_paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        sub_key = winreg.OpenKey(key, winreg.EnumKey(key, i))
                        name, _ = winreg.QueryValueEx(sub_key, "DisplayName")
                        if name and name.strip():
                            results.append(name.strip())
                    except:
                        pass
            except:
                pass
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                  r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    sub_key = winreg.OpenKey(key, winreg.EnumKey(key, i))
                    name, _ = winreg.QueryValueEx(sub_key, "DisplayName")
                    if name and name.strip():
                        results.append(name.strip())
                except:
                    pass
        except:
            pass

        seen, unique = set(), []
        for r in results:
            if r.lower() not in seen:
                seen.add(r.lower())
                unique.append(r)

        matched = []
        for prog in sorted(unique):
            alt = _match_alternative(prog)
            matched.append({"name": prog, "alt": list(alt) if alt else None})
        self._prog_results = matched
        self.after(0, self._scan_done)

    def _scan_done(self):
        n = len(self._prog_results)
        matched = sum(1 for p in self._prog_results if p["alt"])
        self._prog_status.configure(
            text=f"✅ {n} program bulundu · {matched} alternatif eşleşti",
            text_color=SUCCESS)
        self._scan_btn.configure(state="normal", text="🔄  Yeniden Tara")
        self._render_program_list()

    def _render_program_list(self):
        for w in self._prog_scroll.winfo_children():
            w.destroy()
        if not hasattr(self, "_filter_var"):
            self._filter_var = tk.BooleanVar(value=False)
        top = ctk.CTkFrame(self._prog_scroll, fg_color="transparent")
        top.pack(fill="x", pady=(0, 10))
        ctk.CTkCheckBox(top, text="Sadece Linux alternatifi olanları göster",
                        variable=self._filter_var,
                        command=self._render_program_list,
                        text_color=MUTED).pack(side="left")
        for prog in self._prog_results:
            if self._filter_var.get() and not prog["alt"]:
                continue
            card = ctk.CTkFrame(self._prog_scroll, fg_color=BG_CARD, corner_radius=8)
            card.pack(fill="x", pady=3)
            card.columnconfigure(1, weight=1)
            icon = "✅" if prog["alt"] else "❓"
            ctk.CTkLabel(card, text=icon, font=("Segoe UI", 16), width=36).grid(
                row=0, column=0, padx=10, pady=10)
            ctk.CTkLabel(card, text=prog["name"], font=("Segoe UI", 12),
                         text_color=TEXT, anchor="w").grid(row=0, column=1, sticky="w", pady=10)
            if prog["alt"]:
                alt_name, alt_pkg, alt_desc = prog["alt"][0], prog["alt"][1], prog["alt"][2]
                bg = "#0f2b1f" if alt_pkg else "#2d1000"
                fg = SUCCESS if alt_pkg else DANGER
                alt_frame = ctk.CTkFrame(card, fg_color=bg, corner_radius=6)
                alt_frame.grid(row=0, column=2, padx=10, pady=6)
                ctk.CTkLabel(alt_frame, text=f"🐧 {alt_name}",
                             font=("Segoe UI", 11, "bold"), text_color=fg).pack(padx=10, pady=(4, 0))
                ctk.CTkLabel(alt_frame, text=alt_desc,
                             font=("Segoe UI", 9), text_color=MUTED).pack(padx=10, pady=(0, 4))

    # ── Sayfa 3 · Browser ─────────────────────────────────────────────────────
    def _show_browser(self):
        self._clear_content()
        self._activate_nav("🌐  Browser Verileri")
        self._page_header("Browser Verileri",
                          "Chrome, Firefox ve Edge verilerini dışa aktar")

        scroll = ctk.CTkScrollableFrame(self._content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=32, pady=16)
        browsers = self._detect_browsers()

        if not browsers:
            ctk.CTkLabel(scroll, text="⚠️ Desteklenen tarayıcı profili bulunamadı.",
                         font=("Segoe UI", 14), text_color=WARNING).pack(pady=40)
            return

        self._browser_vars: dict[str, tk.BooleanVar] = {}
        for browser_name, profiles in browsers.items():
            section = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=12)
            section.pack(fill="x", pady=8)
            hdr = ctk.CTkFrame(section, fg_color="transparent")
            hdr.pack(fill="x", padx=16, pady=(14, 6))
            icons = {"Chrome": "🔵", "Firefox": "🟠", "Edge": "🟣", "Brave": "🦁"}
            ctk.CTkLabel(hdr, text=f"{icons.get(browser_name, '🌐')} {browser_name}",
                         font=("Segoe UI", 15, "bold"), text_color=TEXT).pack(side="left")
            for profile_name, profile_path in profiles.items():
                row = ctk.CTkFrame(section, fg_color="transparent")
                row.pack(fill="x", padx=16, pady=4)
                key = f"{browser_name}::{profile_name}"
                var = tk.BooleanVar(value=True)
                self._browser_vars[key] = var
                ctk.CTkCheckBox(row, text=profile_name, variable=var,
                                text_color=TEXT, fg_color=ACCENT).pack(side="left")
                ctk.CTkLabel(row, text=profile_path,
                             font=("Segoe UI", 9), text_color=MUTED).pack(side="left", padx=10)
                try:
                    size = sum(f.stat().st_size for f in Path(profile_path).rglob("*") if f.is_file())
                    ctk.CTkLabel(row, text=self._human(size),
                                 font=("Segoe UI", 10), text_color=MUTED).pack(side="right")
                except:
                    pass
            ctk.CTkFrame(section, height=1, fg_color="#1e3a5f").pack(fill="x", padx=16)
            what_frame = ctk.CTkFrame(section, fg_color="transparent")
            what_frame.pack(fill="x", padx=16, pady=(8, 14))
            ctk.CTkLabel(what_frame, text="Ne aktar?", font=("Segoe UI", 11),
                         text_color=MUTED).pack(side="left")
            for item in ["Yer İmleri", "Geçmiş", "Şifreler*", "Uzantılar"]:
                ctk.CTkLabel(what_frame, text=f"  ✓ {item}",
                             font=("Segoe UI", 11), text_color=SUCCESS).pack(side="left")
        ctk.CTkLabel(scroll,
                     text="* Şifreler şifrelenmiş şekilde kopyalanır; aynı tarayıcıya aktarılabilir.",
                     font=("Segoe UI", 10), text_color=MUTED).pack(anchor="w", pady=(8, 0))

    def _detect_browsers(self) -> dict:
        result = {}
        appdata = os.environ.get("LOCALAPPDATA", "")
        roaming  = os.environ.get("APPDATA", "")
        checks = [
            ("Chrome",  os.path.join(appdata, "Google", "Chrome", "User Data")),
            ("Edge",    os.path.join(appdata, "Microsoft", "Edge", "User Data")),
            ("Brave",   os.path.join(appdata, "BraveSoftware", "Brave-Browser", "User Data")),
            ("Firefox", os.path.join(roaming, "Mozilla", "Firefox", "Profiles")),
        ]
        for browser, base in checks:
            if not os.path.exists(base):
                continue
            profiles = {}
            if browser == "Firefox":
                for entry in os.scandir(base):
                    if entry.is_dir():
                        profiles[entry.name] = entry.path
            else:
                for entry in os.scandir(base):
                    if entry.is_dir() and (entry.name.startswith("Profile") or entry.name == "Default"):
                        profiles[entry.name] = entry.path
            if profiles:
                result[browser] = profiles
        return result

    # ── Sayfa 4 · Config ──────────────────────────────────────────────────────
    def _show_config(self):
        self._clear_content()
        self._activate_nav("⚙️  Sistem Config")
        self._page_header("Sistem Konfigürasyonu",
                          "Ortam değişkenleri, hosts ve SSH anahtarlarını aktar")

        scroll = ctk.CTkScrollableFrame(self._content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=32, pady=16)
        self._config_vars: dict[str, tk.BooleanVar] = {}

        items = [
            ("🔑 SSH Anahtarları",
             "SSH özel ve genel anahtarlarını (.ssh klasörü) aktar",
             os.path.expanduser("~/.ssh"), "ssh_keys"),
            ("📋 Hosts Dosyası",
             "Özel alan adı eşleştirmelerini aktar",
             r"C:\Windows\System32\drivers\etc\hosts", "hosts"),
            ("🌍 Ortam Değişkenleri",
             "PATH ve diğer kullanıcı ortam değişkenlerini JSON olarak aktar",
             None, "env_vars"),
            ("🔒 .gitconfig",
             "Git kullanıcı adı, e-posta ve ayarları",
             os.path.expanduser("~/.gitconfig"), "gitconfig"),
            ("📝 VSCode Ayarları",
             "settings.json, keybindings.json ve uzantı listesi",
             os.path.join(os.environ.get("APPDATA", ""), "Code", "User"), "vscode"),
        ]
        for title, desc, path, key in items:
            card = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=10)
            card.pack(fill="x", pady=6)
            exists = path is None or os.path.exists(path)
            var = tk.BooleanVar(value=exists)
            self._config_vars[key] = var
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=16, pady=12)
            row1 = ctk.CTkFrame(inner, fg_color="transparent")
            row1.pack(fill="x")
            ctk.CTkCheckBox(row1, text=title, variable=var,
                            font=("Segoe UI", 13, "bold"),
                            text_color=TEXT if exists else MUTED,
                            fg_color=ACCENT,
                            state="normal" if exists else "disabled").pack(side="left")
            ctk.CTkLabel(row1,
                         text="✅ Mevcut" if exists else "⚠️ Bulunamadı",
                         font=("Segoe UI", 11),
                         text_color=SUCCESS if exists else WARNING).pack(side="right")
            ctk.CTkLabel(inner, text=desc, font=("Segoe UI", 11),
                         text_color=MUTED, anchor="w").pack(anchor="w", pady=(4, 0))
            if path:
                ctk.CTkLabel(inner, text=f"📂 {path}", font=("Segoe UI", 9),
                             text_color="#475569", wraplength=600).pack(anchor="w")

    # ── Sayfa 5 · Export ──────────────────────────────────────────────────────
    def _show_export(self):
        self._clear_content()
        self._activate_nav("🚀  Export")
        self._page_header("Export & Paketleme",
                          "Seçilen her şeyi ZIP veya klasör olarak paketle")

        main = ctk.CTkFrame(self._content, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=32, pady=16)

        dir_frame = ctk.CTkFrame(main, fg_color=BG_CARD, corner_radius=10)
        dir_frame.pack(fill="x", pady=8)
        dir_inner = ctk.CTkFrame(dir_frame, fg_color="transparent")
        dir_inner.pack(fill="x", padx=16, pady=14)
        ctk.CTkLabel(dir_inner, text="📁 Çıktı Dizini",
                     font=("Segoe UI", 13, "bold"), text_color=TEXT).pack(anchor="w")
        row = ctk.CTkFrame(dir_inner, fg_color="transparent")
        row.pack(fill="x", pady=(6, 0))
        ctk.CTkEntry(row, textvariable=self._output_dir,
                     font=("Segoe UI", 11), height=36).pack(
            side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(row, text="Seç", width=60, height=36,
                      command=self._pick_output_dir).pack(side="right")

        # Uyarı etiketi (BUG FIX #1 için görsel uyarı)
        self._loop_warn = ctk.CTkLabel(dir_inner,
            text="", font=("Segoe UI", 10), text_color=DANGER)
        self._loop_warn.pack(anchor="w", pady=(2, 0))
        self._output_dir.trace_add("write", self._check_dir_loop)

        fmt_frame = ctk.CTkFrame(main, fg_color=BG_CARD, corner_radius=10)
        fmt_frame.pack(fill="x", pady=8)
        fmt_inner = ctk.CTkFrame(fmt_frame, fg_color="transparent")
        fmt_inner.pack(fill="x", padx=16, pady=14)
        ctk.CTkLabel(fmt_inner, text="📦 Paket Formatı",
                     font=("Segoe UI", 13, "bold"), text_color=TEXT).pack(anchor="w")
        self._fmt_var = tk.StringVar(value="zip")
        row2 = ctk.CTkFrame(fmt_inner, fg_color="transparent")
        row2.pack(fill="x", pady=(8, 0))
        for val, lbl, desc in [
            ("zip",    "ZIP Arşivi", "Tek dosya, kolay taşıma"),
            ("folder", "Klasör",     "Direkt erişilebilir yapı"),
        ]:
            f = ctk.CTkFrame(row2, fg_color=BG_CARD2, corner_radius=8)
            f.pack(side="left", padx=(0, 10), ipadx=10, ipady=6)
            ctk.CTkRadioButton(f, text=lbl, variable=self._fmt_var, value=val,
                               text_color=TEXT, fg_color=ACCENT).pack(padx=12, pady=(6, 2))
            ctk.CTkLabel(f, text=desc, font=("Segoe UI", 10),
                         text_color=MUTED).pack(padx=12, pady=(0, 6))

        self._log_box = ctk.CTkTextbox(main, height=200,
                                        font=("Cascadia Code", 11),
                                        fg_color=BG_CARD, text_color="#86efac",
                                        corner_radius=10)
        self._log_box.pack(fill="x", pady=12)
        self._log_box.insert("end", "Export başlatmak için aşağıdaki butona tıkla...\n")
        self._log_box.configure(state="disabled")

        self._progress = ctk.CTkProgressBar(main, height=12, corner_radius=6,
                                             fg_color=BG_CARD, progress_color=ACCENT)
        self._progress.pack(fill="x")
        self._progress.set(0)

        self._export_btn = ctk.CTkButton(
            main, text="🚀  Export Başlat",
            command=self._start_export,
            fg_color=ACCENT, hover_color="#2563EB",
            font=("Segoe UI", 14, "bold"), height=46)
        self._export_btn.pack(fill="x", pady=(12, 0))

    def _check_dir_loop(self, *_):
        """BUG FIX #1: Output dizini, herhangi bir kaynak klasörün içindeyse uyar."""
        out = Path(self._output_dir.get())
        conflicts = []
        for name, var in self._folder_vars.items():
            if var.get():
                src = Path(DEFAULT_FOLDERS.get(name, ""))
                if src.exists() and _is_subpath(out, src):
                    conflicts.append(name)
        for p in self._custom_folders:
            if _is_subpath(out, Path(p)):
                conflicts.append(p)
        if conflicts:
            self._loop_warn.configure(
                text=f"⛔ Döngü tehlikesi! Çıktı dizini kaynak klasörün içinde: {', '.join(conflicts)}")
        else:
            self._loop_warn.configure(text="")

    def _pick_output_dir(self):
        path = filedialog.askdirectory(title="Çıktı dizini seç")
        if path:
            self._output_dir.set(path)

    def _log(self, msg: str):
        self._log_box.configure(state="normal")
        self._log_box.insert("end", f"{msg}\n")
        self._log_box.see("end")
        self._log_box.configure(state="disabled")

    def _start_export(self):
        # BUG FIX #1: Export başlamadan önce son kez döngü kontrolü yap
        out = Path(self._output_dir.get())
        for name, var in self._folder_vars.items():
            if var.get():
                src = Path(DEFAULT_FOLDERS.get(name, ""))
                if src.exists() and _is_subpath(out, src):
                    messagebox.showerror(
                        "Döngü Hatası",
                        f"⛔ Çıktı dizini '{name}' klasörünün içinde!\n\n"
                        f"Kaynak: {src}\nÇıktı:  {out}\n\n"
                        "Lütfen farklı bir çıktı dizini seçin.")
                    return
        for p in self._custom_folders:
            if _is_subpath(out, Path(p)):
                messagebox.showerror(
                    "Döngü Hatası",
                    f"⛔ Çıktı dizini özel klasörün içinde!\n\n"
                    f"Kaynak: {p}\nÇıktı:  {out}\n\n"
                    "Lütfen farklı bir çıktı dizini seçin.")
                return

        self._export_btn.configure(state="disabled", text="⏳  Çalışıyor...")
        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")
        self._log_box.configure(state="disabled")
        self._progress.set(0)
        threading.Thread(target=self._do_export, daemon=True).start()

    def _do_export(self):
        out_base = Path(self._output_dir.get())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = out_base / f"W2L_{timestamp}"
        out_dir.mkdir(parents=True, exist_ok=True)

        steps = []
        for name, var in self._folder_vars.items():
            if var.get():
                src = DEFAULT_FOLDERS.get(name, "")
                if src and os.path.exists(src):
                    steps.append(("folder", name, src, out_dir / "files" / name))
        for path in self._custom_folders:
            if os.path.exists(path):
                steps.append(("folder", Path(path).name, path,
                               out_dir / "files" / Path(path).name))
        if self._prog_results:
            steps.append(("programs", "Program Listesi", None, out_dir / "programs.json"))
        if hasattr(self, "_browser_vars"):
            browsers = self._detect_browsers()
            for key, var in self._browser_vars.items():
                if var.get():
                    browser, profile = key.split("::", 1)
                    if browser in browsers and profile in browsers[browser]:
                        src = browsers[browser][profile]
                        steps.append(("folder", f"{browser}/{profile}",
                                      src, out_dir / "browser" / browser / profile))
        if hasattr(self, "_config_vars"):
            config_map = {
                "ssh_keys":  os.path.expanduser("~/.ssh"),
                "hosts":     r"C:\Windows\System32\drivers\etc\hosts",
                "gitconfig": os.path.expanduser("~/.gitconfig"),
                "vscode":    os.path.join(os.environ.get("APPDATA", ""), "Code", "User"),
            }
            for key, var in self._config_vars.items():
                if var.get() and key in config_map:
                    src = config_map[key]
                    if os.path.exists(src):
                        steps.append(("copy", key, src,
                                      out_dir / "config" / Path(src).name))
                elif var.get() and key == "env_vars":
                    steps.append(("env", "Ortam Değişkenleri", None,
                                   out_dir / "config" / "env_vars.json"))

        total = len(steps)
        if total == 0:
            self.after(0, lambda: self._log("⚠️ Seçili öğe yok!"))
            self.after(0, lambda: self._export_btn.configure(
                state="normal", text="🚀  Export Başlat"))
            return

        self.after(0, lambda: self._log(f"📦 {total} öğe export edilecek...\n"))

        for i, step in enumerate(steps):
            kind, name, src, dst = step
            self.after(0, lambda n=name: self._log(f"  → {n}..."))
            try:
                if kind == "folder":
                    if os.path.isdir(src):
                        self._safe_copy(src, dst, out_dir)
                    elif os.path.isfile(src):
                        Path(dst).parent.mkdir(parents=True, exist_ok=True)
                        try:
                            shutil.copy2(src, dst)
                        except (PermissionError, OSError):
                            self.after(0, lambda n=name: self._log(
                                f"    ⚠️ Atlandı (kilitli): {n}"))
                elif kind == "copy":
                    dst_p = Path(dst)
                    if os.path.isdir(src):
                        self._safe_copy(src, dst_p, out_dir)
                    elif os.path.isfile(src):
                        dst_p.parent.mkdir(parents=True, exist_ok=True)
                        try:
                            shutil.copy2(src, dst_p)
                        except (PermissionError, OSError):
                            self.after(0, lambda n=name: self._log(
                                f"    ⚠️ Atlandı (kilitli): {n}"))
                elif kind == "programs":
                    Path(dst).parent.mkdir(parents=True, exist_ok=True)
                    with open(dst, "w", encoding="utf-8") as f:
                        json.dump(self._prog_results, f, ensure_ascii=False, indent=2)
                elif kind == "env":
                    Path(dst).parent.mkdir(parents=True, exist_ok=True)
                    with open(dst, "w", encoding="utf-8") as f:
                        json.dump(dict(os.environ), f, ensure_ascii=False, indent=2)
                self.after(0, lambda n=name: self._log(f"    ✅ {n} tamamlandı"))
            except Exception as e:
                self.after(0, lambda n=name, err=e: self._log(f"    ❌ {n}: {err}"))

            self.after(0, lambda v=(i + 1) / total: self._progress.set(v))

        if self._fmt_var.get() == "zip":
            self.after(0, lambda: self._log("\n📦 ZIP arşivi oluşturuluyor..."))
            zip_path = out_base / f"W2L_{timestamp}.zip"
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for f in out_dir.rglob("*"):
                    if f.is_file():
                        zf.write(f, f.relative_to(out_dir))
            shutil.rmtree(out_dir, onexc=lambda f, p, e: None)
            self.after(0, lambda p=zip_path: self._log(f"✅ ZIP: {p}"))
        else:
            self.after(0, lambda p=out_dir: self._log(f"✅ Klasör: {p}"))

        readme = out_base / f"W2L_{timestamp}_README.txt"
        with open(readme, "w", encoding="utf-8") as f:
            f.write("Win2Linux Migration Paketi\n")
            f.write(f"Oluşturulma: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"Bilgisayar: {platform.node()}\n\n")
            f.write("İÇERİK\n------\n")
            f.write("files/        → Kişisel dosyalar\n")
            f.write("browser/      → Tarayıcı verileri\n")
            f.write("config/       → Sistem konfigürasyonları\n")
            f.write("programs.json → Windows program listesi ve Linux alternatifleri\n\n")
            f.write("NOT: .git klasörleri, node_modules ve __pycache__ atlandı.\n\n")
            f.write("Linux'ta nasıl kullanılır?\n")
            f.write("1. Arşivi aç\n")
            f.write("2. linux2home.py uygulamasını çalıştır\n")
            f.write("3. Bu ZIP / klasörü linux2home.py ile aç\n")

        self.after(0, lambda: self._log("\n🎉 Export tamamlandı!"))
        self.after(0, lambda: self._progress.set(1.0))
        self.after(0, lambda: self._export_btn.configure(
            state="normal", text="🚀  Export Başlat"))
        self.after(0, lambda: messagebox.showinfo(
            "Tamamlandı", "Migration paketi başarıyla oluşturuldu!"))

    # ── CORE FIX: safe_copy ───────────────────────────────────────────────────
    @staticmethod
    def _safe_copy(src, dst, out_dir: Path = None):
        """
        Klasör kopyalar.
        BUG FIX #1: out_dir verilmişse, src içinde out_dir'e giden yol varsa atlar.
        BUG FIX #2: SKIP_DIR_NAMES'teki klasörleri (.git, node_modules vb.) atlar.
        FEATURE:    Kopyalanamayan klasörü önce zip'lemeyi dener, o da olmazsa atlar.
        """
        src_path = Path(src)

        try:
            if src_path.is_symlink():
                return

            if src_path.is_dir():
                # BUG FIX #1: döngü kontrolü
                if out_dir and _is_subpath(src_path, out_dir):
                    return

                # BUG FIX #2: kilitli/gereksiz klasör adı kontrolü
                if src_path.name in SKIP_DIR_NAMES:
                    return

                os.makedirs(dst, exist_ok=True)

                for item in src_path.iterdir():
                    if item.is_symlink():
                        continue
                    # BUG FIX #2: alt klasör adı kontrolü
                    if item.name in SKIP_DIR_NAMES:
                        continue
                    # BUG FIX #1: alt öğe döngü kontrolü
                    if out_dir and _is_subpath(item, out_dir):
                        continue

                    child_dst = Path(dst) / item.name
                    try:
                        Win2LinuxApp._safe_copy(str(item), str(child_dst), out_dir)
                    except PermissionError:
                        # FEATURE: zip fallback — klasör kopyalanamadıysa zip'le
                        if item.is_dir():
                            try:
                                zip_dst = Path(dst) / f"{item.name}_backup.zip"
                                with zipfile.ZipFile(zip_dst, "w",
                                                     zipfile.ZIP_DEFLATED) as zf:
                                    for f in item.rglob("*"):
                                        if f.is_file() and not f.is_symlink():
                                            try:
                                                zf.write(f, f.relative_to(item))
                                            except (PermissionError, OSError):
                                                pass  # kilitli dosyayı atla
                                # Boş zip oluştuysa sil
                                if zip_dst.stat().st_size < 22:
                                    zip_dst.unlink()
                            except Exception:
                                pass  # zip de olmadı, sessizce geç
                    except OSError:
                        pass
            else:
                Path(dst).parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(src, dst)
                except (PermissionError, OSError):
                    pass

        except Exception:
            pass

    # ── Yardımcılar ───────────────────────────────────────────────────────────
    @staticmethod
    def _human(n: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if n < 1024:
                return f"{n:.1f} {unit}"
            n /= 1024
        return f"{n:.1f} TB"


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if platform.system() != "Windows":
        print("Bu uygulama yalnızca Windows'ta çalışır!")
        sys.exit(1)
    app = Win2LinuxApp()
    app.mainloop()
