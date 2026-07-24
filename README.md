 # 🐧 Win2Linux Migration Tool

 ## 📌 Genel Tanım

 Bu proje, Windows kullanıcılarının Linux ortamına geçerken bilgisayarlarını ve uygulamalarını daha kolay taşıyabilmelerini sağlayacak bir araçtır. Sistem dosyalarını, uygulama 
 paketlerini, ortam değişkenlerini ve çok daha fazlasını otomatik olarak tanımlar ve kullanıcıya uygun kurulum komutlarını sunar.

 > **Not:** Bu projenin ana amacı Windows’tan Linux’a geçiş sürecinin kolaylaştırılmasıdır. Ancak bu araç, sadece bir rehber/yardımcıdır. Tüm kurulumlar kullanıcı tarafından 
 kontrol edilmelidir.

 ---

 ## 🚀 Özellikler

 - 🔍 Otomatik sistem tespiti ve paket keşfi (`linux2home.py`)
 - 🧰 Yeni paketler için destek eklenebilirliği
 - 🖥️ Yeni kurulum komutları (örnek: Flatpak, Homebrew
 - 💻 Terminalde komut çalıştırma desteği (komut kopyalama ve terminal üzerinden çalıştırma)
 - 🔧 Ayar dosyalarını (config) yedekleme desteği
 - 📂 Dosya içeriklerini analiz etme (özellikle `.desktop` dosyaları, `~/.config/`, vb.)
 - 🌐 Sistem ve dağıtım bilgisi gösterimi

 ---

 ## 🛠️ Kullanı

 ### `win2linux.py`
 Bu betik, Windows’un altında çalışır. Sisteminizi analiz eder ve Linux’a geçiş sırasında hangi uygulamaların kurulması gerektiğini belirler.bash
 python win2linux.py
 Bu işlem sonucunda bir komut dosyası oluşturulur ve kullanıcının seçimine göre `linux2home.py` ile kullanılabilir hale getirilir. Sistem analizleri, kullanıcı tercihleri ve 
 kurulum komutları kullanıcıya gösterilir.

 ### `linux2home.py`
 Bu betik, Linux ortamında çalışır. Windows’tan gelen analiz verisine göre uygulama kurulumlarını ve sistem ayarlarını gösterir. Kullanıcıya otomatik komutların üretimi ve doğrudan
  terminal üzerinden çalıştırılması imkanı sunar.bash
 python linux2home.py
 ---

 ## 🧪 Örnek Senaryo

 ### 1. Windows'ta `win2linux.py` çalıştırılır

 Yazılımlar, yapılandırmalar, kullanıcı tercihleri ve sistem bilgileri analiz edilir. Bu veriler JSON formatında saklanır (örneğin: `env_vars.json`, `config_info.json`).

 ### 2. Linux'ta `linux2home.py` çalıştırılır

 Bu betik, `win2linux.py` tarafından üretilen dosyalarla birlikte çalışarak:

 - Kurulum komutlarını üretir (ör: `apt install discord`, `flatpak install com.discordapp.Discord`)
 - Ortam değişkenlerini tanımlar (ör: `.bashrc`, `.zshrc`)
 - Uygulama yapılandırması (örneğin: Firefox, VS Code) hakkında bilgiler verir
 - Uygulamaların klasör içerikleri analiz edilir

 ### 3. Terminal üzerinden kurulum komutu çalıştırılır

 Kullanıcıya terminalde çalıştırılacak komutlar gösterilir ve doğrudan çalıştırılabilir veya kopyalanabilir hale getirilir.

 ---

 ## 📝 Yeni Özellikler

 ### ⚙️ Yeni Komutlar
 Bu proje, `linux2home.py` üzerinden yeni kurulum komutları da üretmektedir:

 | Platform | Paket Yöneticisi | Örnek Komut |
 |----------|------------------|-------------|
 | Debian/Ubuntu | `apt` | `sudo apt install discord` |
 | Fedora/CentOS | `dnf` | `sudo dnf install discord` |
 | Arch Linux | `pacman` | `sudo pacman -S discord` |
 | Flatpak | `flatpak` | `flatpak install flathub com.discordapp.Discord` |

 ### 🧠 Uzantılar ve Desteklenen Paketler

 Yeni paket türleri eklemek oldukça kolaydır:python
 win2linux.py dosyasında örnek:
 packages = {
     "discord": {"apt": "discord", "flatpak": "com.discordapp.Discord"},
     ...
 }
 ### 📦 Yeni Dosya Analizleri

 - `.desktop` dosyaları okunarak uygulama bilgileri çıkarılır
 - `~/.config/`, `~/.local/share/`, `~/.cache/` klasörleri analiz edilir

 ---

 ## 🧰 Gereksinimler

 - Python 3.7+
 - `tkinter` (GUI desteği)
 - GNU/Linux dağıtımında `bash`, `flatpak`, ve tercihe göre `apt/dnf/pacman`

 ---

 ## 🧾 Lisans

 Tüm bu proje, açık kaynaklıdır. Lisans bilgileri için `LICENSE` dosyasına bakınız.

 ---

 ## ✅ Katkıda Bulunmak

 Bug veya yeni özellik önerileri için GitHub Issues bölümünü kullanabilirsiniz. Pull Request’lerinizi memnuniyetle karşılıyoruz!

 ---

 ## 💬 Notlar

 Bu proje, Windows’tan Linux’a geçiş sürecinde kullanıcı dostu bir deneyim sunmayı hedeflemektedir. Her sistemin özel durumları olduğundan kullanıcıların doğrudan müdahale ederek 
 kontrolü elinde tutması önerilir.

 ---