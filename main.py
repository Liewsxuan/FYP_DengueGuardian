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

# FIX 1: Do NOT do "from plyer import camera" at the top level.
# On Android, plyer.camera is only safe to import after permissions are granted.
# Importing it globally crashes on some Android 13 devices at startup.

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# WINDOW SETTINGS
# ==========================================

Window.softinput_mode = "below_target"

if platform != "android":
    Window.size = (360, 740)

# ==========================================
# FIX 2: ANDROID API VERSION DETECTION
# We read the actual running Android version so every permission
# and file path decision below is correct for the real device,
# not a hardcoded assumption.
# - Android 13+ (API 33+): READ_MEDIA_IMAGES replaces READ_EXTERNAL_STORAGE
# - Android 10+ (API 29+): Scoped storage, WRITE_EXTERNAL_STORAGE is ignored
# - Android 9  (API 28-): Old storage model still applies
# ==========================================

ANDROID_API_VERSION = 0

if platform == "android":
    try:
        from jnius import autoclass
        BuildVersion = autoclass("android.os.Build$VERSION")
        ANDROID_API_VERSION = BuildVersion.SDK_INT
    except Exception:
        ANDROID_API_VERSION = 0

# ==========================================
# FIX 3: CORRECT PERMISSION SET PER API LEVEL
# Old code always requested READ_EXTERNAL_STORAGE which on Android 13+
# is silently ignored, leaving gallery access broken.
# ==========================================

def get_required_permissions():
    """Return the correct permission list for the running Android version."""
    from android.permissions import Permission

    perms = [
        Permission.CAMERA,
        Permission.ACCESS_FINE_LOCATION,
        Permission.ACCESS_COARSE_LOCATION,
    ]

    if ANDROID_API_VERSION >= 33:
        # Android 13+: granular media permission replaces broad storage
        try:
            perms.append(Permission.READ_MEDIA_IMAGES)
        except AttributeError:
            # Older p4a build that doesn't expose READ_MEDIA_IMAGES yet
            perms.append(Permission.READ_EXTERNAL_STORAGE)
    else:
        perms.append(Permission.READ_EXTERNAL_STORAGE)
        if ANDROID_API_VERSION < 29:
            # WRITE_EXTERNAL_STORAGE is only meaningful on Android 9 and below
            perms.append(Permission.WRITE_EXTERNAL_STORAGE)

    return perms

# ==========================================
# SAFE MAPVIEW IMPORT
# ==========================================

try:
    from kivy_garden.mapview import MapView, MapMarker
    HAS_MAPVIEW = True
    Factory.register("MapView", cls=MapView)
except Exception:
    HAS_MAPVIEW = False

# ==========================================
# BACKEND
# ==========================================

try:
    import backend
