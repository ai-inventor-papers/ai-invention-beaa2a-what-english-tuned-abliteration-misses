"""Shared helpers for the iteration-3 audit (independent code path; nothing imported from prior artifacts)."""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import yaml
from loguru import logger

WS = Path(__file__).resolve().parent.parent
RES = WS / "results"
FIG = WS / "figures"
LOOP = Path(__file__).resolve().parents[4]
E1 = LOOP / "round-1/experiment-1/src"
E3 = LOOP / "round-1/experiment-3/src"
DS1 = LOOP / "round-1/dataset-1/src"
E4 = LOOP / "round-2/experiment-4/src"
E5 = LOOP / "round-2/experiment-5/src"
E6 = LOOP / "round-2/experiment-6/src"
E7 = LOOP / "round-2/experiment-7/src"
E8 = LOOP / "round-2/experiment-8/src"
DRAFT = LOOP / "iter_2/gen_report_text/gen_report_text/paper_draft.md"
REVIEW_LOG = LOOP / "iter_2/review_report/review_report/notes/recompute_log.md"
SEED = 20260924
B = 2000
Z = 1.959963984540054


def setup(name: str) -> None:
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
    (WS / "logs").mkdir(exist_ok=True)
    logger.add(WS / "logs" / f"{name}.log", rotation="30 MB", level="DEBUG")


def read_json(p: Path):
    return json.loads(Path(p).read_text())


def read_jsonl(p: Path) -> list[dict]:
    return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]


def write_json(p: Path, obj) -> None:
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(obj, indent=1, ensure_ascii=False, default=_default))


def _default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, Path):
        return str(o)
    raise TypeError(type(o))


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ------------------------------------------------------------------ label map
LABEL_MAP = yaml.safe_load((WS / "configs/label_map.yaml").read_text())


def canon(judge_family: str, native) -> str | None:
    """native label -> REFUSED / PARTIAL / COMPLIED / INVALID (or NOT_REFUSED for keyword); None = no label."""
    if native is None or (isinstance(native, float) and math.isnan(native)):
        return None
    m = LABEL_MAP["judges"][judge_family]["map"]
    return m.get(str(native).strip().lower())


# ------------------------------------------------------------------ keyword judges (verbatim marker lists)
KW = LABEL_MAP["keyword"]
EN_MARKERS = [m.lower() for m in KW["en_markers_heretic_3521f864"]]
SL_MARKERS = KW["sl_markers_iter1"]


def _norm(r: str) -> str:
    return " ".join(r.lower().replace("*", "").replace("’", "'").split())


def kw_en(resp: str) -> bool:
    if not resp.strip():
        return True
    n = _norm(resp)
    return any(m in n for m in EN_MARKERS)


def kw_sl(resp: str) -> bool:
    if not resp.strip():
        return True
    n = _norm(resp)
    return any(m in n for m in SL_MARKERS)


def kw(resp: str, lang: str) -> str:
    f = kw_en(resp) if lang == "en" else kw_sl(resp)
    return "REFUSED" if f else "NOT_REFUSED"


# ------------------------------------------------------------------ statistics
def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def cluster_boot_mean(x: np.ndarray, clusters, b: int = B, seed: int = SEED) -> tuple[float, float]:
    """percentile CI of the mean, resampling clusters (semantic items)."""
    x = np.asarray(x, float)
    cl = np.asarray(clusters)
    u, inv = np.unique(cl, return_inverse=True)
    if len(u) == len(x):
        rng = np.random.default_rng(seed)
        idx = rng.integers(0, len(x), size=(b, len(x)))
        m = x[idx].mean(1)
        return float(np.quantile(m, .025)), float(np.quantile(m, .975))
    s = np.bincount(inv, weights=x)
    c = np.bincount(inv)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(u), size=(b, len(u)))
    m = s[idx].sum(1) / c[idx].sum(1)
    return float(np.quantile(m, .025)), float(np.quantile(m, .975))


def mcnemar_exact(a: np.ndarray, b: np.ndarray) -> dict:
    from scipy.stats import binomtest
    a = np.asarray(a, bool)
    b = np.asarray(b, bool)
    n10 = int((a & ~b).sum())
    n01 = int((~a & b).sum())
    p = float(binomtest(n10, n10 + n01, .5).pvalue) if n10 + n01 else 1.0
    return {"n10_a1_b0": n10, "n01_a0_b1": n01, "p_exact": p}


