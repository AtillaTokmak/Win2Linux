# Win2Linux Migrator 🐧➡️🏠

Windows’tan Linux’a geçiş sürecini kolaylaştıran modern GUI tabanlı migration aracı.
Bu proje iki parçadan oluşur:

* **Win2Linux Migrator** → Windows tarafında verileri/export paketini oluşturur
* **Linux2Home Importer** → Linux tarafında paketi içe aktarır ve sistemi hazırlar

---

## ✨ Özellikler

### 📁 Dosya Migrasyonu

* Masaüstü
* Belgeler
* İndirilenler
* Müzik
* Resimler
* Videolar
* Özel klasör desteği

### 📦 Program Analizi

Windows’taki kurulu programları tarar ve:

* Linux alternatiflerini önerir
* Paket yöneticisi kurulum komutları üretir
* Toplu install komutu oluşturur

Örnek:

* Microsoft Office → LibreOffice
* Photoshop → GIMP
* Visual Studio → VS Code / JetBrains
* Discord → Discord
* Steam → Steam

---

### 🌐 Browser Verileri

Tarayıcı profillerini taşıyabilir:

* Google Chrome
* Firefox
* Edge
* Brave

Desteklenen veriler:

* Yer imleri
* Profil klasörleri
* Kullanıcı verileri

---

### ⚙️ Sistem Konfigürasyonu

Migrasyon sırasında:

* `.ssh`
* `.gitconfig`
* VSCode ayarları
* ortam değişkenleri
* hosts dosyası

gibi yapılandırmalar aktarılabilir.

---

### 🐧 Linux Paket Yöneticisi Desteği

Importer tarafında otomatik algılama:

* apt
* dnf
* pacman
* zypper
* flatpak

---

## 🖼️ Arayüz

Modern dark-themed GUI:

* CustomTkinter tabanlı
* Sidebar navigasyon
* Kart tabanlı modern tasarım
* Scrollable içerikler
* Paket özeti
* Kurulum komutları
* Durum göstergeleri

---

# 📦 Proje Yapısı

```text
project/
│
├── win2linux.py      # Windows export aracı
├── linux2home.py     # Linux import aracı
│
└── generated_package/
    ├── files/
    ├── browser/
    ├── config/
    └── programs.json
```

---

# 🚀 Kurulum

## Gereksinimler

* Python 3.10+
* pip

## Paketleri Kur

```bash
pip install customtkinter psutil
```

---

# 🪟 Windows Tarafı

## Çalıştırma

```bash
python win2linux.py
```

## Yapabilecekleri

✅ Dosya seçimi
✅ Program taraması
✅ Linux alternatif önerileri
✅ Browser export
✅ Sistem config export
✅ ZIP migration paketi oluşturma

---

# 🐧 Linux Tarafı

## Çalıştırma

```bash
python linux2home.py
```

## Yapabilecekleri

✅ ZIP paketi açma
✅ Dosyaları home dizinine taşıma
✅ Browser profillerini import etme
✅ Sistem config uygulama
✅ Linux paket kurulum komutları oluşturma

---

# 📦 Örnek Migration Akışı

## 1️⃣ Windows’ta export oluştur

```bash
python win2linux.py
```

Export sonucu:

```text
W2L_Migration/
└── W2L_2026-05-08.zip
```

---

## 2️⃣ ZIP dosyasını Linux’a taşı

USB / ağ / cloud üzerinden taşı.

---

## 3️⃣ Linux’ta import et

```bash
python linux2home.py
```

ZIP’i seç → import işlemini başlat.

---

# 🧠 Akıllı Program Eşleştirme

Sistem registry üzerinden kurulu uygulamaları tarar ve:

```python
"photoshop" -> ("GIMP", "gimp", "Güçlü görsel editör")
```

şeklinde Linux karşılıkları bulur.

Desteklenen kategoriler:

* Ofis
* IDE
* Tasarım
* Oyun
* VPN
* Güvenlik
* Medya
* CAD
* Browser
* Sistem araçları
* Geliştirme araçları

100+ uygulama eşleşmesi içerir.

---

# 🔐 Güvenlik

* Veriler tamamen lokal çalışır
* Sunucuya veri gönderilmez
* Offline migration desteklenir
* ZIP paketleri manuel taşınır

---

# 🛠️ Kullanılan Teknolojiler

* Python
* CustomTkinter
* Tkinter
* pathlib
* threading
* shutil
* zipfile
* Windows Registry API (`winreg`)

---

# 📌 Desteklenen Platformlar

| Sistem     | Destek |
| ---------- | ------ |
| Windows 10 | ✅      |
| Windows 11 | ✅      |
| Ubuntu     | ✅      |
| Fedora     | ✅      |
| Arch Linux | ✅      |
| openSUSE   | ✅      |

---

# ⚠️ Notlar

* Bazı Windows uygulamalarının Linux karşılığı olmayabilir
* Anti-cheat kullanan bazı oyunlar çalışmayabilir
* Browser import sırasında hedef browser’ın kurulu olması gerekir

---

# 🔮 Gelecek Planları

* Wine/Proton entegrasyonu
* Otomatik Flatpak fallback
* Tema/export profilleri
* Cloud sync
* Delta migration
* Paket doğrulama sistemi
* Multi-user destek
* AppImage export desteği

---

# 🤝 Katkıda Bulunma

Pull request’ler ve öneriler her zaman açıktır.

```bash
git clone <repo>
```

---

# 📜 Lisans

MIT License

---

# 👨‍💻 Geliştirici

[Atilla Tokmak GitHub](https://github.com/AtillaTokmak?utm_source=chatgpt.com)
