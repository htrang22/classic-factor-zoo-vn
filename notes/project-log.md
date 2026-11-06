# Nhật ký dự án: Factor Zoo cổ điển trên thị trường Việt Nam

> Cập nhật lần cuối: 06/11/2026. Branch: `survivorship-check`.

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

Tổng cộng **21 chỉ số factor**, chưa tính `ret_1m` (đã có ở mục 2.2).

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

```bash
python3 survivorship_check.py --download
```

```bash
python3 survivorship_check.py
```

```bash
python3 survivorship_check.py --min-days 0
```
