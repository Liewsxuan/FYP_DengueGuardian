import os
import time
import urllib3

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.factory import Factory

from kivymd.uix.screen import MDScreen
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import TwoLineAvatarIconListItem

from plyer import camera

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# WINDOW SETTINGS
# ==========================================

Window.softinput_mode = "below_target"

if platform != "android":
    Window.size = (360, 740)

# ==========================================
# ANDROID PERMISSIONS
# ==========================================

if platform == "android":
    from android.permissions import request_permissions, Permission

# ==========================================
# SAFE MAPVIEW IMPORT
# ==========================================

try:
    from kivy_garden.mapview import MapView, MapMarker

    HAS_MAPVIEW = True
    Factory.register("MapView", cls=MapView)

except:
    HAS_MAPVIEW = False

# ==========================================
# BACKEND
# ==========================================

try:
    import backend
except:
    backend = None

# ==========================================
# SCREENS
# ==========================================

class LoginScreen(MDScreen):
    pass

class RegisterScreen(MDScreen):
    pass

class MainMenuScreen(MDScreen):
    pass

class ReportScreen(MDScreen):
    pass

class HistoryScreen(MDScreen):
    pass

class ProfileScreen(MDScreen):
    pass

class MapScreen(MDScreen):
    pass

# ==========================================
# KV DESIGN
# ==========================================

KV = '''

ScreenManager:

    LoginScreen:
    RegisterScreen:
    MainMenuScreen:
    ReportScreen:
    HistoryScreen:
    ProfileScreen:
    MapScreen:


<LoginScreen>:

    name: "login"

    MDBoxLayout:
        orientation: "vertical"
        padding: "20dp"

        MDCard:
            orientation: "vertical"
            padding: "20dp"
            spacing: "15dp"
            radius: [20]
            size_hint: 1, None
            height: "450dp"
            pos_hint: {"center_y": 0.5}

            MDIcon:
                icon: "mosquito"
                halign: "center"
                font_size: "60sp"

            MDLabel:
                text: "SIBU MOSQUITO MONITOR"
                halign: "center"

            MDTextField:
                id: email_field
                hint_text: "Email"

            MDTextField:
                id: password_field
                hint_text: "Password"
                password: True

            MDRaisedButton:
                text: "LOGIN"
                on_release: app.do_login()

            MDTextButton:
                text: "Create Account"
                pos_hint: {"center_x": 0.5}
                on_release: app.switch_to_register()


<RegisterScreen>:

    name: "register"

    MDBoxLayout:
        orientation: "vertical"
        padding: "20dp"

        MDCard:
            orientation: "vertical"
            padding: "20dp"
            spacing: "15dp"
            radius: [20]
            size_hint: 1, None
            height: "500dp"
            pos_hint: {"center_y": 0.5}

            MDLabel:
                text: "REGISTER"
                halign: "center"

            MDTextField:
                id: reg_email
                hint_text: "Email"

            MDTextField:
                id: reg_password
                hint_text: "Password"
                password: True

            MDTextField:
                id: reg_confirm_password
                hint_text: "Confirm Password"
                password: True

            MDRaisedButton:
                text: "REGISTER"
                on_release: app.do_register()

            MDTextButton:
                text: "Back To Login"
                pos_hint: {"center_x": 0.5}
                on_release: app.switch_to_login()


<MainMenuScreen>:

    name: "menu"

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Dashboard"

        MDBoxLayout:
            orientation: "vertical"
            spacing: "15dp"
            padding: "20dp"

            MDRaisedButton:
                text: "Report Case"
                on_release: app.switch_to_report()

            MDRaisedButton:
                text: "Hotspot Map"
                on_release: app.open_all_hotspots()

            MDRaisedButton:
                text: "My History"
                on_release: app.switch_to_history()

            MDRaisedButton:
                text: "My Profile"
                on_release: app.switch_to_profile()

            MDRaisedButton:
                text: "Logout"
                on_release: app.do_logout()


<ReportScreen>:

    name: "report"

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Report Case"
            left_action_items: [["arrow-left", lambda x: app.back_to_menu()]]

        ScrollView:

            MDBoxLayout:
                orientation: "vertical"
                adaptive_height: True
                padding: "20dp"
                spacing: "15dp"

                MDTextField:
                    id: field_location
                    hint_text: "GPS Location"
                    readonly: True

                MDTextField:
                    id: field_description
                    hint_text: "Description"
                    multiline: True

                Image:
                    id: preview_image
                    source: ""
                    size_hint_y: None
                    height: "220dp"
                    allow_stretch: True
                    keep_ratio: True

                MDLabel:
                    id: photo_status
                    text: "No photo selected"
                    halign: "center"

                MDRaisedButton:
                    text: "Get GPS"
                    on_release: app.get_gps_location()

                MDRaisedButton:
                    text: "Open Camera"
                    on_release: app.capture_photo()

                MDRaisedButton:
                    text: "Open Gallery"
                    on_release: app.open_file_manager()

                MDRaisedButton:
                    text: "Submit Report"
                    on_release: app.submit_data()


<HistoryScreen>:

    name: "history"

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "History"
            left_action_items: [["arrow-left", lambda x: app.back_to_menu()]]

        ScrollView:

            MDList:
                id: history_list


<ProfileScreen>:

    name: "profile"

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Profile"
            left_action_items: [["arrow-left", lambda x: app.back_to_menu()]]

        MDBoxLayout:
            orientation: "vertical"
            padding: "20dp"
            spacing: "15dp"

            MDLabel:
                text: app.user_email
                halign: "center"

            MDLabel:
                text: app.user_gender

            MDLabel:
                text: app.user_birthdate

            MDLabel:
                text: app.user_occupation


<MapScreen>:

    name: "map_screen"

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Hotspot Map"
            left_action_items: [["arrow-left", lambda x: app.back_to_menu()]]

        MDBoxLayout:
            id: map_container
'''

