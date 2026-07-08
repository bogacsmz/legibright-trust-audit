# EdgeAuditor — "Is Your Backtest Lying?" (StoxraHack 2026 submission)

**Tek cümle:** Herkes "kazanan" trading stratejisi gösterir; biz stratejinin **sahte olup
olmadığını söyleyen** AI ajanını yaptık.

## Problem
AI ile herkes 10 dakikada backtest'i "kârlı" görünen bir trading botu üretebiliyor. Bunların
ezici çoğunluğu overfit/sızıntı/bias artefaktı — gerçek parayla çöker. Perakende yatırımcının
elinde bunu ayırt edecek araç yok.

## Çözüm — EdgeAuditor
Bir strateji/backtest ver (kod, sinyal listesi veya oran+sonuç CSV'si) → ajan dürüst
validasyon protokolünü koşar ve **"gerçek edge / sahte edge / kararsız"** hükmü + gerekçe verir:
1. **Zamansal split zorlaması** — random k-fold sızıntısını yakalar, walk-forward yeniden koşar.
2. **Bias düzeltmeleri** — longshot/favori bias (power-devig), çoklu-test düzeltmesi
   (taranan N hücrede şans beklentisi), survivorship kontrolü.
3. **Overfit kırmızı bayrakları** — ROI>%20, dönem tutarsızlığı, parametre hassasiyeti.
4. **Realized-doğrulama** — ima edilen vs gerçekleşen isabet (binom z), maliyet/vergi/slipaj
   senaryolu net ROI.
5. **Rapor** — tek sayfalık hüküm kartı: neyin sahte olduğu, hangi testte düştüğü, düzeltilmiş
   gerçek beklenti.

## Neden biz (moat)
Bu protokol teorik değil — **gerçek parayla test edilmiş iki canlı pipeline'dan** damıtıldı
(at yarışı SİB + spor bahisleri cross-platform CLV; 250k+ satır gerçek oran+sonuç verisi).
O projelerde bu protokol tam da "kârlı görünen" 10+ edge adayını dürüstçe ELEDİ — sistem,
kendini kandırmama disiplininin kodlanmış hali. Demo gerçek veriyle koşar, oyuncak veriyle değil.

## Demo akışı (2-3 dk)
1. AI'ya "kârlı trading botu yaz" dedirt → klasik overfit bot çıkar, backtest +%40 ROI der.
2. EdgeAuditor'a ver → 20 saniyede: "SAHTE — random split sızıntısı + longshot bias;
   düzeltilmiş walk-forward ROI −%12."
3. Gerçek (bilinen) küçük bir edge örneği ver → "GERÇEK ama ince: doğrulamada z+2.4,
   vergi sonrası +%1.8, limit riski yüksek" — nüanslı hüküm.
4. Kapanış: "Kazandıran botu satmıyoruz; kaybettiren botu ELEYEN ajanı yapıyoruz."

## Durum
- [x] Uygunluk doğrulandı (platform verisi; form-level teyit kayıtta)
- [ ] Kayıt (kullanıcı adımı) + kural/rubrik/submission-tarihi teyidi
- [ ] İnşa (bkz. PLAN.md — 8 gün)
