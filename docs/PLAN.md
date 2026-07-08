# 34-Günlük Plan — Build with DataHub (8 Tem → 10 Ağu 2026)

**Hedef: erken submit ~5 Ağu** (5 gün buffer). Kapsam ilkesi (rubrik): küçük + çalışır + cilalı.
Kategori: *Agents That Do Real Work*. Proje: hibrit Statistical Trust Layer (Sentinel + Auditor).

## Jüri-kriter hizalaması (8 Tem — bu plan buna göre)
1. **Originality (en kritik):** Auditor YILDIZ (leakage/overfit/calibration — DataHub'da yok).
   Sentinel "extend" konumunda (DataHub profiling+freshness'ı okur, üstüne value-dynamics katar).
   README/demo/kod yorumları hep Auditor'ı öne çıkarıyor.
2. **Use of DataHub:** geri-yazma görünür — Assertion+Incident+Tag canlı GMS'e yazılıyor (✅ doğrulandı).
3. **Real-World Usefulness:** README pratisyen-acısı cümlesiyle açılıyor; örnek = gerçek veride sahte edge.
4. **OSS bonus:** Auditor registry-paketli (`honest_metrics/registry.py`); plan `docs/OSS_CONTRIBUTION.md`.
5. **Submission Quality:** `demo/scenario.md` 3-dk akış hazır; README kurulum adımları net.
6. **Technical Execution:** 8/8 test, canlı uçtan-uca çalışıyor.

## Faz 0 — Scaffold (8 Tem) ✅ TAMAM
- Repo, Apache-2.0, pyproject, MCP/SDK katmanı. Statistical core gerçek+test edilmiş.

## Faz 1 — Uçtan uca canlı (8 Tem) ✅ TAMAM (M1 + M2 aynı gün bitti)
- **M1 ✅:** DataHub quickstart ayakta; iddaa + tr_odds ingest; `milestone1.py` canlı okuma → verdict.
- **M2 ✅:** `writeback.py` — Assertion(CUSTOM/EXTERNAL)+Incident(ACTIVE)+Tag canlı GMS'e yazıp
  geri okundu. `demo_writeback.py` 30.352 gerçek maçta Auditor koşup verdict'i graph'a yazıyor
  (🔴 NOT TRUSTWORTHY: leakage+overfit yakalandı, calibration doğru geçti).

## Faz 2 — Moat derinliği (9–22 Tem)
- **Adım 2 ✅ (8 Tem):** Auditor MCP'den otomatik besleniyor — `split_inference.py` query
  history SQL'ini sqlglot ile TEMPORAL/RANDOM sınıflıyor; `mcp_server.py` Auditor'ı MCP tool
  olarak sunuyor (audit_dataset). Elle timestamp yok.
- **Adım 3 ✅ (8 Tem):** Sentinel suite genişledi — distribution-drift (PSI/KS) + null-spike +
  schema-drift, hepsi "extend" konumunda (DataHub profile/schema okur, üstüne katar).
  `sentinel_scan.py` gerçek DataHub şeması + gerçek oran verisinde çalışıyor. Sentinel registry.
- **Sıradaki:** Auditor+Sentinel'i DataHub Skill olarak paketle (OSS bonus, `docs/OSS_CONTRIBUTION.md`).
- Kabul: gerçek veride sahte-edge'i + veri-sağlığı sorunlarını canlı yakalıyor ✅. 25/25 test.

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
