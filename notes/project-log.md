# Nhật ký dự án: Factor Zoo cổ điển trên thị trường Việt Nam

> Cập nhật lần cuối: 05/11/2026. Branch: `expand-universe-50`.

---

## 1. Dữ liệu

### 1.1 Danh sách mã (50 mã: 42 HOSE + 8 HNX)

| Mã | Sàn | Ngành | BCTC quý |
|---|---|---|---|
| VCB | HOSE | Ngân hàng | ✅ |
| BID | HOSE | Ngân hàng | ✅ |
| CTG | HOSE | Ngân hàng | ✅ |
| TCB | HOSE | Ngân hàng | ✅ |
| MBB | HOSE | Ngân hàng | ✅ |
| ACB | HOSE | Ngân hàng | ✅ |
| VPB | HOSE | Ngân hàng | ✅ |
| VIC | HOSE | Bất động sản | ✅ |
| VHM | HOSE | Bất động sản | ✅ |
| KDH | HOSE | Bất động sản | ✅ |
| DXG | HOSE | Bất động sản | ✅ |
| VNM | HOSE | Tiêu dùng | ✅ |
| MSN | HOSE | Tiêu dùng | ✅ |
| SAB | HOSE | Tiêu dùng | ✅ |
| MWG | HOSE | Bán lẻ | ✅ |
| PNJ | HOSE | Bán lẻ | ✅ |
| HPG | HOSE | Thép | ✅ |
| HSG | HOSE | Thép | ✅ |
| DGC | HOSE | Hóa chất | ✅ |
| GAS | HOSE | Năng lượng | ✅ |
| PLX | HOSE | Năng lượng | ✅ |
| REE | HOSE | Tiện ích | ✅ |
| GMD | HOSE | Cảng biển | ✅ |
| FPT | HOSE | Công nghệ | ✅ |
| SSI | HOSE | Chứng khoán | ✅ |
| SHS | HNX | Chứng khoán | ✅ |
| MBS | HNX | Chứng khoán | ✅ |
| PVS | HNX | Năng lượng | ✅ |
| IDC | HNX | Bất động sản KCN | ✅ |
| CEO | HNX | Bất động sản | ✅ |
| STB | HOSE | Ngân hàng | ✅ |
| HDB | HOSE | Ngân hàng | ✅ |
| TPB | HOSE | Ngân hàng | ✅ |
| EIB | HOSE | Ngân hàng | ✅ |
| VND | HOSE | Chứng khoán | ✅ |
| HCM | HOSE | Chứng khoán | ✅ |
| NLG | HOSE | Bất động sản | ✅ |
| KBC | HOSE | Bất động sản KCN | ✅ |
| VJC | HOSE | Hàng không | ✅ |
| DPM | HOSE | Phân bón | ✅ |
| DHG | HOSE | Dược phẩm | ✅ |
| VHC | HOSE | Thủy sản | ✅ |
| CTD | HOSE | Xây dựng | ✅ |
| PC1 | HOSE | Xây lắp điện | ✅ |
| PVD | HOSE | Dịch vụ dầu khí | ✅ |
| BMP | HOSE | Nhựa | ✅ |
| DRC | HOSE | Cao su | ✅ |
| VCS | HNX | Vật liệu xây dựng | ✅ |
| TNG | HNX | Dệt may | ✅ |
| PLC | HNX | Hóa chất | ✅ |

Benchmark: **VN-Index** (`VNINDEX`).

Tiêu chí chọn: trải đều vốn hóa lớn/vừa/nhỏ và nhiều ngành để các factor
(nhất là Size, Value) có độ phân tán. Danh sách chọn theo thời điểm hiện tại
→ **còn survivorship bias**, chưa xử lý.

Mở rộng 30 → 50 mã (05/11/2026): thêm 20 mã (từ STB đến PLC trong bảng trên),
giữ tỷ lệ của rổ cũ (~85% HOSE, ~1/3 là ngân hàng + chứng khoán), thêm các ngành
chưa có (hàng không, phân bón, dược, thủy sản, xây dựng, nhựa, cao su, dệt may,
vật liệu xây dựng) và thêm mã vốn hóa nhỏ (DRC, TNG, PLC, CTD). Không chọn mã
bảo hiểm vì BCTC bảo hiểm là mẫu thứ tư, `compute_factors.py` chưa ánh xạ.

