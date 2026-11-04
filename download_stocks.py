"""Tải dữ liệu giá OHLCV hằng ngày của ~30 cổ phiếu VN và VN-Index qua vnstock.

Nguồn KBS trả về giá đã điều chỉnh cổ tức/chia tách (đơn vị: nghìn đồng).
Bản cộng đồng của vnstock giới hạn dữ liệu 1D tối đa 8 năm.

Chạy:
    python3 download_stocks.py
    python3 download_stocks.py --start 2020-01-01 --end 2026-11-04
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Union

import pandas as pd


PathLike = Union[str, Path]

PROJECT_DIR = Path(__file__).resolve().parent
RAW_PRICE_DIR = PROJECT_DIR / "data" / "raw" / "prices"
RAW_DIR = PROJECT_DIR / "data" / "raw"

SOURCE = "KBS"
BENCHMARK_SYMBOL = "VNINDEX"
DEFAULT_END = pd.Timestamp.today().normalize()
DEFAULT_START = DEFAULT_END - pd.DateOffset(years=8) + pd.Timedelta(days=1)

# Rổ 50 mã trải đều vốn hóa lớn/vừa/nhỏ và nhiều ngành để các factor
# (đặc biệt là Size, Value) có độ phân tán. Lưu ý: danh sách chọn theo hiện tại
# nên còn survivorship bias, sẽ xử lý ở bước làm sạch dữ liệu.
UNIVERSE = {
    # HOSE - Ngân hàng
    "VCB": ("HOSE", "Ngân hàng"),
    "BID": ("HOSE", "Ngân hàng"),
    "CTG": ("HOSE", "Ngân hàng"),
    "TCB": ("HOSE", "Ngân hàng"),
    "MBB": ("HOSE", "Ngân hàng"),
    "ACB": ("HOSE", "Ngân hàng"),
    "VPB": ("HOSE", "Ngân hàng"),
    # HOSE - Bất động sản
    "VIC": ("HOSE", "Bất động sản"),
    "VHM": ("HOSE", "Bất động sản"),
    "KDH": ("HOSE", "Bất động sản"),
    "DXG": ("HOSE", "Bất động sản"),
    # HOSE - Tiêu dùng, bán lẻ
    "VNM": ("HOSE", "Tiêu dùng"),
    "MSN": ("HOSE", "Tiêu dùng"),
    "SAB": ("HOSE", "Tiêu dùng"),
    "MWG": ("HOSE", "Bán lẻ"),
    "PNJ": ("HOSE", "Bán lẻ"),
    # HOSE - Công nghiệp, nguyên vật liệu, năng lượng
    "HPG": ("HOSE", "Thép"),
    "HSG": ("HOSE", "Thép"),
    "DGC": ("HOSE", "Hóa chất"),
    "GAS": ("HOSE", "Năng lượng"),
    "PLX": ("HOSE", "Năng lượng"),
    "REE": ("HOSE", "Tiện ích"),
    "GMD": ("HOSE", "Cảng biển"),
    # HOSE - Công nghệ, chứng khoán
    "FPT": ("HOSE", "Công nghệ"),
    "SSI": ("HOSE", "Chứng khoán"),
    # HNX
    "SHS": ("HNX", "Chứng khoán"),
    "MBS": ("HNX", "Chứng khoán"),
    "PVS": ("HNX", "Năng lượng"),
    "IDC": ("HNX", "Bất động sản KCN"),
    "CEO": ("HNX", "Bất động sản"),
    # --- Mở rộng lên 50 mã (giữ tỷ lệ ~85% HOSE, ~1/3 tài chính) ---
    # HOSE - Ngân hàng
    "STB": ("HOSE", "Ngân hàng"),
    "HDB": ("HOSE", "Ngân hàng"),
    "TPB": ("HOSE", "Ngân hàng"),
    "EIB": ("HOSE", "Ngân hàng"),
    # HOSE - Chứng khoán
    "VND": ("HOSE", "Chứng khoán"),
    "HCM": ("HOSE", "Chứng khoán"),
    # HOSE - Doanh nghiệp thường
    "NLG": ("HOSE", "Bất động sản"),
    "KBC": ("HOSE", "Bất động sản KCN"),
    "VJC": ("HOSE", "Hàng không"),
    "DPM": ("HOSE", "Phân bón"),
    "DHG": ("HOSE", "Dược phẩm"),
    "VHC": ("HOSE", "Thủy sản"),
    "CTD": ("HOSE", "Xây dựng"),
    "PC1": ("HOSE", "Xây lắp điện"),
    "PVD": ("HOSE", "Dịch vụ dầu khí"),
    "BMP": ("HOSE", "Nhựa"),
    "DRC": ("HOSE", "Cao su"),
    # HNX
    "VCS": ("HNX", "Vật liệu xây dựng"),
    "TNG": ("HNX", "Dệt may"),
    "PLC": ("HNX", "Hóa chất"),
}


def download_symbol(
    symbol: str,
    start_date: str,
    end_date: str,
    source: str = SOURCE,
    retries: int = 3,
    pause: float = 3.0,
) -> pd.DataFrame:
    """Tải OHLCV hằng ngày của ``symbol``, thử lại khi lỗi mạng/giới hạn tần suất.

    ``end_date`` là ngày cuối cùng cần lấy (tính cả ngày này).
    """

    try:
        from vnstock import Quote
    except ImportError as exc:
        raise RuntimeError(
            "Chưa cài vnstock. Hãy chạy: python3 -m pip install -r requirements.txt"
        ) from exc

    source_end = (pd.Timestamp(end_date) + pd.Timedelta(days=1)).strftime(
        "%Y-%m-%d"
    )
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            data = Quote(symbol=symbol, source=source).history(
                symbol=symbol, start=start_date, end=source_end, interval="1D"
            )
            if data is None or data.empty:
                raise RuntimeError(f"Không có dữ liệu {symbol} từ nguồn {source}.")
            data = data.copy()
            data["time"] = pd.to_datetime(data["time"]).dt.normalize()
            data = data[data["time"] <= pd.Timestamp(end_date)]
            data.insert(0, "symbol", symbol)
            return data
        except Exception as exc:  # noqa: BLE001 - vnstock ném nhiều loại lỗi
            last_error = exc
            time.sleep(pause * attempt * 5)
    raise RuntimeError(f"Tải {symbol} thất bại sau {retries} lần: {last_error}")


def download_universe(
    start_date: str,
    end_date: str,
    symbols: list[str] | None = None,
    output_dir: PathLike = RAW_PRICE_DIR,
    pause: float = 3.0,
) -> pd.DataFrame:
    """Tải toàn bộ rổ cổ phiếu, lưu mỗi mã một file và một file gộp dạng long."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    symbols = symbols or list(UNIVERSE)

    frames, failed = [], []
    for i, symbol in enumerate(symbols, start=1):
        try:
            data = download_symbol(symbol, start_date, end_date, pause=pause)
        except RuntimeError as exc:
            print(f"[{i}/{len(symbols)}] {symbol}: LỖI - {exc}")
            failed.append(symbol)
            continue
        data.to_csv(output / f"{symbol}.csv", index=False, encoding="utf-8-sig")
        frames.append(data)
        print(
            f"[{i}/{len(symbols)}] {symbol}: {len(data)} phiên "
            f"({data['time'].min():%Y-%m-%d} → {data['time'].max():%Y-%m-%d})"
        )
        time.sleep(pause)

    if not frames:
        raise RuntimeError("Không tải được mã nào.")
    if failed:
        print(f"Các mã lỗi: {', '.join(failed)}")

    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv(RAW_DIR / "prices_all.csv", index=False, encoding="utf-8-sig")
    return combined


