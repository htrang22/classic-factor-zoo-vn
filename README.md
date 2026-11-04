# classic-factor-zoo-vn
Factor Zoo cổ điển trên thị trường Việt Nam. Value, Momentum, Size, Quality, Low-volatility có tạo premium ở thị trường Việt Nam không?

Câu hỏi: Các factor học thuật (Value, Momentum, Size, Quality, Low-volatility) có tạo ra premium ở thị trường VN (HOSE/HNX) không? Factor nào bền vững sau chi phí giao dịch?

## Cơ sở kinh tế - tài chính: 
Fama-French 3/5 factor, Carhart momentum, Betting-Against-Beta, Quality-minus-Junk.

## Data:

**Rổ cổ phiếu:** 50 mã (42 HOSE + 8 HNX), trải đều vốn hóa lớn/vừa/nhỏ và nhiều ngành: 11 ngân hàng, 5 công ty chứng khoán, 34 doanh nghiệp thường. Không có mã bảo hiểm (mẫu BCTC riêng, chưa xử lý). Benchmark: VN-Index.

| Dữ liệu | Nguồn | Giai đoạn |
|---|---|---|
| Giá OHLCV ngày, đã điều chỉnh cổ tức và chia tách (nghìn đồng) | vnstock, nguồn KBS (bản cộng đồng, tối đa 8 năm) | 11/2018 → 11/2026 |
| VN-Index | vnstock, nguồn KBS | 11/2018 → 11/2026 |
| BCTC quý: bảng cân đối, kết quả kinh doanh, lưu chuyển tiền tệ (đồng) | SSI iBoard, dữ liệu FiinTrade (xuất file Excel, tự động bằng `download_fundamentals.py`) | 2019Q2 → 2026Q3 (30 quý) |

- BCTC có 3 mẫu khác nhau (ngân hàng, công ty chứng khoán, doanh nghiệp thường); `compute_factors.py` tự nhận diện mẫu và quy đổi về cùng bộ chỉ tiêu: tổng tài sản, nợ, vốn chủ, vốn điều lệ, doanh thu, lãi gộp, LNST cổ đông mẹ, CFO.
- Vốn hóa = giá đã điều chỉnh × số cổ phiếu mới nhất (vốn điều lệ / 10.000 đồng).
- **Point-in-time:** nguồn dữ liệu không có ngày công bố BCTC, nên số liệu quý chỉ được dùng từ **ngày kết thúc quý + 45 ngày** (hạn công bố BCTC quý theo Thông tư 96/2020 là 20–30 ngày) để tránh look-ahead bias.
- **Quyền dữ liệu:** dữ liệu gốc (`data/raw/`) và bản đã chuyển định dạng (`data/processed/fundamentals_long.csv`) chỉ lưu ở máy, không đưa lên GitHub vì không có quyền phân phối lại. Repo chỉ chứa code, `data/final/` (các chỉ số đã tính) và `data/processed/fundamentals_coverage.csv` (báo cáo độ phủ BCTC, không chứa số liệu gốc).

**Cấu trúc dữ liệu**

```
data/
├── raw/                 # chỉ ở máy
│   ├── prices/          # giá ngày từng mã
│   ├── prices_all.csv   # giá ngày gộp 50 mã
│   ├── vnindex.csv
│   ├── universe.csv     # mã, sàn, ngành
│   └── quarter-report/  # file Excel BCTC từ SSI iBoard
├── processed/
│   ├── fundamentals_long.csv      # chỉ ở máy
│   └── fundamentals_coverage.csv  # số quý BCTC theo mã × loại báo cáo
└── final/
    └── factor_panel.csv # input của model: mã × cuối tháng, 21 factor
```

## Các bước:

| # | Bước | Trạng thái | Script |
|---|---|---|---|
| 0 | Thu thập dữ liệu: giá, VN-Index, BCTC quý cho 50 mã | ✅ Xong | `download_stocks.py`, `download_fundamentals.py`, `parse_fundamentals.py` |
| 1 | Làm sạch data, xử lý cổ phiếu bị đình chỉ/hủy niêm yết (survivorship bias) | ⏳ Chưa làm | – |
| 2 | Tính 10-20 factor đơn lẻ | ✅ Xong (21 factor) | `compute_factors.py` |
| 3 | Sắp xếp cổ phiếu vào nhóm (quantile) theo từng factor, tính lợi suất từng nhóm | ⏳ Chưa làm | – |
| 4 | Đánh giá: IC (Spearman rank correlation giữa factor và lợi suất kỳ sau), spread long-short, t-stat | ⏳ Chưa làm | – |
| 5 | Kiểm định bằng hồi quy Fama-MacBeth | ⏳ Chưa làm | – |

- **Bước 2:** 21 factor theo 7 nhóm: Size (`mcap`, `log_mcap`), Value (`bm`, `ep`, `sp`, `cfp`), Momentum (`mom_12_1`, `mom_6_1`, `ret_1m`), Low-risk (`beta_12m`, `vol_3m`, `ivol_3m`, `max_ret_1m`), thanh khoản (`amihud_3m`, `turnover_3m`), Quality (`roe`, `roa`, `gross_profitability`, `leverage`, `accruals`, `earnings_growth`), Investment (`asset_growth`). Biến mục tiêu: `ret_fwd_1m` (lợi suất tháng sau).
- **Bước 3:** với 50 mã, chia 3–5 nhóm (tercile/quintile) thay vì 10 nhóm, để mỗi nhóm có đủ số mã.

**Chạy lại pipeline**

```bash
python3 download_stocks.py      # tải giá 50 mã + VN-Index (gọi vnstock, chậm)
python3 download_fundamentals.py  # tải BCTC quý từ SSI iBoard (mở Chrome; lần đầu tự đăng nhập)
python3 parse_fundamentals.py   # gộp file Excel BCTC trong data/raw/quarter-report/
python3 compute_factors.py      # tính panel factor -> data/final/factor_panel.csv
```

Mỗi lần chạy, các script xử lý lại toàn bộ dữ liệu và ghi đè file đầu ra.

## Output:

1. Bảng tổng hợp: IC trung bình, IC IR, Sharpe long-short của từng factor
2. Biểu đồ cumulative return theo decile
3. Báo cáo: factor nào hoạt động, factor nào “chết” ở VN và giải thích kinh tế