### 1.2 Nguồn dữ liệu

| Loại | Nguồn | Script |
|---|---|---|
| Giá OHLCV ngày (50 mã + VN-Index) | vnstock, nguồn KBS (bản cộng đồng) | `download_stocks.py` |
| Danh sách mã, sàn, ngành | Tự định nghĩa trong `download_stocks.py` | `download_stocks.py` |
| BCTC quý (CĐKT, KQKD, LCTT) | SSI iBoard, dữ liệu FiinTrade (file Excel, tải tự động bằng Playwright) | `download_fundamentals.py`, `parse_fundamentals.py` |
| Panel factor tháng | Tính từ hai nguồn trên | `compute_factors.py` |

### 1.3 Mô tả chung

**Giá (vnstock / KBS)**
- Giai đoạn: 06/11/2018 → 04/11/2026. Mỗi mã khoảng 1.990 phiên; IDC 1.973,
  DGC 1.989, ACB 1.990, VND 1.990, PLC 1.980 (thiếu vài phiên, có thể do
  tạm ngừng giao dịch).
- Cột: `time, open, high, low, close, volume`. Giá tính bằng **nghìn đồng**.
- Giá **đã điều chỉnh** cổ tức/chia tách (vd FPT năm 2018 ≈ 12). Đây là suy
  luận từ số liệu, chưa đối chiếu với nguồn khác.
- Bản cộng đồng giới hạn dữ liệu 1D tối đa **8 năm**.

**BCTC quý (SSI / FiinTrade)**
- Đầy đủ **50/50 mã**
- Mỗi mã có 3 loại báo cáo × 2 file (mỗi lần xuất tối đa 15 quý). Ghép lại
  được **30 quý liên tục từ 2019Q2 đến 2026Q3**, không thiếu quý.
- Số liệu tính bằng **đồng**, theo **từng quý** (không cộng dồn từ đầu năm).
- Không có **ngày công bố** → point-in-time dùng độ trễ giả định 45 ngày.
- Có 3 mẫu BCTC, số chỉ tiêu (CĐKT/KQKD/LCTT) khác nhau:
  - **Ngân hàng** (11 mã: VCB, BID, CTG, TCB, MBB, ACB, VPB, STB, HDB, TPB, EIB): 48/27/52.
  - **Công ty chứng khoán** (5 mã: SSI, SHS, MBS, VND, HCM): 161/85/98.
  - **Doanh nghiệp thường** (34 mã còn lại): 120 chỉ tiêu ở bảng cân đối.
- Một số chỉ tiêu trùng tên (ròng/gộp), nên phân biệt bằng `line_no`.
- Cột EPS bằng 0 ở mọi quý (lỗi nguồn)
- Tải tự động: `download_fundamentals.py` điều khiển widget "Báo cáo tài chính"
  trên SSI iBoard (Quý, 15 kỳ, Năm gần nhất 2026 và 2022). Kiểm tra với DGC:
  khớp 100% với file tải tay.
- Môi trường: numpy < 2.3.2 hỏng trên Python 3.14 với mảng > 256 KB (lỗi
  `IndexError` khi sort); đã nâng lên numpy 2.3.5. Panel 30 mã cũ tính lại
  trùng khớp hoàn toàn, nên kết quả trước đó không bị ảnh hưởng.

**Panel factor (`data/final/factor_panel.csv`, chỉ lưu ở máy)**
- 4.800 dòng = 50 mã × 96 tháng, từ 11/2018 đến 10/2026 (bỏ tháng 11/2026
  vì chưa kết thúc).
- 32 cột: 11 cột định danh/lợi suất + 21 chỉ số factor.
---

## 2. Các factor đã tính

### 2.1 Quy ước chung

- **Tần suất:** tháng. Mỗi dòng là một mã tại một ngày cuối tháng `t`.
  `P_t` là giá đóng cửa (đã điều chỉnh) của phiên cuối cùng trong tháng.
