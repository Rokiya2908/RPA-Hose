# RPA-Hose

Bot tải file PDF từ SFTP / share folder Windows / thư mục local, upload từng file lên API trích xuất dữ liệu của HOSE (sdtech), lưu kết quả JSON và đẩy kết quả ra thư mục output.

```
Nguồn (sftp | shared | local)
  → tải PDF về  <BotFolderLocation>\<thời gian chạy>\input
  → upload từng PDF lên API  (apiurl + token trong config)
  → lưu response JSON vào   <BotFolderLocation>\<thời gian chạy>\result
  → đẩy thư mục output ra đích (--output)
```

## 1. Cài đặt

Yêu cầu Python 3.10 trở lên (đã chạy thử với 3.12).

```powershell
cd D:\Work\RPA-Hose
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Cấu hình — `config/config.json`

| Khóa | Ý nghĩa |
|---|---|
| `BotFolderLocation` | Thư mục làm việc của bot. Mỗi lần chạy tạo một thư mục con theo thời gian |
| `apiurl` | API upload file, ví dụ `https://api.sdtech.vn/t/hose.sdtech.vn/api/hose/1.0/bieu-mau/10/upload` |
| `token` | Bearer token gọi API. **Token chỉ sống 10 tiếng**, hết hạn phải dán token mới vào đây |
| `SFTPHost`, `username`, `password` | Thông tin SFTP mặc định |
| `SharedHost`, `SharedUsername`, `SharedPassword` | Thông tin share folder mặc định |

Giá trị `"N/A"` nghĩa là không dùng. Thông tin máy remote truyền qua CLI sẽ **ghi đè** giá trị trong config.

> Kiểm tra token còn hạn: dán token vào https://jwt.io và xem trường `exp`.

## 3. Chạy bằng CLI

```
python src/main.py --input <nguồn> --output <đích> --downloadfrom <sftp|shared|local>
                   [--host <IP>] [--port <port>] [--username <user>] [--password <pass>]
```

| Tham số | Bắt buộc | Ý nghĩa |
|---|---|---|
| `--input` | Có | Thư mục chứa PDF cần xử lý |
| `--output` | Có | Thư mục nhận kết quả |
| `--downloadfrom` | Có | `sftp`, `shared` hoặc `local` |
| `--host` | Không | IP hoặc tên máy remote |
| `--port` | Không | Mặc định 22 (SFTP), 445 (share folder) |
| `--username` | Không | Tài khoản máy remote. Tài khoản domain ghi `DOMAIN\user` |
| `--password` | Không | Mật khẩu tài khoản máy remote |

Xem nhanh: `python src/main.py -h`

### 3.1. Thư mục local

```powershell
python src/main.py --downloadfrom local --input "D:\Hose\input" --output "D:\Hose\output"
```

### 3.2. Share folder Windows

`--input` / `--output` có thể ghi đường dẫn bên trong share (bot tự ghép với `--host`) hoặc đường dẫn UNC đầy đủ.

```powershell
# Có tài khoản
python src/main.py --downloadfrom shared --host 192.168.1.10 `
    --username "CONGTY\rpa_user" --password "***" `
    --input "RPA\input" --output "RPA\output"

# Tương đương, dùng UNC đầy đủ
python src/main.py --downloadfrom shared --host 192.168.1.10 `
    --username "CONGTY\rpa_user" --password "***" `
    --input "\\192.168.1.10\RPA\input" --output "\\192.168.1.10\RPA\output"

# Không truyền tài khoản: dùng quyền của user Windows đang chạy bot
python src/main.py --downloadfrom shared --input "\\192.168.1.10\RPA\input" --output "\\192.168.1.10\RPA\output"
```

### 3.3. SFTP

```powershell
python src/main.py --downloadfrom sftp --host 10.0.0.5 --port 22 `
    --username rpa --password "***" `
    --input "/data/hose/input" --output "/data/hose/output"
```

### 3.4. Gọi từ công cụ RPA / Task Scheduler

Gọi thẳng python trong venv, dùng đường dẫn tuyệt đối:

```bat
D:\Work\RPA-Hose\.venv\Scripts\python.exe D:\Work\RPA-Hose\src\main.py --downloadfrom local --input "D:\Hose\input" --output "D:\Hose\output"
```

> Mật khẩu truyền qua `--password` hiện trong danh sách tiến trình và lịch sử lệnh. Với lịch chạy tự động, nên để mật khẩu trong `config.json` thay vì CLI.

## 4. Kết quả của một lần chạy

```
<BotFolderLocation>\<HH_MM_SS_dd_mm_yyyy>\
├── input\     PDF đã tải về
├── result\    <tên file>.json — response của API cho từng PDF thành công
├── output\    file kết quả sẽ đẩy ra --output
└── logs\log.txt
```

Tra cứu trong `log.txt`:

| Dòng log | Ý nghĩa |
|---|---|
| `Total number of file has been copied ... is N` | Số PDF đã tải về |
| `Upload file ... with status 200` | Upload thành công |
| `Token is invalid or expired` | Token hết hạn → cập nhật `token` trong config |
| `Total number of file has been extracted successfully is X/N` | Tổng kết lần chạy |

## 5. Hạn chế hiện tại

- Bot luôn thoát với exit code 0, kể cả khi lỗi. Muốn biết kết quả phải đọc `log.txt`.
- Chưa có bước ghi dữ liệu vào Excel template (`config/Template`). Thư mục `output` hiện đang trống.
- Bước đẩy output ra `--output` đang copy cả thư mục nên bị lỗi `Permission denied`; kết quả tạm lấy trong thư mục `result`.
- Luồng SFTP chưa được test với server thật. Khi chạy trên Windows, đường dẫn file remote đang bị ghép bằng `\` thay vì `/`, nên việc tải file từ SFTP có thể lỗi.
- Token phải cập nhật tay mỗi 10 tiếng.
- Chỉ lấy file `.pdf` ở cấp đầu của thư mục input, không quét thư mục con.
