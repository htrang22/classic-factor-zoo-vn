"""Gộp các file Excel báo cáo tài chính quý xuất từ SSI iBoard (FiinTrade) thành CSV.

Mỗi file có dạng ``SSI_<MÃ>_Financial_statement_<Loại>_<ddmmyyyy>[ (n)].xlsx``,
chứa tối đa 15 quý. Nhiều file cùng mã/loại (các giai đoạn khác nhau) được ghép
lại; quý trùng giữa các file thì giữ bản có ngày trích xuất mới nhất.

Đầu ra (data/processed):
    fundamentals_long.csv      symbol, statement, line_no, item, period, quarter_end, value
    fundamentals_coverage.csv  số quý có dữ liệu theo mã × loại báo cáo

Chạy:
    python3 parse_fundamentals.py
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Union

import pandas as pd


PathLike = Union[str, Path]

PROJECT_DIR = Path(__file__).resolve().parent
REPORT_DIR = PROJECT_DIR / "data" / "raw" / "quarter-report"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

FILE_PATTERN = re.compile(
    r"^SSI_(?P<symbol>[A-Z0-9]+)_Financial_statement_(?P<statement>.+?)_\d{8}"
    r"(?: \(\d+\))?\.xlsx$",
    re.IGNORECASE,
)
STATEMENTS = {
    "balance_sheet": "balance_sheet",
    "income_statement": "income_statement",
    "cash_flow": "cash_flow",
}
PERIOD_PATTERN = re.compile(r"^Q([1-4]) (\d{4})$")


def parse_file(path: PathLike) -> pd.DataFrame:
    """Đọc một file Excel SSI và trả về bảng dạng long (một dòng = chỉ tiêu × quý)."""

    path = Path(path)
    match = FILE_PATTERN.match(path.name)
    if not match:
        raise ValueError(f"Tên file không đúng định dạng SSI: {path.name}")
    statement = STATEMENTS.get(match["statement"].lower())
    if statement is None:
        raise ValueError(f"Không nhận ra loại báo cáo trong {path.name}")

    raw = pd.read_excel(path, header=None)
    labels = raw[0].astype(str).str.strip()
    # Dòng tiêu đề là dòng đầu tiên có ô thứ 2 dạng "Qn yyyy"; ô đầu thường là
    # "CHỈ TIÊU" nhưng có file để trống.
    is_header = raw[1].astype(str).str.strip().str.match(PERIOD_PATTERN)
    if not is_header.any():
        raise ValueError(f"Không tìm thấy dòng tiêu đề kỳ (Qn yyyy) trong {path.name}")
    header = is_header.idxmax()

    extract_rows = raw.index[labels == "Date Of Extract"]
    extracted_at = (
        pd.Timestamp(raw.iat[extract_rows[0], 1]) if len(extract_rows) else pd.NaT
    )

    periods = raw.iloc[header, 1:].dropna()
    body = raw.iloc[header + 1 :, [0, *periods.index]]
    # Cắt phần chân trang ("Dữ liệu được cung cấp bởi FiinTrade", link). Không cắt
    # theo dòng trống vì có chỉ tiêu trống toàn bộ (vd EBIT), có dòng không tên.
    footer = body[0].astype(str).str.contains("FiinTrade|^https?://", regex=True)
    if footer.any():
        body = body.loc[: footer.idxmax() - 1]
    body = body[~(body[0].isna() & body.iloc[:, 1:].isna().all(axis=1))]
    body.columns = ["item", *periods.astype(str).str.strip()]

    # Giữ thứ tự dòng: một số chỉ tiêu trùng tên (ròng / gộp) nên line_no là khóa.
    body = body.reset_index(drop=True)
    body.insert(0, "line_no", body.index + 1)
    body["item"] = body["item"].astype("string").str.strip()

    long = body.melt(id_vars=["line_no", "item"], var_name="period", value_name="value")
    parts = long["period"].str.extract(PERIOD_PATTERN)
    if parts.isna().any().any():
        bad = long.loc[parts[0].isna(), "period"].unique()
        raise ValueError(f"Kỳ không phải quý trong {path.name}: {list(bad)}")
    long["period"] = parts[1] + "Q" + parts[0]
    long["quarter_end"] = pd.PeriodIndex(long["period"], freq="Q").end_time.normalize()
    long["value"] = pd.to_numeric(long["value"], errors="coerce")
    long.insert(0, "statement", statement)
    long.insert(0, "symbol", match["symbol"].upper())
    long["source_file"] = path.name
    long["extracted_at"] = extracted_at
    return long


def check_item_lists(frames: list[pd.DataFrame]) -> None:
    """Báo lỗi nếu các file cùng mã/loại báo cáo có danh sách chỉ tiêu khác nhau."""

    seen: dict[tuple[str, str], tuple[str, list]] = {}
    for frame in frames:
        key = (frame["symbol"].iat[0], frame["statement"].iat[0])
        items = frame.drop_duplicates("line_no")["item"].fillna("").tolist()
        name = frame["source_file"].iat[0]
        if key in seen and seen[key][1] != items:
            raise ValueError(
                f"Danh sách chỉ tiêu khác nhau giữa {seen[key][0]} và {name}"
            )
        seen.setdefault(key, (name, items))


def parse_all(report_dir: PathLike = REPORT_DIR) -> pd.DataFrame:
    """Đọc toàn bộ file trong ``report_dir`` và ghép thành một bảng long."""

    files = sorted(Path(report_dir).glob("*.xlsx"))
    if not files:
        raise RuntimeError(f"Không có file .xlsx trong {report_dir}")

    frames = []
    for path in files:
        if path.name.startswith("~$"):  # file tạm khi đang mở bằng Excel
            continue
        frames.append(parse_file(path))
    check_item_lists(frames)

    data = pd.concat(frames, ignore_index=True)
    data = (
        data.sort_values("extracted_at")
        .drop_duplicates(["symbol", "statement", "line_no", "period"], keep="last")
        .sort_values(["symbol", "statement", "period", "line_no"])
        .reset_index(drop=True)
    )
    return data


def coverage(data: pd.DataFrame) -> pd.DataFrame:
    """Tóm tắt số quý, quý đầu/cuối và các quý bị thiếu theo mã × loại báo cáo."""

    rows = []
    for (symbol, statement), group in data.groupby(["symbol", "statement"]):
        periods = pd.PeriodIndex(group["period"].unique(), freq="Q").sort_values()
        expected = pd.period_range(periods[0], periods[-1], freq="Q")
        missing = expected.difference(periods)
        rows.append(
            {
                "symbol": symbol,
                "statement": statement,
                "first_period": str(periods[0]),
                "last_period": str(periods[-1]),
                "n_quarters": len(periods),
                "missing_quarters": ",".join(map(str, missing)),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    data = parse_all()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output = data.drop(columns=["source_file", "extracted_at"])
    output.to_csv(PROCESSED_DIR / "fundamentals_long.csv", index=False, encoding="utf-8-sig")

    summary = coverage(data)
    summary.to_csv(PROCESSED_DIR / "fundamentals_coverage.csv", index=False, encoding="utf-8-sig")
    print(f"{len(output)} dòng, {data['symbol'].nunique()} mã")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
