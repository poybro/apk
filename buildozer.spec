[app]

# (str) Title of your application
# [CHỈNH SỬA] Đặt tên cho ứng dụng của bạn
title = SOK Ultimate Wallet

# (str) Package name
# [CHỈNH SỬA] Tên gói, viết thường, không dấu cách
package.name = sokwallet

# (str) Package domain (needed for android/ios packaging)
# [CHỈNH SỬA] Tên miền đảo ngược, để phân biệt ứng dụng
package.domain = org.sokchain

# (str) Source code where the main.py live
# [CHỈNH SỬA] Đổi tên file main cho đúng với dự án của chúng ta
source.dir = .
main.py = kivy_app_final_ui.py

# (list) Source files to include (let empty to include all the files)
# [CHỈNH SỬA] Thêm .kv để Kivy có thể đọc, và .pem cho các file ví
source.include_exts = py,png,jpg,kv,atlas,pem,enc,json

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
# [CHỈNH SỬA] Loại trừ các thư mục không cần thiết để file .apk nhẹ hơn
source.exclude_dirs = tests, bin, venv, .buildozer, __pycache__

# (list) List of exclusions using pattern matching
# Do not prefix with './'
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 1.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
# [CHỈNH SỬA] Liệt kê TẤT CẢ các thư viện Python mà dự án cần
requirements = python3,kivy==2.3.1,requests,cryptography,colorama

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = ../../kivy

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (list) Supported orientations
# Valid options are: landscape, portrait, portrait-reverse or landscape-reverse
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY


#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
# [CHỈNH SỬA] Yêu cầu quyền truy cập Internet
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android NDK version to use
# [CHỈNH SỬA] Ghim phiên bản NDK để đảm bảo ổn định
android.ndk_version = 23c

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# [CHỈNH SỬA] Biên dịch cho cả hai kiến trúc ARM phổ biến
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1