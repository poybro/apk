# sok_kivy_ultimate.py (Ultimate - 100% Python, không .kv, platform-safe)
# -*- coding: utf-8 -*-

import os
import threading
import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, NoTransition
from kivy.uix.modalview import ModalView
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse

from backend import BackendLogic, Wallet

# --- LỚP NỀN VÀ WIDGET TÙY CHỈNH (Giữ nguyên) ---
class GalaxyBackground(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs); self.stars = []
        with self.canvas.before: Color(0.05, 0.0, 0.1, 1); self.rect = Rectangle(size=self.size, pos=self.pos)
        self.generate_stars(70); Clock.schedule_interval(self.update_stars, 1.0 / 30.0)
        self.bind(size=self._update_and_regenerate, pos=self._update_rect)
    def _update_rect(self, i, v): self.rect.pos = i.pos
    def _update_and_regenerate(self, i, v):
        self.rect.size = i.size; self.canvas.before.clear()
        with self.canvas.before: Color(0.05, 0.0, 0.1, 1); self.rect = Rectangle(size=self.size, pos=self.pos)
        self.generate_stars(70)
    def generate_stars(self, count):
        self.stars = [];
        with self.canvas.before:
            for _ in range(count):
                star_size=random.uniform(0.5,2); speed=(0.5+star_size)*0.2; color=Color(hsv=(random.random(),0.05,1));
                instr=Ellipse(pos=(random.uniform(0,self.width),random.uniform(0,self.height)),size=(star_size,star_size))
                self.stars.append({'instr': instr, 'speed': speed}); self.canvas.before.add(color); self.canvas.before.add(instr)
    def update_stars(self, dt):
        for star in self.stars:
            star['instr'].pos = (star['instr'].pos[0], star['instr'].pos[1] - star['speed'] * dt * 50)
            if star['instr'].pos[1] < -5: star['instr'].pos = (random.uniform(0, self.width), self.height + 5)

class Card(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs); self.orientation='vertical'; self.size_hint=(1,None); self.padding=20; self.spacing=10
        with self.canvas.before: Color(1,1,1,0.9); self.rect=RoundedRectangle(size=self.size,pos=self.pos,radius=[15])
        self.bind(pos=self.update_rect, size=self.update_rect)
    def update_rect(self, *args): self.rect.pos=self.pos; self.rect.size=self.size

class AppButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs); self.background_normal=''; self.background_color=get_color_from_hex("#6f42c1"); self.size_hint_y=None; self.height=50

# --- CÁC MÀN HÌNH ---
class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.backend = self.app.backend

class DashboardScreen(BaseScreen):
    # ... (giữ nguyên không đổi)
    def __init__(self, **kwargs):
        super().__init__(**kwargs); layout=BoxLayout(orientation='vertical', padding=20, spacing=20)
        account_card=Card(height=180); self.balance_label=Label(text="Số dư: Đang tải...", font_size='22sp', bold=True, color=(0,0,0,1))
        address_scroll=ScrollView(size_hint_y=None, height=60); self.address_input=TextInput(text="Đang tải ví...", readonly=True, multiline=False, background_color=(.9,.9,.9,1), foreground_color=(0,0,0,1))
        address_scroll.add_widget(self.address_input); account_card.add_widget(Label(text="Tài khoản", font_size='18sp', color=get_color_from_hex("#6f42c1"))); account_card.add_widget(self.balance_label); account_card.add_widget(address_scroll)
        network_card=Card(height=120); self.height_label=Label(text="Khối: ...", font_size='16sp', color=(0,0,0,1)); self.status_label=Label(text="Mạng: ...", font_size='16sp', color=(0,0,0,1))
        network_card.add_widget(Label(text="Trạng thái", font_size='18sp', color=get_color_from_hex("#6f42c1"))); network_card.add_widget(self.height_label); network_card.add_widget(self.status_label)
        refresh_button=AppButton(text="Làm mới"); refresh_button.bind(on_press=self.refresh_data)
        layout.add_widget(account_card); layout.add_widget(network_card); layout.add_widget(BoxLayout()); layout.add_widget(refresh_button)
        self.add_widget(layout)
    def on_enter(self, *args):
        if self.backend and self.backend.wallet: self.address_input.text = self.backend.wallet.get_address(); self.refresh_data()
    def refresh_data(self, *args): threading.Thread(target=self._update_ui_thread, daemon=True).start()
    def _update_ui_thread(self): data = self.backend.refresh_dashboard(); (data and Clock.schedule_once(lambda dt: self._update_labels(data)))
    def _update_labels(self, data):
        profile=data.get('profile',{}); stats=data.get('stats',{})
        self.balance_label.text = f"Số dư: {float(profile.get('sok_balance',0)):.8f} SOK"; self.status_label.text = f"Mạng: {stats.get('status','N/A')}"; self.height_label.text = f"Khối: {stats.get('blockchain_height','N/A')}"

