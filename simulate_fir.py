#!/usr/bin/env python3
"""FIR minimal simulation validation package (v1.1 protocol implementation).

Generates one eta=0.10 environment for the target XOR model and the no-interaction
negative control. Uses complete randomized blocks as the bootstrap resampling unit.
No empirical experiment is performed; all rows are synthetic.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd

MODELS = ("target", "negative_control")
ETA = 0.10
BLOCKS = 40
REPEATS_PER_CELL_PER_BLOCK = 10
N_BOOT = 10_000
EPS_PSI = 0.20
EPS_B = 0.10
HOLDOUT_BLOCKS = 8


def entropy_bits(p: np.ndarray | float) -> np.ndarray | float:
    p = np.asarray(p, dtype=float)
    out = np.zeros_like(p, dtype=float)
    m = (p > 0.0) & (p < 1.0)
    out[m] = -p[m] * np.log2(p[m]) - (1.0-p[m]) * np.log2(1.0-p[m])
    return float(out) if out.ndim == 0 else out


def categorical_entropy_bits(probabilities: np.ndarray, axis: int = -1) -> np.ndarray:
    """Shannon entropy for a categorical distribution along axis."""
    p = np.asarray(probabilities, dtype=float)
    terms = np.zeros_like(p)
    mask = p > 0.0
    terms[mask] = -p[mask] * np.log2(p[mask])
    return terms.sum(axis=axis)


def theoretical(model: str, eta: float) -> dict:
    q = 1.0 - 2.0 * eta
    if model == "target":
        p = np.array([[eta, 1-eta], [1-eta, eta]], dtype=float)  # p[a,b]
        da = [q, -q]
        db = [q, -q]
    else:
        p = np.array([[eta, eta], [1-eta, 1-eta]], dtype=float)
        da = [q, q]
        db = [0.0, 0.0]
    psi = float(p[1,1]-p[1,0]-p[0,1]+p[0,0])
    mi = 1.0 - float(entropy_bits(eta))
    return {"p": p, "delta_A": da, "delta_B": db, "psi": psi, "mi_bits": mi}


def assert_theory() -> dict:
    t = theoretical("target", 0.10)
    n = theoretical("negative_control", 0.10)
    assert np.allclose(t["p"], [[0.1, 0.9], [0.9, 0.1]])
    assert np.allclose(n["p"], [[0.1, 0.1], [0.9, 0.9]])
    assert np.allclose(t["delta_A"], [0.8, -0.8])
    assert np.allclose(t["delta_B"], [0.8, -0.8])
    assert math.isclose(t["psi"], -1.6, abs_tol=1e-12)
    assert np.allclose(n["delta_A"], [0.8, 0.8])
    assert np.allclose(n["delta_B"], [0.0, 0.0])
    assert math.isclose(n["psi"], 0.0, abs_tol=1e-12)
    assert math.isclose(t["mi_bits"], 1.0-entropy_bits(0.1), abs_tol=1e-12)
    assert math.isclose(t["mi_bits"], n["mi_bits"], abs_tol=1e-12)
    return {"target": {"p": t["p"].tolist(), "delta_A": t["delta_A"], "delta_B": t["delta_B"], "psi": t["psi"], "mi_bits": t["mi_bits"]},
            "negative_control": {"p": n["p"].tolist(), "delta_A": n["delta_A"], "delta_B": n["delta_B"], "psi": n["psi"], "mi_bits": n["mi_bits"]}}


def generate_data(seed: int, eta: float, blocks: int, repeats: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for model in MODELS:
        for block in range(blocks):
            cells = [(a,b) for a in (0,1) for b in (0,1) for _ in range(repeats)]
            rng.shuffle(cells)
            for trial_in_block, (a,b) in enumerate(cells):
                c = int(rng.integers(0,2))  # independent C_t; not used by transition
                noise = int(rng.random() < eta)
                y = (a ^ b ^ noise) if model == "target" else (a ^ noise)
                rows.append((model, block, trial_in_block, a, b, c, int(y), noise, "constant"))
    return pd.DataFrame(rows, columns=["model","block","trial_in_block","A_t","B_t","C_t","C_next","N_t","H_o_stratum"])


def metric_from_cell_counts(success: np.ndarray, total: np.ndarray) -> dict:
    # Arrays shape (..., 4), cells ordered (00,01,10,11).
    p = np.divide(success, total, out=np.zeros_like(success, dtype=float), where=total > 0)
    p00,p01,p10,p11 = [p[...,i] for i in range(4)]
    da0, da1 = p10-p00, p11-p01
    db0, db1 = p01-p00, p11-p10
    psi = p11-p10-p01+p00
    return {"p":p, "delta_A_0":da0, "delta_A_1":da1, "delta_B_0":db0, "delta_B_1":db1, "psi":psi}


def mi_from_joint(joint: np.ndarray) -> np.ndarray:
    # joint shape (...,8,2), where 8 states are (A,B,C_t), last dimension C_next.
    n = joint.sum(axis=(-2,-1))
    py = joint.sum(axis=-2) / np.maximum(n[...,None],1)
    px = joint.sum(axis=-1) / np.maximum(n[...,None],1)
    pxy = joint / np.maximum(n[...,None,None],1)
    hy = categorical_entropy_bits(py, axis=-1)
    hx = categorical_entropy_bits(px, axis=-1)
    hxy = categorical_entropy_bits(pxy, axis=(-2,-1))
    return hx + hy - hxy


def pack_blocks(df: pd.DataFrame):
    # Block-level sufficient statistics for cell risks and I(Y; A,B,C_t).
    block_ids = sorted(df.block.unique())
    successes, totals, joint = [], [], []
    for b in block_ids:
        d = df[df.block == b]
        s = np.zeros(4); n = np.zeros(4)
        j = np.zeros((8,2))
        for row in d.itertuples(index=False):
            cell = int(row.A_t)*2 + int(row.B_t)
            s[cell] += int(row.C_next); n[cell] += 1
            state = int(row.A_t)*4 + int(row.B_t)*2 + int(row.C_t)
            j[state, int(row.C_next)] += 1
        successes.append(s); totals.append(n); joint.append(j)
    return np.asarray(successes), np.asarray(totals), np.asarray(joint), block_ids


def bootstrap_metrics(df: pd.DataFrame, rng: np.random.Generator, n_boot: int):
    bs, bn, bj, block_ids = pack_blocks(df)
    idx = rng.integers(0, len(block_ids), size=(n_boot, len(block_ids)))
    s = bs[idx].sum(axis=1); n = bn[idx].sum(axis=1); j = bj[idx].sum(axis=1)
    m = metric_from_cell_counts(s,n)
    mi = mi_from_joint(j)
    return m, mi


def ci_summary(x: np.ndarray, level: float = 0.95) -> dict:
    """Summarize the point estimate only; bootstrap intervals are added separately."""
    x = np.asarray(x, dtype=float)
    return {"estimate": float(np.nanmean(x)), "level": level}


def point_metrics(df: pd.DataFrame):
    s = np.zeros(4); n = np.zeros(4); joint = np.zeros((8,2))
    for row in df.itertuples(index=False):
        k = int(row.A_t)*2+int(row.B_t)
        s[k] += int(row.C_next); n[k] += 1
        z = int(row.A_t)*4+int(row.B_t)*2+int(row.C_t)
        joint[z,int(row.C_next)] += 1
    m = metric_from_cell_counts(s[None,:], n[None,:])
    return m, float(mi_from_joint(joint[None,:,:])[0])


def predict_logloss(train: pd.DataFrame, test: pd.DataFrame, augmented: bool) -> np.ndarray:
    # Jeffreys smoothing (1/2 pseudo-count) prevents infinite log loss.
    y = train.C_next.to_numpy(dtype=int)
    if not augmented:
        p = (y.sum()+0.5)/(len(y)+1.0)
        probs = np.full(len(test), p)
    else:
        state = train.A_t.astype(int)*4+train.B_t.astype(int)*2+train.C_t.astype(int)
        sums = train.assign(_state=state).groupby("_state").C_next.agg(["sum","count"])
        ts = test.A_t.astype(int)*4+test.B_t.astype(int)*2+test.C_t.astype(int)
        probs = np.empty(len(test), dtype=float)
        for i, z in enumerate(ts):
            if int(z) in sums.index:
                probs[i]=(sums.loc[int(z),"sum"]+0.5)/(sums.loc[int(z),"count"]+1.0)
            else:
                probs[i]=(y.sum()+0.5)/(len(y)+1.0)
    probs=np.clip(probs,1e-12,1-1e-12)
    yy=test.C_next.to_numpy(dtype=int)
    return -(yy*np.log(probs)+(1-yy)*np.log(1-probs))


def predictive_check(df: pd.DataFrame, seed: int, n_boot: int):
    rng=np.random.default_rng(seed)
    blocks=sorted(df.block.unique())
    holdout=sorted(rng.choice(blocks,size=HOLDOUT_BLOCKS,replace=False).tolist())
    train=df[~df.block.isin(holdout)].copy(); test=df[df.block.isin(holdout)].copy()
    l0=predict_logloss(train,test,False); l1=predict_logloss(train,test,True)
    test_by_block=[]
    for b in holdout:
        ix=(test.block.to_numpy()==b)
        test_by_block.append((float(l0[ix].mean()),float(l1[ix].mean())))
    arr=np.asarray(test_by_block)
    point=float(arr[:,0].mean()-arr[:,1].mean())
    boot_idx=rng.integers(0,len(holdout),size=(n_boot,len(holdout)))
    boot=(arr[boot_idx,0]-arr[boot_idx,1]).mean(axis=1)
    return {"holdout_blocks":holdout,"n_train_trials":int(len(train)),"n_test_trials":int(len(test)),
            "L_history":float(l0.mean()),"L_history_relations":float(l1.mean()),"delta_L":point,
            "delta_L_ci95":[float(np.quantile(boot,.025)),float(np.quantile(boot,.975))],
            "interpretation":"positive delta_L means lower held-out log loss after adding (A_t,B_t,C_t); this is predictive validation, not an unbiased mutual-information estimate"}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--outdir",default="outputs")
    ap.add_argument("--seed",type=int,default=20261124)
    ap.add_argument("--bootstrap",type=int,default=N_BOOT)
    ap.add_argument("--blocks",type=int,default=BLOCKS)
    ap.add_argument("--repeats-per-cell",type=int,default=REPEATS_PER_CELL_PER_BLOCK)
    ap.add_argument("--eta",type=float,default=ETA)
    args=ap.parse_args()
    if args.bootstrap<100: raise SystemExit("Use at least 100 bootstrap replicates; preregistered default is 10,000.")
    if not 0<args.eta<0.5: raise SystemExit("eta must be between 0 and 0.5")
    theory=assert_theory()
    out=Path(args.outdir); out.mkdir(parents=True,exist_ok=True)
    data=generate_data(args.seed,args.eta,args.blocks,args.repeats_per_cell)
    data.to_csv(out/"simulated_trials.csv",index=False)
    report={"notice":"Synthetic validation only; not empirical evidence.","settings":{"seed":args.seed,"eta":args.eta,"blocks_per_model":args.blocks,"repeats_per_cell_per_block":args.repeats_per_cell,"trials_per_model":args.blocks*4*args.repeats_per_cell,"bootstrap_replicates":args.bootstrap,"bootstrap_unit":"complete randomized block","epsilon_psi":EPS_PSI,"epsilon_B":EPS_B,"holdout_blocks":HOLDOUT_BLOCKS},"theoretical":{},"simulated":{}}
    for model in MODELS:
        d=data[data.model==model].copy()
        m, mi=point_metrics(d)
        rng=np.random.default_rng(args.seed + (1 if model=="target" else 2))
        bm,bmi=bootstrap_metrics(d,rng,args.bootstrap)
        keys=["delta_A_0","delta_A_1","delta_B_0","delta_B_1","psi"]
        summaries={k:ci_summary(m[k][0]) for k in keys}
        for k in keys: summaries[k]["bootstrap_ci95"]=[float(np.quantile(bm[k],.025)),float(np.quantile(bm[k],.975))]
        summaries["mi_bits"]={"estimate":mi,"bootstrap_ci95":[float(np.quantile(bmi,.025)),float(np.quantile(bmi,.975))]}
        pred=predictive_check(d,args.seed+(31 if model=="target" else 32),args.bootstrap)
        th=theoretical(model,args.eta)
        report["theoretical"][model]={"p00_p01_p10_p11":[float(th["p"][0,0]),float(th["p"][0,1]),float(th["p"][1,0]),float(th["p"][1,1])],"delta_A":[float(x) for x in th["delta_A"]],"delta_B":[float(x) for x in th["delta_B"]],"psi":th["psi"],"mi_bits":th["mi_bits"]}
        report["simulated"][model]={"p00_p01_p10_p11":[float(x) for x in m["p"][0]],"statistics":summaries,"psi_theory_deviation":float(m["psi"][0]-th["psi"]),"psi_direction_matches":bool((m["psi"][0]<0) if model=="target" else True),"negative_control_psi_equivalent":bool(model!="negative_control" or (np.quantile(bm["psi"],.05)>=-EPS_PSI and np.quantile(bm["psi"],.95)<=EPS_PSI)),"negative_control_B_equivalent":bool(model!="negative_control" or all(np.quantile(bm[k],.05)>=-EPS_B and np.quantile(bm[k],.95)<=EPS_B for k in ("delta_B_0","delta_B_1"))),"prediction_check":pred}
    with open(out/"validation_results.json","w") as f: json.dump(report,f,indent=2)
    write_markdown(report,out/"validation_report.md")
    print(f"Wrote {out/'simulated_trials.csv'}")
    print(f"Wrote {out/'validation_results.json'}")
    print(f"Wrote {out/'validation_report.md'}")


def write_markdown(r:dict,path:Path):
    lines=["# FIR 仿真验证结果", "", "> **重要：**以下全部是按指定模型生成的合成数据，只用于检查程序与统计流程，不是实证结果。", "", "## 配置", "", f"- 随机种子：`{r['settings']['seed']}`；噪声率：`{r['settings']['eta']}`。", f"- 每模型区块数：{r['settings']['blocks_per_model']}；每区块每格重复：{r['settings']['repeats_per_cell_per_block']}；每模型试次数：{r['settings']['trials_per_model']}。", f"- 区块 bootstrap：{r['settings']['bootstrap_replicates']:,} 次；留出区块：{r['settings']['holdout_blocks']}。", "", "## 理论值与模拟估计", "", "| 模型 | 四格概率 p00,p01,p10,p11 | ΔA(0), ΔA(1) | ΔB(0), ΔB(1) | Ψ 理论 / 估计 | 互信息理论 / 估计 (bit) |", "|---|---|---|---|---|---|"]
    for model in MODELS:
        th=r['theoretical'][model]; s=r['simulated'][model]; st=s['statistics']
        da=[st['delta_A_0']['estimate'],st['delta_A_1']['estimate']]
        db=[st['delta_B_0']['estimate'],st['delta_B_1']['estimate']]
        psi=st['psi']['estimate']; mi=st['mi_bits']['estimate']
        lines.append(f"| {model} | {th['p00_p01_p10_p11']} / {s['p00_p01_p10_p11']} | {th['delta_A']} / {[round(x,4) for x in da]} | {th['delta_B']} / {[round(x,4) for x in db]} | {th['psi']:.4f} / {psi:.4f} | {th['mi_bits']:.4f} / {mi:.4f} |")
    lines += ["", "## 置信区间与检验解释", "", "所有效应区间以完整随机化区块为 bootstrap 单位。负对照等效性按 v1.1 界限评估：Ψ 的 ±0.20、B 简单效应的 ±0.10；程序以 90% bootstrap 区间完全落入界限作为等效性检查。模拟结果受随机抽样影响，等效检验未通过不表示模型定义错误，只表示本次模拟精度未满足门槛。", "", "| 模型 | 统计量 | 点估计 | 95% 区块 bootstrap CI |", "|---|---|---:|---:|"]
    for model in MODELS:
        for k in ['delta_A_0','delta_A_1','delta_B_0','delta_B_1','psi','mi_bits']:
            st=r['simulated'][model]['statistics'][k]
            ci=st.get('bootstrap_ci95')
            if k=='mi_bits': label='I(C_next; A,B,C_t | H_o) bits'; est=st['estimate']
            else: label=k; est=st['estimate']
            lines.append(f"| {model} | {label} | {est:.5f} | [{ci[0]:.5f}, {ci[1]:.5f}] |")
        pred=r['simulated'][model]['prediction_check']
        lines.append(f"| {model} | ΔL held-out | {pred['delta_L']:.5f} | [{pred['delta_L_ci95'][0]:.5f}, {pred['delta_L_ci95'][1]:.5f}] |")
    t=r['simulated']['target']; nt=r['simulated']['negative_control']
    psi_boot_target=np.asarray(t['statistics']['psi']['bootstrap_ci95'])
    psi_dev_ci=[float(psi_boot_target[0]+1.6),float(psi_boot_target[1]+1.6)]
    lines += ["", "## 分层判定摘要", "", f"- **方向符合（目标模型交互）**：{'是' if t['psi_direction_matches'] else '否'}；点估计 Ψ={t['statistics']['psi']['estimate']:.5f}。", f"- **交互理论偏差**：E_Ψ=Ψ̂−(−1.6)={t['psi_theory_deviation']:.5f}；由 95% Ψ 区间平移得到的 95% 区间 [{psi_dev_ci[0]:.5f}, {psi_dev_ci[1]:.5f}]。区间包含 0 仅表示与理论幅度相容，不证明相等。", f"- **负对照 Ψ 等效（±{EPS_PSI:.2f}）**：{'通过' if nt['negative_control_psi_equivalent'] else '未通过'}；按 90% 区块 bootstrap 区间。", f"- **负对照两个 B 简单效应等效（各 ±{EPS_B:.2f}）**：{'通过' if nt['negative_control_B_equivalent'] else '未通过'}；两项均须通过。", "- **预测改善**：见留出 ΔL 及其 95% 区间；这不是互信息的无偏估计。", ""]
    lines += ["", "## 预测核验", ""]
    for model in MODELS:
        p=r['simulated'][model]['prediction_check']
        lines.append(f"- **{model}**：L_history={p['L_history']:.5f}，L_history+relations={p['L_history_relations']:.5f}，ΔL={p['delta_L']:.5f}；95% 区块 bootstrap CI [{p['delta_L_ci95'][0]:.5f}, {p['delta_L_ci95'][1]:.5f}]。正 ΔL 表示留出对数损失下降。该指标不是互信息的无偏估计。")
    lines += ["", "## 自动理论断言", "", "脚本在模拟前断言理论四格概率、简单效应、二阶交互及互信息公式。断言通过只验证推导实现与代码映射一致；不能证明理论模型适用于真实系统。", "", "## 冻结边界", "", "本执行包未修改 v1.1 冻结协议。区块构成、留出划分与仿真输出属于执行准备材料；跨环境复现尚未在此包中实现。", ""]
    path.write_text("\n".join(lines),encoding="utf-8")

if __name__=="__main__":
    main()
