# Build with DataHub: The Agent Hackathon — Rubrik & Gereksinim Özeti (7 Tem 2026)

**Deadline:** 10 Ağu 2026, 23:00 (NL saati) — 34 gün. Erken submit hedefi: ~5-6 Ağu.
**Ödüller:** Grand $6.000 (1) · Challenge Winner $3.000 (×4 — challenge başına 1) ·
Mansiyon $1.000 (×2) · +feedback ödülleri. **216 katılımcı** (7 Tem itibarıyla).
**Uygunluk:** uluslararası (standart istisnalar hariç), 18+, W-8BEN ile nakit ödenir. ✓

## 4 Challenge (birini seç veya birleştir)
1. **Agents That Do Real Work** — veri problemlerini halleden ajan; DataHub'ı **MCP Server**
   veya **Agent Context Kit** ile okur, aksiyon alır, **sonuçları graph'a geri yazar**
   ("writes results back so the next person or agent inherits the knowledge").
2. **Metadata-Aware Code Generation** — gerçek şema/lineage/kuralları okuyup ilk seferde
   çalışan üretim veri kodu (dbt/DAG/ingestion) üreten ajan; çıktı PR-kalitesinde.
3. **Production ML Agents** — ML lineage (veri→feature→model→deploy) üzerinden üretimdeki
   modeli sessiz kırılmalardan koruyan ajan.
4. **Open/Wildcard** — DataHub temelli yaratıcı herhangi bir şey (finansal tahmin,
   regülasyon otomasyonu vb. örnek verilmiş).

## Jüri kriterleri (5 + bonus)
| Kriter | Ne istiyor | Bizim açımız |
|---|---|---|
| **Use of DataHub** | Context graph + MCP/ACK/Skills/Analytics Agent'ın ANLAMLI kullanımı. **"Strong submissions go beyond reading metadata and CONTRIBUTE BACK TO THE GRAPH"** ← kritik cümle | Okuma (MCP) + geri-yazma (Assertions, Incidents, tags, docs, custom properties) ikisi birden |
| **Technical Execution** | Uçtan uca GERÇEKTEN çalışıyor mu | Çalışan demo disiplinimiz + gerçek veri |
| **Originality** | Out-of-box özelliği yeniden yapmak DEĞİL; üstüne inşa/kompozisyon | DataHub'ın Assertions/Monitoring'i var → bizim katkı ORADA OLMAYAN istatistiksel dürüstlük testleri olmalı |
| **Real-World Usefulness** | Gerçek data/ML ekibi değer görür mü | Bayat-veri/sessiz-bozulma = her veri ekibinin yaşadığı acı (biz bizzat yaşadık) |
| **Submission Quality** | ≤3 dk video + README + kurulum netliği | Strateji: 3 iterasyon video, rubrik-madde-madde anlatı |
| **BONUS: Open-Source katkı** | DataHub'a connector/skill/fix/doc katkısı | Küçük bir skill/doc PR'ı planla — ucuz, jüride "favorably" puanı |

## Submission gereksinimleri (eksiksiz liste)
- Jürinin test edebileceği URL (canlı demo / hosted app / kurulum talimatlı repo)
- **Public repo + Apache 2.0 lisansı** (repo About kısmında görünür olmalı!)
- Metin açıklama (özellikler, teknolojiler, kullanılan veri)
- **≤3 dk demo videosu** (YouTube/Vimeo, public)

## "Contribute back to the graph" — geri-yazma yüzeyleri (docs taraması)
DataHub'da ajanla yazılabilenler: **Assertions (data quality)**, **Incidents**,
Tags, Documentation/Context Documents, Custom Properties, Lineage edge'leri,
Metadata Tests. Rubrik #1'in "beyond reading" şartı bunlardan en az 1-2'sinin
anlamlı kullanımıyla karşılanır (bizde: assertion + incident + tag üçlüsü).

## DataHub araç seti (7 Tem docs)
- **MCP Server**: graph'ı ajanlara açan MCP arayüzü (arama, lineage, şema, query history).
- **Agent Context Kit (ACK)**: ajan-taraflı SDK; LangChain/Claude/Cursor entegrasyon
  rehberleri mevcut (Claude entegrasyonu bizim için doğal — MCP zaten günlük dilimiz).
- **DataHub Skills**: hazır ajan becerileri kataloğu.
- **Analytics Agent** (github.com/datahub-project/analytics-agent): referans ajan — bunun
  ÜSTÜNE değer katmak orijinallik kriterine uygun; klonlamak değil.