class SendScreen(BaseScreen):
    # ... (giữ nguyên không đổi)
    def __init__(self, **kwargs):
        super().__init__(**kwargs); layout=BoxLayout(orientation='vertical', padding=20, spacing=15); card=Card(size_hint_y=None, height=250)
        card.add_widget(Label(text="Gửi SOK", font_size='24sp', bold=True, color=get_color_from_hex("#2ecc71")))
        self.recipient_input=TextInput(hint_text="Địa chỉ người nhận", multiline=False, size_hint_y=None, height=44)
        self.amount_input=TextInput(hint_text="Số lượng SOK", multiline=False, input_filter='float', size_hint_y=None, height=44)
        send_button=AppButton(text="Gửi", background_color=get_color_from_hex("#2ecc71")); send_button.bind(on_press=self.send_sok)
        card.add_widget(self.recipient_input); card.add_widget(self.amount_input); card.add_widget(send_button); layout.add_widget(card); layout.add_widget(BoxLayout()); self.add_widget(layout)
    def send_sok(self, instance):
        recipient=self.recipient_input.text.strip(); amount=self.amount_input.text.strip();
        if not recipient or not amount: self.app.show_popup("Lỗi", "Vui lòng nhập đủ thông tin."); return
        self.app.show_popup("Thông báo", "Đang gửi giao dịch..."); threading.Thread(target=self._send_thread, args=(recipient, amount), daemon=True).start()
    def _send_thread(self, recipient, amount):
        result=self.backend.send_transaction(recipient, amount); msg=result.get('message') if result and result.get('message') else "Gửi thất bại."; title="Thành công" if result else "Thất bại"
        Clock.schedule_once(lambda dt: self.app.show_popup(title, msg))

class WebsiteScreen(BaseScreen):
    def __init__(self, **kwargs): super().__init__(**kwargs); self.add_widget(Label(text="Màn hình Website (Sắp ra mắt)"))
    
