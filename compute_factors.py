"""Tính panel factor theo tháng (mã × cuối tháng) làm input cho model.

Đầu vào (không đưa lên GitHub vì không có quyền phân phối dữ liệu gốc):
    data/raw/prices_all.csv, data/raw/vnindex.csv, data/raw/universe.csv
    data/processed/fundamentals_long.csv   (từ parse_fundamentals.py)

Đầu ra (chỉ gồm chỉ số đã tính, không chứa giá hay số liệu BCTC gốc):
    data/final/factor_panel.csv

Point-in-time: số liệu quý chỉ được dùng từ ``quarter_end + REPORT_LAG_DAYS``.
Hạn công bố BCTC quý là 20-30 ngày (Thông tư 96/2020), chọn 45 ngày cho an toàn.

Chạy:
    python3 compute_factors.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from download_stocks import BENCHMARK_SYMBOL, PROJECT_DIR, RAW_DIR
from parse_fundamentals import PROCESSED_DIR


FINAL_DIR = PROJECT_DIR / "data" / "final"
OUTPUT_FILE = FINAL_DIR / "factor_panel.csv"

REPORT_LAG_DAYS = 45
PAR_VALUE = 10_000  # mệnh giá cổ phiếu VN, đồng
PRICE_UNIT = 1_000  # giá vnstock tính bằng nghìn đồng
TRADING_DAYS = 252

# Tên chỉ tiêu theo từng mẫu BCTC của FiinTrade. Lấy dòng đầu tiên khớp tên.
ITEM_MAP = {
    "bank": {
        "total_assets": ("balance_sheet", "TỔNG TÀI SẢN"),
        "total_liabilities": ("balance_sheet", "Tổng nợ phải trả"),
        "equity": ("balance_sheet", "Vốn chủ sở hữu"),
        "minority": ("balance_sheet", "Lợi ích của cổ đông thiểu số"),
        "charter_capital": ("balance_sheet", "Vốn điều lệ"),
        "revenue": ("income_statement", "Tổng thu nhập hoạt động"),
        "net_income": ("income_statement", "Cổ đông của Công ty mẹ"),
        "cfo": ("cash_flow", "Lưu chuyển tiền thuần từ các hoạt động sản xuất kinh doanh"),
    },
    "corporate": {
        "total_assets": ("balance_sheet", "TỔNG TÀI SẢN"),
        "total_liabilities": ("balance_sheet", "NỢ PHẢI TRẢ"),
        "equity": ("balance_sheet", "VỐN CHỦ SỞ HỮU"),
        "minority": ("balance_sheet", "Lợi ích cổ đông không kiểm soát"),
        "charter_capital": ("balance_sheet", "Vốn góp"),
        "revenue": ("income_statement", "Doanh số thuần"),
        "gross_profit": ("income_statement", "Lãi gộp"),
        "net_income": ("income_statement", "Lợi nhuận của Cổ đông của Công ty mẹ"),
        "cfo": ("cash_flow", "Lưu chuyển tiền thuần từ các hoạt động sản xuất kinh doanh"),
    },
}
FLOW_ITEMS = ["revenue", "gross_profit", "net_income", "cfo"]
# Nhận diện mẫu ngân hàng qua một chỉ tiêu chỉ ngân hàng có.
BANK_MARKER = ("income_statement", "Tổng thu nhập hoạt động")


# --------------------------------------------------------------------------- #
# Báo cáo tài chính
# --------------------------------------------------------------------------- #
def extract_items(fund: pd.DataFrame) -> pd.DataFrame:
    """Chọn các chỉ tiêu chuẩn hóa cho từng mã, trả về bảng rộng (mã × quý)."""

    rows = []
    for symbol, group in fund.groupby("symbol"):
        has_marker = (
            (group["statement"] == BANK_MARKER[0]) & (group["item"] == BANK_MARKER[1])
        ).any()
        template = "bank" if has_marker else "corporate"
        out = pd.DataFrame(index=pd.PeriodIndex(sorted(group["period"].unique()), freq="Q"))
        for name, (statement, item) in ITEM_MAP[template].items():
            match = group[(group["statement"] == statement) & (group["item"] == item)]
            if match.empty:
                print(f"{symbol}: không tìm thấy '{item}' ({statement})")
                continue
            first_line = match["line_no"].min()
            series = match[match["line_no"] == first_line].set_index("period")["value"]
            series.index = pd.PeriodIndex(series.index, freq="Q")
            out[name] = series
        out = out.reindex(pd.period_range(out.index.min(), out.index.max(), freq="Q"))
        out.index.name = "period"
        out = out.reset_index()
        out.insert(0, "is_bank", template == "bank")
        out.insert(0, "symbol", symbol)
        rows.append(out)
    return pd.concat(rows, ignore_index=True)


def fundamental_ratios(items: pd.DataFrame) -> pd.DataFrame:
    """Tính các biến TTM và tỷ lệ không cần giá, cộng ngày có thể dùng (PIT)."""

    frames = []
    for _, g in items.groupby("symbol"):
        g = g.sort_values("period").copy()
        for col in ["gross_profit"]:
            if col not in g:
                g[col] = np.nan
        g["book_equity"] = g["equity"] - g["minority"].fillna(0)
        g["shares"] = g["charter_capital"] / PAR_VALUE
        for col in FLOW_ITEMS:
            g[f"{col}_ttm"] = g[col].rolling(4, min_periods=4).sum()

        assets_lag4 = g["total_assets"].shift(4)
        equity_avg = (g["book_equity"] + g["book_equity"].shift(4)) / 2
        ni_ttm_lag4 = g["net_income_ttm"].shift(4)

        g["roe"] = g["net_income_ttm"] / equity_avg
        g["roa"] = g["net_income_ttm"] / g["total_assets"]
        g["gross_profitability"] = g["gross_profit_ttm"] / g["total_assets"]
        g["leverage"] = g["total_liabilities"] / g["total_assets"]
        g["asset_growth"] = g["total_assets"] / assets_lag4 - 1
        g["earnings_growth"] = (g["net_income_ttm"] - ni_ttm_lag4) / ni_ttm_lag4.abs()
        g["accruals"] = (g["net_income_ttm"] - g["cfo_ttm"]) / g["total_assets"]
        # CFO của ngân hàng gồm biến động tiền gửi/cho vay nên không phản ánh
        # chất lượng lợi nhuận; bỏ accruals cho nhóm này.
        g.loc[g["is_bank"], "accruals"] = np.nan
        frames.append(g)

    data = pd.concat(frames, ignore_index=True)
    data["available_date"] = (
        data["period"].dt.end_time.dt.normalize() + pd.Timedelta(days=REPORT_LAG_DAYS)
    )
    return data


# --------------------------------------------------------------------------- #
# Giá
# --------------------------------------------------------------------------- #
def daily_returns(prices: pd.DataFrame, market: pd.DataFrame) -> pd.DataFrame:
    """Thêm lợi suất ngày của mã và thị trường, giá trị giao dịch (đồng)."""

    prices = prices.sort_values(["symbol", "time"]).copy()
    prices["ret"] = prices.groupby("symbol")["close"].pct_change()
    prices["value_traded"] = prices["close"] * PRICE_UNIT * prices["volume"]
    market = market.sort_values("time").assign(mkt_ret=lambda d: d["close"].pct_change())
    return prices.merge(market[["time", "mkt_ret"]], on="time", how="left")


def rolling_price_stats(daily: pd.DataFrame) -> pd.DataFrame:
    """Beta, độ biến động, idiosyncratic vol, Amihud theo cửa sổ trượt."""

    frames = []
    for _, g in daily.groupby("symbol"):
        g = g.copy()
        r, m = g["ret"], g["mkt_ret"]
        cov_12m = r.rolling(TRADING_DAYS, min_periods=120).cov(m)
        var_m_12m = m.rolling(TRADING_DAYS, min_periods=120).var()
        g["beta_12m"] = cov_12m / var_m_12m

        cov_3m = r.rolling(63, min_periods=40).cov(m)
        var_m_3m = m.rolling(63, min_periods=40).var()
        var_r_3m = r.rolling(63, min_periods=40).var()
        resid_var = (var_r_3m - cov_3m**2 / var_m_3m).clip(lower=0)
        g["vol_3m"] = np.sqrt(var_r_3m * TRADING_DAYS)
        g["ivol_3m"] = np.sqrt(resid_var * TRADING_DAYS)

        illiq = (r.abs() / g["value_traded"].replace(0, np.nan)) * 1e9
        g["amihud_3m"] = illiq.rolling(63, min_periods=40).mean()
        g["volume_3m"] = g["volume"].rolling(63, min_periods=40).mean()
        frames.append(g)
    return pd.concat(frames, ignore_index=True)


def monthly_panel(daily: pd.DataFrame) -> pd.DataFrame:
    """Lấy phiên cuối mỗi tháng, tính lợi suất tháng, momentum, max."""

    daily = daily.copy()
    daily["month"] = daily["time"].dt.to_period("M")
    # Bỏ tháng cuối nếu chưa kết thúc (dữ liệu dừng trước ngày làm việc cuối tháng).
    last_day = daily["time"].max()
    if last_day < last_day + pd.offsets.BMonthEnd(0):
        daily = daily[daily["month"] < last_day.to_period("M")]
    grouped = daily.groupby(["symbol", "month"])
    monthly = grouped.last().reset_index()
    monthly["n_trading_days"] = grouped.size().values
    monthly["max_ret_1m"] = grouped["ret"].max().values

    market = daily.drop_duplicates("time").groupby("month")["mkt_ret"].apply(
        lambda x: (1 + x).prod() - 1
    )

    frames = []
    for _, g in monthly.groupby("symbol"):
        g = g.sort_values("month").copy()
        # Bỏ qua tháng trống (đình chỉ) khi dịch: reindex theo dãy tháng liên tục.
        g = g.set_index("month").reindex(
            pd.period_range(g["month"].min(), g["month"].max(), freq="M")
        )
        g["symbol"] = g["symbol"].ffill()
        close = g["close"]
        g["ret_1m"] = close / close.shift(1) - 1
        g["ret_fwd_1m"] = g["ret_1m"].shift(-1)
        g["mom_12_1"] = close.shift(1) / close.shift(12) - 1
        g["mom_6_1"] = close.shift(1) / close.shift(6) - 1
        frames.append(g.rename_axis("month").reset_index())

    panel = pd.concat(frames, ignore_index=True)
    panel["mkt_ret_1m"] = panel["month"].map(market)
    panel["date"] = panel["month"].dt.end_time.dt.normalize()
    return panel


# --------------------------------------------------------------------------- #
# Ghép
# --------------------------------------------------------------------------- #
def attach_fundamentals(panel: pd.DataFrame, fund: pd.DataFrame) -> pd.DataFrame:
    """Gắn BCTC mới nhất đã công bố tại mỗi cuối tháng (merge_asof theo ngày)."""

    cols = [
        "symbol", "available_date", "period", "is_bank", "book_equity", "shares",
        "revenue_ttm", "net_income_ttm", "cfo_ttm", "roe", "roa",
        "gross_profitability", "leverage", "asset_growth", "earnings_growth", "accruals",
    ]
    fund = fund[cols].rename(columns={"period": "fiscal_quarter"}).sort_values("available_date")
    panel = panel.sort_values("date")
    merged = pd.merge_asof(
        panel, fund, left_on="date", right_on="available_date", by="symbol",
        direction="backward",
    )

    # Vốn hóa: giá vnstock đã điều chỉnh chia tách/cổ tức về hiện tại, nên nhân
    # với số cổ phiếu mới nhất cho ra xấp xỉ vốn hóa thực tại thời điểm t.
    latest_shares = fund.sort_values("available_date").groupby("symbol")["shares"].last()
    merged["mcap"] = merged["close"] * PRICE_UNIT * merged["symbol"].map(latest_shares)
    merged["log_mcap"] = np.log(merged["mcap"])
    merged["bm"] = merged["book_equity"] / merged["mcap"]
    merged["ep"] = merged["net_income_ttm"] / merged["mcap"]
    merged["sp"] = merged["revenue_ttm"] / merged["mcap"]
    merged["cfp"] = merged["cfo_ttm"] / merged["mcap"]
    merged.loc[merged["is_bank"].eq(True), "cfp"] = np.nan
    merged["turnover_3m"] = merged["volume_3m"] / merged["symbol"].map(latest_shares)
    return merged


OUTPUT_COLUMNS = [
    "date", "symbol", "exchange", "sector", "is_bank", "fiscal_quarter",
    "n_trading_days", "ret_1m", "ret_fwd_1m", "mkt_ret_1m",
    # Size
    "mcap", "log_mcap",
    # Value
    "bm", "ep", "sp", "cfp",
    # Momentum / reversal
    "mom_12_1", "mom_6_1",
    # Low risk
    "beta_12m", "vol_3m", "ivol_3m", "max_ret_1m",
    # Liquidity
    "amihud_3m", "turnover_3m",
    # Quality / profitability / investment
    "roe", "roa", "gross_profitability", "leverage", "accruals",
    "earnings_growth", "asset_growth",
]


def main() -> None:
    prices = pd.read_csv(RAW_DIR / "prices_all.csv", parse_dates=["time"])
    market = pd.read_csv(RAW_DIR / "vnindex.csv", parse_dates=["time"])
    market["time"] = market["time"].dt.normalize()
    universe = pd.read_csv(RAW_DIR / "universe.csv")
    fundamentals = pd.read_csv(PROCESSED_DIR / "fundamentals_long.csv")

    daily = rolling_price_stats(daily_returns(prices, market))
    panel = monthly_panel(daily)
    ratios = fundamental_ratios(extract_items(fundamentals))
    panel = attach_fundamentals(panel, ratios)
    panel = panel.merge(universe, on="symbol", how="left")
    panel["fiscal_quarter"] = panel["fiscal_quarter"].astype(str).replace("NaT", "")

    output = panel[OUTPUT_COLUMNS].sort_values(["date", "symbol"]).reset_index(drop=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"{len(output)} dòng, {output['symbol'].nunique()} mã, "
          f"{output['date'].min():%Y-%m} → {output['date'].max():%Y-%m}")
    print("Tỷ lệ có dữ liệu theo cột:")
    print(output.notna().mean().round(2).to_string())


if __name__ == "__main__":
    main()
