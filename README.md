# 🍏 Fewly Repo • iPhone Jailbreak (Dopamine Rootless & iOS)

Kho lưu trữ Tweak, Tiện ích và Ứng dụng dành cho **iPhone Jailbreak** bằng **Dopamine (Rootless iOS 15.0 – 16.6.5)** và các công cụ Jailbreak iOS khác.

🌐 **Website Repo:** [https://fewly11.github.io/](https://fewly11.github.io/)

---

## ⚡ Hướng dẫn thêm nguồn vào thiết bị

### 1. Dành cho Dopamine (Rootless - Sileo / Zebra)
- Mở **Sileo** hoặc **Zebra** trên iPhone.
- Chuyển sang tab **Nguồn (Sources)**.
- Bấm nút **(+) Thêm nguồn**.
- Nhập địa chỉ: `https://fewly11.github.io/`
- Hoặc mở Safari trên iPhone truy cập [https://fewly11.github.io/](https://fewly11.github.io/) rồi bấm nút **"Thêm vào Sileo (Dopamine)"**.

### 2. Dành cho Cydia (Legacy Rootful)
- Mở **Cydia** -> **Sources** -> **Edit** -> **Add**.
- Nhập: `https://fewly11.github.io/`

---

## 🛠️ Cấu trúc kho lưu trữ (APT Debian Repository)

Kho lưu trữ tuân thủ đầy đủ chuẩn APT Debian cho iOS Jailbreak:

- `Release`: Khai báo siêu dữ liệu kho, hỗ trợ kiến trúc `iphoneos-arm64` (Dopamine Rootless) và `iphoneos-arm` cùng đầy đủ mã băm SHA256, SHA1, MD5.
- `Packages`, `Packages.gz`, `Packages.bz2`, `Packages.xz`: Danh sách gói cài đặt và thông tin kiểm tra tính toàn vẹn gói.
- `sileo-featured.json`: Banner trang chủ tích hợp native trong ứng dụng Sileo.
- `packages.json`: Dữ liệu cho giao diện web trực quan.
- `debs/`: Thư mục chứa các tệp gói tin `.deb`.
- `build_repo.py`: Tập lệnh tự động quét thư mục `debs/`, trích xuất thông tin `control`, tính toán mã băm và cập nhật toàn bộ kho lưu trữ chỉ với 1 lệnh.

---

## 🚀 Cách thêm Tweak mới vào Repo

1. Thả tệp `.deb` mới vào thư mục `debs/`.
2. Mở terminal và chạy lệnh:
   ```bash
   python build_repo.py
   ```
3. Commit và đẩy lên GitHub:
   ```bash
   git add .
   git commit -m "Update repo packages"
   git push origin main
   ```
4. GitHub Pages sẽ tự động cập nhật và các máy iPhone sử dụng Dopamine có thể cập nhật nguồn ngay lập tức!
