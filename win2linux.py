"""
Win2Linux Migrator — v2.2
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
# Yapı: "windows_anahtar": {
#     "name":     "Linux uygulama adı (görüntüleme için)",
#     "desc":     "Açıklama",
#     "packages": {
#         "apt":     "paket-adi",       # Debian/Ubuntu
#         "dnf":     "paket-adi",       # Fedora/RHEL
#         "pacman":  "paket-adi",       # Arch/Manjaro
#         "zypper":  "paket-adi",       # openSUSE
#         "flatpak": "org.app.Id",      # Flathub (evrensel)
#     }
# }
# Bir paket yöneticisinde yoksa o anahtar girilmez.
# "packages" boşsa (desteklenmiyor), dict boş bırakılır.

LINUX_ALTERNATIVES = {
    # ── Ofis ──────────────────────────────────────────────────────────────────
    "microsoft office":  {"name": "LibreOffice",         "desc": "Tam uyumlu ofis paketi",
        "packages": {"apt": "libreoffice", "dnf": "libreoffice", "pacman": "libreoffice-fresh", "zypper": "libreoffice", "flatpak": "org.libreoffice.LibreOffice"}},
    "ms office":         {"name": "LibreOffice",         "desc": "Tam uyumlu ofis paketi",
        "packages": {"apt": "libreoffice", "dnf": "libreoffice", "pacman": "libreoffice-fresh", "zypper": "libreoffice", "flatpak": "org.libreoffice.LibreOffice"}},
    "word":              {"name": "LibreOffice Writer",  "desc": "Word belgelerini açar",
        "packages": {"apt": "libreoffice-writer", "dnf": "libreoffice-writer", "pacman": "libreoffice-fresh", "zypper": "libreoffice-writer", "flatpak": "org.libreoffice.LibreOffice"}},
    "excel":             {"name": "LibreOffice Calc",    "desc": "Excel dosyalarını açar",
        "packages": {"apt": "libreoffice-calc", "dnf": "libreoffice-calc", "pacman": "libreoffice-fresh", "zypper": "libreoffice-calc", "flatpak": "org.libreoffice.LibreOffice"}},
    "powerpoint":        {"name": "LibreOffice Impress", "desc": "Sunum uygulaması",
        "packages": {"apt": "libreoffice-impress", "dnf": "libreoffice-impress", "pacman": "libreoffice-fresh", "zypper": "libreoffice-impress", "flatpak": "org.libreoffice.LibreOffice"}},
    "onenote":           {"name": "Obsidian",            "desc": "Markdown tabanlı not",
        "packages": {"apt": "obsidian", "dnf": "obsidian", "pacman": "obsidian", "flatpak": "md.obsidian.Obsidian"}},
    "outlook":           {"name": "Thunderbird",         "desc": "E-posta istemcisi",
        "packages": {"apt": "thunderbird", "dnf": "thunderbird", "pacman": "thunderbird", "zypper": "thunderbird", "flatpak": "org.mozilla.Thunderbird"}},
    "publisher":         {"name": "Scribus",             "desc": "Masaüstü yayıncılık",
        "packages": {"apt": "scribus", "dnf": "scribus", "pacman": "scribus", "zypper": "scribus", "flatpak": "net.scribus.Scribus"}},
    "visio":             {"name": "Dia",                 "desc": "Diyagram aracı",
        "packages": {"apt": "dia", "dnf": "dia", "pacman": "dia", "zypper": "dia"}},
    "project":           {"name": "ProjectLibre",        "desc": "Proje yönetimi",
        "packages": {"apt": "projectlibre", "flatpak": "com.projectlibre.ProjectLibre"}},
    "microsoft project": {"name": "ProjectLibre",        "desc": "Proje yönetimi",
        "packages": {"apt": "projectlibre", "flatpak": "com.projectlibre.ProjectLibre"}},
    "access":            {"name": "LibreOffice Base",    "desc": "Veritabanı yönetimi",
        "packages": {"apt": "libreoffice-base", "dnf": "libreoffice-base", "pacman": "libreoffice-fresh", "zypper": "libreoffice-base"}},
    "libreoffice":       {"name": "LibreOffice",         "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "libreoffice", "dnf": "libreoffice", "pacman": "libreoffice-fresh", "zypper": "libreoffice", "flatpak": "org.libreoffice.LibreOffice"}},

    # ── Tarayıcılar ────────────────────────────────────────────────────────────
    "google chrome":     {"name": "Chromium",            "desc": "Açık kaynak Chrome tabanlı tarayıcı",
        "packages": {"apt": "chromium-browser", "dnf": "chromium", "pacman": "chromium", "zypper": "chromium", "flatpak": "org.chromium.Chromium"}},
    "microsoft edge":    {"name": "Firefox",             "desc": "Gizlilik odaklı tarayıcı",
        "packages": {"apt": "firefox", "dnf": "firefox", "pacman": "firefox", "zypper": "firefox", "flatpak": "org.mozilla.firefox"}},
    "opera":             {"name": "Vivaldi",             "desc": "Özelleştirilebilir tarayıcı",
        "packages": {"apt": "vivaldi-stable", "dnf": "vivaldi-stable", "pacman": "vivaldi", "flatpak": "com.vivaldi.Vivaldi"}},
    "opera gx":          {"name": "Vivaldi",             "desc": "Özelleştirilebilir tarayıcı",
        "packages": {"apt": "vivaldi-stable", "dnf": "vivaldi-stable", "pacman": "vivaldi", "flatpak": "com.vivaldi.Vivaldi"}},
    "firefox":           {"name": "Firefox",             "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "firefox", "dnf": "firefox", "pacman": "firefox", "zypper": "firefox", "flatpak": "org.mozilla.firefox"}},
    "brave":             {"name": "Brave",               "desc": "Linux sürümü mevcut",
        "packages": {"apt": "brave-browser", "dnf": "brave-browser", "pacman": "brave-bin", "flatpak": "com.brave.Browser"}},
    "vivaldi":           {"name": "Vivaldi",             "desc": "Linux sürümü mevcut",
        "packages": {"apt": "vivaldi-stable", "dnf": "vivaldi-stable", "pacman": "vivaldi", "flatpak": "com.vivaldi.Vivaldi"}},
    "chromium":          {"name": "Chromium",            "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "chromium-browser", "dnf": "chromium", "pacman": "chromium", "zypper": "chromium", "flatpak": "org.chromium.Chromium"}},
    "tor browser":       {"name": "Tor Browser",         "desc": "Anonimlik tarayıcısı",
        "packages": {"apt": "torbrowser-launcher", "dnf": "torbrowser-launcher", "pacman": "torbrowser-launcher", "flatpak": "com.github.micahflee.torbrowser-launcher"}},
    "arc browser":       {"name": "Zen Browser",         "desc": "Modern sekmeli deneyim",
        "packages": {"flatpak": "io.github.zen_browser.zen"}},

    # ── Medya ──────────────────────────────────────────────────────────────────
    "vlc":               {"name": "VLC",                 "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "vlc", "dnf": "vlc", "pacman": "vlc", "zypper": "vlc", "flatpak": "org.videolan.VLC"}},
    "spotify":           {"name": "Spotify",             "desc": "Linux sürümü mevcut",
        "packages": {"apt": "spotify-client", "pacman": "spotify", "flatpak": "com.spotify.Client"}},
    "apple music":       {"name": "Cider",               "desc": "Apple Music istemcisi",
        "packages": {"flatpak": "sh.cider.Cider"}},
    "itunes":            {"name": "Rhythmbox",           "desc": "Müzik çalar",
        "packages": {"apt": "rhythmbox", "dnf": "rhythmbox", "pacman": "rhythmbox", "zypper": "rhythmbox", "flatpak": "org.gnome.Rhythmbox3"}},
    "windows media":     {"name": "VLC",                 "desc": "Evrensel medya oynatıcı",
        "packages": {"apt": "vlc", "dnf": "vlc", "pacman": "vlc", "zypper": "vlc", "flatpak": "org.videolan.VLC"}},
    "foobar":            {"name": "DeaDBeeF",            "desc": "Hafif müzik çalar",
        "packages": {"apt": "deadbeef", "dnf": "deadbeef", "pacman": "deadbeef", "flatpak": "io.gitlab.deadbeef_player.DeaDBeeF"}},
    "musicbee":          {"name": "Rhythmbox",           "desc": "Müzik yöneticisi",
        "packages": {"apt": "rhythmbox", "dnf": "rhythmbox", "pacman": "rhythmbox", "flatpak": "org.gnome.Rhythmbox3"}},
    "potplayer":         {"name": "mpv",                 "desc": "Video oynatıcı",
        "packages": {"apt": "mpv", "dnf": "mpv", "pacman": "mpv", "zypper": "mpv", "flatpak": "io.mpv.Mpv"}},
    "mpc-hc":            {"name": "mpv",                 "desc": "Hafif video oynatıcı",
        "packages": {"apt": "mpv", "dnf": "mpv", "pacman": "mpv", "zypper": "mpv", "flatpak": "io.mpv.Mpv"}},
    "mpv":               {"name": "mpv",                 "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "mpv", "dnf": "mpv", "pacman": "mpv", "zypper": "mpv", "flatpak": "io.mpv.Mpv"}},
    "kodi":              {"name": "Kodi",                "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "kodi", "dnf": "kodi", "pacman": "kodi", "flatpak": "tv.kodi.Kodi"}},
    "plex":              {"name": "Jellyfin",            "desc": "Medya sunucusu",
        "packages": {"apt": "jellyfin", "dnf": "jellyfin", "flatpak": "com.github.iwalton3.jellyfin-media-player"}},

    # ── Ses Üretim ────────────────────────────────────────────────────────────
    "audacity":          {"name": "Audacity",            "desc": "Ses düzenleyici",
        "packages": {"apt": "audacity", "dnf": "audacity", "pacman": "audacity", "zypper": "audacity", "flatpak": "org.audacityteam.Audacity"}},
    "fl studio":         {"name": "LMMS",                "desc": "Beat yapım aracı",
        "packages": {"apt": "lmms", "dnf": "lmms", "pacman": "lmms", "zypper": "lmms", "flatpak": "io.lmms.LMMS"}},
    "cubase":            {"name": "Ardour",              "desc": "DAW alternatifi",
        "packages": {"apt": "ardour", "dnf": "ardour", "pacman": "ardour", "flatpak": "org.ardour.Ardour"}},
    "reaper":            {"name": "REAPER",              "desc": "Linux sürümü mevcut (manuel kurulum)",
        "packages": {}},
    "ableton":           {"name": "Bitwig Studio",       "desc": "Müzik prodüksiyonu",
        "packages": {"flatpak": "com.bitwig.BitwigStudio"}},

    # ── Video Kayıt / Yayın ───────────────────────────────────────────────────
    "obs studio":        {"name": "OBS Studio",          "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "obs-studio", "dnf": "obs-studio", "pacman": "obs-studio", "zypper": "obs-studio", "flatpak": "com.obsproject.Studio"}},
    "obs":               {"name": "OBS Studio",          "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "obs-studio", "dnf": "obs-studio", "pacman": "obs-studio", "zypper": "obs-studio", "flatpak": "com.obsproject.Studio"}},
    "bandicam":          {"name": "OBS Studio",          "desc": "Ekran kayıt aracı",
        "packages": {"apt": "obs-studio", "dnf": "obs-studio", "pacman": "obs-studio", "flatpak": "com.obsproject.Studio"}},
    "camtasia":          {"name": "Kdenlive",            "desc": "Video kayıt & düzenleme",
        "packages": {"apt": "kdenlive", "dnf": "kdenlive", "pacman": "kdenlive", "zypper": "kdenlive", "flatpak": "org.kde.kdenlive"}},

    # ── Grafik & Tasarım ──────────────────────────────────────────────────────
    "adobe photoshop":   {"name": "GIMP",                "desc": "Güçlü görsel editör",
        "packages": {"apt": "gimp", "dnf": "gimp", "pacman": "gimp", "zypper": "gimp", "flatpak": "org.gimp.GIMP"}},
    "photoshop":         {"name": "GIMP",                "desc": "Güçlü görsel editör",
        "packages": {"apt": "gimp", "dnf": "gimp", "pacman": "gimp", "zypper": "gimp", "flatpak": "org.gimp.GIMP"}},
    "adobe illustrator": {"name": "Inkscape",            "desc": "Vektör grafik editörü",
        "packages": {"apt": "inkscape", "dnf": "inkscape", "pacman": "inkscape", "zypper": "inkscape", "flatpak": "org.inkscape.Inkscape"}},
    "illustrator":       {"name": "Inkscape",            "desc": "Vektör grafik editörü",
        "packages": {"apt": "inkscape", "dnf": "inkscape", "pacman": "inkscape", "zypper": "inkscape", "flatpak": "org.inkscape.Inkscape"}},
    "adobe premiere":    {"name": "Kdenlive",            "desc": "Video editörü",
        "packages": {"apt": "kdenlive", "dnf": "kdenlive", "pacman": "kdenlive", "zypper": "kdenlive", "flatpak": "org.kde.kdenlive"}},
    "premiere":          {"name": "Kdenlive",            "desc": "Video editörü",
        "packages": {"apt": "kdenlive", "dnf": "kdenlive", "pacman": "kdenlive", "zypper": "kdenlive", "flatpak": "org.kde.kdenlive"}},
    "after effects":     {"name": "Natron",              "desc": "Efekt & kompozisyon",
        "packages": {"apt": "natron", "dnf": "natron", "pacman": "natron", "flatpak": "fr.natron.Natron"}},
    "cinema 4d":         {"name": "Blender",             "desc": "3D modelleme",
        "packages": {"apt": "blender", "dnf": "blender", "pacman": "blender", "zypper": "blender", "flatpak": "org.blender.Blender"}},
    "maya":              {"name": "Blender",             "desc": "3D animasyon",
        "packages": {"apt": "blender", "dnf": "blender", "pacman": "blender", "zypper": "blender", "flatpak": "org.blender.Blender"}},
    "zbrush":            {"name": "Blender Sculpt",      "desc": "Dijital heykel",
        "packages": {"apt": "blender", "dnf": "blender", "pacman": "blender", "zypper": "blender", "flatpak": "org.blender.Blender"}},
    "paint tool sai":    {"name": "Krita",               "desc": "Dijital çizim",
        "packages": {"apt": "krita", "dnf": "krita", "pacman": "krita", "zypper": "krita", "flatpak": "org.kde.krita"}},
    "clip studio paint": {"name": "Krita",               "desc": "Manga & çizim",
        "packages": {"apt": "krita", "dnf": "krita", "pacman": "krita", "zypper": "krita", "flatpak": "org.kde.krita"}},
    "paint.net":         {"name": "Pinta",               "desc": "Basit görsel editör",
        "packages": {"apt": "pinta", "dnf": "pinta", "pacman": "pinta", "flatpak": "com.github.PintaProject.Pinta"}},
    "adobe xd":          {"name": "Penpot",              "desc": "UI/UX tasarım aracı (web)",
        "packages": {"flatpak": "design.penpot.Penpot"}},
    "lightroom":         {"name": "Darktable",           "desc": "Fotoğraf düzenleme",
        "packages": {"apt": "darktable", "dnf": "darktable", "pacman": "darktable", "zypper": "darktable", "flatpak": "org.darktable.Darktable"}},
    "adobe lightroom":   {"name": "Darktable",           "desc": "RAW fotoğraf işleme",
        "packages": {"apt": "darktable", "dnf": "darktable", "pacman": "darktable", "zypper": "darktable", "flatpak": "org.darktable.Darktable"}},
    "adobe acrobat":     {"name": "Okular",              "desc": "PDF okuyucu & editör",
        "packages": {"apt": "okular", "dnf": "okular", "pacman": "okular", "zypper": "okular", "flatpak": "org.kde.okular"}},
    "acrobat":           {"name": "Okular",              "desc": "PDF okuyucu",
        "packages": {"apt": "okular", "dnf": "okular", "pacman": "okular", "zypper": "okular", "flatpak": "org.kde.okular"}},
    "figma":             {"name": "Figma",               "desc": "Linux sürümü mevcut",
        "packages": {"flatpak": "io.github.Figma_Linux.figma_linux"}},
    "blender":           {"name": "Blender",             "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "blender", "dnf": "blender", "pacman": "blender", "zypper": "blender", "flatpak": "org.blender.Blender"}},
    "inkscape":          {"name": "Inkscape",            "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "inkscape", "dnf": "inkscape", "pacman": "inkscape", "zypper": "inkscape", "flatpak": "org.inkscape.Inkscape"}},
    "gimp":              {"name": "GIMP",                "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "gimp", "dnf": "gimp", "pacman": "gimp", "zypper": "gimp", "flatpak": "org.gimp.GIMP"}},
    "krita":             {"name": "Krita",               "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "krita", "dnf": "krita", "pacman": "krita", "zypper": "krita", "flatpak": "org.kde.krita"}},
    "darktable":         {"name": "Darktable",           "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "darktable", "dnf": "darktable", "pacman": "darktable", "zypper": "darktable", "flatpak": "org.darktable.Darktable"}},

    # ── Geliştirme Ortamları ──────────────────────────────────────────────────
    "visual studio code":{"name": "VS Code",             "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "code", "dnf": "code", "pacman": "code", "zypper": "code", "flatpak": "com.visualstudio.code"}},
    "visual studio":     {"name": "VS Code",             "desc": "IDE alternatifi",
        "packages": {"apt": "code", "dnf": "code", "pacman": "code", "flatpak": "com.visualstudio.code"}},
    "notepad++":         {"name": "Kate",                "desc": "Güçlü metin editörü",
        "packages": {"apt": "kate", "dnf": "kate", "pacman": "kate", "zypper": "kate", "flatpak": "org.kde.kate"}},
    "sublime text":      {"name": "Kate",                "desc": "Metin editörü",
        "packages": {"apt": "kate", "dnf": "kate", "pacman": "kate", "zypper": "kate", "flatpak": "org.kde.kate"}},
    "atom":              {"name": "VS Code",             "desc": "Modern editör",
        "packages": {"apt": "code", "dnf": "code", "pacman": "code", "flatpak": "com.visualstudio.code"}},
    "intellij":          {"name": "IntelliJ IDEA",       "desc": "Linux sürümü mevcut",
        "packages": {"pacman": "intellij-idea-community-edition", "flatpak": "com.jetbrains.IntelliJ-IDEA-Community"}},
    "pycharm":           {"name": "PyCharm",             "desc": "Linux sürümü mevcut",
        "packages": {"pacman": "pycharm-community", "flatpak": "com.jetbrains.PyCharm-Community"}},
    "rider":             {"name": "JetBrains Rider",     "desc": "C# IDE",
        "packages": {"flatpak": "com.jetbrains.Rider"}},
    "android studio":    {"name": "Android Studio",      "desc": "Linux sürümü mevcut",
        "packages": {"pacman": "android-studio", "flatpak": "com.google.AndroidStudio"}},
    "eclipse":           {"name": "Eclipse",             "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "eclipse", "dnf": "eclipse", "pacman": "eclipse-java", "flatpak": "org.eclipse.Java"}},
    "arduino":           {"name": "Arduino IDE",         "desc": "Linux sürümü mevcut",
        "packages": {"apt": "arduino", "dnf": "arduino", "pacman": "arduino", "flatpak": "cc.arduino.IDE2"}},
    "putty":             {"name": "OpenSSH (built-in)",  "desc": "Linux'ta yerleşik",
        "packages": {"apt": "openssh-client", "dnf": "openssh-clients", "pacman": "openssh", "zypper": "openssh"}},
    "winscp":            {"name": "FileZilla",           "desc": "Dosya aktarımı",
        "packages": {"apt": "filezilla", "dnf": "filezilla", "pacman": "filezilla", "zypper": "filezilla", "flatpak": "org.filezilla_project.FileZilla"}},
    "github desktop":    {"name": "GitHub Desktop",      "desc": "Linux sürümü mevcut",
        "packages": {"apt": "github-desktop", "pacman": "github-desktop-bin", "flatpak": "io.github.shiftey.Desktop"}},
    "gitkraken":         {"name": "GitKraken",           "desc": "Git GUI istemcisi",
        "packages": {"apt": "gitkraken", "dnf": "gitkraken", "pacman": "gitkraken", "flatpak": "com.axosoft.GitKraken"}},
    "postman":           {"name": "Postman",             "desc": "Linux sürümü mevcut",
        "packages": {"apt": "postman", "dnf": "postman", "pacman": "postman-bin", "flatpak": "com.getpostman.Postman"}},
    "insomnia":          {"name": "Insomnia",            "desc": "Linux sürümü mevcut",
        "packages": {"apt": "insomnia", "pacman": "insomnia-bin", "flatpak": "rest.insomnia.Insomnia"}},
    "dbeaver":           {"name": "DBeaver",             "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "dbeaver-ce", "dnf": "dbeaver-ce", "pacman": "dbeaver", "flatpak": "io.dbeaver.DBeaverCommunity"}},
    "docker desktop":    {"name": "Docker",              "desc": "Linux'ta yerel destek",
        "packages": {"apt": "docker.io", "dnf": "docker-ce", "pacman": "docker", "zypper": "docker"}},
    "git":               {"name": "Git",                 "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "git", "dnf": "git", "pacman": "git", "zypper": "git"}},
    "node.js":           {"name": "Node.js",             "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "nodejs", "dnf": "nodejs", "pacman": "nodejs", "zypper": "nodejs"}},
    "python":            {"name": "Python",              "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "python3", "dnf": "python3", "pacman": "python", "zypper": "python3"}},
    "wireshark":         {"name": "Wireshark",           "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "wireshark", "dnf": "wireshark", "pacman": "wireshark-qt", "zypper": "wireshark", "flatpak": "org.wireshark.Wireshark"}},
    "virtualbox":        {"name": "VirtualBox",          "desc": "Linux sürümü mevcut",
        "packages": {"apt": "virtualbox", "dnf": "VirtualBox", "pacman": "virtualbox", "zypper": "virtualbox", "flatpak": "org.virtualbox.VirtualBox"}},
    "vmware":            {"name": "VirtualBox / QEMU",   "desc": "Sanallaştırma",
        "packages": {"apt": "virtualbox", "dnf": "VirtualBox", "pacman": "virtualbox", "zypper": "virtualbox"}},
    "hyper-v":           {"name": "KVM / QEMU",          "desc": "Linux yerleşik VM",
        "packages": {"apt": "qemu-kvm", "dnf": "qemu-kvm", "pacman": "qemu", "zypper": "qemu-kvm"}},
    "xampp":             {"name": "LAMP Stack",          "desc": "Web sunucu paketi",
        "packages": {"apt": "apache2", "dnf": "httpd", "pacman": "apache"}},
    "wamp":              {"name": "LAMP Stack",          "desc": "Apache + PHP + MariaDB",
        "packages": {"apt": "apache2", "dnf": "httpd", "pacman": "apache"}},

    # ── Sistem Araçları ───────────────────────────────────────────────────────
    "7-zip":             {"name": "p7zip",               "desc": "Arşiv aracı",
        "packages": {"apt": "p7zip-full", "dnf": "p7zip", "pacman": "p7zip", "zypper": "p7zip"}},
    "winrar":            {"name": "p7zip",               "desc": "Arşiv aracı",
        "packages": {"apt": "p7zip-full", "dnf": "p7zip", "pacman": "p7zip", "zypper": "p7zip"}},
    "ccleaner":          {"name": "BleachBit",           "desc": "Sistem temizleyici",
        "packages": {"apt": "bleachbit", "dnf": "bleachbit", "pacman": "bleachbit", "zypper": "bleachbit", "flatpak": "org.bleachbit.BleachBit"}},
    "rainmeter":         {"name": "Conky",               "desc": "Masaüstü widget sistemi",
        "packages": {"apt": "conky", "dnf": "conky", "pacman": "conky", "zypper": "conky"}},
    "everything":        {"name": "fd",                  "desc": "Terminal tabanlı arama",
        "packages": {"apt": "fd-find", "dnf": "fd-find", "pacman": "fd", "zypper": "fd"}},
    "hwmonitor":         {"name": "Psensor",             "desc": "Donanım izleme",
        "packages": {"apt": "psensor", "dnf": "psensor", "pacman": "psensor"}},
    "cpu-z":             {"name": "CPU-X",               "desc": "CPU bilgisi",
        "packages": {"apt": "cpu-x", "dnf": "cpu-x", "pacman": "cpu-x", "flatpak": "io.github.thetumultuousunicornofdarkness.cpu-x"}},
    "msi afterburner":   {"name": "CoreCtrl",            "desc": "GPU hız aşırtma",
        "packages": {"apt": "corectrl", "dnf": "corectrl", "pacman": "corectrl"}},
    "autohotkey":        {"name": "AutoKey",             "desc": "Tuş makroları",
        "packages": {"apt": "autokey-gtk", "dnf": "autokey", "pacman": "autokey", "flatpak": "com.github.autokey.AutoKey"}},
    "process hacker":    {"name": "btop",                "desc": "Sistem süreç yöneticisi",
        "packages": {"apt": "btop", "dnf": "btop", "pacman": "btop", "zypper": "btop", "flatpak": "io.missioncenter.MissionCenter"}},
    "task manager":      {"name": "btop",                "desc": "Sistem izleme",
        "packages": {"apt": "btop", "dnf": "btop", "pacman": "btop", "zypper": "btop"}},
    "rufus":             {"name": "Ventoy",              "desc": "USB boot aracı",
        "packages": {"apt": "ventoy", "pacman": "ventoy", "flatpak": "org.gabmus.gfeeds"}},
    "balena etcher":     {"name": "Etcher",              "desc": "USB yazdırma aracı",
        "packages": {"apt": "balena-etcher", "dnf": "balena-etcher", "pacman": "balena-etcher-bin", "flatpak": "io.balena.Etcher"}},
    "crystaldiskinfo":   {"name": "GSmartControl",       "desc": "Disk sağlığı izleyici",
        "packages": {"apt": "gsmartcontrol", "dnf": "gsmartcontrol", "pacman": "gsmartcontrol", "flatpak": "net.sourceforge.gsmartcontrol"}},

    # ── İletişim ──────────────────────────────────────────────────────────────
    "discord":           {"name": "Discord",             "desc": "Linux sürümü mevcut",
        "packages": {"apt": "discord", "dnf": "discord", "pacman": "discord", "flatpak": "com.discordapp.Discord"}},
    "slack":             {"name": "Slack",               "desc": "Linux sürümü mevcut",
        "packages": {"apt": "slack-desktop", "dnf": "slack", "pacman": "slack-desktop", "flatpak": "com.slack.Slack"}},
    "telegram":          {"name": "Telegram",            "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "telegram-desktop", "dnf": "telegram-desktop", "pacman": "telegram-desktop", "zypper": "telegram-desktop", "flatpak": "org.telegram.desktop"}},
    "zoom":              {"name": "Zoom",                "desc": "Linux sürümü mevcut",
        "packages": {"apt": "zoom", "dnf": "zoom", "pacman": "zoom", "flatpak": "us.zoom.Zoom"}},
    "microsoft teams":   {"name": "MS Teams",            "desc": "Linux sürümü mevcut",
        "packages": {"apt": "teams", "dnf": "teams", "pacman": "teams", "flatpak": "com.microsoft.Teams"}},
    "skype":             {"name": "Skype",               "desc": "Linux sürümü mevcut",
        "packages": {"apt": "skype", "dnf": "skype", "pacman": "skype", "flatpak": "com.skype.Client"}},
    "whatsapp":          {"name": "Signal",              "desc": "Gizlilik odaklı alternatif",
        "packages": {"apt": "signal-desktop", "dnf": "signal-desktop", "pacman": "signal-desktop", "flatpak": "org.signal.Signal"}},
    "signal":            {"name": "Signal",              "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "signal-desktop", "dnf": "signal-desktop", "pacman": "signal-desktop", "flatpak": "org.signal.Signal"}},
    "element":           {"name": "Element",             "desc": "Matrix istemcisi",
        "packages": {"apt": "element-desktop", "dnf": "element-desktop", "pacman": "element-desktop", "flatpak": "im.riot.Riot"}},

    # ── Güvenlik & VPN ────────────────────────────────────────────────────────
    "bitwarden":         {"name": "Bitwarden",           "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "bitwarden", "dnf": "bitwarden", "pacman": "bitwarden", "flatpak": "com.bitwarden.desktop"}},
    "keepass":           {"name": "KeePassXC",           "desc": "Şifre yöneticisi",
        "packages": {"apt": "keepassxc", "dnf": "keepassxc", "pacman": "keepassxc", "zypper": "keepassxc", "flatpak": "org.keepassxc.KeePassXC"}},
    "malwarebytes":      {"name": "ClamAV",              "desc": "Açık kaynak antivirüs",
        "packages": {"apt": "clamav", "dnf": "clamav", "pacman": "clamav", "zypper": "clamav"}},
    "nordvpn":           {"name": "NordVPN",             "desc": "Linux sürümü mevcut",
        "packages": {"apt": "nordvpn", "dnf": "nordvpn", "pacman": "nordvpn-bin"}},
    "expressvpn":        {"name": "ProtonVPN",           "desc": "VPN alternatifi",
        "packages": {"apt": "protonvpn", "dnf": "protonvpn", "pacman": "protonvpn", "flatpak": "com.protonvpn.www"}},
    "protonvpn":         {"name": "ProtonVPN",           "desc": "Linux sürümü mevcut",
        "packages": {"apt": "protonvpn", "dnf": "protonvpn", "pacman": "protonvpn", "flatpak": "com.protonvpn.www"}},
    "mullvad":           {"name": "Mullvad VPN",         "desc": "Linux sürümü mevcut",
        "packages": {"apt": "mullvad-vpn", "dnf": "mullvad-vpn", "pacman": "mullvad-vpn-bin", "flatpak": "net.mullvad.MullvadVPN"}},
    "openvpn":           {"name": "OpenVPN",             "desc": "VPN istemcisi",
        "packages": {"apt": "openvpn", "dnf": "openvpn", "pacman": "openvpn", "zypper": "openvpn"}},
    "tailscale":         {"name": "Tailscale",           "desc": "Linux sürümü mevcut",
        "packages": {"apt": "tailscale", "dnf": "tailscale", "pacman": "tailscale"}},

    # ── Uzak Masaüstü & Senkronizasyon ───────────────────────────────────────
    "teamviewer":        {"name": "RustDesk",            "desc": "Açık kaynak uzak masaüstü",
        "packages": {"apt": "rustdesk", "dnf": "rustdesk", "pacman": "rustdesk-bin", "flatpak": "com.rustdesk.RustDesk"}},
    "anydesk":           {"name": "AnyDesk",             "desc": "Linux sürümü mevcut",
        "packages": {"apt": "anydesk", "dnf": "anydesk", "pacman": "anydesk-bin", "flatpak": "com.anydesk.Anydesk"}},
    "rustdesk":          {"name": "RustDesk",            "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "rustdesk", "dnf": "rustdesk", "pacman": "rustdesk-bin", "flatpak": "com.rustdesk.RustDesk"}},
    "syncthing":         {"name": "Syncthing",           "desc": "Dosya senkronizasyonu",
        "packages": {"apt": "syncthing", "dnf": "syncthing", "pacman": "syncthing", "zypper": "syncthing", "flatpak": "me.kozec.syncthingtk"}},
    "onedrive":          {"name": "Nextcloud",           "desc": "Bulut depolama",
        "packages": {"apt": "nextcloud-desktop", "dnf": "nextcloud-client", "pacman": "nextcloud-client", "flatpak": "com.nextcloud.desktopclient.nextcloud"}},
    "dropbox":           {"name": "Dropbox",             "desc": "Linux sürümü mevcut",
        "packages": {"apt": "dropbox", "dnf": "dropbox", "pacman": "dropbox", "flatpak": "com.dropbox.Client"}},
    "google drive":      {"name": "rclone",              "desc": "Google Drive bağlantısı",
        "packages": {"apt": "rclone", "dnf": "rclone", "pacman": "rclone", "zypper": "rclone"}},
    "mega":              {"name": "MEGAsync",            "desc": "Bulut depolama",
        "packages": {"apt": "megasync", "dnf": "megasync", "pacman": "megasync", "flatpak": "nz.mega.MEGAsync"}},

    # ── Oyun ──────────────────────────────────────────────────────────────────
    "steam":             {"name": "Steam",               "desc": "Linux'ta çalışır",
        "packages": {"apt": "steam", "dnf": "steam", "pacman": "steam", "flatpak": "com.valvesoftware.Steam"}},
    "epic games":        {"name": "Heroic Games Launcher","desc": "Epic & GOG alternatif launcher",
        "packages": {"apt": "heroic", "dnf": "heroic", "pacman": "heroic-games-launcher-bin", "flatpak": "com.heroicgameslauncher.hgl"}},
    "gog galaxy":        {"name": "Heroic Games Launcher","desc": "GOG kütüphanesi",
        "packages": {"apt": "heroic", "dnf": "heroic", "pacman": "heroic-games-launcher-bin", "flatpak": "com.heroicgameslauncher.hgl"}},
    "battle.net":        {"name": "Lutris",              "desc": "Blizzard oyunları için",
        "packages": {"apt": "lutris", "dnf": "lutris", "pacman": "lutris", "flatpak": "net.lutris.Lutris"}},
    "minecraft launcher":{"name": "Prism Launcher",      "desc": "Minecraft launcher",
        "packages": {"apt": "prismlauncher", "dnf": "prismlauncher", "pacman": "prismlauncher", "flatpak": "org.prismlauncher.PrismLauncher"}},
    "curseforge":        {"name": "Prism Launcher",      "desc": "Minecraft mod yönetimi",
        "packages": {"apt": "prismlauncher", "dnf": "prismlauncher", "pacman": "prismlauncher", "flatpak": "org.prismlauncher.PrismLauncher"}},
    "osu!":              {"name": "osu!lazer",           "desc": "Linux sürümü mevcut",
        "packages": {"pacman": "osu-lazer-bin", "flatpak": "sh.ppy.osu"}},
    "roblox":            {"name": "Sober",               "desc": "Native Linux Roblox istemcisi",
        "packages": {"flatpak": "org.vinegarhq.Sober"}},
    "retroarch":         {"name": "RetroArch",           "desc": "Emülasyon platformu",
        "packages": {"apt": "retroarch", "dnf": "retroarch", "pacman": "retroarch", "zypper": "retroarch", "flatpak": "org.libretro.RetroArch"}},
    "valorant":          {"name": "— Desteklenmiyor",    "desc": "Vanguard kernel-level AC, Linux'ta yok",
        "packages": {}},
    "riot vanguard":     {"name": "— Desteklenmiyor",    "desc": "Kernel-level AC, Linux'ta çalışmaz",
        "packages": {}},

    # ── Not Alma & Verimlilik ─────────────────────────────────────────────────
    "notion":            {"name": "Notion",              "desc": "Linux istemcisi mevcut",
        "packages": {"apt": "notion-app", "pacman": "notion-app-electron", "flatpak": "io.github.davidoc.notion"}},
    "obsidian":          {"name": "Obsidian",            "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "obsidian", "dnf": "obsidian", "pacman": "obsidian", "flatpak": "md.obsidian.Obsidian"}},
    "joplin":            {"name": "Joplin",              "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "joplin", "pacman": "joplin", "flatpak": "net.cozic.joplin_desktop"}},
    "anki":              {"name": "Anki",                "desc": "Kart tabanlı öğrenme",
        "packages": {"apt": "anki", "dnf": "anki", "pacman": "anki", "flatpak": "net.ankiweb.Anki"}},
    "draw.io":           {"name": "draw.io",             "desc": "Diyagram oluşturucu",
        "packages": {"flatpak": "com.jgraph.drawio.desktop"}},
    "amazon kindle":     {"name": "Calibre",             "desc": "E-kitap yöneticisi",
        "packages": {"apt": "calibre", "dnf": "calibre", "pacman": "calibre", "zypper": "calibre", "flatpak": "com.calibre_ebook.calibre"}},
    "calibre":           {"name": "Calibre",             "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "calibre", "dnf": "calibre", "pacman": "calibre", "zypper": "calibre", "flatpak": "com.calibre_ebook.calibre"}},

    # ── Mühendislik / CAD ─────────────────────────────────────────────────────
    "solidworks":        {"name": "FreeCAD",             "desc": "Açık kaynak CAD",
        "packages": {"apt": "freecad", "dnf": "freecad", "pacman": "freecad", "zypper": "freecad", "flatpak": "org.freecad.FreeCAD"}},
    "autocad":           {"name": "FreeCAD",             "desc": "2D/3D CAD alternatifi",
        "packages": {"apt": "freecad", "dnf": "freecad", "pacman": "freecad", "zypper": "freecad", "flatpak": "org.freecad.FreeCAD"}},
    "fusion 360":        {"name": "FreeCAD",             "desc": "3D modelleme",
        "packages": {"apt": "freecad", "dnf": "freecad", "pacman": "freecad", "zypper": "freecad", "flatpak": "org.freecad.FreeCAD"}},
    "matlab":            {"name": "GNU Octave",          "desc": "Matematiksel analiz",
        "packages": {"apt": "octave", "dnf": "octave", "pacman": "octave", "zypper": "octave", "flatpak": "org.octave.Octave"}},

    # ── Torrent & Dosya Paylaşımı ─────────────────────────────────────────────
    "qbittorrent":       {"name": "qBittorrent",         "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "qbittorrent", "dnf": "qbittorrent", "pacman": "qbittorrent", "zypper": "qbittorrent", "flatpak": "org.qbittorrent.qBittorrent"}},
    "utorrent":          {"name": "qBittorrent",         "desc": "Açık kaynak alternatif",
        "packages": {"apt": "qbittorrent", "dnf": "qbittorrent", "pacman": "qbittorrent", "zypper": "qbittorrent", "flatpak": "org.qbittorrent.qBittorrent"}},
    "filezilla":         {"name": "FileZilla",           "desc": "Zaten Linux'ta var!",
        "packages": {"apt": "filezilla", "dnf": "filezilla", "pacman": "filezilla", "zypper": "filezilla", "flatpak": "org.filezilla_project.FileZilla"}},
    "teracopy":          {"name": "rsync",               "desc": "Hızlı dosya kopyalama",
        "packages": {"apt": "rsync", "dnf": "rsync", "pacman": "rsync", "zypper": "rsync"}},
    "winmerge":          {"name": "Meld",                "desc": "Dosya karşılaştırma",
        "packages": {"apt": "meld", "dnf": "meld", "pacman": "meld", "zypper": "meld", "flatpak": "org.gnome.meld"}},

    # ── Geliştirici Araçları (Runtime/SDK) ───────────────────────────────────
    "microsoft .net":    {"name": ".NET SDK",            "desc": "Linux .NET desteği tam",
        "packages": {"apt": "dotnet-sdk-8", "dnf": "dotnet-sdk-8.0", "pacman": "dotnet-sdk-8", "zypper": "dotnet-sdk-8"}},
    "visual c++":        {"name": "GCC / Clang",         "desc": "Linux derleyici araçları",
        "packages": {"apt": "build-essential", "dnf": "gcc gcc-c++", "pacman": "base-devel", "zypper": "gcc gcc-c++"}},
    "java runtime":      {"name": "OpenJDK",             "desc": "Java runtime",
        "packages": {"apt": "openjdk-21-jdk", "dnf": "java-21-openjdk", "pacman": "jdk-openjdk", "zypper": "java-21-openjdk"}},
    "golang":            {"name": "Go",                  "desc": "Linux desteği mevcut",
        "packages": {"apt": "golang", "dnf": "golang", "pacman": "go", "zypper": "go"}},
    "rust":              {"name": "Rust",                "desc": "Linux desteği mevcut",
        "packages": {"apt": "rustc", "dnf": "rust", "pacman": "rust", "zypper": "rust"}},
}

# ── Atlanacak dosya/klasör kalıpları ─────────────────────────────────────────
_SKIP_PATTERNS = [
    "kinect for windows speech", "sdk arm64", "wpt redistributable",
    "wptx64", "winrt intellisense", "windows app certification",
    "universal crt", "clickonce bootstrapper", "kits configuration",
    "diagnoticshub", "icecap_collection", "launcher prerequisites",
    "setup 0.0", "${{"  ,
]

SKIP_DIR_NAMES = {
    "Müziğim", "Resimlerim", "Videolarım",
    "My Music", "My Pictures", "My Videos",
    "Application Data", "Local Settings",
    ".git", ".hg", ".svn",
    "node_modules", "__pycache__",
    ".venv", "venv",
}


def _is_subpath(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _match_alternative(prog_name: str) -> dict | None:
    """Windows program adını arayıp LINUX_ALTERNATIVES dict döndürür."""
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
        ctk.CTkLabel(logo_frame, text="Migrator v2.2", font=("Segoe UI", 12),
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

        ctk.CTkLabel(sidebar, text=f"v2.2 · {platform.node()}",
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

    # ── Sayfa 1 · Dosyalar (değişmedi) ───────────────────────────────────────
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
            entry: dict = {"name": prog, "alt": None}
            if alt:
                # Yeni JSON yapısı: alt artık dict
                entry["alt"] = {
                    "name":     alt["name"],
                    "desc":     alt["desc"],
                    "packages": alt["packages"],   # {"apt":..., "dnf":..., "pacman":..., "flatpak":...}
                }
            matched.append(entry)
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
                alt = prog["alt"]
                has_pkgs = bool(alt["packages"])
                bg = "#0f2b1f" if has_pkgs else "#2d1000"
                fg = SUCCESS if has_pkgs else DANGER
                alt_frame = ctk.CTkFrame(card, fg_color=bg, corner_radius=6)
                alt_frame.grid(row=0, column=2, padx=10, pady=6)
                ctk.CTkLabel(alt_frame, text=f"🐧 {alt['name']}",
                             font=("Segoe UI", 11, "bold"), text_color=fg).pack(padx=10, pady=(4, 0))
                ctk.CTkLabel(alt_frame, text=alt["desc"],
                             font=("Segoe UI", 9), text_color=MUTED).pack(padx=10, pady=(0, 4))
                # Paket yöneticisi etiketleri
                if alt["packages"]:
                    pkg_row = ctk.CTkFrame(alt_frame, fg_color="transparent")
                    pkg_row.pack(padx=10, pady=(0, 4))
                    for mgr in ["apt", "dnf", "pacman", "flatpak"]:
                        if mgr in alt["packages"]:
                            ctk.CTkLabel(pkg_row, text=mgr,
                                         font=("Segoe UI", 8),
                                         text_color="#60a5fa",
                                         fg_color="#1e3a5f",
                                         corner_radius=4,
                                         padx=4, pady=1).pack(side="left", padx=2)

    # ── Sayfa 3 · Browser (değişmedi) ─────────────────────────────────────────
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
                ff_bases = [base, os.path.join(roaming, "Mozilla", "Firefox")]
                for ff_base in ff_bases:
                    if os.path.exists(ff_base):
                        for entry in os.scandir(ff_base):
                            if entry.is_dir() and entry.name not in ("Crash Reports", "Pending Pings", "Profiles"):
                                has_profile_files = any((Path(entry.path) / f).exists() for f in ["places.sqlite", "prefs.js", "logins.json", "key4.db"])
                                if has_profile_files or ".default" in entry.name:
                                    profiles[entry.name] = entry.path
            else:
                for entry in os.scandir(base):
                    if entry.is_dir() and (entry.name.startswith("Profile") or entry.name == "Default"):
                        profiles[entry.name] = entry.path
            if profiles:
                result[browser] = profiles
        return result

    # ── Sayfa 4 · Config (değişmedi) ──────────────────────────────────────────
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
                    # ── YENİ JSON YAPISI ──
                    # Her kayıt:
                    # {
                    #   "name": "Discord",
                    #   "alt": {
                    #     "name": "Discord",
                    #     "desc": "Linux sürümü mevcut",
                    #     "packages": {
                    #       "apt": "discord",
                    #       "dnf": "discord",
                    #       "pacman": "discord",
                    #       "flatpak": "com.discordapp.Discord"
                    #     }
                    #   }
                    # }
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

        self.after(0, lambda: self._log("\n🎉 Export tamamlandı!"))
        self.after(0, lambda: self._progress.set(1.0))
        self.after(0, lambda: self._export_btn.configure(
            state="normal", text="🚀  Export Başlat"))
        self.after(0, lambda: messagebox.showinfo(
            "Tamamlandı", "Migration paketi başarıyla oluşturuldu!"))

    @staticmethod
    def _safe_copy(src, dst, out_dir: Path = None):
        src_path = Path(src)
        try:
            if src_path.is_symlink():
                return
            if src_path.is_dir():
                if out_dir and _is_subpath(src_path, out_dir):
                    return
                if src_path.name in SKIP_DIR_NAMES:
                    return
                os.makedirs(dst, exist_ok=True)
                for item in src_path.iterdir():
                    if item.is_symlink():
                        continue
                    if item.name in SKIP_DIR_NAMES:
                        continue
                    if out_dir and _is_subpath(item, out_dir):
                        continue
                    child_dst = Path(dst) / item.name
                    try:
                        Win2LinuxApp._safe_copy(str(item), str(child_dst), out_dir)
                    except PermissionError:
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
                                                pass
                                if zip_dst.stat().st_size < 22:
                                    zip_dst.unlink()
                            except Exception:
                                pass
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
