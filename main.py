#pylint:disable=W0611
import json
import os
import re
import functools
from kivymd.uix.dialog import MDDialogContentContainer
from datetime import datetime, timedelta, date
from kivy.lang import Builder
from kivy.factory import Factory
from kivymd.utils.set_bars_colors import set_bars_colors
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.list import (
    MDList, MDListItem, MDListItemSupportingText,
    MDListItemHeadlineText, MDListItemTrailingIcon, MDListItemTertiaryText
)
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
)
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.scrollview import MDScrollView
from kivy.clock import Clock
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import NumericProperty, StringProperty, DictProperty
from kivy.graphics import PushMatrix, PopMatrix, Rotate, Color, Line
from kivy.animation import Animation
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.textfield import MDTextField
from kivymd.uix.appbar import MDTopAppBar, MDTopAppBarLeadingButtonContainer, MDTopAppBarTrailingButtonContainer, MDActionTopAppBarButton
from kivymd.uix.pickers import MDDockedDatePicker
from kivymd.uix.selectioncontrol import MDSwitch
from kivy.utils import get_color_from_hex
from kivy.core.clipboard import Clipboard
from collections import Counter, defaultdict

try:
    from plyer import share
except ImportError:
    class DummyShare:
        def share(self, **kwargs):
            # Placeholder pre desktop testovanie, ak plyer nie je k dispozícii
            print("Plyer 'share' nie je k dispozícii na tejto platforme.")
    share = DummyShare()

# ====================================================================================
# HELPER FUNKCIE PRE BEZPEČNÉ CESTY (Android vyžaduje user_data_dir pre zápis)
# ====================================================================================

def get_data_path(filename):
    """Vráti celú cestu k súboru v adresári dát aplikácie."""
    from kivy.app import App
    try:
        app_instance = App.get_running_app()
        if app_instance:
            return os.path.join(app_instance.user_data_dir, filename)
    except Exception:
        # Fallback pre prípady, kedy App ešte nie je spustená (napr. pri prvom load_settings)
        pass
    # Použijeme os.getcwd() ako núdzový fallback, hoci v Androide by mal fungovať user_data_dir
    return os.path.join(os.getcwd(), filename)


# ====================================================================================
# BEZPEČNÉ FUNKCIE PRE SÚBOROVÉ I/O (upravené pre spracovanie FileNotFoundError)
# ====================================================================================

