# Nhật ký dự án: Factor Zoo cổ điển trên thị trường Việt Nam

> Cập nhật lần cuối: 09/11/2026. Branch: `factor-evaluation`.

---

## 1. Dữ liệu

### 1.1 Danh sách mã (50 mã: 42 HOSE + 8 HNX)

| STT | Mã | Sàn | Ngành | BCTC quý |
|---|---|---|---|---|
| 1 | ACB | HOSE | Ngân hàng | ✅ |
| 2 | BID | HOSE | Ngân hàng | ✅ |
| 3 | CTG | HOSE | Ngân hàng | ✅ |
| 4 | EIB | HOSE | Ngân hàng | ✅ |
| 5 | HDB | HOSE | Ngân hàng | ✅ |
| 6 | MBB | HOSE | Ngân hàng | ✅ |
| 7 | STB | HOSE | Ngân hàng | ✅ |
| 8 | TCB | HOSE | Ngân hàng | ✅ |
| 9 | TPB | HOSE | Ngân hàng | ✅ |
| 10 | VCB | HOSE | Ngân hàng | ✅ |
| 11 | VPB | HOSE | Ngân hàng | ✅ |
| 12 | CEO | HNX | Bất động sản | ✅ |
| 13 | DXG | HOSE | Bất động sản | ✅ |
| 14 | KDH | HOSE | Bất động sản | ✅ |
| 15 | NLG | HOSE | Bất động sản | ✅ |
| 16 | VHM | HOSE | Bất động sản | ✅ |
| 17 | VIC | HOSE | Bất động sản | ✅ |
| 18 | HCM | HOSE | Chứng khoán | ✅ |
| 19 | MBS | HNX | Chứng khoán | ✅ |
| 20 | SHS | HNX | Chứng khoán | ✅ |
| 21 | SSI | HOSE | Chứng khoán | ✅ |
| 22 | VND | HOSE | Chứng khoán | ✅ |
| 23 | GAS | HOSE | Năng lượng | ✅ |
| 24 | PLX | HOSE | Năng lượng | ✅ |
| 25 | PVS | HNX | Năng lượng | ✅ |
| 26 | MSN | HOSE | Tiêu dùng | ✅ |
| 27 | SAB | HOSE | Tiêu dùng | ✅ |
| 28 | VNM | HOSE | Tiêu dùng | ✅ |
| 29 | MWG | HOSE | Bán lẻ | ✅ |
| 30 | PNJ | HOSE | Bán lẻ | ✅ |
| 31 | IDC | HNX | Bất động sản KCN | ✅ |
| 32 | KBC | HOSE | Bất động sản KCN | ✅ |
| 33 | DGC | HOSE | Hóa chất | ✅ |
| 34 | PLC | HNX | Hóa chất | ✅ |
| 35 | HPG | HOSE | Thép | ✅ |
| 36 | HSG | HOSE | Thép | ✅ |
| 37 | BMP | HOSE | Nhựa | ✅ |
| 38 | CTD | HOSE | Xây dựng | ✅ |
| 39 | DHG | HOSE | Dược phẩm | ✅ |
| 40 | DPM | HOSE | Phân bón | ✅ |
| 41 | DRC | HOSE | Cao su | ✅ |
| 42 | FPT | HOSE | Công nghệ | ✅ |
| 43 | GMD | HOSE | Cảng biển | ✅ |
| 44 | PC1 | HOSE | Xây lắp điện | ✅ |
| 45 | PVD | HOSE | Dịch vụ dầu khí | ✅ |
| 46 | REE | HOSE | Tiện ích | ✅ |
| 47 | TNG | HNX | Dệt may | ✅ |
| 48 | VCS | HNX | Vật liệu xây dựng | ✅ |
| 49 | VHC | HOSE | Thủy sản | ✅ |
| 50 | VJC | HOSE | Hàng không | ✅ |

