"""The Auditor — honest-metrics checks. This is the moat.

Given a metric/backtest claim on a dataset, decide whether the number is trustworthy
by running the failure-mode tests that generic 'my backtest wins!' submissions skip:
temporal leakage, overfit flags, calibration/longshot bias, multiple-testing luck.

Distilled from two production betting-model pipelines (250k+ rows of real odds+results)
where this exact protocol honestly KILLED 10+ 'profitable-looking' edge candidates.
"""