def save_universe(path: PathLike = RAW_DIR / "universe.csv") -> pd.DataFrame:
    """Lưu danh sách mã cùng sàn và ngành."""

    universe = pd.DataFrame(
        [(s, ex, sector) for s, (ex, sector) in UNIVERSE.items()],
        columns=["symbol", "exchange", "sector"],
    )
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    universe.to_csv(path, index=False, encoding="utf-8-sig")
    return universe


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--start", default=DEFAULT_START.strftime("%Y-%m-%d"))
    parser.add_argument("--end", default=DEFAULT_END.strftime("%Y-%m-%d"))
    parser.add_argument("--pause", type=float, default=3.0,
                        help="Số giây nghỉ giữa các request (tránh giới hạn tần suất).")
    args = parser.parse_args()

    print(f"Tải {len(UNIVERSE)} mã + {BENCHMARK_SYMBOL}, {args.start} → {args.end}")
    save_universe()
    download_universe(args.start, args.end, pause=args.pause)

    benchmark = download_symbol(BENCHMARK_SYMBOL, args.start, args.end, pause=args.pause)
    benchmark.to_csv(RAW_DIR / "vnindex.csv", index=False, encoding="utf-8-sig")
    print(f"{BENCHMARK_SYMBOL}: {len(benchmark)} phiên")


if __name__ == "__main__":
    main()