Benchmark: **VN-Index** (`VNINDEX`).

Tiêu chí chọn: trải đều vốn hóa lớn/vừa/nhỏ và nhiều ngành để các factor
(nhất là Size, Value) có độ phân tán, với tỷ lệ ~85% HOSE và ~1/3 là ngân hàng +
chứng khoán. Không chọn mã bảo hiểm. Danh sách chọn theo thời điểm hiện tại
→ **còn survivorship bias**, mới đo độ nhạy (mục 3), chưa xử lý trong rổ.

Mở rộng 30 → 50 mã (05/11/2026): thêm 20 mã (STB, HDB, TPB, EIB, VND, HCM, NLG,
KBC, VJC, DPM, DHG, VHC, CTD, PC1, PVD, BMP, DRC, VCS, TNG, PLC), giữ tỷ lệ của
rổ cũ, thêm các ngành chưa có (hàng không, phân bón, dược, thủy sản, xây dựng,
nhựa, cao su, dệt may, vật liệu xây dựng) và thêm mã vốn hóa nhỏ (DRC, TNG, PLC,
CTD).

### 1.2 Nguồn dữ liệu

| Loại | Nguồn | Script |
|---|---|---|
| Giá OHLCV ngày (50 mã + VN-Index) | vnstock, nguồn KBS (bản cộng đồng) | `download_stocks.py` |
| Giá OHLCV ngày (34 mã đã hủy niêm yết) | vnstock, nguồn KBS (bản cộng đồng) | `survivorship_check.py` |
| Danh sách mã, sàn, ngành | Tự định nghĩa trong `download_stocks.py` | `download_stocks.py` |
| BCTC quý (CĐKT, KQKD, LCTT) | SSI iBoard, dữ liệu FiinTrade (file Excel, tải tự động bằng Playwright) | `download_fundamentals.py`, `parse_fundamentals.py` |
| Panel factor tháng | Tính từ hai nguồn trên | `compute_factors.py` |

### 1.3 Mô tả chung

**Giá (vnstock / KBS)**
- Giai đoạn: 8 năm từ 06/11/2018 → 04/11/2026. 45 mã có 1.995–1.996 phiên; IDC 1.973,
  PLC 1.980, DGC 1.989, ACB 1.990, VND 1.990.
- Cột: `time, open, high, low, close, volume`. Giá tính bằng **nghìn đồng**.
- Giá **đã điều chỉnh** cổ tức/chia tách.

**BCTC quý (SSI / FiinTrade)**
- Đầy đủ **50/50 mã**
- Mỗi mã có 3 loại báo cáo cho 30 quý liên tục từ **2019 Q2 đến 2026 Q3**.
- Số liệu tính bằng **đồng**.
- Không có **ngày công bố**, dùng độ trễ giả định 45 ngày.
- Có 3 mẫu BCTC, số chỉ tiêu (CĐKT/KQKD/LCTT) khác nhau:
  - **Ngân hàng** (11 mã: VCB, BID, CTG, TCB, MBB, ACB, VPB, STB, HDB, TPB, EIB): 48/27/52.
  - **Công ty chứng khoán** (5 mã: SSI, SHS, MBS, VND, HCM): 161/85/98.
  - **Doanh nghiệp thường** (34 mã còn lại): 120 chỉ tiêu ở bảng cân đối.
- Một số chỉ tiêu trùng tên (ròng/gộp), nên phân biệt bằng `line_no`.

