# Lưu trữ PR và issue của repo cũ

Bản sao nguyên văn mô tả PR #1, #2, #3, #5 và issue #4 của repo cũ, lưu lại trước khi xóa repo (xem mục 3 của `project-log.md`). Số PR và số issue là số ở repo cũ.

## PR #1: Data collection pipeline and monthly factor panel

Trạng thái: MERGED. Branch: `data-collection` → `main`. Tạo: 2026-11-04T09:58:35Z. Merge: 2026-11-04T15:10:03Z.

## Tóm tắt
Giai đoạn thu thập dữ liệu và tính factor cho Factor Zoo VN.

- `download_stocks.py`: tải OHLCV ngày (giá đã điều chỉnh) của 30 mã HOSE/HNX + VN-Index qua vnstock (nguồn KBS, tối đa 8 năm ở bản cộng đồng).
- `parse_fundamentals.py`: gộp file Excel BCTC quý xuất từ SSI iBoard (FiinTrade) thành bảng long + báo cáo độ phủ theo mã × loại báo cáo.
- `compute_factors.py`: panel tháng (mã × cuối tháng) → `data/final/factor_panel.csv`.
  - Size, Value (B/M, E/P, S/P, CF/P), Momentum (12-1, 6-1), Low-risk (beta, vol, ivol, MAX), thanh khoản (Amihud, turnover), Quality/Investment (ROE, ROA, GP/A, leverage, accruals, tăng trưởng LN, tăng trưởng tài sản).
  - Point-in-time: BCTC quý chỉ dùng từ quarter_end + 45 ngày.
  - Biến mục tiêu `ret_fwd_1m`; bỏ tháng chưa kết thúc.

## Dữ liệu
`data/raw/` và `data/processed/` được gitignore — không có quyền phân phối dữ liệu gốc. Repo chỉ chứa code và `data/final/` (chỉ số đã tính).

## Còn thiếu
- BCTC mới có 5/30 mã (VCB, BID, CTG, TCB, VIC).
- Vốn hóa xấp xỉ bằng giá điều chỉnh × số cổ phiếu mới nhất.
- Chưa xử lý survivorship bias (rổ chọn theo hiện tại).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## PR #2: Map brokerage statement template; refresh factor panel for 30 tickers

Trạng thái: MERGED. Branch: `fix-broker-mapping` → `main`. Tạo: 2026-11-04T15:26:33Z. Merge: 2026-11-04T15:28:57Z.

## Tóm tắt
Bổ sung mapping chỉ tiêu BCTC cho mẫu công ty chứng khoán và cập nhật panel factor khi BCTC đã có đủ 30 mã.

- Thêm mẫu `broker` trong `ITEM_MAP` cho SSI, SHS, MBS (mẫu CTCK của FiinTrade): tổng tài sản, nợ phải trả, vốn chủ, vốn góp, doanh thu thuần hoạt động kinh doanh, LNST phân bổ cho chủ sở hữu, CFO.
- Nhận diện mẫu BCTC qua `TEMPLATE_MARKERS` (bank / broker / corporate).
- Cột `is_bank` được thay bằng `template` và `is_financial`. `cfp` và `accruals` để trống cho cả ngân hàng và CTCK, vì CFO của nhóm này gồm biến động cho vay/margin/tự doanh.
- Cập nhật `data/final/factor_panel.csv`: 7 ngân hàng, 3 CTCK, 20 doanh nghiệp thường.

## DGC
Đã bổ sung 2 file Kết quả kinh doanh của DGC. Từ 2021, cả 30 mã đều có đủ factor từ BCTC.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## PR #3: Update README and project log to match current pipeline

Trạng thái: MERGED. Branch: `docs-project-log-template` → `main`. Tạo: 2026-11-04T15:35:28Z. Merge: 2026-11-04T15:44:05Z.

## Tóm tắt
Cập nhật tài liệu theo hiện trạng pipeline.

### `notes/project-log.md`