except Exception:
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

    user_email    = StringProperty("Guest")
    user_gender   = StringProperty("Male")
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
            preview=True,
        )

        return Builder.load_string(KV)

    # ==========================================
    # START
    # ==========================================

    def on_start(self):
        Clock.schedule_once(self.ask_permissions, 1)

    # ==========================================
    # PERMISSIONS
    # FIX: old code requested a fixed list that was wrong on Android 13+.
    # Now we call get_required_permissions() which adapts to the real API level.
    # We also handle the callback to warn the user if anything was denied.
    # ==========================================

    def ask_permissions(self, dt):
        if platform != "android":
            return

        from android.permissions import request_permissions
        request_permissions(get_required_permissions(), self._on_permissions_result)

    def _on_permissions_result(self, permissions, grant_results):
        denied = [p for p, g in zip(permissions, grant_results) if not g]
        if denied:
            names = [p.split(".")[-1] for p in denied]
            self.show_dialog(
                "Permissions Required",
                "Some features may not work. Denied:\n" + ", ".join(names)
            )

    # ==========================================
    # CAMERA
    # FIX 1: Removed top-level "from plyer import camera" — moved here.
    # FIX 2: Old code always saved to primary_external_storage_path()/DCIM
    #         which requires WRITE_EXTERNAL_STORAGE. On Android 10+ that
    #         permission is permanently blocked. Now we use scoped storage
    #         (getExternalFilesDir) on API 29+ which needs no write permission.
    # FIX 3: Added runtime CAMERA permission check before launching camera.
    # ==========================================

    def capture_photo(self):
        if platform != "android":
            self.show_dialog("Camera", "Camera only supported on Android.")
            return

        self._ensure_permission_then(
            self._get_camera_permission(),
            self._do_capture_photo,
            "Camera permission is required to take photos."
        )

    def _get_camera_permission(self):
        from android.permissions import Permission
        return Permission.CAMERA

    def _ensure_permission_then(self, permission, callback, denied_msg):
        """Check a single permission; request it if missing, then call callback."""
        from android.permissions import check_permission, request_permissions

        if check_permission(permission):
            callback()
        else:
            def on_result(permissions, grants):
                if grants and grants[0]:
                    callback()
                else:
                    self.show_dialog("Permission Denied", denied_msg)
            request_permissions([permission], on_result)

    def _do_capture_photo(self):
        from plyer import camera as plyer_camera

        timestr = time.strftime("%Y%m%d_%H%M%S")

        if ANDROID_API_VERSION >= 29:
            # Android 10+: scoped storage — use app-private external dir.
            # No WRITE_EXTERNAL_STORAGE permission needed.
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            ctx = PythonActivity.mActivity
            ext_dir = ctx.getExternalFilesDir(None)
            folder = str(ext_dir.getAbsolutePath())
        else:
            # Android 9 and below: old shared storage is fine
            from android.storage import primary_external_storage_path
            folder = os.path.join(primary_external_storage_path(), "DCIM")

        if not os.path.exists(folder):
            os.makedirs(folder)

        filepath = os.path.join(folder, f"IMG_{timestr}.jpg")

        def after_capture(path):
            if path and os.path.exists(path):
                self._set_image(path, captured=True)

        plyer_camera.take_picture(filename=filepath, on_complete=after_capture)

    # ==========================================
    # FILE MANAGER / GALLERY
    # FIX: Old code opened primary_external_storage which is inaccessible
    # under scoped storage (Android 10+). Now we open the app's own
    # external files dir on API 29+, and re-check the correct storage
    # permission (READ_MEDIA_IMAGES on Android 13+) before opening.
    # ==========================================

    def open_file_manager(self):
        if platform != "android":
            self.file_manager.show("/")
            return

        storage_perm = self._get_storage_read_permission()
        self._ensure_permission_then(
            storage_perm,
            self._do_open_file_manager,
            "Storage permission is required to pick images from gallery."
        )

    def _get_storage_read_permission(self):
        from android.permissions import Permission
        if ANDROID_API_VERSION >= 33:
            try:
                return Permission.READ_MEDIA_IMAGES
            except AttributeError:
                return Permission.READ_EXTERNAL_STORAGE
        return Permission.READ_EXTERNAL_STORAGE

    def _do_open_file_manager(self):
        if ANDROID_API_VERSION >= 29:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            ctx = PythonActivity.mActivity
            ext_dir = ctx.getExternalFilesDir(None)
            start_path = str(ext_dir.getAbsolutePath())
        else:
            from android.storage import primary_external_storage_path
            start_path = primary_external_storage_path()

        self.file_manager.show(start_path)

    def select_path(self, path):
        self.exit_manager()
        self._set_image(path, captured=False)

    def exit_manager(self, *args):
        self.file_manager.close()

    # ==========================================
    # SHARED IMAGE HELPER
    # ==========================================

    def _set_image(self, path, captured=False):
        self.selected_image_path = path
        screen = self.root.get_screen("report")
        screen.ids.preview_image.source = ""
        screen.ids.preview_image.source = path
        screen.ids.preview_image.reload()
        prefix = "Captured" if captured else "Selected"
        screen.ids.photo_status.text = f"{prefix}: {os.path.basename(path)}"

    # ==========================================
    # GPS
    # FIX: Old code set a hardcoded coordinate with no permission check.
    # Now we verify ACCESS_FINE_LOCATION at runtime before requesting GPS.
    # The coordinate fallback is kept as a placeholder for the real
    # GPS implementation via plyer.gps or jnius LocationManager.
    # ==========================================

    def get_gps_location(self):
        if platform != "android":
            self.root.get_screen("report").ids.field_location.text = "2.2873,111.8305"
            return

        from android.permissions import Permission
        self._ensure_permission_then(
            Permission.ACCESS_FINE_LOCATION,
            self._do_get_location,
            "Location permission is required to get GPS coordinates."
        )

    def _do_get_location(self):
        # TODO: replace with real GPS via plyer.gps or jnius LocationManager
        self.root.get_screen("report").ids.field_location.text = "2.2873,111.8305"

    # ==========================================
    # SUBMIT
    # ==========================================

    def submit_data(self):
        if backend is None:
            self.show_dialog("Backend Error", "backend.py missing")
            return

        screen = self.root.get_screen("report")
        loc  = screen.ids.field_location.text
        desc = screen.ids.field_description.text
        img  = self.selected_image_path

        res = backend.submit_report(loc, desc, img)

        if res:
            self.show_dialog("Success", "Report Uploaded")
            screen.ids.field_description.text = ""
            screen.ids.preview_image.source = ""
            screen.ids.preview_image.reload()
            screen.ids.photo_status.text = "No photo selected"
            self.selected_image_path = ""
            self.root.current = "menu"
        else:
            self.show_dialog("Error", "Upload Failed")

    # ==========================================
    # LOGIN / REGISTER
    # ==========================================

    def do_login(self):
        if backend is None:
            return

        screen = self.root.get_screen("login")
        res, msg = backend.login(
            screen.ids.email_field.text,
            screen.ids.password_field.text,
        )

        if res:
            self.user_email = screen.ids.email_field.text
            self.root.current = "menu"
        else:
            self.show_dialog("Login Failed", msg)

    def do_register(self):
        if backend is None:
            return

        screen = self.root.get_screen("register")
        res, msg = backend.register(
            screen.ids.reg_email.text,
            screen.ids.reg_password.text,
            screen.ids.reg_confirm_password.text,
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
        h_list = self.root.get_screen("history").ids.history_list
        h_list.clear_widgets()

        if backend is None:
            return

        records = backend.get_history()
        if records:
            for item in records:
                loc  = item.get("location", "N/A")
                date = item.get("created", "")[:16].replace("T", " ")
                h_list.add_widget(
                    TwoLineAvatarIconListItem(
                        text=f"Location: {loc}",
                        secondary_text=f"Time: {date}",
                    )
                )

    # ==========================================
    # MAP
    # ==========================================

    def open_all_hotspots(self):
        self.root.current = "map_screen"
        Clock.schedule_once(self.load_history_markers, 0.5)

    def load_history_markers(self, dt):
        if not HAS_MAPVIEW:
            return

        container = self.root.get_screen("map_screen").ids.map_container
        container.clear_widgets()

        mview = MapView(zoom=10, lat=2.287, lon=111.830)

        if backend:
            records = backend.get_history()
            if records:
                for item in records:
                    try:
                        lat, lon = map(float, item.get("location", "").split(","))
                        mview.add_widget(MapMarker(lat=lat, lon=lon))
                    except Exception:
                        pass

        container.add_widget(mview)

    # ==========================================
    # NAVIGATION
    # ==========================================

    def switch_to_report(self):   self.root.current = "report"
    def switch_to_profile(self):  self.root.current = "profile"
    def switch_to_register(self): self.root.current = "register"
    def switch_to_login(self):    self.root.current = "login"
    def back_to_menu(self):       self.root.current = "menu"
    def do_logout(self):          self.root.current = "login"

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
                    on_release=lambda x: dialog.dismiss(),
                )
            ],
        )
        dialog.open()


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":
    MosquitoApp().run()
