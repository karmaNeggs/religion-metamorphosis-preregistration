#!/usr/bin/env python3
"""GS-1 judge panel — 3-model LLM majority on gold-set snippets.

Panel (pre-registered deviation 2026-08-10, GOLD_SET_Plan.md):
  nemotron-3-ultra-free  (tie-break model)
  laguna-s-2.1-free
  mimo-v2.5-free
Each call: `opencode run --model <id> --dir <neutral>` — blind, no project context,
single-shot, strict JSON. 2-of-3 majority; two-way tie broken by the tie-break model;
no majority -> snippet dropped from precision, kept in agreement table.

Panel selection (2026-08-10, BEFORE any gold-set data existed — on handcrafted test
snippets only): deepseek-v4-flash-free (non-compliant ~30%, slow/timeouts),
longcat-2.0-free (occasional drift), north-mini-code-free (timeouts),
big-pickle-free (empty output), ling-3.0-tiny-free (compliant but tiny) were evaluated
and excluded; the three panel members returned strict JSON 3/3 and were correct 3/3
on target/off spot-checks.

Usage:
  python code/goldset/judge_gs1.py [--workers W] [--dry-run]
"""
import argparse
import csv
import json
import os
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SNIPPETS_CSV = os.path.join(ROOT, "data", "gold", "gold_set_gs1_snippets.csv")
LABELS_CSV = os.path.join(ROOT, "data", "gold", "gold_set_gs1_labels_judges.csv")
SUMMARY_CSV = os.path.join(ROOT, "data", "gold", "gold_set_gs1_summary.csv")
LOG_DIR = os.path.join(ROOT, "data", "gold", "judge_logs")

OPENCODE_BIN = os.environ.get("OPENCODE_BIN", "opencode")
NEUTRAL_DIR = os.environ.get("JUDGE_NEUTRAL_DIR",
    "/var/folders/jj/kz3yf9bs5z98tyrs438g5tkw0000gn/T/opencode/neutral")

JUDGES = ["nemotron-3-ultra-free", "laguna-s-2.1-free", "mimo-v2.5-free"]
TIE_BREAK = "nemotron-3-ultra-free"
LABELS = ("TARGET", "OFF", "AMBIG")

SENSES = {
    "sin": "theological transgression against divine law",
    "salvation": "deliverance from sin and eternal damnation by grace",
    "damnation": "eternal punishment after death",
    "repentance": "remorse for sin and turning away from it",
    "grace": "divine unmerited favor freely given by God",
    "faith": "religious belief in and trust in God",
    "worship": "religious devotion rendered to a deity",
    "eternal life": "life after death, the afterlife",
    "church attendance": "participation in religious services at a church",
    "prayer": "communication with the divine",
    "self-esteem": "psychological self-evaluation of one's own worth",
    "self-improvement": "deliberate betterment of the self",
    "self-care": "personal wellness maintenance",
    "personal development": "self-help category of career and character growth",
    "mindfulness": "meditative attention practice, usually secularized",
    "well-being": "subjective welfare and wellness",
    "self-actualization": "realizing one's full potential, the apex of Maslow's need hierarchy",
    "manifestation": "the New Age practice of attracting reality through intention",
    "inner peace": "calmness and emotional serenity, especially in self-help",
    "positive thinking": "the self-help affirmative mindset of Norman Vincent Peale's lineage",
}

PROMPT = (
    "You classify word sense. WORD: {term} — {sense}. "
    'SNIPPET: "{snippet}". '
    'TARGET = word used in the intended sense; OFF = different sense; AMBIG = unclear. '
    'Reply with ONLY a JSON object like {{"label":"TARGET"}}. Nothing else.'
)

_print_lock = threading.Lock()


def log(msg):
    with _print_lock:
        print(msg, flush=True)


def parse_label(raw):
    if not raw:
        return None
    text = re.sub(r"\x1b\[[0-9;]*m", "", raw)
    text = re.sub(r"```[a-zA-Z]*", "", text)
    m = re.search(r'"label"\s*:\s*"(TARGET|OFF|AMBIG)"', text)
    if m:
        return m.group(1)
    m = re.search(r"\b(TARGET|OFF|AMBIG)\b", text)
    return m.group(1) if m else None


def judge_once(model, term, snippet, dry_run=False):
    prompt = PROMPT.format(term=term, sense=SENSES[term], snippet=snippet)
    if dry_run:
        return "TARGET"
    model_arg = f"opencode/{model}" if not model.startswith("opencode/") else model
    cmd = [OPENCODE_BIN, "run", "--model", model_arg, "--dir", NEUTRAL_DIR, prompt]
    for attempt in range(3):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            label = parse_label(r.stdout + r.stderr)
            if label:
                return label
            log(f"  [{model}] rc={r.returncode} unparseable (attempt {attempt + 1}): "
                f"stdout={r.stdout[-150:]!r} stderr={r.stderr[-150:]!r}")
        except subprocess.TimeoutExpired:
            log(f"  [{model}] timeout (attempt {attempt + 1})")
        except FileNotFoundError:
            log(f"  [{model}] opencode binary not found: {OPENCODE_BIN}")
            return None
        time.sleep(5 * (2 ** attempt))
    return None