**Panel factor (`data/final/factor_panel.csv`, chỉ lưu ở máy)**
- 4.800 dòng = 50 mã × 96 tháng, từ 11/2018 đến 10/2026.
- 32 cột: 11 cột định danh/lợi suất + 22 cột factor (đã bao gồm `ret_1m` nằm ở cả 2 cột).
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
| | `cfp` | `CFO_TTM / mcap` | Chỉ doanh nghiệp thường (trống khi `is_financial` = True) |
| **Momentum** | `mom_12_1` | `P_{t−1} / P_{t−12} − 1` | Carhart; bỏ tháng gần nhất |
| | `mom_6_1` | `P_{t−1} / P_{t−6} − 1` | Momentum trung hạn |
| | `ret_1m` | `P_t / P_{t−1} − 1` | Dùng làm factor short-term reversal |
| **Low-risk** | `beta_12m` | `Cov(r_i, r_m) / Var(r_m)`, 252 phiên (≥ 120) | Betting-Against-Beta |
| | `vol_3m` | `std(r_i) × √252`, 63 phiên (≥ 40) | Biến động tổng |
| | `ivol_3m` | `√[(Var(r_i) − Cov(r_i,r_m)² / Var(r_m)) × 252]`, 63 phiên | Biến động riêng (phần dư CAPM) |
| | `max_ret_1m` | `max(r_d)` trong tháng | Hiệu ứng "xổ số" (MAX) |
| **Thanh khoản** | `amihud_3m` | `mean(|r_d| / (P_d × 1.000 × Volume_d)) × 10⁹`, 63 phiên | Amihud illiquidity |
| | `turnover_3m` | `mean(Volume_d, 63 phiên) / shares_mới_nhất` | Vòng quay cổ phiếu |
| **Quality / Profitability** | `roe` | `NI_TTM / ((BE_q + BE_{q−4}) / 2)` | Cần 5 quý → có từ 2020Q2 |
| | `roa` | `NI_TTM / TA_q` | |
| | `gross_profitability` | `GP_TTM / TA_q` | Novy-Marx; chỉ doanh nghiệp thường |
| | `leverage` | `TL_q / TA_q` | QMJ – safety |
| | `accruals` | `(NI_TTM − CFO_TTM) / TA_q` | Sloan; chỉ doanh nghiệp thường (trống khi `is_financial` = True) |
| | `earnings_growth` | `(NI_TTM − NI_TTM,q−4) / |NI_TTM,q−4|` | QMJ – growth |
| **Investment** | `asset_growth` | `TA_q / TA_{q−4} − 1` | FF5 CMA |

Tổng cộng **22 chỉ số factor**.

---

## 3. Kiểm tra survivorship bias

`survivorship_check.py` đo độ nhạy của các factor dùng giá với survivorship bias.
Script so sánh rổ 50 mã với rổ có thêm 34 mã bị hủy niêm yết bắt buộc trên
HOSE/HNX, cho 8 factor: `mom_12_1`, `mom_6_1`, `ret_1m`, `beta_12m`, `vol_3m`,
`ivol_3m`, `max_ret_1m`, `amihud_3m`. Các factor còn lại không được kiểm tra vì
cần BCTC hoặc số cổ phiếu.

- Danh sách 34 mã: ACM, AMD, APP, ART, C92, DAG, FLC, FTM, GAB, GMC, HAI, HBC, HHG, HNG, HOT, HPM, LCS, MCG, PDC, PHP, PVL, PXI, PXS, QBS, RIC, ROS, SD2, TNA, TST, TTB, UDC, VIE, VKC, VXB.
- Giá các mã này lưu ở `data/raw/delisted/`, chỉ ở máy.
- Kết quả tổng hợp lưu ở `results/`:
  - `survivorship_check.csv`: IC và spread theo factor và kịch bản lợi suất hủy niêm yết.
  - `survivorship_levels.csv`: lợi suất đều trọng số của hai rổ.
  - `survivorship_draws.csv`: chênh lệch khi chỉ thêm 7 mã chết ngẫu nhiên.
  - Các file `*_min0.csv`: cùng nội dung, không lọc số phiên tối thiểu trong tháng.

---

## 4. Chia nhóm và đánh giá factor (bước 3–4)

`evaluate_factors.py` đánh giá 21 factor. `mcap` bị bỏ vì cùng thứ hạng với `log_mcap`.
Mọi kết quả là **trước chi phí giao dịch**, trên rổ 50 mã chọn theo năm 2026.

