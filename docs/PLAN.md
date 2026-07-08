# 34-Günlük Plan — Build with DataHub (8 Tem → 10 Ağu 2026)

**Hedef: erken submit ~5 Ağu** (5 gün buffer). Kapsam ilkesi (rubrik): küçük + çalışır + cilalı.
Kategori: *Agents That Do Real Work*. Proje: hibrit Statistical Trust Layer (Sentinel + Auditor).

## Faz 0 — Scaffold (8 Tem) ✅ TAMAM
- Repo yapısı, Apache-2.0, pyproject, config, MCP/SDK bağlantı katmanı.
- Statistical core: freshness + temporal-leakage + overfit checks — **gerçek, test edilmiş**.
- `trust-layer selftest` çalışıyor, 6/6 pytest yeşil. Milestone-1 script + quickstart + demo script.

## Faz 1 — Uçtan uca canlı (9–14 Tem) → **Milestone 1 & 2**
- **M1 (9-10 Tem):** Docker başlat → `datahub docker quickstart` → local DataHub ayağa kalk.
  İddaa snaps tablosunu ingest et → `milestone1.py` gerçek şemayı okusun (placeholder değil,
  gerçek son-değerleri query'leyip freshness koştursun). **Kabul: canlı DataHub'dan hüküm kartı.**
- **M2 (11-14 Tem):** Write-back'i bağla — `add_tags` + structured property (MCP mutation,
  doğrulandı). Lineage stamp (raw→analytics→metric). Downstream propagation çalışsın.
  Assertions/Incidents SDK emit'ini netleştir (docs muğlaktı — SDK sürümüne karşı doğrula;
  tag+property zaten "write-back" şartını karşılıyor, bunlar fidelity artışı).

## Faz 2 — Moat derinliği (15–22 Tem)
- Auditor'ı gerçek pipeline verimize bağla: `claim → lineage/query-history → split bul →
  leakage+overfit+calibration` zinciri. Kalibrasyon + çoklu-test check'lerini ekle (mevcut
  tr-spor-value/tjk-sib kodundan damıt).
- Sentinel'e distribution-drift (PSI/KS), null-spike, schema-drift check'leri.
- Her check için unit test. **Kabul: gerçek 250k satırda sahte-edge'i canlı yakalıyor.**

## Faz 3 — Demo + cila (23–31 Tem)
- Demo ortamını kur (seed script: donmuş feed + sahte +40% ROI metriği + temiz kontrol metrik).
- Verdict card'ı görsel iyileştir (rich/html). CLI cila.
- **OSS bonus:** DataHub'a küçük katkı — "statistical freshness assertion" örneği veya doc PR
  (jüri notunda "favorably"). Düşük maliyet, gün 28 civarı.
- README rubrik-madde-madde geçir; "originality" savunmasını (out-of-box'ta yok) öne yaz.

## Faz 4 — Submit paketi (1–5 Ağu)
- ≤3 dk demo video (3 iterasyon — strateji: herkes 1 çeker, biz 3), YouTube public.
- Repo temizliği, kurulum talimatı sıfırdan test (temiz makine simülasyonu).
- Devpost submission: repo URL + video + açıklama + Apache-2.0 About'ta görünür.
- **5 Ağu erken submit.** 6-10 Ağu: buffer / feedback ödülü / son rötuş.

## Risk & kesme kuralları
- DataHub quickstart takılırsa (Docker/kaynak): agent'ı DataHub Cloud free-trial'a yönelt
  (aynı MCP/SDK) — plan B, gün 10'da karar.
- Assertions/Incidents SDK'de zahmetli çıkarsa: tag + structured property + description
  ile yetin (write-back şartı zaten karşılanıyor); incident'ı "nice to have"a düşür.
- Kapsam şişerse: Sentinel'i 2 check'e (freshness + drift), Auditor'ı 3'e (leakage +
  overfit + calibration) sabitle. Demo tek killer akış — dağılma.

## Paralel (dokunma)
- TJK + İddaa bekleme-fazı cron'ları arka planda akmaya devam; bu proje onları besliyor
  (demo verisi oradan) ama onların toplama/analiz akışını değiştirmiyor.
