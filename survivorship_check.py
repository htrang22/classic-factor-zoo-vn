"""Đo độ nhạy của các factor dùng giá với survivorship bias.

So sánh rổ 50 mã hiện tại với rổ có thêm các mã đã bị hủy niêm yết bắt buộc.
Chỉ dùng factor tính được từ giá và khối lượng, vì các mã này không có BCTC trong
pipeline. Kết quả đo phần bias do thiếu mã chết, không đo lỗi chọn rổ theo năm 2026.

Đầu vào (chỉ ở máy):
    data/raw/prices_all.csv, data/raw/vnindex.csv
    data/raw/delisted/*.csv   (giá mã đã hủy niêm yết, tải bằng --download)

Đầu ra (chỉ gồm số tổng hợp qua nhiều mã, không chứa dữ liệu theo mã):
    results/survivorship_check.csv    (IC, spread theo factor và kịch bản)
    results/survivorship_levels.csv   (lợi suất đều trọng số của hai rổ)
    results/survivorship_draws.csv    (chênh lệch khi chỉ thêm vài mã chết)

Chạy:
    python3 survivorship_check.py --download
    python3 survivorship_check.py
"""

from __future__ import annotations

import argparse
import time

import numpy as np
import pandas as pd

from compute_factors import daily_returns, monthly_panel, rolling_price_stats
from download_stocks import (
    DEFAULT_END,
    DEFAULT_START,
    PROJECT_DIR,
    RAW_DIR,
    download_symbol,
)


DELISTED_DIR = RAW_DIR / "delisted"
RESULT_DIR = PROJECT_DIR / "results"

# Mã bị hủy niêm yết bắt buộc trên HOSE/HNX, tổng hợp từ báo chí 2022-2025. Danh
# sách KHÔNG đầy đủ: các nguồn đều chỉ liệt kê một phần. Chưa đưa vào vì chưa xác
# nhận được: HU3, THI, POM, SJF, VIS.
DELISTED = [
    # Họ FLC
    "FLC", "ROS", "HAI", "ART", "AMD", "GAB",
    # HOSE 2022-2023
    "PXI", "RIC", "FTM", "PXS", "HOT", "MCG", "UDC",
    # HOSE 2024-2025
    "DAG", "HBC", "HNG", "TNA", "TTB", "QBS", "GMC",
    # HNX 2022-2023
    "ACM", "VXB", "VIE", "HPM", "C92", "APP", "SD2", "PDC", "TST", "PHP",
    "LCS", "HHG", "VKC", "PVL",
]

# Hướng kỳ vọng: +1 nếu giá trị cao được kỳ vọng có lợi suất cao, -1 nếu ngược lại.
FACTORS = {
    "mom_12_1": 1,
    "mom_6_1": 1,
    "ret_1m": -1,
    "beta_12m": -1,
    "vol_3m": -1,
    "ivol_3m": -1,
    "max_ret_1m": -1,
    "amihud_3m": 1,
}
# Lợi suất tháng cuối của mã hết dữ liệu. None: bỏ tháng đó, như pipeline hiện tại.
DELISTING_RETURNS = [None, 0.0, -0.30, -0.55, -1.00]
N_QUANTILES = 5
MIN_STOCKS = 25
# Rổ tỷ lệ thực tế: giả định khoảng 12% số mã chết trong 8 năm (1,5%/năm).
REALISTIC_DEAD = 7
N_DRAWS = 200
SEED = 20261106


def download_delisted(pause: float) -> None:
    """Tải giá các mã đã hủy niêm yết vào thư mục riêng, không đụng dữ liệu cũ."""

    DELISTED_DIR.mkdir(parents=True, exist_ok=True)
    failed = []
    for i, symbol in enumerate(DELISTED, start=1):
        try:
            data = download_symbol(
                symbol,
                DEFAULT_START.strftime("%Y-%m-%d"),
                DEFAULT_END.strftime("%Y-%m-%d"),
                retries=1,
                pause=pause,
            )
        except RuntimeError as exc:
            print(f"[{i}/{len(DELISTED)}] {symbol}: LỖI - {str(exc)[:80]}")
            failed.append(symbol)
            time.sleep(pause)
            continue
        data.to_csv(DELISTED_DIR / f"{symbol}.csv", index=False, encoding="utf-8-sig")
        print(
            f"[{i}/{len(DELISTED)}] {symbol}: {len(data)} phiên "
            f"({data['time'].min():%Y-%m-%d} → {data['time'].max():%Y-%m-%d})"
        )
        time.sleep(pause)
    print(f"Tải được {len(DELISTED) - len(failed)}/{len(DELISTED)} mã.")
    if failed:
        print(f"Không có dữ liệu: {', '.join(failed)}")