- **Lợi suất ngày:** `r_d = P_d / P_{d-1} − 1`, lợi suất thị trường `r_m,d`
  lấy từ VN-Index.
- **Point-in-time:** số liệu quý `q` chỉ được dùng từ
  `ngày kết thúc quý + 45 ngày`. Tại mỗi cuối tháng, lấy quý mới nhất đã qua
  mốc này (cột `fiscal_quarter` ghi quý đang dùng).
- **TTM (12 tháng gần nhất):** tổng 4 quý liên tiếp gần nhất của chỉ tiêu dòng
  (doanh thu, lợi nhuận, CFO, lãi gộp).
- **Số cổ phiếu:** `shares = Vốn điều lệ / 10.000` (mệnh giá 10.000 đồng).
- **Vốn chủ sở hữu sổ sách:** `book_equity = Vốn chủ sở hữu − Lợi ích cổ đông thiểu số`
  (mẫu công ty chứng khoán không trừ, vì Vốn chủ sở hữu đã bằng Tổng tài sản − Nợ phải trả).

Chỉ tiêu BCTC được lấy theo tên dòng:

| Biến | Mẫu ngân hàng (`bank`) | Mẫu công ty chứng khoán (`broker`) | Mẫu doanh nghiệp (`corporate`) |
|---|---|---|---|
| Tổng tài sản `TA` | TỔNG TÀI SẢN | TỔNG CỘNG TÀI SẢN | TỔNG TÀI SẢN |
| Tổng nợ `TL` | Tổng nợ phải trả | NỢ PHẢI TRẢ | NỢ PHẢI TRẢ |
| Vốn chủ sở hữu | Vốn chủ sở hữu | VỐN CHỦ SỞ HỮU | VỐN CHỦ SỞ HỮU |
| Lợi ích CĐ thiểu số | Lợi ích của cổ đông thiểu số | – | Lợi ích cổ đông không kiểm soát |
| Vốn điều lệ | Vốn điều lệ | Vốn góp | Vốn góp |
| Doanh thu `Rev` | Tổng thu nhập hoạt động | Doanh thu thuần về hoạt động kinh doanh | Doanh số thuần |
| Lãi gộp `GP` | – | – | Lãi gộp |
| LNST cổ đông mẹ `NI` | Cổ đông của Công ty mẹ | Lợi nhuận sau thuế phân bổ cho chủ sở hữu | Lợi nhuận của Cổ đông của Công ty mẹ |
| CFO | Lưu chuyển tiền thuần từ các hoạt động sản xuất kinh doanh | Lưu chuyển thuần từ hoạt động kinh doanh chứng khoán | Lưu chuyển tiền thuần từ các hoạt động sản xuất kinh doanh |

Mẫu BCTC được nhận diện tự động: có "Tổng thu nhập hoạt động" → ngân hàng; có
"Doanh thu thuần về hoạt động kinh doanh" → công ty chứng khoán; còn lại →
doanh nghiệp thường.

### 2.2 Cột định danh và lợi suất

| Tên biến | Ý nghĩa / công thức |
|---|---|
| `date` | Ngày cuối tháng |
| `symbol`, `exchange`, `sector` | Mã, sàn, ngành |
| `template` | Mẫu BCTC: `bank`, `broker` hoặc `corporate` (trống khi chưa có BCTC đã công bố) |
| `is_financial` | `True` nếu là ngân hàng hoặc công ty chứng khoán |
| `fiscal_quarter` | Quý BCTC đang được dùng tại `date` (theo point-in-time) |
| `n_trading_days` | Số phiên giao dịch trong tháng (dùng để lọc mã bị đình chỉ) |
| `ret_1m` | `P_t / P_{t−1} − 1` |
| `ret_fwd_1m` | Lợi suất tháng sau `ret_1m(t+1)`: **biến mục tiêu** |
| `mkt_ret_1m` | `∏(1 + r_m,d) − 1` trong tháng, theo VN-Index |

### 2.3 Factor