### 4.1 Cách làm

- Mỗi cuối tháng, chia mã thành 5 nhóm đều trọng số theo factor nhân với hướng kỳ
  vọng, rồi đo `ret_fwd_1m`. Q5 là nhóm kỳ vọng cao, nên số dương là đúng hướng.
- Tháng có dưới 25 mã bị bỏ, mã dưới 10 phiên trong tháng không được xếp. Với 50 mã
  hiện tại, bộ lọc phiên không loại dòng nào.
- Hai cách chia: `raw` xếp chung cả rổ; `neutral` xếp riêng trong từng mẫu BCTC rồi gộp.
  `cfp`, `accruals`, `gross_profitability` chỉ có doanh nghiệp thường nên hai cách trùng nhau.
- Thống kê t dùng sai số chuẩn Newey-West, 3 độ trễ với độ dài mẫu hiện tại.
- Đa kiểm định: hoán vị lợi suất giữa các mã trong từng tháng, 2.000 lần, rồi lấy
  max|t| trên 21 factor. Ban đầu dùng Holm theo phân phối chuẩn nhưng đã bỏ: với factor
  nhiễu thuần, |t| ≥ 3,39 xảy ra 0,6% số lần, so với khoảng 0,07% theo phân phối chuẩn.

### 4.2 Kết quả

Kết quả đầy đủ ở `results/factor_summary.csv`, `results/factor_quintiles.csv`,
`results/factor_spreads.png` và `results/factor_cumulative.png`.

Bản `neutral`, cửa sổ `full`. Spread tính bằng %/tháng; Sharpe là Sharpe năm của long-short.
Ngưỡng max|t| ở mức 5% là 3,26.

| Factor | Số tháng | IC | t(IC) | Spread | t(spread) | Sharpe | p max-t |
|---|---|---|---|---|---|---|---|
| `log_mcap` | 95 | 0,037 | 1,58 | 1,31 | 1,96 | 0,70 | 0,69 |
| `bm` | 86 | 0,077 | 2,86 | 2,46 | 3,39 | 1,36 | 0,035 |
| `ep` | 77 | 0,051 | 2,62 | 0,23 | 0,30 | 0,13 | 1,00 |
| `sp` | 77 | 0,062 | 3,34 | 0,83 | 1,24 | 0,47 | 0,98 |
| `cfp` | 77 | 0,066 | 2,77 | 1,20 | 1,21 | 0,53 | 0,99 |
| `mom_12_1` | 83 | 0,006 | 0,26 | 0,37 | 0,59 | 0,22 | 1,00 |
| `mom_6_1` | 89 | 0,008 | 0,50 | 0,02 | 0,03 | 0,01 | 1,00 |
| `ret_1m` | 94 | 0,004 | 0,27 | −0,02 | −0,05 | −0,01 | 1,00 |
| `beta_12m` | 89 | 0,001 | 0,06 | −0,64 | −0,75 | −0,29 | 1,00 |
| `vol_3m` | 93 | −0,009 | −0,40 | −1,23 | −1,70 | −0,60 | 0,86 |
| `ivol_3m` | 93 | 0,007 | 0,32 | −0,92 | −1,22 | −0,46 | 0,99 |
| `max_ret_1m` | 95 | 0,019 | 1,16 | 0,11 | 0,18 | 0,07 | 1,00 |
| `amihud_3m` | 93 | 0,022 | 1,33 | 1,02 | 1,66 | 0,73 | 0,87 |
| `turnover_3m` | 93 | 0,002 | 0,07 | −0,15 | −0,20 | −0,07 | 1,00 |
| `roe` | 74 | 0,002 | 0,08 | −0,92 | −1,12 | −0,50 | 0,99 |
| `roa` | 77 | −0,006 | −0,30 | −1,33 | −1,64 | −0,71 | 0,88 |
| `gross_profitability` | 77 | −0,029 | −1,03 | −2,22 | −1,86 | −0,85 | 0,77 |
| `leverage` | 86 | −0,010 | −0,65 | −0,59 | −1,25 | −0,52 | 0,98 |
| `accruals` | 77 | 0,069 | 3,56 | 1,08 | 1,72 | 0,68 | 0,85 |
| `earnings_growth` | 65 | −0,011 | −0,63 | −0,05 | −0,07 | −0,03 | 1,00 |
| `asset_growth` | 74 | −0,020 | −1,12 | −0,62 | −0,85 | −0,35 | 1,00 |