def load_panel() -> tuple[pd.DataFrame, list[str], list[str]]:
    """Tính panel giá cho cả mã sống và mã chết bằng đúng hàm của pipeline chính."""

    alive = pd.read_csv(RAW_DIR / "prices_all.csv", parse_dates=["time"])
    market = pd.read_csv(RAW_DIR / "vnindex.csv", parse_dates=["time"])
    market["time"] = market["time"].dt.normalize()

    frames = [
        pd.read_csv(DELISTED_DIR / f"{symbol}.csv", parse_dates=["time"])
        for symbol in DELISTED
        if (DELISTED_DIR / f"{symbol}.csv").exists()
    ]
    dead = pd.concat(frames, ignore_index=True)
    prices = pd.concat([alive, dead], ignore_index=True)
    prices = prices.drop_duplicates(["symbol", "time"])

    panel = monthly_panel(rolling_price_stats(daily_returns(prices, market)))
    return panel, sorted(alive["symbol"].unique()), sorted(dead["symbol"].unique())


def apply_delisting_return(panel: pd.DataFrame, dead: list[str], value: float | None) -> pd.DataFrame:
    """Gán lợi suất tháng kế tiếp cho tháng cuối của mã chết đã hết dữ liệu."""

    panel = panel.copy()
    if value is None:
        return panel
    last_month = panel["month"].max()
    last_rows = panel[panel["symbol"].isin(dead)].groupby("symbol")["month"].idxmax()
    # Mã còn giá đến cuối mẫu (đã sang UPCoM) không cần giả định.
    last_rows = last_rows[panel.loc[last_rows, "month"].values < last_month]
    panel.loc[last_rows, "ret_fwd_1m"] = value
    return panel


def monthly_stats(panel: pd.DataFrame, factor: str, sign: int) -> pd.DataFrame:
    """Rank IC và spread Q5-Q1 mỗi tháng, theo hướng kỳ vọng của factor."""

    data = panel.loc[panel[factor].notna() & panel["ret_fwd_1m"].notna(),
                     ["month", factor, "ret_fwd_1m"]]
    rows = []
    for month, g in data.groupby("month"):
        if len(g) < MIN_STOCKS:
            continue
        score = g[factor] * sign
        ranks = score.rank(method="first")
        bucket = np.ceil(ranks * N_QUANTILES / len(g))
        rows.append({
            "month": month,
            "ic": score.corr(g["ret_fwd_1m"], method="spearman"),
            "spread": g.loc[bucket == N_QUANTILES, "ret_fwd_1m"].mean()
            - g.loc[bucket == 1, "ret_fwd_1m"].mean(),
        })
    return pd.DataFrame(rows).set_index("month")


def t_stat(series: pd.Series) -> float:
    series = series.dropna()
    return series.mean() / (series.std(ddof=1) / np.sqrt(len(series)))


def compare(base: pd.DataFrame, panel: pd.DataFrame) -> list[dict]:
    """So sánh từng factor giữa rổ gốc và ``panel`` trên cùng các tháng."""

    rows = []
    for factor, sign in FACTORS.items():
        a = monthly_stats(base, factor, sign)
        b = monthly_stats(panel, factor, sign)
        months = a.index.intersection(b.index)
        a, b = a.loc[months], b.loc[months]
        diff = b["spread"] - a["spread"]
        rows.append({
            "factor": factor,
            "n_months": len(months),
            "ic_base": a["ic"].mean(),
            "ic_new": b["ic"].mean(),
            "spread_base_pct_m": a["spread"].mean() * 100,
            "spread_new_pct_m": b["spread"].mean() * 100,
            "t_base": t_stat(a["spread"]),
            "t_new": t_stat(b["spread"]),
            "diff_pct_m": diff.mean() * 100,
            "t_diff": t_stat(diff),
        })
    return rows


