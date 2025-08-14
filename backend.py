# backend.py (Upgraded for platform safety)
# -*- coding: utf-8 -*-

import os, sys, requests, json, time, logging, random, socket, threading, getpass, base64
from typing import List, Dict, Any, Optional
from decimal import Decimal, getcontext
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

# --- [THÊM ĐỂ CHẨN ĐOÁN] ---
# Cấu hình logging để xem lỗi chi tiết trên console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Thêm đường dẫn dự án để có thể import từ 'sok'
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path: sys.path.insert(0, project_root)
from sok.wallet import Wallet
from sok.transaction import Transaction

# --- CẤU HÌNH ---
DEFAULT_WALLET_FILE = "my_smart_wallet.enc"
# ... (các hằng số khác giữ nguyên)

getcontext().prec = 18

class BackendLogic:
    def __init__(self, app_data_dir: str, log_callback=None):
        self.app_data_dir = app_data_dir
        
        # --- [SỬA LỖI QUAN TRỌNG] ---
        # Đảm bảo thư mục dữ liệu ứng dụng tồn tại trước khi làm bất cứ điều gì khác.
        try:
            os.makedirs(self.app_data_dir, exist_ok=True)
            logging.info(f"Thư mục dữ liệu được đảm bảo tồn tại tại: {self.app_data_dir}")
        except Exception as e:
            # Lỗi này rất nghiêm trọng, có thể do quyền truy cập.
            logging.error(f"KHÔNG THỂ TẠO THƯ MỤC DỮ LIỆU! Lỗi: {e}", exc_info=True)
            
        self.wallet_file_path = os.path.join(self.app_data_dir, DEFAULT_WALLET_FILE)
        logging.info(f"Đường dẫn file ví được thiết lập là: {self.wallet_file_path}")
        
        self.wallet: Optional[Wallet] = None
        self.server_url: Optional[str] = None
        self.treasury_address: Optional[str] = None
        self.price_info: Dict[str, Any] = {}
        
        # ... (các thuộc tính miner giữ nguyên)
        self.miner_status = {"state": "STOPPED", "current_node": "None", "last_log": "Thợ mỏ chưa được khởi động."}
        self.miner_is_active = threading.Event()
        self.miner_thread: Optional[threading.Thread] = None
        self.heartbeat_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.log_callback = log_callback or (lambda state, msg: logging.info(f"[{state}] {msg}"))


    def _derive_key(self, password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
        return base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))

    def _encrypt_pem(self, pem_data: str, password: str) -> bytes:
        salt = os.urandom(16); key = self._derive_key(password, salt)
        return salt + Fernet(key).encrypt(pem_data.encode('utf-8'))

    def _decrypt_pem(self, encrypted_data: bytes, password: str) -> Optional[str]:
        try:
            salt, token = encrypted_data[:16], encrypted_data[16:]
            key = self._derive_key(password, salt)
            return Fernet(key).decrypt(token).decode('utf-8')
        except (InvalidToken, IndexError, TypeError): return None
        
    def load_wallet_from_file(self, password: str) -> (bool, str):
        logging.info(f"Bắt đầu tải ví từ: {self.wallet_file_path}")
        if not os.path.exists(self.wallet_file_path): 
            logging.warning("File ví không tồn tại.")
            return False, f"File ví '{self.wallet_file_path}' không tồn tại."
        
        try:
            with open(self.wallet_file_path, 'rb') as f: 
                encrypted_data = f.read()
            
            pem_data = self._decrypt_pem(encrypted_data, password)

            if pem_data:
                self.wallet = Wallet(private_key_pem=pem_data)
                logging.info("Giải mã và tải ví thành công.")
                return True, "Giải mã và tải ví thành công."
            else: 
                logging.warning("Mật khẩu sai hoặc file ví bị lỗi.")
                return False, "Mật khẩu sai hoặc file ví bị lỗi."
        except Exception as e:
            logging.error(f"Lỗi không xác định khi tải ví: {e}", exc_info=True)
            return False, "Lỗi không xác định khi tải ví."

    def create_new_wallet(self, password: str) -> (bool, str):
        logging.info("Bắt đầu quy trình tạo ví mới.")
        try:
            self.wallet = Wallet()
            pem_data = self.wallet.get_private_key_pem()
            logging.info("Đã tạo cặp khóa PEM.")

            if not pem_data or not isinstance(pem_data, str):
                error_msg = "Không thể lấy private key từ sok.wallet."
                logging.error(error_msg)
                return False, error_msg

            encrypted_data = self._encrypt_pem(pem_data, password)
            logging.info("Đã mã hóa dữ liệu ví thành công.")
            
            with open(self.wallet_file_path, 'wb') as f: 
                f.write(encrypted_data)
                
            logging.info(f"VÍ ĐÃ ĐƯỢC GHI THÀNH CÔNG VÀO: {self.wallet_file_path}")
            return True, f"Đã tạo và mã hóa ví, lưu tại '{self.wallet_file_path}'."
            
        except Exception as e: 
            logging.error(f"LỖI NGHIÊM TRỌNG KHI TẠO VÍ: {e}", exc_info=True)
            return False, f"Lỗi nghiêm trọng khi tạo ví: {e}"

    # --- CÁC HÀM KHÁC GIỮ NGUYÊN ---
    def connect_to_server(self, server_ip: str) -> (bool, str):
        # ... (giữ nguyên)
        self.server_url = f"http://{server_ip}:9000"
        try:
            response = requests.get(f"{self.server_url}/ping", timeout=3)
            if response.status_code == 200:
                payment_data = self._make_api_request('GET', '/api/v1/payment_info')
                if payment_data:
                    self.treasury_address = payment_data.get('treasury_address')
                    self.price_info = payment_data
                    return True, "Kết nối và tải cấu hình thành công."
                return False, "Kết nối được nhưng không thể tải cấu hình."
            return False, f"Server phản hồi lỗi: {response.status_code}"
        except requests.RequestException as e:
            return False, f"Không thể kết nối đến server: {e}"
            
    def _make_api_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        # ... (giữ nguyên)
        if not self.server_url: return None
        url = f"{self.server_url}{endpoint}"; kwargs.setdefault('timeout', 15)
        try:
            response = requests.request(method.upper(), url, **kwargs)
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.RequestException, json.JSONDecodeError):
            return None
    
    def refresh_dashboard(self) -> Optional[Dict]:
        # ... (giữ nguyên)
        profile_data = self._make_api_request('GET', f"/api/v1/user_profile/{self.wallet.get_address()}")
        stats_data = self._make_api_request('GET', '/api/v1/dashboard_stats')
        if profile_data and stats_data:
            return {"profile": profile_data, "stats": stats_data}
        return None
        
    def list_open_p2p_orders(self) -> Optional[List[Dict]]:
        # ... (giữ nguyên)
        return self._make_api_request('GET', '/api/v1/p2p/orders/list')
        
    def list_my_p2p_orders(self) -> Optional[List[Dict]]:
        # ... (giữ nguyên)
        return self._make_api_request('GET', f"/api/v1/p2p/my_orders?address={self.wallet.get_address()}")

    def send_transaction(self, recipient: str, amount_str: str) -> Optional[Dict]:
        # ... (giữ nguyên)
        return self._make_api_request('POST', '/api/direct_fund', json={"private_key_pem": self.wallet.get_private_key_pem(), "recipient_address": recipient, "amount": amount_str})

    def start_miner(self):
        # ... (giữ nguyên)
        if not self.miner_is_active.is_set():
            self.miner_is_active.set()
            if not self.miner_thread or not self.miner_thread.is_alive():
                self.stop_event.clear()
                self.miner_thread = threading.Thread(target=self._miner_main_loop, daemon=True, name="MinerThread")
                self.miner_thread.start()
            if not self.heartbeat_thread or not self.heartbeat_thread.is_alive():
                self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True, name="HeartbeatThread")
                self.heartbeat_thread.start()
            return True, "Thợ mỏ đã được kích hoạt."
        return False, "Thợ mỏ đã đang chạy."

    def stop_miner(self):
        # ... (giữ nguyên)
        if self.miner_is_active.is_set():
            self.miner_is_active.clear()
            self.log_callback("PAUSED", "Đã nhận lệnh tạm dừng từ người dùng.")
            return True, "Đã gửi lệnh tạm dừng."
        return False, "Thợ mỏ đã dừng từ trước."

    def shutdown(self):
        # ... (giữ nguyên)
        self.stop_event.set()
        
    def _miner_log(self, state: str, message: str):
        # ... (giữ nguyên)
        self.miner_status.update({"state": state, "last_log": message})
        self.log_callback(state, message)
        
    def _miner_load_all_known_nodes(self) -> List[str]:
        # ... (giữ nguyên)
        nodes = set()
        for file in ["live_network_nodes.json", "bootstrap_config.json"]:
            if os.path.exists(file):
                try:
                    with open(file, 'r', encoding='utf-8') as f: data = json.load(f)
                    if "active_nodes" in data: nodes.update(data["active_nodes"])
                    if "trusted_bootstrap_peers" in data: nodes.update([p.get('last_known_address') for p in data["trusted_bootstrap_peers"].values()])
                except Exception: pass
        return list(filter(None, nodes))

    def _miner_find_best_node(self) -> Optional[Dict]:
        # ... (giữ nguyên)
        known_nodes = self._miner_load_all_known_nodes()
        if not known_nodes: self._miner_log("FAILED", "Không có node nào trong file config."); return None
        healthy_nodes = []
        threads = []
        def check_node(url, result_list):
            try:
                stats = requests.get(f'{url}/chain/stats', timeout=4).json()
                result_list.append({"url": url, "height": stats.get('block_height', -1)})
            except: pass
        for url in known_nodes:
            thread = threading.Thread(target=check_node, args=(url, healthy_nodes)); threads.append(thread); thread.start()
        for thread in threads: thread.join(4)
        if not healthy_nodes: self._miner_log("FAILED", "Không tìm thấy node nào hoạt động."); return None
        max_height = max(n['height'] for n in healthy_nodes)
        top_tier = [n for n in healthy_nodes if n['height'] >= max_height - 1]
        return random.choice(top_tier) if top_tier else None
        
    def _miner_main_loop(self):
        # ... (giữ nguyên)
        last_node_re_evaluation_time = 0
        while not self.stop_event.is_set():
            if not self.miner_is_active.is_set():
                if self.miner_status['state'] != "PAUSED": self._miner_log("PAUSED", "Chờ lệnh...")
                self.stop_event.wait(5)
                continue
            try:
                node_is_stale = (time.time() - last_node_re_evaluation_time) > 300
                if not self.miner_status.get('current_node') or node_is_stale:
                    self._miner_log("SEARCHING", "Bắt đầu quét mạng lưới...")
                    target_node_info = self._miner_find_best_node()
                    if not target_node_info:
                        self._miner_log("FAILED", f"Không tìm thấy node. Thử lại sau 30s.")
                        self.stop_event.wait(30)
                        continue
                    self.miner_status['current_node'] = target_node_info['url']
                    last_node_re_evaluation_time = time.time()
                    self._miner_log("NODE_SWITCHED", f"Đã chọn: {self.miner_status['current_node']} (Block: {target_node_info.get('height')})")
                node_url = self.miner_status['current_node']
                self._miner_log("MINING", f"Gửi yêu cầu khai thác...")
                response = requests.get(f"{node_url}/mine", params={'miner_address': self.wallet.get_address()}, timeout=130)
                if response.status_code == 200:
                    self._miner_log("SUCCESS", f"Đã đào Khối #{response.json().get('block', {}).get('index', '?')}.")
                    self.stop_event.wait(120)
                elif response.status_code == 409:
                    pause_duration = random.uniform(3, 8)
                    self._miner_log("CONFLICT", f"Cạnh tranh! Tạm dừng {pause_duration:.1f}s.")
                    self.miner_status['current_node'] = None; self.stop_event.wait(pause_duration)
                else:
                    self._miner_log("FAILED", f"Node từ chối: {response.status_code}")
                    self.miner_status['current_node'] = None; self.stop_event.wait(5)
            except requests.exceptions.ReadTimeout:
                pause_duration = random.uniform(3, 8)
                self._miner_log("TIMEOUT", f"Hết thời gian chờ. Tạm dừng {pause_duration:.1f}s.")
                self.miner_status['current_node'] = None; self.stop_event.wait(pause_duration)
            except requests.exceptions.RequestException:
                self._miner_log("CONNECTION_ERROR", f"Mất kết nối tới node.")
                self.miner_status['current_node'] = None; self.stop_event.wait(5)
            except Exception as e:
                self._miner_log("CRITICAL", f"Lỗi nghiêm trọng: {e}")
                self.miner_status['current_node'] = None; self.stop_event.wait(60)

    def _heartbeat_loop(self):
        # ... (giữ nguyên)
        while not self.stop_event.is_set():
            self.stop_event.wait(90)
            if self.miner_is_active.is_set():
                try: requests.post(f"{self.server_url}/heartbeat", json={"worker_address": self.wallet.get_address(), "type": "miner", "status": self.miner_status['state']}, timeout=5)
                except: pass
