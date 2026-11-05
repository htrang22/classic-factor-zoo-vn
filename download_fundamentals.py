"""Tự động tải BCTC quý (FiinTrade) từ widget "Báo cáo tài chính" trên SSI iBoard.

Script lặp lại các bước tải tay: mở Giao diện của tôi, gõ mã, chọn từng tab
(Cân đối kế toán, Kết quả kinh doanh, Lưu chuyển tiền tệ), chọn Xem theo = Quý,
Số kỳ = 15, Năm gần nhất = mỗi năm trong ``--years``, rồi bấm Tải xuống.

File được lưu vào ``data/raw/quarter-report/`` với tên SSI gốc và đuôi
`` (<năm>)``, ví dụ ``SSI_ACB_Financial_statement_Cash_Flow_05112026 (2022).xlsx``,
để ``parse_fundamentals.py`` đọc được ngay.

Yêu cầu:
    pip install playwright        # dùng Google Chrome có sẵn trên máy
    Tài khoản SSI iBoard, giao diện tiếng Việt, và widget "Báo cáo tài chính"
    đã được thêm vào Giao diện của tôi (làm một lần, xem SETUP_HINT hoặc README).

Lần chạy đầu, cửa sổ Chrome mở ra trang đăng nhập: tự đăng nhập bằng tay, script
chờ đến khi widget hiện ra. Phiên đăng nhập được lưu ở ``~/.cache/ssi-iboard-profile``
(ngoài repo) nên các lần sau không cần đăng nhập lại.

Chạy:
    python3 download_fundamentals.py                       # toàn bộ mã trong universe.csv
    python3 download_fundamentals.py --symbols ACB DGC     # vài mã
    python3 download_fundamentals.py --years 2026 2022 --force
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

import pandas as pd
from playwright.sync_api import BrowserContext, FrameLocator, Page, sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeout


PROJECT_DIR = Path(__file__).resolve().parent
UNIVERSE_FILE = PROJECT_DIR / "data" / "raw" / "universe.csv"
REPORT_DIR = PROJECT_DIR / "data" / "raw" / "quarter-report"
PROFILE_DIR = Path.home() / ".cache" / "ssi-iboard-profile"

DASHBOARD_URL = "https://iboard.ssi.com.vn/dynamic-dashboard"
WIDGET_IFRAME = 'iframe[src*="fiin-app.ssi.com.vn/financial-statement"]'
TABS = {
    "Cân Đối Kế Toán": "Balance_Sheet",  # phần tên loại báo cáo trong tên file SSI
    "Kết Quả Kinh Doanh": "Income_Statement",
    "Lưu Chuyển Tiền Tệ": "Cash_Flow",
}
DEFAULT_YEARS = [pd.Timestamp.today().year, pd.Timestamp.today().year - 4]
N_PERIODS = "15"
PAUSE = 2.0  # giây nghỉ sau mỗi thao tác tải dữ liệu, tránh dồn yêu cầu lên server
LOGIN_TIMEOUT = 10 * 60  # giây chờ người dùng đăng nhập
WIDGET_TIMEOUT = 30  # giây chờ widget hiện ra sau khi đã đăng nhập
SETUP_HINT = """\
Không thấy widget "Báo cáo tài chính" trong Giao diện của tôi. Cài đặt một lần:
  1. Click tab "Giao diện của tôi"
  2. Click nút "+" (Thêm bảng)
  3. Chọn "Thêm bảng" trong cửa sổ vừa mở
  4. Click "Thêm tính năng"
  5. Tìm mục "Theo dõi"
  6. Chọn "Báo cáo tài chính" và kéo vào màn hình
