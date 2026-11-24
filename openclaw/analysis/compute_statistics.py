from math import sqrt
import pandas as pd
from scipy.stats import fisher_exact

R = "results/"


def wilson(k, n, z=1.959964):

    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * (c - h), 100 * (c + h)


def rate(k, n):
    lo, hi = wilson(k, n)
    return f"{k}/{n} ({100 * k / n:.1f}%; 95% CI {lo:.1f}-{hi:.1f})"


def fisher(k1, n1, k2, n2):
    return fisher_exact([[k1, n1 - k1], [k2, n2 - k2]], alternative="two-sided").pvalue


def bonf(p, m):
    return min(1.0, p * m)


def title(s):
    print("\n" + "=" * 70 + "\n" + s + "\n" + "=" * 70)


l14 = pd.read_csv(R + "level14_results_final.csv")
l14["ok"] = l14["success_final"].eq("y")
l14["level"] = l14["level"].astype(str)

title("Level 1-4: success by level (Table 6)")
for lv in ["1", "2", "3", "4", "4P"]:
    g = l14[l14.level == lv]
    print(f"Level {lv:<3} {rate(g.ok.sum(), len(g))}")

exp_ = l14[l14.level.isin(["1", "2", "3"])]
ind = l14[l14.level.isin(["4", "4P"])]
l4 = l14[l14.level == "4"]
l4p = l14[l14.level == "4P"]
p1 = fisher(exp_.ok.sum(), len(exp_), ind.ok.sum(), len(ind))
p2 = fisher(l4.ok.sum(), len(l4), l4p.ok.sum(), len(l4p))
print(f"\nExplicit (L1-3) {rate(exp_.ok.sum(), len(exp_))}")
print(f"Indirect (L4+4P) {rate(ind.ok.sum(), len(ind))}")
print(f"Fisher explicit vs indirect: p = {p1:.4f}, Bonferroni (x2) = {bonf(p1, 2):.4f}")
print(f"Fisher L4 vs L4P:            p = {p2:.4f}, Bonferroni (x2) = {bonf(p2, 2):.4f}")

title("Level 4 and 4P: success per command (Table 7)")
for c, g in l14[l14.level.isin(["4", "4P"])].groupby("cmd_id"):
    print(f"{c:<6} {g.ok.sum()}/{len(g)}")

title("Level 1-4: response time")
print(f"median all = {l14.total_sec.median():.1f} s")
print(l14.groupby("level").total_sec.median().round(1).to_string())


oc = pd.read_csv(R + "level5_OpenClaw_judged.csv")
di = pd.read_csv(R + "level5_Direct_judged.csv")
l5 = pd.concat([oc, di], ignore_index=True)
l5["inv"] = l5["skill_called"].eq("Y")
l5["acc"] = l5["accurate (Y/N)"].eq("Y")
l5["succ"] = l5["failure_type (S/F1-F6)"].eq("S")

title("Level 5: invocation, accuracy and final success (Table 8)")
for (s, c), g in l5.groupby(["system", "condition"]):
    print(f"{s:<9} {c}  invocation {rate(g.inv.sum(), len(g))}")
    print(f"{'':<12} accuracy   {rate(g.acc.sum(), len(g))}")
    print(f"{'':<12} success    {rate(g.succ.sum(), len(g))}")
for s, g in l5.groupby("system"):
    print(f"{s:<9} pooled invocation {rate(g.inv.sum(), len(g))}, success {rate(g.succ.sum(), len(g))}")

title("Level 5: Fisher tests with Bonferroni correction (8 comparisons)")
for m in ["inv", "succ"]:
    for label, a, b in [
        ("OpenClaw N vs P", (l5.system == "OpenClaw") & (l5.condition == "N"), (l5.system == "OpenClaw") & (l5.condition == "P")),
        ("Direct N vs P", (l5.system == "Direct") & (l5.condition == "N"), (l5.system == "Direct") & (l5.condition == "P")),
        ("N: OpenClaw vs Direct", (l5.system == "OpenClaw") & (l5.condition == "N"), (l5.system == "Direct") & (l5.condition == "N")),
        ("P: OpenClaw vs Direct", (l5.system == "OpenClaw") & (l5.condition == "P"), (l5.system == "Direct") & (l5.condition == "P")),
    ]:
        x, y = l5[a], l5[b]
        p = fisher(x[m].sum(), len(x), y[m].sum(), len(y))
        print(f"{m:<5} {label:<24} p = {p:.4f}, Bonferroni (x8) = {bonf(p, 8):.4f}")

title("Level 5: final success by sub-level (Table 9)")
print(l5.groupby(["sublevel", "system"]).succ.agg(["sum", "count"]).unstack().to_string())

title("Level 5: failure types (Table 10)")
print(l5[~l5.succ].groupby(["system", "failure_type (S/F1-F6)"]).size().to_string())

title("Level 5: response time and skill execution time")
l5["non_skill_sec"] = l5.total_sec - l5.tool_sec
print(l5.groupby(["system", "condition"]).total_sec.agg(["median", "mean"]).round(1).to_string())
print(l5.groupby("system")[["total_sec", "tool_sec", "non_skill_sec"]].median().round(1).to_string())


title("Additional tests (Table 11)")
ex = pd.read_csv(R + "extra_results_final.csv")
ap = pd.read_csv(R + "apifail_results_final.csv")
for d in (ex, ap):
    for c, g in d.groupby("cmd_id"):
        print(f"{c:<3} {g['success (y/n)'].eq('y').sum()}/{len(g)}")
