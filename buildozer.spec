[app]

# (str) Tên ứng dụng của bạn
title = Sok Wallet

# (str) Tên gói, không dấu, không khoảng trắng, không gạch ngang
package.name = sokwallet

# (str) Tên miền của gói, dùng để định danh duy nhất
package.domain = org.sokchain.wallet

# (str) Thư mục chứa mã nguồn (main.py)
source.dir = .

# (list) Các loại file cần được đóng gói vào APK
source.include_exts = py,png,jpg,kv,atlas,json,ttf

# (str) Phiên bản của ứng dụng
version = 1.0.0

# (list) [QUAN TRỌNG NHẤT] Danh sách các thư viện Python cần thiết.
# Các phiên bản này đã được ghim để đảm bảo quá trình build ổn định.
requirements = python3,kivy==2.3.1,requests,cffi==1.15.1,pycparser==2.21,idna==3.4,charset-normalizer==2.1.1,urllib3==1.26.12,certifi==2022.9.24,openssl==1.1.1q,cryptography==38.0.3,colorama,qrcode[pil]

# (str) Hướng màn hình. 'portrait' (dọc) là phù hợp cho ví.
orientation = portrait

# (bool) Cho phép ứng dụng truy cập Internet (bắt buộc cho `requests`)
fullscreen = 0

# (str) Đường dẫn đến icon của ứng dụng. Cần có file icon.png trong thư mục dự án.
icon.filename = %(source.dir)s/icon.png

# (str) Đường dẫn đến màn hình chờ. Cần có file presplash.png.
presplash.filename = %(source.dir)s/presplash.png

# (str) [QUAN TRỌNG] Sử dụng nhánh 'develop' của python-for-android để có các công thức build đã được sửa lỗi.
p4a.branch = develop


[android]

# (list) Các kiến trúc CPU cần build. Tối ưu cho hầu hết điện thoại.
android.archs = arm64-v8a, armeabi-v7a

# (int) API level tối thiểu để chạy ứng dụng
android.minapi = 21

# (int) API level mục tiêu
android.api = 31

# (list) Các quyền mà ứng dụng cần. INTERNET là bắt buộc.
android.permissions = INTERNET

# (str) The Android NDK version to use
# [QUAN TRỌNG] Bỏ trống hoặc comment lại dòng này. 
# Chúng ta để cho p4a tự chọn phiên bản NDK tương thích.
# android.ndk_version = 23c

# (str) The Android build tools version to use
# [QUAN TRỌNG] Comment dòng này lại. 
# Chúng ta đã cài đặt build-tools thủ công trong file build.yml.
# android.build_tools_version = 34.0.0

# (str) Path to the Android SDK.
# [QUAN TRỌNG] Comment dòng này lại.
# Môi trường GitHub Actions sẽ tự thiết lập biến môi trường ANDROID_HOME.
# android.sdk_path = /home/runner/android-sdk

# (bool) If True, then skip the clean step. Automatically set to True when rebuilding with the same requirements.
# android.skip_update = False


[buildozer]

# (int) Log level (0 = error, 1 = info, 2 = debug (rất chi tiết))
log_level = 2

# (int) Số lần Buildozer sẽ thử lại nếu một lần tải về thất bại
download_attempts = 3