- Mô tả 3 mẫu BCTC: ngân hàng (7 mã), công ty chứng khoán (SSI, SHS, MBS), doanh nghiệp thường (20 mã).
- Bảng chỉ tiêu BCTC: thêm cột mẫu công ty chứng khoán và cách nhận diện mẫu tự động.
- Thay `is_bank` bằng `template` và `is_financial`; panel giờ có 32 cột.
- Ghi chú `cfp` và `accruals`: để trống cho mọi mã thuộc nhóm tài chính.

### `README.md`
- **Data:** nguồn thực tế (vnstock/KBS cho giá, SSI iBoard/FiinTrade cho BCTC), giai đoạn, 3 mẫu BCTC, cách tính vốn hóa, point-in-time bằng độ trễ 45 ngày, quy định chỉ lưu dữ liệu gốc ở máy, cấu trúc thư mục `data/`.
- **Các bước:** bảng trạng thái từng bước và script tương ứng, danh sách 21 factor, gợi ý chia 3–5 nhóm cho rổ 30 mã, lệnh chạy lại pipeline.

### `data/processed/fundamentals_coverage.csv`
- Đưa báo cáo độ phủ BCTC lên repo để minh chứng quá trình xử lý: 30 mã × 3 loại báo cáo, mỗi dòng ghi quý đầu, quý cuối, số quý và các quý bị thiếu. File không chứa số liệu tài chính gốc.
- `.gitignore`: đổi `data/processed/` thành `data/processed/*` kèm ngoại lệ cho file này; `fundamentals_long.csv` vẫn chỉ ở máy.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Review của htrang22 (2026-11-04T15:43:45Z): hêh

## PR #5: Expand universe to 50 tickers and automate SSI statement downloads

Trạng thái: OPEN. Branch: `expand-universe-50` → `main`. Tạo: 2026-11-04T18:05:16Z. Merge: chưa.

## Summary
- **New `download_fundamentals.py`**: drives the SSI iBoard "Báo cáo tài chính" (FiinTrade) widget with Playwright (quarterly, 15 periods, latest year 2026 and 2022) and saves the Excel exports with the naming `parse_fundamentals.py` already reads. Login is manual; the session is kept in `~/.cache/ssi-iboard-profile`, outside the repo.
- **Universe 30 → 50 tickers** (42 HOSE + 8 HNX; 11 banks, 5 brokers, 34 corporates). The 20 new tickers add sectors the universe lacked (airline, fertiliser, pharma, seafood, construction, plastics, rubber, textiles, building materials) and smaller caps. No insurers, because their statement template is not mapped yet.
- **Refreshed data**: `factor_panel.csv` now has 4,800 rows (50 × 96 months). Every ticker has 30 quarters (2019Q2–2026Q3) for all three statements.
- **Setup docs and fail-fast checks**: README explains how to add the widget once per account. The script stops after about 30 s with those steps if the widget is missing, and checks the tabs, dropdowns and download button before looping over tickers.
- **`numpy>=2.3.2`**: older numpy breaks on arrays larger than 256 KB under Python 3.14 (`IndexError` while sorting).

## Verification
- DGC auto-download vs manual export: 5,640/5,640 values identical.
- Rows for the original 30 tickers in `factor_panel.csv` are unchanged; the diff only adds rows.
- Missing-widget path tested on a real account by pointing the script at a non-existent widget: it stops and prints the setup steps.

Raw data (`data/raw/`, `fundamentals_long.csv`) remains local only, as before.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Issue #4: Tái lập

Trạng thái: OPEN. Tạo: 2026-11-04T15:48:24Z.

Dự án này có lẽ chỉ tái lập được khi không cần phải tạo tài khoản ở broker để tải từng BCTC quý bằng tay. 😿

Bình luận của htrang22 (2026-11-04T17:26:25Z): dù sao thì, thêm playwright để giúp tiết kiệm thời gian và tăng độ chính xác khi tải file. vẫn tái lập được nếu đã có sẵn dữ liệu tương ứng, hoặc ít nhất có tài khoản trên broker.