def equal_weight_return(panel: pd.DataFrame, months: pd.Index) -> float:
    """Lợi suất tháng trung bình của danh mục đều trọng số, %/tháng."""

    data = panel[panel["month"].isin(months)]
    return data.groupby("month")["ret_fwd_1m"].mean().mean() * 100


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--download", action="store_true", help="Tải giá mã đã hủy niêm yết.")
    parser.add_argument("--pause", type=float, default=3.0)
    parser.add_argument("--min-days", type=int, default=10,
                        help="Số phiên tối thiểu trong tháng để mã được xếp hạng; 0 là không lọc.")
    args = parser.parse_args()
    if args.download:
        download_delisted(args.pause)
        return

    panel, alive, dead = load_panel()
    # Lọc sau khi gán lợi suất hủy niêm yết để không làm dời tháng cuối của mã chết.
    tradable = lambda data: data[data["n_trading_days"] >= args.min_days]
    suffix = "" if args.min_days == 10 else f"_min{args.min_days}"
    base = tradable(panel[panel["symbol"].isin(alive)])
    last_dead = panel[panel["symbol"].isin(dead)].groupby("symbol")["month"].max()
    # Sau khi mã chết cuối cùng rời mẫu, hai rổ trùng nhau nên chỉ so đến trước đó.
    window_end = last_dead[last_dead < panel["month"].max()].max()
    months = pd.period_range(panel["month"].min(), window_end, freq="M")
    print(f"{len(alive)} mã sống, {len(dead)} mã chết, so sánh đến {window_end}")
    print("Số mã chết có dữ liệu theo tháng (nhỏ nhất, lớn nhất):",
          panel[panel["symbol"].isin(dead)].groupby("month")["close"].count().agg(["min", "max"]).tolist())

    rows, levels = [], []
    for value in DELISTING_RETURNS:
        label = "bo_thang_cuoi" if value is None else f"{value:.0%}"
        full = tradable(apply_delisting_return(panel, dead, value))
        full = full[full["month"].isin(months)]
        scoped_base = base[base["month"].isin(months)]
        for row in compare(scoped_base, full):
            rows.append({"delisting_return": label, **row})
        levels.append({
            "delisting_return": label,
            "ew_base_pct_m": equal_weight_return(scoped_base, months),
            "ew_new_pct_m": equal_weight_return(full, months),
        })
    result = pd.DataFrame(rows)
    RESULT_DIR.mkdir(exist_ok=True)
    result.round(4).to_csv(RESULT_DIR / f"survivorship_check{suffix}.csv", index=False)
    pd.DataFrame(levels).round(4).to_csv(RESULT_DIR / f"survivorship_levels{suffix}.csv", index=False)

    # Rổ tỷ lệ thực tế: rút ngẫu nhiên vài mã chết thay vì thêm tất cả.
    rng = np.random.default_rng(SEED)
    full = tradable(apply_delisting_return(panel, dead, -0.55))
    full = full[full["month"].isin(months)]
    scoped_base = base[base["month"].isin(months)]
    draws, ew_draws = [], []
    for _ in range(N_DRAWS):
        picked = list(rng.choice(dead, size=REALISTIC_DEAD, replace=False))
        drawn = full[full["symbol"].isin(alive + picked)]
        draws += compare(scoped_base, drawn)
        ew_draws.append(equal_weight_return(drawn, months))
    summary = (
        pd.DataFrame(draws).groupby("factor", sort=False)["diff_pct_m"]
        .describe(percentiles=[0.05, 0.5, 0.95])[["5%", "50%", "95%"]]
        .rename(columns={"5%": "p05", "50%": "median", "95%": "p95"})
    )
    summary.round(4).to_csv(RESULT_DIR / f"survivorship_draws{suffix}.csv")

    pd.set_option("display.width", 160, "display.max_columns", 20)
    print(pd.DataFrame(levels).round(3).to_string(index=False))
    print(result.round(3).to_string(index=False))
    print(f"\nChênh lệch spread (%/tháng) khi thêm {REALISTIC_DEAD} mã chết ngẫu nhiên, "
          f"{N_DRAWS} lần rút, lợi suất hủy niêm yết -55%:")
    print(summary.round(3).to_string())
    ew = np.percentile(ew_draws, [5, 50, 95]).round(3)
    print(f"Lợi suất đều trọng số các lần rút, %/tháng (p05, trung vị, p95): {ew.tolist()}")


if __name__ == "__main__":
    main()
