# 🚀 Win2Linux Sürüm Notları (v2.3)

### 🦊 1. Firefox Profil ve Veri Import Desteği
- Firefox profil verileri içe aktarıldığında `~/.mozilla/firefox/profiles.ini` dosyası otomatik oluşturulur/güncellenir.
- Aktarılan yer imleri, geçmiş, parolalar ve profil dosyaları Linux üzerinde Firefox açıldığında doğrudan tanınır ve kullanılabilir.

### 📁 2. Dinamik XDG Kullanıcı Dizinleri Eşlemesi
- Yedeklenen klasör adları (`Musics`, `Music`, `Müzik`, `Documents`, `Belgeler`, `Downloads` vb.) hedef Linux sistemindeki `xdg-user-dir` yerelleştirilmiş klasör yollarına (örneğin Türkçe sistemlerde `~/Müzikler`, `~/Belgeler`) otomatik eşlenir.
- İçe aktarma sırasında `Musics` gibi fazladan veya İngilizce isimli farklı klasörlerin açılması engellenir.

### 🐧 3. Dağıtım Tespiti ve Canlı Depo Sorgulama
- `/etc/os-release` üzerinden aktif Linux dağıtımı (Fedora, Ubuntu, Arch, openSUSE vb.) ve varsayılan paket yöneticisi (`apt`, `dnf`, `pacman`, `zypper`, `flatpak`) tespit edilir.
- Programlar sekmesine **"🔍 Dağıtım Depolarında Sorgula"** özelliği eklendi. Dağıtım depolarına (`apt-cache`, `dnf info/search`, `pacman -Si/-Ss` vb.) canlı sorgu atılarak paket mevcudiyeti doğrulanır ve toplu kurulum komutları buna göre güncellenir.
