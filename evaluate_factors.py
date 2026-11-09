"""Bước 3-4: chia nhóm quintile theo từng factor, tính IC, spread long-short, t-stat.

Mỗi cuối tháng, xếp mã theo factor (đã nhân với hướng kỳ vọng), chia 5 nhóm đều
trọng số, rồi đo lợi suất tháng sau. Q5 là nhóm kỳ vọng có lợi suất cao, nên số
dương nghĩa là factor đúng hướng.

Hai cách chia nhóm:
    raw      xếp chung cả rổ
    neutral  xếp riêng trong từng mẫu BCTC (bank, broker, corporate) rồi gộp, để
             factor không thành phép chia theo ngành (leverage, sp là rõ nhất)

Các cửa sổ:
    full         mọi tháng factor có dữ liệu (mỗi factor một độ dài khác nhau)
    common       chỉ các tháng mọi factor đều có dữ liệu, để so sánh giữa các factor
    first_half, second_half   chia đôi số tháng của từng factor
    ex_covid     bỏ các tháng tạo danh mục từ 03/2020 đến 06/2021

Đa kiểm định: hoán vị lợi suất giữa các mã trong từng tháng rồi lấy max|t| trên
toàn bộ factor. Cách này giữ tương quan giữa các factor và không dựa vào phân phối
chuẩn, vốn quá lạc quan với t Newey-West khi mẫu chỉ khoảng 80 tháng.

Đầu vào (chỉ ở máy):
    data/final/factor_panel.csv

Đầu ra:
    results/factor_summary.csv    (IC, IC IR, spread, Sharpe, t-stat theo factor)
    results/factor_quintiles.csv  (lợi suất trung bình từng nhóm)
    results/factor_spreads.png, results/factor_cumulative.png

Chuỗi lợi suất theo tháng chỉ dùng để vẽ, không được lưu ra file.

Chạy:
    python3 evaluate_factors.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from compute_factors import OUTPUT_FILE as PANEL_FILE
from download_stocks import PROJECT_DIR


RESULT_DIR = PROJECT_DIR / "results"

# Factor -> (nhóm, hướng kỳ vọng). `mcap` bỏ qua vì cùng thứ hạng với `log_mcap`.
FACTORS = {
    "log_mcap": ("Size", -1),
    "bm": ("Value", 1),
    "ep": ("Value", 1),
    "sp": ("Value", 1),
    "cfp": ("Value", 1),
    "mom_12_1": ("Momentum", 1),
    "mom_6_1": ("Momentum", 1),
    "ret_1m": ("Momentum", -1),
    "beta_12m": ("Low-risk", -1),
    "vol_3m": ("Low-risk", -1),
    "ivol_3m": ("Low-risk", -1),
    "max_ret_1m": ("Low-risk", -1),
    "amihud_3m": ("Thanh khoản", 1),
    "turnover_3m": ("Thanh khoản", -1),
    "roe": ("Quality", 1),
    "roa": ("Quality", 1),
    "gross_profitability": ("Quality", 1),
    "leverage": ("Quality", -1),
    "accruals": ("Quality", -1),
    "earnings_growth": ("Quality", 1),
    "asset_growth": ("Investment", -1),
}
SPECS = ["raw", "neutral"]
N_QUANTILES = 5
# Giống survivorship_check.py: tháng có ít mã hơn bị bỏ, mã ít phiên không được xếp.
MIN_STOCKS = 25
MIN_TRADING_DAYS = 10
MONTHS_PER_YEAR = 12
COVID_START, COVID_END = "2020-03-01", "2021-06-30"
# Đa kiểm định chỉ tính cho hai cửa sổ chính.
TESTED_WINDOWS = ["full", "common"]
N_PERMUTATIONS = 2000
SEED = 20261109


def newey_west_lags(n: int) -> int:
    """Số độ trễ theo quy tắc Newey-West (1994): floor(4 * (T/100)^(2/9))."""

    return int(np.floor(4 * (n / 100) ** (2 / 9)))


def newey_west_t(series: pd.Series | np.ndarray) -> float:
    """Thống kê t của trung bình, sai số chuẩn Newey-West với nhân Bartlett."""

    x = np.asarray(series, dtype=float)
    x = x[~np.isnan(x)]
    n = len(x)
    e = x - x.mean()
    variance = e @ e / n
    lags = newey_west_lags(n)
    for lag in range(1, lags + 1):
        variance += 2 * (1 - lag / (lags + 1)) * (e[lag:] @ e[:-lag]) / n
    return x.mean() / np.sqrt(variance / n)


def assign_buckets(score: pd.Series, groups: pd.Series | None = None) -> pd.Series:
    """Chia 1..N_QUANTILES theo score; có ``groups`` thì chia riêng trong từng nhóm.

    Giá trị bằng nhau được xếp theo thứ tự dòng, nên panel phải sắp theo mã trước
    để kết quả không đổi giữa các lần chạy.
    """

    def bucket(values: pd.Series) -> pd.Series:
        return np.ceil(values.rank(method="first") * N_QUANTILES / len(values))

    if groups is None:
        return bucket(score)
    return score.groupby(groups, group_keys=False).apply(bucket)


def within_group_percentile(score: pd.Series, groups: pd.Series) -> pd.Series:
    """Thứ hạng phần trăm trong từng nhóm, để IC bản neutral bỏ chênh lệch giữa nhóm."""

    return score.groupby(groups).rank(pct=True)


def monthly_series(panel: pd.DataFrame, factor: str, sign: int, spec: str) -> pd.DataFrame:
    """Mỗi tháng một dòng: IC, lợi suất Q1..Q5, spread Q5-Q1, số mã."""

    data = panel.loc[
        panel[factor].notna() & panel["ret_fwd_1m"].notna(),
        ["date", "symbol", "group", factor, "ret_fwd_1m"],
    ]
    rows = []
    for date, g in data.groupby("date"):
        if len(g) < MIN_STOCKS:
            continue
        score = g[factor] * sign
        if spec == "neutral":
            buckets = assign_buckets(score, g["group"])
            ic_score = within_group_percentile(score, g["group"])
        else:
            buckets = assign_buckets(score)
            ic_score = score
        means = g["ret_fwd_1m"].groupby(buckets).mean()
        row = {f"q{q}": means.get(float(q), np.nan) for q in range(1, N_QUANTILES + 1)}
        row.update(
            date=date,
            n_stocks=len(g),
            ic=ic_score.corr(g["ret_fwd_1m"], method="spearman"),
            spread=row[f"q{N_QUANTILES}"] - row["q1"],
        )
        rows.append(row)
    return pd.DataFrame(rows).set_index("date")


def summarize(series: pd.DataFrame) -> dict:
    """Gộp chuỗi tháng thành các thống kê của bước 4."""

    ic, spread = series["ic"].dropna(), series["spread"].dropna()
    quintile_means = [series[f"q{q}"].mean() for q in range(1, N_QUANTILES + 1)]
    return {
        "n_months": len(series),
        "first_month": series.index.min().strftime("%Y-%m"),
        "last_month": series.index.max().strftime("%Y-%m"),
        "avg_stocks": series["n_stocks"].mean(),
        "ic_mean": ic.mean(),
        "ic_ir": ic.mean() / ic.std(ddof=1),
        "ic_t_nw": newey_west_t(ic),
        "ic_positive_share": (ic > 0).mean(),
        "spread_pct_m": spread.mean() * 100,
        "spread_t_simple": spread.mean() / (spread.std(ddof=1) / np.sqrt(len(spread))),
        "spread_t_nw": newey_west_t(spread),
        "sharpe_ann": spread.mean() / spread.std(ddof=1) * np.sqrt(MONTHS_PER_YEAR),
        "spread_positive_share": (spread > 0).mean(),
        # 1 là lợi suất tăng đều từ Q1 đến Q5, -1 là giảm đều.
        "monotonicity": pd.Series(quintile_means).corr(
            pd.Series(range(N_QUANTILES)), method="spearman"
        ),
    }


def extreme_masks(panel: pd.DataFrame, factor: str, sign: int, spec: str,
                  dates: pd.Index, symbols: pd.Index) -> tuple[np.ndarray, np.ndarray]:
    """Ma trận tháng × mã đánh dấu Q1 và Q5, chia nhóm đúng như ``monthly_series``."""

    low = np.zeros((len(dates), len(symbols)), dtype=bool)
    high = low.copy()
    data = panel[panel[factor].notna() & panel["ret_fwd_1m"].notna()]
    for date, g in data.groupby("date"):
        if len(g) < MIN_STOCKS:
            continue
        score = g[factor] * sign
        buckets = assign_buckets(score, g["group"] if spec == "neutral" else None)
        row, columns = dates.get_loc(date), symbols.get_indexer(g["symbol"])
        low[row, columns] = buckets.to_numpy() == 1
        high[row, columns] = buckets.to_numpy() == N_QUANTILES
    return low, high


def permute_returns(returns: np.ndarray, blocks: list[np.ndarray],
                    rng: np.random.Generator) -> np.ndarray:
    """Xáo lợi suất giữa các mã trong từng tháng và từng khối, giữ nguyên ô trống."""

    shuffled = returns.copy()
    for row in range(returns.shape[0]):
        for block in blocks:
            present = block[~np.isnan(returns[row, block])]
            shuffled[row, present] = rng.permutation(returns[row, present])
    return shuffled


def permutation_tests(panel: pd.DataFrame, summary: pd.DataFrame, windows: dict,
                      n_permutations: int, seed: int) -> pd.DataFrame:
    """Thêm p-value hoán vị: riêng từng factor, và max-t trên mọi factor.

    Bản raw xáo trong cả rổ; bản neutral xáo trong từng mẫu BCTC, đúng với cách chia
    nhóm của từng bản. ``windows`` là {(factor, spec, window): các tháng}.
    """

    returns_table = panel.pivot(index="date", columns="symbol", values="ret_fwd_1m")
    dates, symbols = returns_table.index, returns_table.columns
    returns = returns_table.to_numpy()
    group_of = panel.groupby("symbol")["group"].first().reindex(symbols).to_numpy()
    blocks_by_spec = {
        "raw": [np.arange(len(symbols))],
        "neutral": [np.flatnonzero(group_of == name) for name in np.unique(group_of)],
    }

    rng = np.random.default_rng(seed)
    summary = summary.copy()
    for spec in SPECS:
        masks = {
            factor: extreme_masks(panel, factor, sign, spec, dates, symbols)
            for factor, (_, sign) in FACTORS.items()
        }
        draws = {window: np.zeros((n_permutations, len(FACTORS))) for window in TESTED_WINDOWS}
        rows = {
            window: [dates.get_indexer(windows[(factor, spec, window)]) for factor in FACTORS]
            for window in TESTED_WINDOWS
        }
        for draw in range(n_permutations):
            filled = np.nan_to_num(permute_returns(returns, blocks_by_spec[spec], rng))
            for column, (low, high) in enumerate(masks.values()):
                with np.errstate(invalid="ignore", divide="ignore"):
                    spread = (filled * high).sum(1) / high.sum(1) - (filled * low).sum(1) / low.sum(1)
                for window in TESTED_WINDOWS:
                    draws[window][draw, column] = abs(newey_west_t(spread[rows[window][column]]))

        for window in TESTED_WINDOWS:
            max_t = draws[window].max(axis=1)
            for column, factor in enumerate(FACTORS):
                where = (summary["factor"] == factor) & (summary["spec"] == spec) & (summary["window"] == window)
                observed = abs(summary.loc[where, "spread_t_nw"].iloc[0])
                exceed = (draws[window][:, column] >= observed).sum()
                summary.loc[where, "spread_p_perm"] = (1 + exceed) / (1 + n_permutations)
                summary.loc[where, "spread_p_maxt"] = (1 + (max_t >= observed).sum()) / (1 + n_permutations)
                summary.loc[where, "maxt_threshold_5pct"] = np.quantile(max_t, 0.95)
    return summary


def load_panel(path: Path) -> pd.DataFrame:
    """Đọc panel, lọc mã ít phiên, gán mỗi mã một mẫu BCTC cố định làm nhóm."""

    panel = pd.read_csv(path, parse_dates=["date"], encoding="utf-8-sig")
    panel = panel[panel["n_trading_days"] >= MIN_TRADING_DAYS]
    # `template` trống trước khi có BCTC, nhưng mẫu của một mã không đổi theo thời gian.
    template = panel.dropna(subset=["template"]).groupby("symbol")["template"].last()
    panel = panel.assign(group=panel["symbol"].map(template))
    if panel["group"].isna().any():
        raise ValueError("Có mã không xác định được mẫu BCTC.")
    return panel.sort_values(["date", "symbol"]).reset_index(drop=True)


def common_months(all_series: dict) -> pd.DatetimeIndex:
    """Các tháng mọi factor đều có giá trị, dùng để so sánh công bằng giữa factor."""

    months = None
    for series in all_series.values():
        months = series.index if months is None else months.intersection(series.index)
    return months


def window_months(index: pd.DatetimeIndex, common: pd.DatetimeIndex) -> dict[str, pd.DatetimeIndex]:
    """Các tháng của từng cửa sổ, cho một factor có chuỗi tháng ``index``."""

    middle = len(index) // 2
    return {
        "full": index,
        "common": common,
        "first_half": index[:middle],
        "second_half": index[middle:],
        "ex_covid": index[(index < COVID_START) | (index > COVID_END)],
    }


def evaluate(panel: pd.DataFrame, n_permutations: int = N_PERMUTATIONS,
             seed: int = SEED) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Chạy mọi factor × spec × window. Trả về bảng tổng hợp, bảng nhóm, chuỗi tháng."""

    all_series = {
        (factor, spec): monthly_series(panel, factor, sign, spec)
        for factor, (_, sign) in FACTORS.items()
        for spec in SPECS
    }
    months = common_months(all_series)

    summary_rows, quintile_rows, windows = [], [], {}
    for (factor, spec), series in all_series.items():
        group_name, sign = FACTORS[factor]
        for window, scope in window_months(series.index, months).items():
            windows[(factor, spec, window)] = scope
            scoped = series.loc[scope]
            key = {"factor": factor, "group": group_name, "sign": sign, "spec": spec, "window": window}
            summary_rows.append({**key, **summarize(scoped)})
            for q in range(1, N_QUANTILES + 1):
                quintile_rows.append({
                    **key,
                    "quintile": q,
                    "ret_pct_m": scoped[f"q{q}"].mean() * 100,
                })
    summary = permutation_tests(panel, pd.DataFrame(summary_rows), windows, n_permutations, seed)
    return summary, pd.DataFrame(quintile_rows), all_series


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--panel", type=Path, default=PANEL_FILE)
    parser.add_argument("--output-dir", type=Path, default=RESULT_DIR,
                        help="Thư mục ghi kết quả; dùng thư mục tạm khi thử.")
    parser.add_argument("--no-charts", action="store_true")
    parser.add_argument("--permutations", type=int, default=N_PERMUTATIONS)
    args = parser.parse_args()

    panel = load_panel(args.panel)
    summary, quintiles, all_series = evaluate(panel, args.permutations)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary.round(4).to_csv(args.output_dir / "factor_summary.csv", index=False)
    quintiles.round(4).to_csv(args.output_dir / "factor_quintiles.csv", index=False)
    if not args.no_charts:
        from plot_factors import plot_cumulative, plot_spreads

        plot_spreads(summary, args.output_dir / "factor_spreads.png")
        plot_cumulative(all_series, args.output_dir / "factor_cumulative.png")

    columns = ["factor", "n_months", "ic_mean", "ic_t_nw", "spread_pct_m", "spread_t_nw",
               "sharpe_ann", "monotonicity", "spread_p_perm", "spread_p_maxt"]
    pd.set_option("display.width", 170, "display.max_columns", 20)
    for spec in SPECS:
        for window in TESTED_WINDOWS:
            table = summary[(summary["spec"] == spec) & (summary["window"] == window)]
            threshold = table["maxt_threshold_5pct"].iloc[0]
            print(f"\n{spec}, cửa sổ {window}, ngưỡng max|t| ở mức 5%: {threshold:.2f}")
            print(table[columns].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
