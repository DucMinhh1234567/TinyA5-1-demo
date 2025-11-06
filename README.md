# TinyA5/1 Stream Cipher Visualizer

Bài tập nhóm môn An toàn bảo mật thông tin

## Tính Năng

- **Giao Diện Web**: Hiển thị tương tác với các thao tác thanh ghi từng bước
- **Công Cụ CLI**: Mã hóa/giải mã dựa trên terminal
- **Hỗ Trợ Đầu Vào Kép**: Chuỗi nhị phân hoặc đầu vào ký tự (A-H)
- **Hiển Thị Thời Gian Thực**: Xem các thanh ghi xoay và tạo keystream
- **Visualizer**: Hiển thị rõ ràng các thành phần bên trong của thuật toán

## Cài Đặt

### Yêu Cầu

- Python 3.7 trở lên
- pip (trình quản lý gói Python)

### Thiết Lập

1. **Clone hoặc tải xuống các tệp dự án**

2. **Cài đặt các phụ thuộc**:
   ```bash
   pip install flask flask-cors
   ```

3. **Chạy ứng dụng web**:
   ```bash
   python app.py
   ```

4. **Mở trình duyệt** và truy cập `http://localhost:5000`

## Cách Sử Dụng

### Giao Diện Web

1. **Chọn Định Dạng Đầu Vào**:
   - **Nhị phân**: Nhập chuỗi nhị phân (ví dụ: "111")
   - **Ký tự**: Nhập chữ cái A-H (ví dụ: "H")

2. **Chọn Chế Độ**:
   - **Tức thì**: Nhận kết quả mã hóa/giải mã ngay lập tức
   - **Hiển thị từng bước**: Xem thuật toán thực thi từng bước

3. **Nhập Dữ Liệu**:
   - **Plaintext/Ciphertext**: Dữ liệu để mã hóa/giải mã
   - **Khóa**: 23 bit (ví dụ: "10010101001110100110000")

4. **Điều Khiển Hiển Thị** (ở chế độ từng bước):
   - **Trước/Tiếp**: Điều hướng qua các bước thủ công
   - **Phát/Tạm dừng**: Tự động phát qua tất cả các bước
   - **Hiển Thị Thanh Ghi**: Xem các thanh ghi X (6 bit), Y (8 bit), Z (9 bit)
   - **Bit Điều Khiển**: Các vị trí x2, y7, z8 được tô sáng
   - **Hàm Đa Số**: Hiển thị phép tính maj(x2, y7, z8)
   - **Xoay**: Chỉ báo trực quan về các thanh ghi nào đang xoay
   - **Keystream**: Hiển thị phép tính s = x5 ⊕ y7 ⊕ z8
   - **Mã Hóa**: Hiển thị dữ liệu ⊕ keystream = kết quả

### Giao Diện Dòng Lệnh

#### Chế Độ Tương Tác
```bash
python cli.py --interactive
```

#### Lệnh Trực Tiếp

**Mã hóa dữ liệu nhị phân**:
```bash
python cli.py --encrypt --data "111" --key "10010101001110100110000"
```

**Giải mã dữ liệu nhị phân**:
```bash
python cli.py --decrypt --data "011" --key "10010101001110100110000"
```

**Mã hóa dữ liệu ký tự**:
```bash
python cli.py --encrypt --data "H" --key "10010101001110100110000" --char
```

**Chế độ chi tiết (hiển thị từng bước)**:
```bash
python cli.py --encrypt --data "111" --key "10010101001110100110000" --verbose
```

## Chi Tiết Thuật Toán

### Tổng Quan TinyA5/1

TinyA5/1 là phiên bản đơn giản hóa của stream cipher A5/1 được sử dụng trong điện thoại di động GSM. Nó có các tính năng:

- **3 Thanh Ghi**: X (6 bit), Y (8 bit), Z (9 bit)
- **Khóa 23-bit**: Chia nhỏ qua ba thanh ghi
- **Hàm Đa Số**: Xác định thanh ghi nào xoay
- **Phản Hồi XOR**: Các thanh ghi xoay với phản hồi XOR
- **Keystream**: Được tạo bằng cách XOR các bit thanh ghi cụ thể

### Mã Hóa Ký Tự

Hệ thống hỗ trợ đầu vào ký tự sử dụng mapping:
- A → 000
- B → 001
- C → 010
- D → 011
- E → 100
- F → 101
- G → 110
- H → 111

### Các Bước Thuật Toán

1. **Khởi tạo**: Tải khóa 23-bit vào các thanh ghi X, Y, Z
2. **Cho mỗi bit**:
   - Đọc các bit điều khiển: x1, y3, z3
   - Tính đa số: maj(x1, y3, z3)
   - Xoay các thanh ghi nơi bit điều khiển bằng đa số
   - Tạo bit keystream: s = x5 ⊕ y7 ⊕ z8
   - XOR với bit dữ liệu: cipher_bit = data_bit ⊕ s

## Ví Dụ

### Ví Dụ 1: Mã Hóa "H" (111)

**Đầu vào**:
- Plaintext: "H" (nhị phân: "111")
- Khóa: "10010101001110100110000"

**Quá trình**:
1. Chia khóa: X="100101", Y="01001110", Z="100110000"
2. Bước 0: x1=0, y3=0, z3=1 → maj(0,0,1)=0 → xoay X,Y
3. Bước 1: x1=1, y3=0, z3=1 → maj(1,0,1)=1 → xoay X,Z
4. Bước 2: x1=1, y3=0, z3=0 → maj(1,0,0)=0 → xoay Y,Z
5. Tạo keystream: "100"
6. Kết quả: "111" ⊕ "100" = "011" (D)

### Ví Dụ 2: Sử Dụng CLI

```bash
# Mã hóa "H" với đầu ra chi tiết
python cli.py --encrypt --data "H" --key "10010101001110100110000" --char --verbose

# Giải mã kết quả
python cli.py --decrypt --data "D" --key "10010101001110100110000" --char --verbose
```

## Cấu Trúc Tệp

```
TinyA51/
├── tinya51.py          # Triển khai thuật toán cốt lõi
├── cli.py              # Giao diện dòng lệnh
├── app.py              # Máy chủ web Flask
├── requirements.txt    # Phụ thuộc Python
├── README.md           # Tệp này
├── templates/
│   └── index.html      # HTML giao diện web
└── static/
    ├── style.css       # Kiểu giao diện web
    └── app.js          # JavaScript giao diện web
```

## Khắc Phục Sự Cố

### Các Vấn Đề Thường Gặp

1. **"Khóa phải chính xác 23 bit"**
   - Đảm bảo khóa của bạn có chính xác 23 ký tự
   - Chỉ sử dụng 0 và 1

2. **"Dữ liệu chỉ được chứa 0 và 1"**
   - Đối với chế độ nhị phân, chỉ sử dụng 0 và 1
   - Đối với chế độ ký tự, chỉ sử dụng A-H

3. **Giao diện web không tải**
   - Đảm bảo máy chủ Flask đang chạy (`python app.py`)
   - Kiểm tra xem cổng 5000 có sẵn không
   - Thử `http://127.0.0.1:5000` thay vì localhost

4. **Lỗi "Module not found"**
   - Cài đặt các phụ thuộc: `pip install flask flask-cors`
   - Đảm bảo bạn đang ở đúng thư mục
