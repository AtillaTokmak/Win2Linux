# Win2Linux Migrator 🐧➡️🏠

Modern GUI-based migration toolkit for moving from Windows to Linux with minimal setup and maximum convenience.

This project consists of two applications:

* **Win2Linux Migrator** → Creates a migration/export package on Windows
* **Linux2Home Importer** → Imports and restores the package on Linux

---
# 🖼️ Screenshots
Windows Enviroment:
![Windows](https://i.hizliresim.com/dqfm3ih.png)

# ✨ Features

## 📁 File Migration

Transfer your important folders easily:

* Desktop
* Documents
* Downloads
* Music
* Pictures
* Videos
* Custom folders

---

## 📦 Installed Program Detection

Automatically scans installed Windows applications and suggests Linux alternatives.

Examples:

* Microsoft Office → LibreOffice
* Photoshop → GIMP
* Visual Studio → VS Code / JetBrains
* Discord → Discord
* Steam → Steam

Also generates ready-to-use Linux package manager install commands.

---

## 🌐 Browser Migration

Supports browser profile importing for:

* Google Chrome
* Firefox
* Microsoft Edge
* Brave

Transfer:

* bookmarks
* profiles
* user data
* browser settings

---

## ⚙️ System Configuration Migration

Move important configs including:

* `.ssh`
* `.gitconfig`
* VSCode settings
* environment variables
* hosts file

---

## 🐧 Linux Package Manager Support

Automatically detects:

* apt
* dnf
* pacman
* zypper
* flatpak

---

# 🖼️ Interface

Modern dark-themed GUI built with CustomTkinter.

Features:

* Sidebar navigation
* Scrollable views
* Modern card UI
* Package summary
* Installation command generator
* Status indicators
* Multi-page workflow

---

# 📦 Project Structure

```text id="9z8g1l"
project/
│
├── win2linux.py      # Windows exporter
├── linux2home.py     # Linux importer
│
└── generated_package/
    ├── files/
    ├── browser/
    ├── config/
    └── programs.json
```

---

# 🚀 Installation

## Requirements

* Python 3.10+
* pip

## Install Dependencies

```bash id="3czg2m"
pip install customtkinter psutil
```

---

# 🪟 Windows Side

## Run

```bash id="h1v90j"
python win2linux.py
```

## What It Can Do

✅ Select files and folders
✅ Scan installed applications
✅ Suggest Linux alternatives
✅ Export browser data
✅ Export system configs
✅ Create ZIP migration package

---

# 🐧 Linux Side

## Run

```bash id="4kj6np"
python linux2home.py
```

## What It Can Do

✅ Open migration ZIP package
✅ Restore files into home directory
✅ Import browser profiles
✅ Apply system configurations
✅ Generate Linux install commands

---

# 📦 Example Workflow

## 1️⃣ Create Export Package on Windows

```bash id="0b9u7w"
python win2linux.py
```

Generated output:

```text id="70lm0d"
W2L_Migration/
└── W2L_2026-05-08.zip
```

---

## 2️⃣ Transfer ZIP to Linux

Move it using:

* USB drive
* local network
* cloud storage

---

## 3️⃣ Import on Linux

```bash id="kg8lzp"
python linux2home.py
```

Select the ZIP package and start migration.

---

# 🧠 Smart Program Matching

The application scans Windows registry entries and intelligently matches Linux alternatives.

Example:

```python id="q8jqn7"
"photoshop" -> ("GIMP", "gimp", "Powerful image editor")
```

Supports:

* Office tools
* Browsers
* IDEs
* Gaming launchers
* VPN clients
* Security software
* Media tools
* CAD software
* Development tools
* System utilities

Includes 100+ application mappings.

---

# 🔐 Privacy & Security

* Fully local operation
* No cloud upload
* No telemetry
* Offline migration supported
* ZIP packages transferred manually

---

# 🛠️ Technologies Used

* Python
* CustomTkinter
* Tkinter
* pathlib
* threading
* shutil
* zipfile
* Windows Registry API (`winreg`)

---

# 📌 Supported Platforms

| Platform   | Supported |
| ---------- | --------- |
| Windows 10 | ✅         |
| Windows 11 | ✅         |
| Ubuntu     | ✅         |
| Fedora     | ✅         |
| Arch Linux | ✅         |
| openSUSE   | ✅         |

---

# ⚠️ Notes

* Some Windows applications may not have Linux alternatives
* Certain anti-cheat games may not work on Linux
* Browser importing requires the target browser to be installed

---

# 🔮 Future Plans

* Wine/Proton integration
* Automatic Flatpak fallback
* Migration profiles
* Cloud sync
* Delta migration
* Package verification system
* Multi-user support
* AppImage export support

---

# 🤝 Contributing

Pull requests and suggestions are welcome.

```bash id="0xksw0"
git clone <repo>
```

---

# 📜 License

MIT License

---

# 👨‍💻 Developer

[Atilla Tokmak GitHub](https://github.com/AtillaTokmak?utm_source=chatgpt.com)