class MinerScreen(BaseScreen):
    # ... (giữ nguyên không đổi)
    def __init__(self, **kwargs):
        super().__init__(**kwargs); layout=BoxLayout(orientation='vertical', padding=20, spacing=15); card=Card(size_hint_y=None, height=200); card.add_widget(Label(text="Thợ Mỏ", font_size='24sp', bold=True, color=get_color_from_hex("#9b59b6")))
        self.state_label=Label(text="Trạng thái: STOPPED", font_size='18sp', color=(0,0,0,1)); self.log_label=Label(text="Log: ...", font_size='14sp', color=(.3,.3,.3,1), halign='center')
        card.add_widget(self.state_label); card.add_widget(self.log_label);
        start_button=AppButton(text="Bắt đầu", background_color=get_color_from_hex("#27ae60")); stop_button=AppButton(text="Tạm dừng", background_color=get_color_from_hex("#c0392b"))
        start_button.bind(on_press=self.start_mining); stop_button.bind(on_press=self.stop_mining)
        layout.add_widget(card); layout.add_widget(BoxLayout()); layout.add_widget(start_button); layout.add_widget(stop_button); self.add_widget(layout)
    def on_enter(self, *args):
        if self.backend: self.backend.log_callback = self.update_miner_ui
    def start_mining(self, instance):
        if self.backend: self.backend.start_miner()
    def stop_mining(self, instance):
        if self.backend: self.backend.stop_miner()
    def update_miner_ui(self, state, message): Clock.schedule_once(lambda dt: self._update_labels(state, message))
    def _update_labels(self, state, message): self.state_label.text=f"Trạng thái: {state}"; self.log_label.text=f"Log: {message}"

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical'); self.sm = ScreenManager(transition=SlideTransition());
        self.sm.add_widget(DashboardScreen(name='dashboard')); self.sm.add_widget(SendScreen(name='send')); self.sm.add_widget(WebsiteScreen(name='website')); self.sm.add_widget(MinerScreen(name='miner'));
        nav_layout = GridLayout(cols=4, size_hint_y=None, height=60)
        buttons = {"Bảng tin": "dashboard", "Gửi SOK": "send", "Website": "website", "Thợ mỏ": "miner"}
        for text, screen_name in buttons.items():
            btn = Button(text=text); btn.bind(on_press=lambda i, s=screen_name: setattr(self.sm, 'current', s)); nav_layout.add_widget(btn)
        main_layout.add_widget(self.sm); main_layout.add_widget(nav_layout); self.add_widget(main_layout)

# --- [SỬA LỖI TRIỆT ĐỂ TẠI ĐÂY] ---
class ManagerScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Bố cục chính của màn hình này, sẽ chứa 1 trong 2 layout kia.
        self.main_container = FloatLayout()
        self.add_widget(self.main_container)

        # ---- Định nghĩa layout Tạo ví ----
        self.create_layout = BoxLayout(
            orientation='vertical', size_hint=(.9, None),
            pos_hint={'center_x': .5, 'center_y': .5}, height=280
        )
        card_create = Card()
        card_create.add_widget(Label(text="Chào mừng!", font_size='24sp', bold=True, color=(0,0,0,1)))
        self.new_password_input = TextInput(hint_text="Nhập mật khẩu mới", password=True, size_hint_y=None, height=44)
        self.confirm_password_input = TextInput(hint_text="Xác nhận mật khẩu", password=True, size_hint_y=None, height=44)
        create_button = AppButton(text="Tạo Ví"); create_button.bind(on_press=self.create_wallet)
        card_create.add_widget(self.new_password_input)
        card_create.add_widget(self.confirm_password_input)
        card_create.add_widget(create_button)
        self.create_layout.add_widget(card_create)
        
        # ---- Định nghĩa layout Đăng nhập ----
        self.login_layout = BoxLayout(
            orientation='vertical', size_hint=(.9, None),
            pos_hint={'center_x': .5, 'center_y': .5}, height=200
        )
        card_login = Card()
        card_login.add_widget(Label(text="Mở khóa Ví", font_size='24sp', bold=True, color=(0,0,0,1)))
        self.password_input = TextInput(hint_text="Nhập mật khẩu", password=True, size_hint_y=None, height=44)
        login_button = AppButton(text="Mở khóa"); login_button.bind(on_press=self.login)
        card_login.add_widget(self.password_input)
        card_login.add_widget(login_button)
        self.login_layout.add_widget(card_login)
    
    def on_enter(self, *args):
        # [SỬA LỖI] Xóa sạch mọi thứ đang có và chỉ thêm vào cái cần thiết.
        self.main_container.clear_widgets() 
        
        if os.path.exists(self.backend.wallet_file_path):
            # Nếu có ví, chỉ thêm layout đăng nhập vào màn hình.
            self.main_container.add_widget(self.login_layout)
        else:
            # Nếu chưa có ví, chỉ thêm layout tạo ví vào màn hình.
            self.main_container.add_widget(self.create_layout)
            
    def create_wallet(self, instance):
        password = self.new_password_input.text
        confirm_password = self.confirm_password_input.text
        if not password or password != confirm_password: 
            self.app.show_popup("Lỗi", "Mật khẩu không khớp hoặc bị bỏ trống.")
            return
        
        success, msg = self.backend.create_new_wallet(password)
        if success: 
            self.app.show_backup_popup(self.backend.wallet.get_private_key_pem())
        else: 
            self.app.show_popup("Lỗi tạo ví", msg)
            
    def login(self, instance):
        password = self.password_input.text
        if not password:
            self.app.show_popup("Lỗi", "Vui lòng nhập mật khẩu.")
            return
        
        success, msg = self.backend.load_wallet_from_file(password)
        if success: 
            self.manager.current = 'main'
        else: 
            self.app.show_popup("Lỗi đăng nhập", msg)

