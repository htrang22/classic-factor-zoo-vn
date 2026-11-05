Hướng dẫn cho AI khi làm việc trong repo này. Đọc toàn bộ file này và thư mục `notes/` trước khi viết bất kỳ dòng code nào.

## Dữ liệu

* Không commit, push hay public dữ liệu gốc hoặc dữ liệu suy ra được ra dữ liệu gốc. Cụ thể: `data/raw/`, `data/processed/fundamentals_long.csv`, `data/final/` (gồm `factor_panel.csv`), và mọi bảng mã × ngày hoặc mã × tháng có giá, lợi suất, vốn hóa, khối lượng hay chỉ tiêu BCTC, kể cả khi chép vào README, `notes/` hay mô tả PR. Lý do: dữ liệu vnstock và FiinTrade không có quyền phân phối lại.
* Chỉ được public: code, tài liệu, `fundamentals_coverage.csv`, và kết quả đã tổng hợp qua nhiều mã (IC, Sharpe, biểu đồ cumulative return của danh mục).
* Trước mỗi commit, chạy `git diff --cached --stat` và kiểm tra không có file dữ liệu. Thấy file mới trong `data/` thì hỏi trước.
* Test bằng thư mục tạm, không ghi đè `data/raw/` khi chỉ đang test.

## Tài khoản SSI

* Không nhập mật khẩu hay OTP thay người dùng. Người dùng tự đăng nhập.
* Không thay đổi Giao diện của tôi hay cài đặt tài khoản. Không bấm MUA/BÁN.
* Không commit hay chia sẻ `~/.cache/ssi-iboard-profile`.
* Tải chậm (nghỉ ≥ 2 giây giữa các thao tác). Chỉ tải các mã cần dùng.