def done_cache():
    done = {}
    for model in JUDGES:
        p = os.path.join(LOG_DIR, f"gs1_judge_{model}.jsonl")
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                if rec["label"]:
                    done[(model, rec["snippet_id"])] = rec["label"]
    return done


def save(model, rec):
    os.makedirs(LOG_DIR, exist_ok=True)
    p = os.path.join(LOG_DIR, f"gs1_judge_{model}.jsonl")
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def kappa2(a, b):
    cats = sorted(set(a) | set(b))
    n = len(a)
    if n == 0:
        return float("nan")
    observed = sum(1 for x, y in zip(a, b) if x == y) / n
    pa = {c: a.count(c) / n for c in cats}
    pb = {c: b.count(c) / n for c in cats}
    expected = sum(pa[c] * pb[c] for c in cats)
    if expected == 1:
        return float("nan")
    return (observed - expected) / (1 - expected)


def majority(labels):
    from collections import Counter
    cnt = Counter(l for l in labels.values() if l)
    if not cnt:
        return None, "no-valid-labels"
    top = cnt.most_common()
    if top[0][1] >= 2:
        return top[0][0], "majority"
    if len(cnt) == 2 and top[0][1] == 1:
        if TIE_BREAK in labels and labels[TIE_BREAK]:
            return labels[TIE_BREAK], "tiebreak"
        return None, "unresolvable-tie"
    return None, "no-majority"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=1, help="parallel judge processes (1 = sequential; free tier throttles concurrency)")
    ap.add_argument("--sleep", type=float, default=5.0, help="seconds between judge calls")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="judge only first N snippets (testing)")
    args = ap.parse_args()

    with open(SNIPPETS_CSV, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if args.limit:
        rows = rows[: args.limit]
    if not rows:
        print("No snippets in", SNIPPETS_CSV)
        sys.exit(1)

    cache = done_cache()
    jobs = []
    for row in rows:
        for model in JUDGES:
            if (model, row["snippet_id"]) not in cache:
                jobs.append((row, model))
    print(f"{len(rows)} snippets, {len(jobs)} outstanding judge calls", flush=True)

    if args.dry_run:
        print("Dry run: skipping calls")
        jobs = [(r, m) for (r, m) in jobs[:3]]

    def work(job):
        row, model = job
        label = judge_once(model, row["term"], row["text"], dry_run=args.dry_run)
        rec = {"snippet_id": row["snippet_id"], "term": row["term"], "label": label}
        save(model, rec)
        if args.sleep and not args.dry_run:
            time.sleep(args.sleep)
        return rec

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(work, j) for j in jobs]
        for i, fut in enumerate(as_completed(futs), 1):
            rec = fut.result()
            log(f"[{i}/{len(jobs)}] {rec['term']} {rec['snippet_id']} {rec['label']}")

    cache = done_cache()
    out = []
    for row in rows:
        labels = {m: cache.get((m, row["snippet_id"])) for m in JUDGES}
        label, how = majority(labels)
        out.append({**row, **{f"j_{m}": labels[m] for m in JUDGES},
                    "majority": label, "decision": how})

    with open(LABELS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)

    summary = []
    for term in sorted({r["term"] for r in out}):
        tr = [r for r in out if r["term"] == term and r["majority"] in ("TARGET", "OFF")]
        n_t = sum(1 for r in tr if r["majority"] == "TARGET")
        n_ambig = sum(1 for r in out if r["term"] == term and r["majority"] == "AMBIG")
        n_total = sum(1 for r in out if r["term"] == term)
        prec = n_t / len(tr) if tr else float("nan")
        agree3 = sum(1 for r in out if r["term"] == term
                     and r["j_deepseek-v4-flash-free"] == r["j_nemotron-3-ultra-free"]
                     == r["j_longcat-2.0-free"] and r["j_deepseek-v4-flash-free"] is not None)
        summary.append({
            "term": term, "n": n_total, "n_ambig": n_ambig, "n_eval": len(tr),
            "precision": round(prec, 4), "flag": "YES" if prec < 0.70 else "NO",
            "all3_agree": round(agree3 / n_total, 4) if n_total else float("nan"),
        })

    pairs = []
    for i, m1 in enumerate(JUDGES):
        for m2 in JUDGES[i + 1:]:
            a, b = [], []
            for r in out:
                x, y = r[f"j_{m1}"], r[f"j_{m2}"]
                if x and y:
                    a.append(x)
                    b.append(y)
            pairs.append({"judge1": m1, "judge2": m2, "n": len(a),
                          "cohens_kappa": round(kappa2(a, b), 4)})

    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        w.writeheader()
        w.writerows(summary)
        w.writerows([])
        for p in pairs:
            w.writerow({"term": f"{p['judge1']} vs {p['judge2']}", "n": p["n"],
                        "precision": p["cohens_kappa"]})

    print(f"WROTE {LABELS_CSV} + {SUMMARY_CSV}", flush=True)
    for s in summary:
        print(f"  {s['term']:22s} prec={s['precision']:.3f} n={s['n']} flag={s['flag']}", flush=True)
    for p in pairs:
        print(f"  kappa {p['judge1']:26s} vs {p['judge2']:26s} = {p['cohens_kappa']:.3f} (n={p['n']})", flush=True)


if __name__ == "__main__":
    main()