Độ bền của `bm` (spread %/tháng, trong ngoặc là t Newey-West):

| Cửa sổ | `raw` | `neutral` |
|---|---|---|
| `full` | 2,11 (3,16) | 2,46 (3,39) |
| `common`, 65 tháng từ 05/2021 | 1,74 (2,53) | 1,88 (2,43) |
| `first_half`, trước 03/2023 | 2,94 (2,87) | 3,85 (3,59) |
| `second_half`, từ 03/2023 | 1,28 (1,75) | 1,07 (1,49) |
| `ex_covid`, bỏ 03/2020–06/2021 | 1,66 (2,37) | 1,75 (2,34) |

### 4.3 Cách đọc

- **Chỉ `bm` vượt ngưỡng đa kiểm định, và chỉ ở một đặc tả.** Bản `neutral` cửa sổ `full`
  có p max-t 0,035, bản `raw` là 0,062. Ở cửa sổ `common`, p max-t là 0,31–0,34. Tín hiệu
  vẫn cùng hướng ở mọi cửa sổ, nhưng yếu đi rõ ở nửa sau của mẫu.
- **Chưa thể gọi `bm` là premium đã xác nhận.** Rổ chọn theo năm 2026 loại các mã rẻ đã
  chết, nên Value có thể bị thổi phồng, và phép đo survivorship ở mục 3 chưa bao phủ factor
  này vì mã chết không có BCTC. `bm` còn dựa trên vốn hóa xấp xỉ (mục 2.3).
- **Không có bằng chứng cho Momentum.** Spread gần 0 và IC không có ý nghĩa thống kê.
- **Phần lớn Low-risk và Quality có spread âm nhưng không vượt ngưỡng đa kiểm định.** Không
  nên kết luận các factor này "chết": mẫu ngắn, và survivorship có thể làm lệch kết quả. Amihud
  càng phải đọc cùng mục 3, vì spread của nó giảm mạnh khi thêm mã chết.
- **IC và spread đôi khi không khớp.** `accruals` và `sp` có t(IC) trên 3 nhưng t(spread)
  dưới 2, nên cần xem thêm ở hồi quy Fama-MacBeth.

### 4.4 Hạn chế đã biết

- **Vốn hóa:** `mcap` lấy giá điều chỉnh nhân số cổ phiếu mới nhất, tức dùng thông tin
  tương lai, ảnh hưởng đến Size, Value và `turnover_3m`. Trung vị của số cổ phiếu mới nhất
  so với số cổ phiếu tại quý đang dùng là 1,42 lần. Riêng tỷ lệ này cũng dự báo được lợi
  suất (t khoảng 2,0–2,6), nên thay bằng số cổ phiếu theo quý không phải cách sửa đúng.
  Muốn sửa cần giá chưa điều chỉnh, và mức lệch hiện chưa đo được. Hai con số này và phép
  thử nhiễu ở mục 4.1 đến từ phép đo riêng, chưa có trong `evaluate_factors.py`.
- **Đều trọng số:** chưa có bản theo trọng số vốn hóa, vì nó phụ thuộc biến vốn hóa trên.
- **Cửa sổ `ex_covid`** là mốc tự chọn để kiểm tra độ bền, không phải mốc học thuật.