# Predpokladaná štruktúra Vašich funkcií - kritická úprava je try/except
def load_settings():
    path = get_data_path('settings.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Vráti predvolené hodnoty pre prvé spustenie alebo poškodený súbor
        print(f"DEBUG: Súbor {path} nenájdený alebo poškodený. Používam default.")
        return {'theme_style': 'Light', 'primary_color': 'Blue', 'dark_mode': False}

def save_settings(settings):
    path = get_data_path('settings.json')
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(settings, f)
    except Exception as e:
        print(f"ERROR: Zlyhalo uloženie settings.json: {e}")

def load_poruchy():
    path = get_data_path('poruchy.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Vráti prázdny slovník pre prvé spustenie
        print(f"DEBUG: Súbor {path} nenájdený alebo poškodený. Používam default.")
        return {}

def save_poruchy(data):
    path = get_data_path('poruchy.json')
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"ERROR: Zlyhalo uloženie poruchy.json: {e}")

def load_jph():
    path = get_data_path('jph.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Vráti prázdny slovník pre prvé spustenie
        print(f"DEBUG: Súbor {path} nenájdený alebo poškodený. Používam default.")
        return {}

def save_jph(data):
    path = get_data_path('jph.json')
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"ERROR: Zlyhalo uloženie jph.json: {e}")


# ====================================================================================
# KLASY - PREDPOKLADANÉ DEFINÍCIE TRIED (Aby bol kód spustiteľný)
# ====================================================================================

# Vytvorenie základných tried, ktoré boli referované v build()
class HlavnaScreen(MDScreen):
    def update_poruchy_list(self):
        # Dummy implementácia, aby kód fungoval
        pass
    def clear_dialog_textfields(self):
        pass
    
class SettingsScreen(MDScreen):
    pass

class ReportScreen(MDScreen):
    pass

class ShareScreen(MDScreen):
    pass

# Triedy, ktoré boli referované v metódach (napr. v jph_menu)
class MyExpansionPanel(MDCard):
    panel_key = StringProperty("")
    
class MyListItem(MDListItem):
    pass

class AppDialogContent(MDBoxLayout):
    pass

# ====================================================================================
# HLAVNÁ TRIEDA APLIKÁCIE S DEBUG BLOKOM V build()
# ====================================================================================

class HlaseniaApp(MDApp):
    # Definícia potrebných Property (predpokladané)
    current_date = StringProperty(date.today().strftime('%d.%m.%Y'))
    selected_date = StringProperty(date.today().strftime('%d.%m.%Y'))
    dialog = None # Pre MDDialog

    def jph_menu(self, panel: MyExpansionPanel):
        # Dummy implementácia, aby bol kód kompletný
        menu_items = [
            {"text": str(i), "on_release": lambda x=str(i): self.save_jph_from_menu(panel, x)}
            for i in range(66)
        ]
        caller = panel # Predpokladám, že panel má ids.jph_button, ak nie, zmeňte
        self.jph_menu = MDDropdownMenu(
            caller=caller, items=menu_items, width=dp(100), max_height=dp(400), radius=[20, 7, 20, 7]
        )
        Clock.schedule_once(lambda dt: self.jph_menu.open(), 0.01)

    def save_jph_from_menu(self, panel: MyExpansionPanel, jph_str: str):
        if hasattr(self, 'jph_menu'):
            self.jph_menu.dismiss()

        panel_key = panel.panel_key
        jph_data = load_jph()
        # POZOR: Tu by mohla byť chyba, ak panel_key nie je v správnom formáte.
        try:
            jph_data[panel_key] = int(jph_str)
            save_jph(jph_data)

            # POZOR: get_screen('hlavna') môže zlyhať, ak nie je načítaný KV súbor!
            self.root.get_screen('hlavna').update_poruchy_list()
            MDSnackbar(MDSnackbarText(text=f"JPH pre {datetime.strptime(panel_key, '%d.%m.%y_%H:00').strftime('%H:00')} uložené: {jph_str}")).open()
        except Exception as e:
            # Ak zlyhá až tu, problém nie je v štarte, ale v runtime logike
            MDSnackbar(MDSnackbarText(text=f"Chyba pri JPH save: {e}")).open()

    def build(self):
        # --- ZAČIATOK KRITICKÉHO DEBUG BLOKU PRE ZACHYTÁVANIE CHYB PRI ŠTARTE ---
        try:
            # Pôvodný kód z build()
            settings = load_settings()
            self.theme_cls.theme_style = settings.get('theme_style', 'Light')
            self.theme_cls.primary_palette = settings.get('primary_color', 'Blue')

            # Nastavenie farieb stavového riadku (používam get_color_from_hex pre istotu, že farba je platná)
            if Window.height != Window.default_height:
                # POZNÁMKA: Ak tu bol Váš originálny kód, použite ho.
                set_bars_colors(get_color_from_hex(self.theme_cls.primary_color), self.theme_cls.bg_dark)

            # KRITICKÝ KROK: Načítanie KV súboru
            Builder.load_file("main.kv")

            self.root = MDScreenManager()
            self.root.add_widget(HlavnaScreen(name="hlavna"))
            self.root.add_widget(SettingsScreen(name="nastavenia"))
            self.root.add_widget(ReportScreen(name="report"))
            self.root.add_widget(ShareScreen(name="share"))

            self.root.current = "hlavna"
            return self.root

        except Exception as e:
            # Ak nastane akákoľvek chyba (FileNotFoundError, AttributeError, atď.),
            # zobrazí chybovú správu namiesto pádu/prepnute na pozadie.
            
            error_screen = MDScreen()
            error_screen.add_widget(
                MDLabel(
                    text=f"[b]KRITICKÁ CHYBA V BUILD():[/b]\n\n{type(e).__name__}: {e}\n\n"
                         f"Skontrolujte súbory (main.kv, settings.json) a logiku inicializácie. Ak chyba pretrváva, skúste použiť stabilnú verziu KivyMD (1.1.1 namiesto master.zip).",
                    markup=True,
                    halign="center",
                    valign="middle",
                    font_style="Headline",
                    theme_text_color="Error"
                )
            )
            # Vráti chybovú obrazovku, aby ste videli správu
            return error_screen
        # --- KONIEC KRITICKÉHO DEBUG BLOKU ---


if __name__ == '__main__':
    # factory registrácia pre MyExpansionPanel (predpokladané)
    Factory.register('MyExpansionPanel', cls=MyExpansionPanel)
    Factory.register('MyListItem', cls=MyListItem)
    Factory.register('AppDialogContent', cls=AppDialogContent)
    
    # Skrátená Factory registrácia pre ostatné triedy
    Factory.register('HlavnaScreen', cls=HlavnaScreen)
    Factory.register('SettingsScreen', cls=SettingsScreen)
    Factory.register('ReportScreen', cls=ReportScreen)
    Factory.register('ShareScreen', cls=ShareScreen)

    HlaseniaApp().run()
