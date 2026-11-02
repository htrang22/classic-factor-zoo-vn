# classic-factor-zoo-vn
Factor Zoo cổ điển trên thị trường Việt Nam. Value, Momentum, Size, Quality, Low-volatility có tạo premium ở thị trường Việt Nam không?

Câu hỏi: Các factor học thuật (Value, Momentum, Size, Quality, Low-volatility) có tạo ra premium ở thị trường VN (HOSE/HNX) không? Factor nào bền vững sau chi phí giao dịch?

## Cơ sở kinh tế - tài chính: 
Fama-French 3/5 factor, Carhart momentum, Betting-Against-Beta, Quality-minus-Junk.

## Data:

Giá đóng cửa/mở cửa/cao/thấp, khối lượng, đã điều chỉnh cổ tức và chia tách (nguồn: vnstock, SSI iBoard API, Fireant, hoặc WiChart)
Báo cáo tài chính quý (doanh thu, lợi nhuận, tổng tài sản, vốn chủ, nợ) để tính P/B, P/E, ROE, tăng trưởng lợi nhuận
Vốn hóa, danh sách VN30/VN-Index để làm benchmark
Lưu ý: phải dùng point-in-time (dùng ngày công bố BCTC, không dùng ngày kết thúc quý) để tránh look-ahead bias

## Các bước:

1. Làm sạch data, xử lý cổ phiếu bị đình chỉ/hủy niêm yết (survivorship bias)
2. Tính 10-20 factor đơn lẻ
3. Sắp xếp cổ phiếu vào 5-10 nhóm (quantile) theo từng factor, tính lợi suất từng nhóm
4. Đánh giá: IC (Spearman rank correlation giữa factor và lợi suất kỳ sau), spread long-short, t-stat
5. Kiểm định bằng hồi quy Fama-MacBeth

## Output:

1. Bảng tổng hợp: IC trung bình, IC IR, Sharpe long-short của từng factor
2. Biểu đồ cumulative return theo decile
3. Báo cáo: factor nào hoạt động, factor nào “chết” ở VN và giải thích kinh tế