Để bảng chứa widget là bảng hiện ra đầu tiên khi mở Giao diện của tôi, và để
giao diện iBoard bằng tiếng Việt. Sau đó chạy lại script."""


class SetupError(RuntimeError):
    """Board iBoard chưa được cài đặt đúng để script chạy."""
PERIOD_PATTERN = re.compile(r"^Q[1-4] (\d{4})$")


def load_symbols(path: Path = UNIVERSE_FILE) -> list[str]:
    return pd.read_csv(path, encoding="utf-8-sig")["symbol"].str.strip().tolist()


def open_widget(page: Page) -> FrameLocator:
    """Mở Giao diện của tôi, chờ đăng nhập (nếu cần) đến khi widget BCTC hiện ra."""

    page.goto(DASHBOARD_URL)
    iframe = page.locator(WIDGET_IFRAME)
    deadline = time.monotonic() + LOGIN_TIMEOUT
    on_dashboard_since = None
    asked_login = False
    while iframe.count() == 0:
        now = time.monotonic()
        if "/auth/login" in page.url:
            on_dashboard_since = None
            if not asked_login:
                print("Chưa đăng nhập: hãy đăng nhập SSI iBoard trong cửa sổ Chrome vừa mở...")
                asked_login = True
            if now > deadline:
                raise SetupError("Hết thời gian chờ đăng nhập.")
        elif "/dynamic-dashboard" not in page.url:
            # Đăng nhập xong iBoard thường chuyển về trang chủ: mở lại Giao diện của tôi.
            on_dashboard_since = None
            page.goto(DASHBOARD_URL)
            continue
        elif on_dashboard_since is None:
            on_dashboard_since = now
        elif now - on_dashboard_since > WIDGET_TIMEOUT:
            raise SetupError(SETUP_HINT)
        page.wait_for_timeout(1000)

    widget = page.frame_locator(WIDGET_IFRAME)
    check_widget(widget)
    return widget


def check_widget(widget: FrameLocator) -> None:
    """Kiểm tra widget có đủ 3 tab, 3 dropdown và nút Tải xuống (giao diện tiếng Việt)."""

    timeout_ms = WIDGET_TIMEOUT * 1000
    try:
        widget.get_by_text("TẢI XUỐNG").wait_for(timeout=timeout_ms)
    except PlaywrightTimeout:
        raise SetupError(
            "Widget đã hiện nhưng không thấy nút \"TẢI XUỐNG\". "
            "Hãy chuyển iBoard sang giao diện tiếng Việt rồi chạy lại."
        ) from None
    missing = [tab for tab in TABS if widget.locator("a.m-tabs__link", has_text=tab).count() == 0]
    n_dropdowns = widget.locator("button.drop-cus").count()
    if missing or n_dropdowns < 3:
        raise SetupError(
            f"Widget không đúng cấu trúc mong đợi (thiếu tab: {missing or 'không'}, "
            f"số dropdown: {n_dropdowns}/3). Có thể SSI đã đổi giao diện; cần cập nhật selector."
        )


def choose(page: Page, widget: FrameLocator, index: int, value: str) -> None:
    """Chọn ``value`` trong dropdown thứ ``index`` (0 Xem theo, 1 Năm gần nhất, 2 Số kỳ)."""

    button = widget.locator("button.drop-cus").nth(index)
    if button.get_attribute("title") == value:
        return
    button.click()
    menu = button.locator("xpath=..").locator(f'a.dropdown-item[title="{value}"]')
    menu.click()
    page.wait_for_timeout(PAUSE * 1000)
    actual = button.get_attribute("title")
    if actual != value:
        raise RuntimeError(f"Không chọn được '{value}' (đang là '{actual}')")


def select_symbol(page: Page, widget: FrameLocator, symbol: str) -> None:
    ticker = widget.locator("div.ticker[contenteditable]")
    ticker.click()
    page.keyboard.press("Meta+A" if sys.platform == "darwin" else "Control+A")
    page.keyboard.type(symbol, delay=80)
    suggestion = widget.locator(".drop-search a.dropdown-item").filter(
        has=widget.locator("span.w-20", has_text=re.compile(rf"^{symbol}$"))
    )
    suggestion.first.click()
    # Đổi mã làm iframe nạp lại: chờ widget mới hiện đúng mã.
    widget.locator("div.ticker", has_text=re.compile(rf"^{symbol}$")).wait_for()
    widget.get_by_text("TẢI XUỐNG").wait_for()
    page.wait_for_timeout(PAUSE * 1000)


def check_file(path: Path, year: int) -> str:
    """Kiểm tra file có cột kỳ dạng 'Qn yyyy' và kỳ mới nhất thuộc ``year``."""

    raw = pd.read_excel(path, header=None)
    cells = raw.iloc[:, 1:].astype(str).apply(lambda s: s.str.strip())
    is_header = cells.apply(lambda s: s.str.match(PERIOD_PATTERN)).any(axis=1)
    if not is_header.any():
        return "CẢNH BÁO: không thấy cột quý"
    periods = [p for p in cells.loc[is_header.idxmax()] if PERIOD_PATTERN.match(p)]
    years = [int(PERIOD_PATTERN.match(p)[1]) for p in periods]
    note = f"{len(periods)} quý, {periods[0]} → {periods[-1]}"
    if max(years) != year:
        note += f" — CẢNH BÁO: năm mới nhất {max(years)} ≠ {year}"
    return note


def download_symbol(
    page: Page,
    widget: FrameLocator,
    symbol: str,
    years: list[int],
    out_dir: Path,
    force: bool,
) -> int:
    select_symbol(page, widget, symbol)
    saved = 0
    for tab, statement in TABS.items():
        widget.locator("a.m-tabs__link", has_text=tab).click()
        page.wait_for_timeout(PAUSE * 1000)
        choose(page, widget, 0, "Quý")
        choose(page, widget, 2, N_PERIODS)
        for year in years:
            existing = list(out_dir.glob(f"SSI_{symbol}_Financial_*_{statement}_* ({year}).xlsx"))
            if existing and not force:
                print(f"  {symbol} {statement} {year}: đã có, bỏ qua ({existing[0].name})")
                continue
            choose(page, widget, 1, str(year))
            with page.expect_download() as info:
                widget.get_by_text("TẢI XUỐNG").click()
            download = info.value
            target = out_dir / f"{Path(download.suggested_filename).stem} ({year}).xlsx"
            download.save_as(target)
            print(f"  {symbol} {statement} {year}: {target.name} — {check_file(target, year)}")
            saved += 1
            page.wait_for_timeout(PAUSE * 1000)
    return saved


def launch(playwright) -> BrowserContext:
    return playwright.chromium.launch_persistent_context(
        str(PROFILE_DIR),
        channel="chrome",
        headless=False,
        accept_downloads=True,
        viewport={"width": 1400, "height": 900},
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--symbols", nargs="+", help="mặc định: toàn bộ mã trong universe.csv")
    parser.add_argument("--years", nargs="+", type=int, default=DEFAULT_YEARS,
                        help="các giá trị 'Năm gần nhất' cần tải (mặc định: %(default)s)")
    parser.add_argument("--out-dir", type=Path, default=REPORT_DIR)
    parser.add_argument("--force", action="store_true", help="tải lại cả file đã có")
    args = parser.parse_args()

    symbols = [s.upper() for s in (args.symbols or load_symbols())]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    failed: list[str] = []
    with sync_playwright() as playwright:
        context = launch(playwright)
        page = context.pages[0] if context.pages else context.new_page()
        try:
            widget = open_widget(page)
        except SetupError as exc:
            context.close()
            sys.exit(f"\n{exc}")
        for i, symbol in enumerate(symbols, 1):
            print(f"[{i}/{len(symbols)}] {symbol}")
            try:
                download_symbol(page, widget, symbol, args.years, args.out_dir, args.force)
            except SetupError:
                raise
            except Exception as exc:  # một mã lỗi thì ghi lại rồi chạy tiếp mã sau
                print(f"  LỖI {symbol}: {exc}")
                failed.append(symbol)
                widget = open_widget(page)
        context.close()
    if failed:
        print(f"Các mã lỗi, chạy lại với --symbols {' '.join(failed)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