class SokKivyApp(App):
    # ... (giữ nguyên không đổi)
    def build(self):
        self.backend = BackendLogic(app_data_dir=self.user_data_dir)
        
        connected, msg = self.backend.connect_to_server("127.0.0.1")
        if not connected:
            Clock.schedule_once(lambda dt: self.show_popup("Lỗi kết nối", f"{msg}\nVui lòng kiểm tra server và khởi động lại ứng dụng."))
            
        root = FloatLayout()
        root.add_widget(GalaxyBackground())
        
        self.sm = ScreenManager(transition=NoTransition())
        manager_screen = ManagerScreen(name='manager')
        main_screen = MainScreen(name='main')
        self.sm.add_widget(manager_screen)
        self.sm.add_widget(main_screen)
        
        root.add_widget(self.sm)
        return root
        
    def show_popup(self, title, message):
        popup_layout=BoxLayout(orientation='vertical',padding=10,spacing=10); 
        content_label = Label(text=message, size_hint_y=1, text_size=(self.root.width * 0.7, None))
        content_label.bind(texture_size=content_label.setter('size'))
        
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(content_label)

        close_button=Button(text="Đóng",size_hint_y=None, height=50); 
        
        popup_content = BoxLayout(orientation='vertical', spacing=5, padding=5)
        popup_content.add_widget(Label(text=title, font_size='18sp', bold=True, size_hint_y=None, height=40))
        popup_content.add_widget(scroll_view)
        popup_content.add_widget(close_button)

        popup=ModalView(size_hint=(0.8,0.5)); 
        popup.add_widget(popup_content);
        close_button.bind(on_press=popup.dismiss); 
        popup.open()
        
    def show_backup_popup(self, private_key):
        def switch_screen(*args):
            self.sm.current = 'main'
            
        popup_layout=BoxLayout(orientation='vertical',padding=10,spacing=10)
        popup_layout.add_widget(Label(text="SAO LƯU KEY NÀY CẨN THẬN!", bold=True, size_hint_y=None, height=40))
        scroll = ScrollView(size_hint_y=0.8)
        scroll.add_widget(TextInput(text=private_key, readonly=True, size_hint_y=None, height=250))
        popup_layout.add_widget(scroll)
        close_button=Button(text="Tôi đã sao lưu, chuyển đến ví",size_hint_y=None, height=50)
        popup_layout.add_widget(close_button)
        
        popup=ModalView(size_hint=(0.9,0.7), auto_dismiss=False)
        popup.add_widget(popup_layout)
        
        close_button.bind(on_press=popup.dismiss)
        popup.bind(on_dismiss=switch_screen)
        popup.open()
        
    def on_stop(self):
        if hasattr(self, 'backend'): 
            self.backend.shutdown()

if __name__ == '__main__':
    SokKivyApp().run()