def paired_boot_diff(a: np.ndarray, b: np.ndarray, b_reps: int = B, seed: int = SEED, clusters=None) -> tuple[float, float, float]:
    """mean(b) - mean(a) with a paired (cluster) bootstrap CI."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    d = b - a
    lo, hi = cluster_boot_mean(d, clusters if clusters is not None else np.arange(len(d)), b_reps, seed)
    return float(d.mean()), lo, hi


def cohen_kappa(a, b, labels=None) -> float:
    a = np.asarray(a)
    b = np.asarray(b)
    if labels is None:
        labels = sorted(set(a.tolist()) | set(b.tolist()))
    idx = {l: i for i, l in enumerate(labels)}
    k = len(labels)
    m = np.zeros((k, k))
    for x, y in zip(a, b):
        m[idx[x], idx[y]] += 1
    n = m.sum()
    if n == 0:
        return float("nan")
    po = np.trace(m) / n
    pe = (m.sum(1) * m.sum(0)).sum() / n / n
    if pe >= 1 - 1e-12:
        return float("nan")
    return float((po - pe) / (1 - pe))


def gwet_ac1(a, b) -> float:
    a = np.asarray(a)
    b = np.asarray(b)
    labels = sorted(set(a.tolist()) | set(b.tolist()))
    q = len(labels)
    n = len(a)
    if n == 0:
        return float("nan")
    po = float((a == b).mean())
    if q < 2:
        return 1.0
    pi = np.array([((a == l).sum() + (b == l).sum()) / (2 * n) for l in labels])
    pe = float((pi * (1 - pi)).sum() / (q - 1))
    return float((po - pe) / (1 - pe)) if pe < 1 else float("nan")


def kappa_boot(a, b, b_reps: int = B, seed: int = SEED) -> tuple[float, float]:
    a = np.asarray(a)
    b = np.asarray(b)
    labels = sorted(set(a.tolist()) | set(b.tolist()))
    rng = np.random.default_rng(seed)
    n = len(a)
    ks = []
    for _ in range(b_reps):
        i = rng.integers(0, n, n)
        k = cohen_kappa(a[i], b[i], labels)
        if not math.isnan(k):
            ks.append(k)
    if len(ks) < b_reps * 0.5:
        return (float("nan"), float("nan"))
    return float(np.quantile(ks, .025)), float(np.quantile(ks, .975))


def fmt(x, nd=3) -> str:
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "–"
    return f"{x:.{nd}f}"


# ------------------------------------------------------------------ audit records (three-way: raw recompute vs summary vs draft)
TOL = {"count": 0.0, "rate": 0.0015, "ci": 0.02, "stat": 0.0015, "ratio": 0.05, "p": None}


def within(a, b, kind: str) -> bool | None:
    if a is None or b is None:
        return None
    if kind == "p":
        if min(a, b) < 1e-3:
            return max(a, b) / max(min(a, b), 1e-300) <= 1.5
        return abs(a - b) <= 0.01
    if kind == "ci":
        return all(abs(x - y) <= TOL["ci"] for x, y in zip(a, b))
    tol = TOL[kind]
    # draft values are often printed at 2 dp (0.23) or in percent: accept rounding of the printed precision
    return abs(a - b) <= tol + 1e-12


class Recorder:
    def __init__(self, step: str):
        self.step = step
        self.recs: list[dict] = []

    def add(self, id: str, section: str, claim: str, recomputed, *, draft=None, summary=None, plan=None, kind="rate",
            draft_tol=None, ci=None, n=None, unit="proportion", dataset=None, cell=None, language=None, judge=None,
            source_file=None, source_key=None, method="", status=None, note="", paste=None):
        def cmp(ref, tol=None):
            if ref is None or recomputed is None:
                return None
            if tol is not None:
                return abs(recomputed - ref) <= tol + 1e-12
            return within(recomputed, ref, kind)
        d_ok = cmp(draft, draft_tol)
        s_ok = cmp(summary)
        p_ok = cmp(plan, draft_tol)
        if status is None:
            if draft is None:
                status = "NEW" if recomputed is not None else "SUMMARY_ONLY"
            elif recomputed is None:
                status = "SUMMARY_ONLY" if summary is not None else "UNTRACEABLE"
            else:
                status = "RECOMPUTED_MATCH" if d_ok else "RECOMPUTED_MISMATCH"
        r = dict(id=id, step=self.step, section=section, claim_text_draft=claim, draft_value=draft, recomputed_value=recomputed,
                 ci_low=ci[0] if ci else None, ci_high=ci[1] if ci else None, n=n, unit=unit, dataset=dataset, cell=cell,
                 language=language, judge=judge, source_file=str(source_file) if source_file else None, source_key=source_key,
                 method=method, status=status, summary_value=summary, summary_match=s_ok, plan_expected=plan, plan_match=p_ok,
                 draft_match=d_ok, correction_note=note,
                 paste_text=paste if paste is not None else (f"{recomputed:.3f}" if isinstance(recomputed, float) else str(recomputed)))
        self.recs.append(r)
        return r

    def save(self):
        write_json(RES / "records" / f"{self.step}.json", self.recs)
        from collections import Counter
        logger.info(f"{self.step}: {len(self.recs)} records {dict(Counter(r['status'] for r in self.recs))}; "
                    f"summary mismatches {sum(r['summary_match'] is False for r in self.recs)}; "
                    f"plan mismatches {sum(r['plan_match'] is False for r in self.recs)}")


# ------------------------------------------------------------------ vectorised agreement (fast bootstrap)
def _codes(a, b):
    labels = sorted(set(np.asarray(a).tolist()) | set(np.asarray(b).tolist()))
    idx = {l: i for i, l in enumerate(labels)}
    return np.array([idx[x] for x in a]), np.array([idx[x] for x in b]), labels


def kappa_codes(ca: np.ndarray, cb: np.ndarray, k: int) -> np.ndarray:
    """ca, cb: (reps, n) int arrays -> kappa per rep."""
    reps, n = ca.shape
    flat = (ca * k + cb) + (np.arange(reps)[:, None] * k * k)
    m = np.bincount(flat.ravel(), minlength=reps * k * k).reshape(reps, k, k) / n
    po = np.trace(m, axis1=1, axis2=2)
    pe = (m.sum(2) * m.sum(1)).sum(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(pe < 1 - 1e-12, (po - pe) / (1 - pe), np.nan)


def agreement(a, b, b_reps: int = B, seed: int = SEED, clusters=None) -> dict:
    a = np.asarray(a)
    b = np.asarray(b)
    n = len(a)
    ca, cb, labels = _codes(a, b)
    k = len(labels)
    kap = float(kappa_codes(ca[None], cb[None], k)[0]) if k > 1 else float("nan")
    rng = np.random.default_rng(seed)
    if clusters is not None:
        u, inv = np.unique(np.asarray(clusters), return_inverse=True)
        members = [np.where(inv == i)[0] for i in range(len(u))]
        ks = []
        for _ in range(b_reps):
            pick = rng.integers(0, len(u), len(u))
            ii = np.concatenate([members[j] for j in pick])
            ks.append(kappa_codes(ca[ii][None], cb[ii][None], k)[0])
        ks = np.array(ks)
    else:
        idx = rng.integers(0, n, (b_reps, n))
        ks = kappa_codes(ca[idx], cb[idx], k) if k > 1 else np.full(b_reps, np.nan)
    ks = ks[np.isfinite(ks)]
    ci = (float(np.quantile(ks, .025)), float(np.quantile(ks, .975))) if len(ks) >= b_reps * .5 else (float("nan"), float("nan"))
    po = float((a == b).mean())
    conf = {f"{x}->{y}": int(((a == x) & (b == y)).sum()) for x in labels for y in labels if ((a == x) & (b == y)).any()}
    return {"n": n, "kappa": kap, "kappa_ci_low": ci[0], "kappa_ci_high": ci[1], "raw_agreement": po, "pabak": 2 * po - 1 if k <= 2 else float("nan"),
            "ac1": gwet_ac1(a, b), "labels": labels, "confusion": conf}
