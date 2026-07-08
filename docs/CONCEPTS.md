# Konsept Varyantları — rubriğe göre puanlanmış 2 seçenek (7 Tem 2026)

> Not (8 Tem): Nihai proje adı **Statistical Trust Layer**; aşağıdaki Varyant B'nin "Honest Metrics Auditor" adı, bugün paketin YILDIZ bileşeni olan **Auditor**'a dönüştü (gövde = Sentinel). Bu doküman seçim geçmişini korur.


Ortak zemin: MCP/ACK ile context graph'ı oku → istatistiksel dürüst-validasyon koş →
bulguları graph'a GERİ YAZ (assertion+incident+tag) → lineage ile kök-neden anlatısı.
Demo verisi: 250k+ satır gerçek oran+sonuç setimiz (tjk_sib.db + tr_odds.db + iddaa_snap.db
→ DataHub'a ingest). Fark, ajanın KİMLİĞİNDE:

---

## Varyant A — "Data Health Sentinel" (Challenge 1: Agents That Do Real Work)
**Tek cümle:** Pipeline'larını sürekli kollayan ajan: bayat-veri / drift / kalibrasyon-bozulması
yakalar, lineage'la kök-nedene iner, Incident açar + Assertion yazar + downstream'i tag'ler.

**Demo akışı (2-3 dk):** Oran feed'lerimiz DataHub'da lineage'lı; birini "sessizce donduruyoruz"
(gerçekte yaşadığımız İddaa/TJK staleness hikâyesi!). Ajan: (1) istatistiksel tazelik testi
düşer → (2) lineage'ı yürüyüp 3 downstream analitik tabloyu "contaminated" tag'ler →
(3) Incident açar, Assertion'ı graph'a yazar → (4) ertesi "gün" ikinci ajan/kişi graph'tan
bu bilgiyi miras alır (challenge metnindeki cümlenin birebir canlandırması).

| Rubrik | Puan beklentisi |
|---|---|
| Use of DataHub | ★★★★★ okuma+üçlü geri-yazma, challenge metniyle birebir |
| Technical Execution | ★★★★☆ bileşenler elimizde (tazelik/kalibrasyon testleri hazır kod) |
| Originality | ★★★☆☆ RİSK BURADA: "data quality monitoring" kalabalık; DataHub'ın kendi Assertions/Monitoring'i var → farkımızı "out-of-box'ta OLMAYAN istatistiksel testler" (kalibrasyon, dağılım-drift, power-devig tipi domain testleri) olarak keskin anlatmak ŞART |
| Real-World Usefulness | ★★★★★ her veri ekibinin günlük acısı |
| Submission Quality | ★★★★★ hikâye gerçek ve görsel (donmuş feed → yayılan kirlilik) |

**Artı:** en düşük icra riski (kod %70 damıtma), challenge-1 ödül kulvarına tam oturur, video anlatımı somut.
**Eksi:** orijinallik savunması dikkat ister; "monitoring aracı zaten var" itirazına cevabı
README'de peşinen vermek gerekir.

---

## Varyant B — "Honest Metrics Auditor" (Challenge 4 Wildcard + 1 karışımı)
**Tek cümle:** Bir metriğin/backtest'in/model raporunun SAYISINA değil SOYUNA bakan ajan:
lineage + query history'den metriğin nasıl üretildiğini çıkarır, sızıntı/overfit/bias
testleri koşar (zaman-split ihlali, join-kaynaklı duplikasyon, survivorship, çoklu-test),
"bu sayıya güvenilir mi" hükmünü audit-damgası olarak graph'a yazar.

**Demo akışı:** Dashboard'da "+%40 ROI" iddialı bir backtest metriği; ajan lineage'dan eğitim/test
tablolarını bulur, zaman-sızıntısını yakalar ("test satırlarının %30'u eğitimden eski"),
metrik asset'ine "AUDIT FAILED: leakage" assertion'ı + düzeltilmiş değeri yazar; ikinci
(temiz) metrik "AUDIT PASSED" damgası alır.

| Rubrik | Puan beklentisi |
|---|---|
| Use of DataHub | ★★★★☆ okuma+geri-yazma var; query-history/lineage kullanımı derin |
| Technical Execution | ★★★☆☆ "claim→lineage→test" genelleştirmesi ekstra iş; 34 günde yapılır ama A'dan riskli |
| Originality | ★★★★★ metadata graph'ında dürüstlük-denetimi kimsede yok; moat'ımızın en saf hali |
| Real-World Usefulness | ★★★★☆ "kimsenin güvenmediği dashboard metriği" gerçek acı; ama günlük operasyon aracı değil denetim aracı |
| Submission Quality | ★★★★☆ kavram güçlü ama 3 dk'da anlatması A'dan zor (soyut) |

**Artı:** jüride "bunu daha önce görmedim" etkisi; EdgeAuditor moat'ının graph-native hali; Grand Prize profili.
**Eksi:** icra + anlatı riski daha yüksek; "claim" kavramını DataHub modeline oturtmak (custom
properties/entities) ek tasarım işi.

---

## Karşılaştırma & öneri
- **A = güvenli, challenge-kulvarlı, $3k Challenge-Winner olasılığı yüksek**; orijinallik zayıf karnı.
- **B = yüksek risk/yüksek tavan, Grand Prize ($6k) profili**; icra ve anlatı riski.
- **Önerim: A gövdesi + B'nin imza testi.** Sentinel ajanına (A) "honest-metrics" modülünü
  TEK killer örnekle göm: donmuş feed'i yakalamakla kalmaz, o feed'den beslenen backtest
  metriğine "bu sayı artık güvenilmez" damgası vurur. Böylece A'nın icra güvenliği + B'nin
  orijinallik puanı birleşir; challenge-1 kulvarında yarışır, wildcard'a da göz kırpar.
- Bonus kriter (her iki varyantta): DataHub'a küçük OSS katkısı — ör. "statistical freshness
  assertion" örneği/doc PR'ı — düşük maliyet, jüri notunda "favorably".