# ==========================================
# APP
# ==========================================

class MosquitoApp(MDApp):

    user_email = StringProperty("Guest")
    user_gender = StringProperty("Male")
    user_birthdate = StringProperty("2000-01-01")
    user_occupation = StringProperty("Student")

    selected_image_path = StringProperty("")

    # ==========================================
    # BUILD
    # ==========================================

    def build(self):

        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"

        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True
        )

        return Builder.load_string(KV)

    # ==========================================
    # START
    # ==========================================

    def on_start(self):

        Clock.schedule_once(
            self.ask_permissions,
            1
        )

    # ==========================================
    # PERMISSIONS
    # ==========================================

    def ask_permissions(self, dt):

        if platform == "android":

            request_permissions([
                Permission.CAMERA,
                Permission.ACCESS_FINE_LOCATION,
                Permission.ACCESS_COARSE_LOCATION
            ])

    # ==========================================
    # CAMERA
    # ==========================================

    def capture_photo(self):

        if platform != "android":

            self.show_dialog(
                "Camera",
                "Camera only supported on Android."
            )

            return

        from android.storage import primary_external_storage_path

        timestr = time.strftime("%Y%m%d_%H%M%S")

        folder = os.path.join(
            primary_external_storage_path(),
            "DCIM"
        )

        if not os.path.exists(folder):
            os.makedirs(folder)

        filepath = os.path.join(
            folder,
            f"IMG_{timestr}.jpg"
        )

        def after_capture(path):

            if path and os.path.exists(path):

                self.selected_image_path = path

                screen = self.root.get_screen("report")

                screen.ids.preview_image.source = ""
                screen.ids.preview_image.source = path
                screen.ids.preview_image.reload()

                screen.ids.photo_status.text = f"Captured: {os.path.basename(path)}"

        camera.take_picture(
            filename=filepath,
            on_complete=after_capture
        )

    # ==========================================
    # FILE MANAGER
    # ==========================================

    def open_file_manager(self):

        if platform == "android":

            from android.storage import primary_external_storage_path

            self.file_manager.show(
                primary_external_storage_path()
            )

        else:
            self.file_manager.show("/")

    def select_path(self, path):

        self.exit_manager()

        self.selected_image_path = path

        screen = self.root.get_screen("report")

        screen.ids.preview_image.source = ""
        screen.ids.preview_image.source = path
        screen.ids.preview_image.reload()

        screen.ids.photo_status.text = f"Selected: {os.path.basename(path)}"

    def exit_manager(self, *args):
        self.file_manager.close()

    # ==========================================
    # GPS
    # ==========================================

    def get_gps_location(self):

        self.root.get_screen(
            "report"
        ).ids.field_location.text = "2.2873,111.8305"

    # ==========================================
    # SUBMIT
    # ==========================================

    def submit_data(self):

        if backend is None:

            self.show_dialog(
                "Backend Error",
                "backend.py missing"
            )

            return

        screen = self.root.get_screen("report")

        loc = screen.ids.field_location.text
        desc = screen.ids.field_description.text
        img = self.selected_image_path

        res = backend.submit_report(
            loc,
            desc,
            img
        )

        if res:

            self.show_dialog(
                "Success",
                "Report Uploaded"
            )

            screen.ids.field_description.text = ""
            screen.ids.preview_image.source = ""
            screen.ids.preview_image.reload()

            self.root.current = "menu"

        else:

            self.show_dialog(
                "Error",
                "Upload Failed"
            )

    # ==========================================
    # LOGIN
    # ==========================================

    def do_login(self):

        if backend is None:
            return

        screen = self.root.get_screen("login")

        res, msg = backend.login(
            screen.ids.email_field.text,
            screen.ids.password_field.text
        )

        if res:

            self.user_email = screen.ids.email_field.text

            self.root.current = "menu"

        else:

            self.show_dialog(
                "Login Failed",
                msg
            )

    def do_register(self):

        if backend is None:
            return

        screen = self.root.get_screen("register")

        res, msg = backend.register(
            screen.ids.reg_email.text,
            screen.ids.reg_password.text,
            screen.ids.reg_confirm_password.text
        )

        self.show_dialog("Info", msg)

        if res:
            self.root.current = "login"

    # ==========================================
    # HISTORY
    # ==========================================

    def switch_to_history(self):

        self.root.current = "history"

        self.load_history_data()

    def load_history_data(self):

        h_list = self.root.get_screen(
            "history"
        ).ids.history_list

        h_list.clear_widgets()

        if backend is None:
            return

        records = backend.get_history()

        if records:

            for item in records:

                loc = item.get("location", "N/A")

                date = item.get(
                    "created",
                    ""
                )[:16].replace("T", " ")

                h_list.add_widget(
                    TwoLineAvatarIconListItem(
                        text=f"Location: {loc}",
                        secondary_text=f"Time: {date}"
                    )
                )

    # ==========================================
    # MAP
    # ==========================================

    def open_all_hotspots(self):

        self.root.current = "map_screen"

        Clock.schedule_once(
            self.load_history_markers,
            0.5
        )

    def load_history_markers(self, dt):

        if not HAS_MAPVIEW:
            return

        container = self.root.get_screen(
            "map_screen"
        ).ids.map_container

        container.clear_widgets()

        mview = MapView(
            zoom=10,
            lat=2.287,
            lon=111.830
        )

        if backend:

            records = backend.get_history()

            if records:

                for item in records:

                    try:

                        loc_str = item.get(
                            "location",
                            ""
                        )

                        lat, lon = map(
                            float,
                            loc_str.split(",")
                        )

                        marker = MapMarker(
                            lat=lat,
                            lon=lon
                        )

                        mview.add_widget(marker)

                    except:
                        pass

        container.add_widget(mview)

    # ==========================================
    # NAVIGATION
    # ==========================================

    def switch_to_report(self):
        self.root.current = "report"

    def switch_to_profile(self):
        self.root.current = "profile"

    def switch_to_register(self):
        self.root.current = "register"

    def switch_to_login(self):
        self.root.current = "login"

    def back_to_menu(self):
        self.root.current = "menu"

    def do_logout(self):
        self.root.current = "login"

    # ==========================================
    # DIALOG
    # ==========================================

    def show_dialog(self, title, text):

        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )

        dialog.open()

# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":
    MosquitoApp().run()