| Nhóm | Tên biến | Công thức | Ghi chú |
|---|---|---|---|
| **Size** | `mcap` | `P_t × 1.000 × shares_mới_nhất` | Đồng. Xấp xỉ: giá điều chỉnh × số cổ phiếu mới nhất |
| | `log_mcap` | `ln(mcap)` | Fama-French SMB |
| **Value** | `bm` | `book_equity / mcap` | Book-to-market, FF HML |
| | `ep` | `NI_TTM / mcap` | Earnings yield (nghịch đảo P/E) |
| | `sp` | `Rev_TTM / mcap` | Sales-to-price |
| | `cfp` | `CFO_TTM / mcap` | Chỉ doanh nghiệp thường (`is_financial` = trống) |
| **Momentum** | `mom_12_1` | `P_{t−1} / P_{t−12} − 1` | Carhart; bỏ tháng gần nhất |
| | `mom_6_1` | `P_{t−1} / P_{t−6} − 1` | Momentum trung hạn |
| | `ret_1m` | `P_t / P_{t−1} − 1` | Dùng làm factor short-term reversal |
| **Low-risk** | `beta_12m` | `Cov(r_i, r_m) / Var(r_m)`, 252 phiên (≥ 120) | Betting-Against-Beta |
| | `vol_3m` | `std(r_i) × √252`, 63 phiên (≥ 40) | Biến động tổng |
| | `ivol_3m` | `√[(Var(r_i) − Cov(r_i,r_m)² / Var(r_m)) × 252]`, 63 phiên | Biến động riêng (phần dư CAPM) |
| | `max_ret_1m` | `max(r_d)` trong tháng | Hiệu ứng "xổ số" (MAX) |
| **Thanh khoản** | `amihud_3m` | `mean(|r_d| / (P_d × 1.000 × Volume_d)) × 10⁹`, 63 phiên | Amihud illiquidity |
| | `turnover_3m` | `mean(Volume_d, 63 phiên) / shares_mới_nhất` | Vòng quay cổ phiếu |
| **Quality / Profitability** | `roe` | `NI_TTM / ((BE_q + BE_{q−4}) / 2)` | Cần 8 quý → có từ 2020Q1 |
| | `roa` | `NI_TTM / TA_q` | |
| | `gross_profitability` | `GP_TTM / TA_q` | Novy-Marx; chỉ doanh nghiệp thường |
| | `leverage` | `TL_q / TA_q` | QMJ – safety |
| | `accruals` | `(NI_TTM − CFO_TTM) / TA_q` | Sloan; chỉ doanh nghiệp thường (`is_financial` = trống) |
| | `earnings_growth` | `(NI_TTM − NI_TTM,q−4) / |NI_TTM,q−4|` | QMJ – growth |
| **Investment** | `asset_growth` | `TA_q / TA_{q−4} − 1` | FF5 CMA |

Tổng cộng **21 chỉ số factor**.

---

## 3. Xóa và tạo lại repo (11/2026)

Trong khoảng 04–05/11/2026, repo public có chứa `data/final/factor_panel.csv`.
File này không chứa giá gốc, nhưng từ `ret_1m`, `mcap` và các tỷ lệ như `bm`,
`ep`, `sp`, `cfp` có thể dựng lại đường giá và số liệu BCTC. Dữ liệu vnstock và
FiinTrade không có quyền phân phối lại, nên repo đã được chuyển sang private,
file bị xóa khỏi mọi commit bằng `git filter-repo`, rồi repo cũ bị xóa và tạo
lại cùng tên. Phải xóa repo vì GitHub vẫn giữ commit cũ trong ref ẩn của các PR
dù lịch sử đã được viết lại.

Vì vậy, hash commit đã đổi và các trang PR #1–#5, issue #4 cũ không còn. Số PR
trong tiêu đề commit là số ở repo cũ, nội dung được lưu ở
`notes/github-archive.md`. Những bản đã được sao chép khi repo còn public thì
không thu hồi được. Từ nay `data/final/` chỉ lưu ở máy, quy định chi tiết nằm
trong `AGENTS.md`.
