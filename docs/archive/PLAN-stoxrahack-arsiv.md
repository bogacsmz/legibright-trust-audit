# PLAN — StoxraHack 2026, 8 gün (7→15 Tem)

## Uygunluk (7 Tem doğrulaması — Unstop API, kesin platform verisi)
- **Eligible filtresi: "All"** (öğrenci kısıtı YOK — başlıktaki "Student" pazarlama)
- **Region: online** (NL'den katılım OK) | **Takım: 1-5** (bireysel OK)
- **Kayıt: STARTED, son gün 15 Tem 2026 00:00 IST** (≈14 Tem 20:30 NL!)
- Ödüller: 1. ₹200.000 + sertifika + staj + mentorluk; (2./3. kademeler var)
- ⚠️ Kalan tek teyit: kayıt FORMU öğrenci alanı zorunlu kılıyor mu → **KULLANICI ADIMI:
  Unstop hesabıyla kaydol, submission deadline'ını + rubriği + form alanlarını gör.**
  (Kayıt/hesap işlemlerini Claude yapamaz — policy.)

## Kapsam felsefesi (strateji dosyası §2/§4)
Küçük + çalışan + cilalı >> büyük + yarım. AI %80 boilerplate'i yazar; bizim zamanımız
%20'ye gider: hüküm protokolünün doğruluğu, demo akışı, anlatı.

## 8 günlük plan
| Gün | İş |
|---|---|
| **1 (bugün)** | Kayıt (kullanıcı) → kurallar/rubrik/submission tarihi netleşir. Repo iskeleti + veri örnekleri (tr_odds.db + iddaa_snap.db'den anonim export). |
| **2-3** | Çekirdek: `audit.py` — mevcut motorlardan damıtma (zaman-split, power-devig, çoklu-test, overfit bayrakları, binom-z realized). Girdi formatı: oran+sonuç CSV / sinyal listesi. |
| **4** | "Sahte bot" üreteci (demo villain): kasıtlı overfit stratejiler → EdgeAuditor yakalıyor mu, birim testleri. |
| **5** | Hüküm kartı çıktısı (tek sayfa HTML/PDF) + CLI cilası. Rubrik maddeleriyle eşleme. |
| **6** | Demo videosu (2-3 dk) + README/pitch metni. 3 iterasyon (strateji: herkes 1 yapar, biz 3). |
| **7** | Uçtan uca prova ×3, temiz repo, edge-case temizliği. |
| **8 (yedek)** | Tampon — submission formu + son kontrol. ERKEN submit et. |

## Rubrik varsayımı (kayıtta teyit edilecek)
FinTech hackathon standart: yenilikçilik / teknik derinlik / çalışırlık / sunum / etki.
Her birine anlatıda tek tek değinilecek; "responsible investing/investor protection" açısı
etki maddesini taşır (dürüst-validasyon = yatırımcı koruma aracı).

## Riskler
- Form öğrenci-zorunlu çıkarsa → **anında pivot: KDD Data Agents** (dataagent.top, 31 Tem,
  ~$30k) — aynı motor "çok-adımlı veri analitiği ajanı" olarak paketlenir; 16 gün kalır, yeterli.
- Submission deadline'ı kayıt deadline'ından erken/aynı çıkarsa → kapsamı 5 güne sıkıştır
  (gün 4-5 birleşir, video 1 iterasyon).
- Jüri kalitesi bilinmiyor (üniversite ortaklı) → anlatıyı hem teknik hem teknik-olmayan
  jüriye çalışacak şekilde iki katmanlı yaz.

## YAPILMAYACAKLAR
- Canlı trading / para bağlama yok. Yeni veri kaynağı avı yok (mevcut DB'ler yeter).
- TJK/İddaa bekleme-fazı cron'larına dokunulmaz (paralel akmaya devam).
