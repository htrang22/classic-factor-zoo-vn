# Nhật ký dự án: Factor Zoo cổ điển trên thị trường Việt Nam

> Cập nhật lần cuối: 04/11/2026. Branch: `data-collection` — PR #1 vào `main`.

---

## 1. Dữ liệu

### 1.1 Danh sách mã (30 mã: 25 HOSE + 5 HNX)

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

Benchmark: **VN-Index** (`VNINDEX`).

Tiêu chí chọn: trải đều vốn hóa lớn/vừa/nhỏ và nhiều ngành để các factor
(nhất là Size, Value) có độ phân tán. Danh sách chọn theo thời điểm hiện tại
→ **còn survivorship bias**, chưa xử lý.

### 1.2 Nguồn dữ liệu

| Loại | Nguồn | Script |
|---|---|---|
| Giá OHLCV ngày (30 mã + VN-Index) | vnstock, nguồn KBS (bản cộng đồng) | `download_stocks.py` |
| Danh sách mã, sàn, ngành | Tự định nghĩa trong `download_stocks.py` | `download_stocks.py` |
| BCTC quý (CĐKT, KQKD, LCTT) | SSI iBoard, dữ liệu FiinTrade (tải tay file Excel) | `parse_fundamentals.py` |
| Panel factor tháng | Tính từ hai nguồn trên | `compute_factors.py` |

### 1.3 Mô tả chung

**Giá (vnstock / KBS)**
- Giai đoạn: 06/11/2018 → 04/11/2026. Mỗi mã khoảng 1.990 phiên; IDC 1.973,
  DGC 1.989, ACB 1.990 (thiếu vài phiên, có thể do tạm ngừng giao dịch).
- Cột: `time, open, high, low, close, volume`. Giá tính bằng **nghìn đồng**.
- Giá **đã điều chỉnh** cổ tức/chia tách (vd FPT năm 2018 ≈ 12). Đây là suy
  luận từ số liệu, chưa đối chiếu với nguồn khác.
- Bản cộng đồng giới hạn dữ liệu 1D tối đa **8 năm**.

**BCTC quý (SSI / FiinTrade)**
- Đầy đủ **30/30 mã**
- Mỗi mã có 3 loại báo cáo × 2 file (mỗi lần xuất tối đa 15 quý). Ghép lại
  được **30 quý liên tục từ 2019Q2 đến 2026Q3**, không thiếu quý.
- Số liệu tính bằng **đồng**, theo **từng quý** (không cộng dồn từ đầu năm).
- Không có **ngày công bố** → point-in-time dùng độ trễ giả định 45 ngày.
- Mẫu ngân hàng (48/27/52 chỉ tiêu) khác mẫu doanh nghiệp thường (120 chỉ
  tiêu ở bảng cân đối của VIC). Một số chỉ tiêu trùng tên (ròng/gộp), nên
  phân biệt bằng `line_no`.
- Cột EPS bằng 0 ở mọi quý (lỗi nguồn)

**Panel factor (`data/final/factor_panel.csv`)**
- 2.880 dòng = 30 mã × 96 tháng, từ 11/2018 đến 10/2026 (bỏ tháng 11/2026
  vì chưa kết thúc).
- 31 cột: 10 cột định danh/lợi suất + 21 chỉ số factor.
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
- **Vốn chủ sở hữu sổ sách:** `book_equity = Vốn chủ sở hữu − Lợi ích cổ đông thiểu số`.

Chỉ tiêu BCTC được lấy theo tên dòng:

| Biến | Mẫu ngân hàng | Mẫu doanh nghiệp |
|---|---|---|
| Tổng tài sản `TA` | TỔNG TÀI SẢN | TỔNG TÀI SẢN |
| Tổng nợ `TL` | Tổng nợ phải trả | NỢ PHẢI TRẢ |
| Vốn chủ sở hữu | Vốn chủ sở hữu | VỐN CHỦ SỞ HỮU |
| Lợi ích CĐ thiểu số | Lợi ích của cổ đông thiểu số | Lợi ích cổ đông không kiểm soát |
| Vốn điều lệ | Vốn điều lệ | Vốn góp |
| Doanh thu `Rev` | Tổng thu nhập hoạt động | Doanh số thuần |
| Lãi gộp `GP` | – | Lãi gộp |
| LNST cổ đông mẹ `NI` | Cổ đông của Công ty mẹ | Lợi nhuận của Cổ đông của Công ty mẹ |
| CFO | Lưu chuyển tiền thuần từ các hoạt động sản xuất kinh doanh | (như bên trái) |

### 2.2 Cột định danh và lợi suất

| Tên biến | Ý nghĩa / công thức |
|---|---|
| `date` | Ngày cuối tháng |
| `symbol`, `exchange`, `sector` | Mã, sàn, ngành |
| `is_bank` | `True` nếu BCTC theo mẫu ngân hàng |
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
| | `cfp` | `CFO_TTM / mcap` | Chỉ doanh nghiệp thường (ngân hàng = trống) |
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
| | `accruals` | `(NI_TTM − CFO_TTM) / TA_q` | Sloan; chỉ doanh nghiệp thường |
| | `earnings_growth` | `(NI_TTM − NI_TTM,q−4) / |NI_TTM,q−4|` | QMJ – growth |
| **Investment** | `asset_growth` | `TA_q / TA_{q−4} − 1` | FF5 CMA |

Tổng cộng **21 chỉ số factor**.
