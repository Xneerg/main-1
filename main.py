#7#pylint:disable=W0611
import json
import os
import re
import functools
from kivy.app import App # Import z Kivy pre App.user_data_dir
from pathlib import Path # Import z Pythonu pre prácu s cestami
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
            print("Plyer Share API nie je dostupné. Nainštalujte Plyer pre mobilné zdieľanie.")
            Clock.schedule_once(lambda dt: MDSnackbar(MDSnackbarText(text="Zdieľanie dostupné len na mobilných zariadeniach (chýba Plyer).")).open(), 0.5)
    share = DummyShare()

# --- UTILITY FUNKCIE PRE PRÁCU SO SÚBORMI (Android kompatibilné) ---
# Odkaz na Kivy dokumentáciu: Strana 704 v kivy-readthedocs-io-en-latest_kópia.pdf (Vlastnosť App.user_data_dir)
def get_data_dir() -> Path:
    """Získa a vytvorí priečinok pre dáta aplikácie (platformovo nezávislé)."""
    try:
        # App.get_running_app() je dostupné až po spustení aplikácie
        data_dir = Path(App.get_running_app().user_data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    except AttributeError:
        # Fallback (len pre testovanie alebo ak kód beží mimo Kivy loop)
        return Path('.') 

def get_data_path(filename: str) -> Path:
    """Získa kompletnú cestu k súboru v priečinku dát aplikácie."""
    return get_data_dir() / filename

def op_sort_key(op_name):
    match = re.search(r'\d+', op_name)
    if match:
        return (0, int(match.group(0)), op_name)
    else:
        return (1, op_name)

COLOR_CATEGORIES = {
    # ... (ostatné konštanty sú nezmenené) ...
    "🔵 MODRÉ ODTIENE": ['Aliceblue', 'Aqua', 'Aquamarine', 'Azure', 'Blue', 'Blueviolet', 'Cadetblue', 'Cornflowerblue', 'Cyan', 'Darkblue', 'Darkcyan', 'Darkslateblue', 'Darkslategray', 'Darkslategrey', 'Darkturquoise', 'Deepskyblue', 'Dodgerblue', 'Indigo', 'Lightblue', 'Lightcyan', 'Lightskyblue', 'Lightslategray', 'Lightslategrey', 'Lightsteelblue', 'Mediumaquamarine', 'Mediumblue', 'Mediumslateblue', 'Mediumspringgreen', 'Mediumturquoise', 'Midnightblue', 'Navy', 'Paleturquoise', 'Powderblue', 'Royalblue', 'Skyblue', 'Slateblue', 'Slategray', 'Slategrey', 'Steelblue', 'Teal', 'Turquoise'],
    "🌿 ZELENÉ ODTIENE": ['Chartreuse', 'Darkgreen', 'Darkkhaki', 'Darkolivegreen', 'Darkseagreen', 'Forestgreen', 'Green', 'Greenyellow', 'Lawngreen', 'Lightgreen', 'Lightseagreen', 'Lime', 'Limegreen', 'Mediumseagreen', 'Olive', 'Olivedrab', 'Palegreen', 'Seagreen', 'Springgreen', 'Yellowgreen'],
    "🔴 ČERVENÉ A HNEDÉ ODTIENE": ['Brown', 'Chocolate', 'Coral', 'Crimson', 'Darkred', 'Darksalmon', 'Firebrick', 'Indianred', 'Lightcoral', 'Lightsalmon', 'Maroon', 'Orangered', 'Peru', 'Red', 'Rosybrown', 'Saddlebrown', 'Salmon', 'Sienna', 'Tomato'],
    "🟠 ORANŽOVÉ A BÉŽOVÉ ODTIENE": ['Antiquewhite', 'Bisque', 'Blanchedalmond', 'Burlywood', 'Cornsilk', 'Darkgoldenrod', 'Darkorange', 'Goldenrod', 'Lightgoldenrodyellow', 'Lightyellow', 'Moccasin', 'Navajowhite', 'Oldlace', 'Orange', 'Orangered', 'Papayawhip', 'Peachpuff', 'SandyBrown', 'Tan', 'Wheat'],
    "🌸 RUŽOVÉ A FIALOVÉ ODTIENE": ['Darkmagenta', 'Darkorchid', 'Darkviolet', 'Deeppink', 'Fuchsia', 'Hotpink', 'Lavender', 'Lavenderblush', 'Lightpink', 'Magenta', 'Mediumorchid', 'Mediumpurple', 'Mediumvioletred', 'Mistyrose', 'Orchid', 'Palevioletred', 'Pink', 'Plum', 'Purple', 'Thistle', 'Violet'],
    "🌞 ŽLTÉ ODTIENE": ['Gold', 'Khaki', 'Lemonchiffon', 'Palegoldenrod', 'Yellow'],
    "⚫ SIVÉ, ČIERNE A NEUTRÁLNE ODTIENE": ['Black', 'Darkgray', 'Darkgrey', 'Dimgray', 'Dimgrey', 'Gainsboro', 'Ghostwhite', 'Gray', 'Grey', 'Lightgray', 'Lightgrey', 'Silver', 'White', 'Whitesmoke'],
    "⚪ SVETLÉ NEUTRÁLNE": ['Beige', 'Floralwhite', 'Honeydew', 'Ivory', 'Linen', 'Mintcream', 'Seashell', 'Snow']
}

COLOR_HEX_MAP = {
    # ... (mapa farieb je nezmenená) ...
    'Aliceblue': '#F0F8FF', 'Aqua': '#00FFFF', 'Aquamarine': '#7FFFD4', 'Azure': '#F0FFFF', 'Blue': '#0000FF',
    'Blueviolet': '#8A2BE2', 'Cadetblue': '#5F9EA0', 'Cornflowerblue': '#6495ED', 'Cyan': '#00FFFF',
    'Darkblue': '#00008B', 'Darkcyan': '#008B8B', 'Darkslateblue': '#483D8B', 'Darkslategray': '#2F4F4F',
    'Darkslategrey': '#2F4F4F', 'Darkturquoise': '#00CED1', 'Deepskyblue': '#00BFFF', 'Dodgerblue': '#1E90FF',
    'Indigo': '#4B0082', 'Lightblue': '#ADD8E6', 'Lightcyan': '#E0FFFF', 'Lightskyblue': '#87CEFA',
    'Lightslategray': '#778899', 'Lightslategrey': '#778899', 'Lightsteelblue': '#B0C4DE',
    'Mediumaquamarine': '#66CDAA', 'Mediumblue': '#0000CD', 'Mediumslateblue': '#7B68EE',
    'Mediumspringgreen': '#00FA9A', 'Mediumturquoise': '#48D1CC', 'Midnightblue': '#191970', 'Navy': '#000080',
    'Paleturquoise': '#AFEEEE', 'Powderblue': '#B0E0E6', 'Royalblue': '#4169E1', 'Skyblue': '#87CEEB',
    'Slateblue': '#6A5ACD', 'Slategray': '#708090', 'Slategrey': '#708090', 'Steelblue': '#4682B4',
    'Teal': '#008080', 'Turquoise': '#40E0D0', 'Chartreuse': '#7FFF00', 'Darkgreen': '#006400',
    'Darkkhaki': '#BDB76B', 'Darkolivegreen': '#556B2F', 'Darkseagreen': '#8FBC8F', 'Forestgreen': '#228B22',
    'Green': '#008000', 'Greenyellow': '#ADFF2F', 'Lawngreen': '#7CFC00', 'Lightgreen': '#90EE90',
    'Lightseagreen': '#20B2AA', 'Lime': '#00FF00', 'Limegreen': '#32CD32', 'Mediumseagreen': '#3CB371',
    'Olive': '#808000', 'Olivedrab': '#6B8E23', 'Palegreen': '#98FB98', 'Seagreen': '#2E8B57',
    'Springgreen': '#00FF7F', 'Yellowgreen': '#9ACD32', 'Brown': '#A52A2A', 'Chocolate': '#D2691E',
    'Coral': '#FF7F50', 'Crimson': '#DC143C', 'Darkred': '#8B0000', 'Darksalmon': '#E9967A',
    'Firebrick': '#B22222', 'Indianred': '#CD5C5C', 'Lightcoral': '#F08080', 'Lightsalmon': '#FFA07A',
    'Maroon': '#800000', 'Orangered': '#FF4500', 'Peru': '#CD853F', 'Red': '#FF0000',
    'Rosybrown': '#BC8F8F', 'Saddlebrown': '#8B4513', 'Salmon': '#FA8072', 'Sienna': '#A0522D',
    'Tomato': '#FF6347', 'Antiquewhite': '#FAEBD7', 'Bisque': '#FFE4C4', 'Blanchedalmond': '#FFEBCD',
    'Burlywood': '#DEB887', 'Cornsilk': '#FFF8DC', 'Darkgoldenrod': '#B8860B', 'Darkorange': '#FF8C00',
    'Goldenrod': '#DAA520', 'Lightgoldenrodyellow': '#FAFAD2', 'Lightyellow': '#FFFFE0', 'Moccasin': '#FFE4B5',
    'Navajowhite': '#FFDEAD', 'Oldlace': '#FDF5E6', 'Orange': '#FFA500', 'Papayawhip': '#FFEFD5',
    'Peachpuff': '#FFDAB9', 'SandyBrown': '#F4A460', 'Tan': '#D2B48C', 'Wheat': '#F5DEB3',
    'Darkmagenta': '#8B008B', 'Darkorchid': '#9932CC', 'Darkviolet': '#9400D3', 'Deeppink': '#FF1493',
    'Fuchsia': '#FF00FF', 'Hotpink': '#FF69B4', 'Lavender': '#E6E6FA', 'Lavenderblush': '#FFF0F5',
    'Lightpink': '#FFB6C1', 'Magenta': '#FF00FF', 'Mediumorchid': '#BA55D3', 'Mediumpurple': '#9370DB',
    'Mediumvioletred': '#C71585', 'Mistyrose': '#FFE4E1', 'Orchid': '#DA70D6', 'Palevioletred': '#DB7093',
    'Pink': '#FFC0CB', 'Plum': '#DDA0DD', 'Purple': '#800080', 'Thistle': '#D8BFD8', 'Violet': '#EE82EE',
    'Gold': '#FFD700', 'Khaki': '#F0E68C', 'Lemonchiffon': '#FFFACD', 'Palegoldenrod': '#EEE8AA',
    'Yellow': '#FFFF00', 'Black': '#000000', 'Darkgray': '#A9A9A9', 'Darkgrey': '#A9A9A9',
    'Dimgray': '#696969', 'Dimgrey': '#696969', 'Gainsboro': '#DCDCDC', 'Ghostwhite': '#F8F8FF',
    'Gray': '#808080', 'Grey': '#808080', 'Lightgray': '#D3D3D3', 'Lightgrey': '#D3D3D3',
    'Silver': '#C0C0C0', 'White': '#FFFFFF', 'Whitesmoke': '#F5F5F5', 'Beige': '#F5F5DC',
    'Floralwhite': '#FFFAF0', 'Honeydew': '#F0FFF0', 'Ivory': '#FFFFF0', 'Linen': '#FAF0E6',
    'Mintcream': '#F5FFFA', 'Seashell': '#FFF5EE', 'Snow': '#FFFAFA'
}

class TimeDurationChip(ButtonBehavior, MDBoxLayout):
    # ... (trieda je nezmenená) ...
    hlasenie_data = DictProperty({})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.size_hint_x = None
        self.width = dp(70)
        self.padding = (0, 0, 0, 0)
        self.pos_hint = {"center_y": .5}

    def on_release(self):
        app = MDApp.get_running_app()
        hlavna_screen = app.root.get_screen('hlavna')
        parent_item = self.parent
        while parent_item and not isinstance(parent_item, MDListItem):
             parent_item = parent_item.parent
        if parent_item:
            hlavna_screen.show_time_duration_menu(self.hlasenie_data, parent_item)
        else:
            print("Chyba: Nepodarilo sa nájsť MDListItem parent.")

class TrailingPressedIconButton(ButtonBehavior, MDListItemTrailingIcon):
    # ... (trieda je nezmenená) ...
    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            PushMatrix()
            self.rot = Rotate(angle=self.angle, origin=self.center)
        self.bind(pos=self.update_origin, size=self.update_origin, angle=self.update_angle)
        self.canvas.after.add(PopMatrix())

    def update_origin(self, *args):
        self.rot.origin = self.center

    def update_angle(self, *args):
        self.rot.angle = self.angle

    def animate_to(self, new_angle):
        Animation(angle=new_angle, d=0.2, t="out_quad").start(self)

class MyExpansionPanel(MDBoxLayout):
    # ... (trieda je nezmenená) ...
    is_open = False
    panel_key = StringProperty("")
    hour_hlasenia = DictProperty({'jph': 0, 'list': []})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(48)
        self.is_open = False
        Clock.schedule_once(self._set_initial_height, 0)

    def _set_initial_height(self, dt):
        self.height = self.ids.header.height
        for child in self.ids.content_list.children:
            child.opacity = 0
            child.disabled = True
        self.ids.content_list.height = 0

    def toggle(self):
        self.is_open = not self.is_open
        if self.is_open:
            self.open_panel()
        else:
            self.close_panel()

    def open_panel(self):
        Animation.stop_all(self, 'height')
        Animation.stop_all(self.ids.content_list, 'height')
        content_list = self.ids.content_list
        content_height = sum(child.height for child in content_list.children)

        # --- UPRAVENÁ LOGIKA: Pridá label, len ak je zoznam PRÁZDNY a neobsahuje ani tlačidlo ---
        if not content_list.children:
            placeholder = MDLabel(
                text="Žiadne hlásenia v tejto hodine.",
                halign="center",
                adaptive_height=True,
                padding=[0, "8dp"]
            )
            content_list.add_widget(placeholder)
            content_height = placeholder.height # Prepočítame výšku

        for child in content_list.children:
            child.opacity = 1
            child.disabled = False
        anim_content = Animation(height=content_height, duration=0.2, t='out_quad')
        anim_content.start(content_list)
        panel_height = self.ids.header.height + content_height + self.ids.content.padding[3] + self.ids.content.padding[1] + dp(8)
        anim_panel = Animation(height=panel_height, duration=0.2, t='out_quad')
        anim_panel.start(self)

    def close_panel(self):
        Animation.stop_all(self, 'height')
        Animation.stop_all(self.ids.content_list, 'height')
        content_list = self.ids.content_list

        # Odstránime placeholder label, ak tam bol
        for child in list(content_list.children):
            if isinstance(child, MDLabel) and child.text == "Žiadne hlásenia v tejto hodine.":
                content_list.remove_widget(child)

        for child in content_list.children:
            child.opacity = 0
            child.disabled = True
        anim_content = Animation(height=0, duration=0.2, t='out_quad')
        anim_content.start(content_list)
        panel_height = self.ids.header.height + self.ids.header.padding[1] + self.ids.header.padding[3]
        anim_panel = Animation(height=panel_height, duration=0.2, t='out_quad')
        anim_panel.start(self)

    def copy_hour_summary(self):
        hodina_cas = datetime.strptime(self.panel_key, '%d.%m.%y_%H:00').strftime('%H:00')
        jph_value = self.hour_hlasenia.get('jph', 0)
        hlasenia = self.hour_hlasenia.get('list', [])
        summary_text = f"SÚHRN PORÚCH | Hodina: {hodina_cas}\n"
        summary_text += f"JPH: {jph_value} ks\n"
        summary_text += "=" * 30 + "\n"
        if hlasenia:
            summary_text += "Poruchy:\n"
            hlasenia.sort(key=lambda x: datetime.strptime(x['datum_cas'], '%Y-%m-%d %H:%M:%S'))
            for hlasenie in hlasenia:
                hlasenie_time_str = datetime.strptime(hlasenie['datum_cas'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')
                duration = hlasenie.get('trvanie_minuty', 0)
                summary_text += f"- [{hlasenie_time_str}] OP: {hlasenie['op']}, Porucha: {hlasenie['porucha']}, Trvanie: {duration} min\n"
        else:
            summary_text += "Žiadne hlásenia porúch zaznamenané.\n"
        try:
            Clipboard.copy(summary_text)
            MDSnackbar(MDSnackbarText(text=f"Súhrn pre {hodina_cas} skopírovaný do schránky!")).open()
        except Exception as e:
            MDSnackbar(MDSnackbarText(text=f"Chyba pri kopírovaní! {e}")).open()

# --- NOVÁ TRIEDA PRE OBSAH DIALÓGU ŠTATISTÍK ---
class StatisticsDialogContent(MDBoxLayout):
    pass

KV = '''
#:import MDFabButton kivymd.uix.button.MDFabButton

<MyExpansionPanel>:
# ... (KV je nezmenené) ...
    orientation: "vertical"
    size_hint_y: None
    spacing: "4dp"
    padding: "4dp"
    height: self.minimum_height

    MDExpansionPanelHeader:
        id: header
        adaptive_height: True
        size_hint_y: None
        height: self.minimum_height
        MDListItem:
            id: header_list_item
            theme_bg_color: "Custom"
            md_bg_color: self.theme_cls.surfaceContainerLowestColor
            ripple_effect: False
            radius: dp(12)

            MDListItemHeadlineText:
                id: headline_text
                text: "default text"
                font_style: "Label"
                adaptive_height: True
                markup: True

            MDButton:
                id: jph_button
                style: "filled"
                size_hint: None, None
                width: "60dp"
                height: "40dp"
                pos_hint: {'center_y': .5}
                MDButtonText:
                    id: jph_button_text
                    text: "0"

            TrailingPressedIconButton:
                id: chevron
                icon: "chevron-right"
                on_release: app.tap_expansion_chevron(root, chevron)

    MDBoxLayout:
        id: content
        orientation: "vertical"
        size_hint_y: None
        height: self.minimum_height
        padding: "8dp", 0, "8dp", "8dp"
        md_bg_color: self.theme_cls.surfaceContainerLowColor
        radius: [0, 0, dp(12), dp(12)]

        MDList:
            id: content_list
            size_hint_y: None
            height: 0
            spacing: "8dp"

<StatisticsDialogContent>
    orientation: 'vertical'
    adaptive_height: True
    spacing: "8dp"
    padding: "8dp"

    MDLabel:
        id: stats_title
        text: "Súhrnné štatistiky"
        font_style: "Title"
        adaptive_height: True
        halign: "center"
        padding: [0, "8dp"]
    MDLabel:
        id: stats_total_faults
        text: "Celkový počet porúch: 0"
        adaptive_height: True
        font_style: "Body"
    MDLabel:
        id: stats_total_downtime
        text: "Celkové trvanie porúch: 0 min"
        adaptive_height: True
        font_style: "Body"
    MDLabel:
        id: stats_avg_downtime
        text: "Priemerné trvanie poruchy: 0.0 min"
        adaptive_height: True
        font_style: "Body"
    MDLabel:
        id: stats_total_jph
        text: "Celkové JPH: 0 ks"
        adaptive_height: True
        font_style: "Body"

    MDLabel:
        id: stats_top_op_freq_title
        text: "Najčastejšie OP (počet):"
        adaptive_height: True
        font_style: "Body"
        bold: True
        padding_top: "8dp"
    MDLabel:
        id: stats_top_op_freq_data
        text: "-"
        adaptive_height: True
        font_style: "Label"

    MDLabel:
        id: stats_top_op_time_title
        text: "Najviac odstávok OP (min):"
        adaptive_height: True
        font_style: "Body"
        bold: True
        padding_top: "8dp"
    MDLabel:
        id: stats_top_op_time_data
        text: "-"
        adaptive_height: True
        font_style: "Label"

    MDLabel:
        id: stats_top_porucha_freq_title
        text: "Najčastejšie poruchy (počet):"
        adaptive_height: True
        font_style: "Body"
        bold: True
        padding_top: "8dp"
    MDLabel:
        id: stats_top_porucha_freq_data
        text: "-"
        adaptive_height: True
        font_style: "Label"

    MDLabel:
        id: stats_top_porucha_time_title
        text: "Najviac odstávok poruchy (min):"
        adaptive_height: True
        font_style: "Body"
        bold: True
        padding_top: "8dp"
    MDLabel:
        id: stats_top_porucha_time_data
        text: "-"
        adaptive_height: True
        font_style: "Label"

MDScreenManager:
    HlavnaScreen:
    NastavenieScreen:
    SearchScreen:
    JPHScreen:
    EditHlasenieScreen:

<HlavnaScreen>:
    # ... (ostatný KV kód je nezmenený) ...
    name: 'hlavna'
    MDFloatLayout:
        MDBoxLayout:
            orientation: 'vertical'
            md_bg_color: self.theme_cls.backgroundColor

            MDTopAppBar:
                id: top_appbar
                title: "Hlásenie"
                style: "filled"
                elevation: 4
                color_scheme: "primary"
                MDTopAppBarLeadingButtonContainer:
                    MDActionTopAppBarButton:
                        icon: "menu"
                MDTopAppBarTitle:
                    text: top_appbar.title
                MDTopAppBarTrailingButtonContainer:
                    MDActionTopAppBarButton:
                        id: copy_button
                        icon: "content-copy"
                        on_release: root.open_copy_menu()
                    MDActionTopAppBarButton:
                        icon: "share-variant"
                        on_release: root.share_current_faults()
                    MDActionTopAppBarButton:
                        icon: "magnify"
                        on_release: app.root.current = 'search'
                    MDActionTopAppBarButton:
                        icon: "chart-line"
                        on_release: app.root.current = 'jph'
                    MDActionTopAppBarButton:
                        icon: "cog"
                        on_release: app.root.current = 'nastavenie'

            MDBoxLayout:
                orientation: 'horizontal'
                adaptive_height: True
                padding: "8dp", "12dp"
                spacing: "8dp"

                MDBoxLayout:
                    orientation: 'vertical'
                    size_hint_x: 0.6
                    adaptive_height: True

                    MDLabel:
                        id: date_label_static
                        text: "Dnešné Hlásenia"
                        halign: "left"
                        adaptive_height: True
                        font_style: "Body"
                        bold: True

                    MDLabel:
                        id: total_jph_label
                        text: "Celkové JPH: 0 ks"
                        halign: "left"
                        adaptive_height: True
                        font_style: "Label"

                MDTextField:
                    id: shift_goal_input
                    hint_text: "Cieľ (ks)"
                    input_filter: "int"
                    mode: "outlined"
                    size_hint_x: 0.4
                    height: "48dp"
                    size_hint_y: None
                    on_text: root.update_poruchy_list()

            MDScrollView:
                id: main_scroll_view
                do_scroll_y: True
                MDBoxLayout:
                    id: poruchy_list
                    orientation: 'vertical'
                    adaptive_height: True
                    spacing: "4dp"
                    padding: "4dp"
                    md_bg_color: self.theme_cls.backgroundColor

        MDFabButton:
            icon: "plus"
            pos_hint: {"center_x": .5, "center_y": .1}
            on_release: root.show_op_selection_dialog()


<NastavenieScreen>:
    name: 'nastavenie'
    MDBoxLayout:
# ... (zvyšok KV kódu je nezmenený) ...
        orientation: 'vertical'
        md_bg_color: self.theme_cls.backgroundColor

        MDTopAppBar:
            id: nastavenie_app_bar
            title: "Nastavenia"
            style: "filled"
            elevation: 4
            color_scheme: "primary"
            MDTopAppBarLeadingButtonContainer:
                MDActionTopAppBarButton:
                    icon: "arrow-left"
                    on_release: root.go_back_to_hlavna()
            MDTopAppBarTitle:
                text: nastavenie_app_bar.title

        MDScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                adaptive_height: True
                padding: "20dp"
                spacing: "20dp"

                MDBoxLayout:
                    adaptive_height: True
                    md_bg_color: self.theme_cls.surfaceContainerColor
                    radius: dp(8)
                    padding: dp(8)
                    MDLabel:
                        text: "Vzhľad aplikácie"
                        font_style: "Body"
                        adaptive_height: True
                        halign: "center"

                MDBoxLayout:
                    orientation: 'horizontal'
                    spacing: "10dp"
                    size_hint_y: None
                    height: "48dp"

                    MDButton:
                        id: theme_button
                        style: "outlined"
                        size_hint_x: 0.5
                        on_release: root.show_theme_menu()
                        MDButtonText:
                            id: theme_button_text
                            text: "Vybrať tému"

                    MDBoxLayout:
                        orientation: 'horizontal'
                        size_hint_x: 0.5
                        adaptive_width: True
                        spacing: "4dp"
                        pos_hint: {"center_y": 0.5}

                        MDIconButton:
                            icon: "chevron-left"
                            on_release: root.change_color_by_arrow(-1)

                        MDButton:
                            id: color_button
                            style: "outlined"
                            size_hint_x: 1
                            on_release: root.show_color_menu()
                            MDButtonText:
                                id: color_button_text
                                text: "Farba"

                        MDIconButton:
                            icon: "chevron-right"
                            on_release: root.change_color_by_arrow(1)

                MDBoxLayout:
                    size_hint_y: None
                    height: "20dp"

                MDBoxLayout:
                    adaptive_height: True
                    md_bg_color: self.theme_cls.surfaceContainerColor
                    radius: dp(8)
                    padding: dp(8)
                    MDLabel:
                        text: "Pridať nové OP a Poruchu"
                        font_style: "Body"
                        adaptive_height: True
                        halign: "center"

                MDBoxLayout:
                    size_hint_y: None
                    height: "20dp"

                MDLabel:
                    text: "Pridať nové OP (napr. OP001)"
                    font_style: "Label"
                    adaptive_height: True

                MDTextField:
                    id: op_input
                    hint_text: "OPxxx"
                    mode: "outlined"
                    size_hint_y: None
                    height: "48dp"

                MDLabel:
                    text: "Pridať novú Poruchu"
                    font_style: "Label"
                    adaptive_height: True

                MDTextField:
                    id: porucha_input
                    hint_text: "Text poruchy (napr. Porucha1)"
                    mode: "outlined"
                    size_hint_y: None
                    height: "48dp"

                MDButton:
                    style: "filled"
                    size_hint: 0.8, None
                    height: "48dp"
                    on_release: root.ulozit_op_a_poruchu()
                    pos_hint: {'center_x': 0.5}
                    MDButtonText:
                        text: "Uložiť OP a Poruchu"

<SearchScreen>:
    name: 'search'
    MDBoxLayout:
# ... (zvyšok KV kódu je nezmenený) ...
        orientation: 'vertical'
        md_bg_color: self.theme_cls.backgroundColor

        MDTopAppBar:
            id: search_app_bar
            title: "Vyhľadávanie porúch"
            style: "filled"
            elevation: 4
            color_scheme: "primary"
            MDTopAppBarLeadingButtonContainer:
                MDActionTopAppBarButton:
                    icon: "arrow-left"
                    on_release: app.root.current = 'hlavna'
            MDTopAppBarTitle:
                text: search_app_bar.title
            MDTopAppBarTrailingButtonContainer:
                MDActionTopAppBarButton:
                    icon: "poll"
                    on_release: root.show_statistics_dialog()
                MDActionTopAppBarButton:
                    icon: "filter-variant"
                    on_release: root.open_filter_dialog()

        MDScrollView:
            MDBoxLayout:
                id: search_results_list
                orientation: 'vertical'
                adaptive_height: True
                padding: "8dp"
                spacing: "4dp"

<JPHScreen>:
    name: 'jph'
    MDBoxLayout:
# ... (zvyšok KV kódu je nezmenený) ...
        orientation: 'vertical'
        md_bg_color: self.theme_cls.backgroundColor

        MDTopAppBar:
            id: jph_app_bar
            title: "Prehľad Smien JPH"
            style: "filled"
            elevation: 4
            color_scheme: "primary"
            MDTopAppBarLeadingButtonContainer:
                MDActionTopAppBarButton:
                    icon: "arrow-left"
                    on_release: root.go_back_to_hlavna()
            MDTopAppBarTitle:
                text: jph_app_bar.title
            MDTopAppBarTrailingButtonContainer:
                MDActionTopAppBarButton:
                    icon: "filter-variant"
                    on_release: root.show_filter_dialog()

        MDCard:
            id: summary_card
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            padding: "12dp"
            spacing: "8dp"
            style: "outlined"
            md_bg_color: self.theme_cls.surfaceContainerLowColor
            radius: [12, 12, 12, 12]
            pos_hint: {"center_x": 0.5}
            size_hint_x: 0.95
            height: 0
            opacity: 0
            MDLabel:
                id: summary_total_shifts
                text: "Počet smien: 0"
                adaptive_height: True
                font_style: "Body"
                bold: True
            MDLabel:
                id: summary_total_pieces
                text: "Celkovo kusov: 0 ks"
                adaptive_height: True
                font_style: "Body"
            MDLabel:
                id: summary_avg_per_shift
                text: "Priemer / smena (12h): 0.00 ks"
                adaptive_height: True
                font_style: "Body"
            MDLabel:
                id: summary_avg_per_hour
                text: "Priemer / hodina: 0.00 ks"
                adaptive_height: True
                font_style: "Body"

        MDScrollView:
            MDList:
                id: shift_list
                padding: "10dp"
                spacing: "10dp"

<EditHlasenieScreen>:
    name: 'edit_hlasenie'
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: self.theme_cls.backgroundColor

        MDTopAppBar:
            id: edit_app_bar
            title: "Upraviť hlásenie"
            style: "filled"
            elevation: 4
            color_scheme: "primary"
            MDTopAppBarLeadingButtonContainer:
                MDActionTopAppBarButton:
                    icon: "arrow-left"
                    on_release: root.go_back_to_hlavna()
            MDTopAppBarTitle:
                text: edit_app_bar.title
            MDTopAppBarTrailingButtonContainer:
                MDActionTopAppBarButton:
                    icon: "check"
                    on_release: root.save_changes()

        MDScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                adaptive_height: True
                padding: "20dp"
                spacing: "24dp"

                MDLabel:
                    text: "Operačné pracovisko"
                    font_style: "Body"
                    adaptive_height: True
                    theme_text_color: "Secondary"

                MDButton:
                    id: op_button
                    style: "outlined"
                    on_release: root.show_op_menu()
                    MDButtonText:
                        id: op_button_text
                        text: "Načítava sa..."

                MDLabel:
                    text: "Porucha"
                    font_style: "Body"
                    adaptive_height: True
                    theme_text_color: "Secondary"

                MDButton:
                    id: porucha_button
                    style: "outlined"
                    on_release: root.show_porucha_menu()
                    MDButtonText:
                        id: porucha_button_text
                        text: "Načítava sa..."

                MDLabel:
                    text: "Trvanie minuti"
                    font_style: "Body"
                    adaptive_height: True
                    theme_text_color: "Secondary"

                MDButton:
                    id: duration_button
                    style: "outlined"
                    on_release: root.show_duration_menu()
                    MDButtonText:
                        id: duration_button_text
                        text: "Načítava sa..."

                MDLabel:
                    text: "Poznámka"
                    font_style: "Body"
                    adaptive_height: True
                    theme_text_color: "Secondary"

                MDTextField:
                    id: note_input
                    hint_text: "Text poznámky (voliteľné)"
                    mode: "outlined"
'''

def get_shift_type(hour):
    return "D" if 6 <= hour < 18 else "N"

def get_current_shift_timeframe():
    now = datetime.now()
    if 6 <= now.hour < 18:
        start_of_shift = now.replace(hour=6, minute=0, second=0, microsecond=0)
        end_of_shift = now.replace(hour=17, minute=59, second=59, microsecond=999999)
    else:
        if now.hour >= 18:
            start_of_shift = now.replace(hour=18, minute=0, second=0, microsecond=0)
            end_of_shift = (now + timedelta(days=1)).replace(hour=5, minute=59, second=59, microsecond=999999)
        else:
            start_of_shift = (now - timedelta(days=1)).replace(hour=18, minute=0, second=0, microsecond=0)
            end_of_shift = now.replace(hour=5, minute=59, second=59, microsecond=999999)
    return start_of_shift, end_of_shift

def get_slovak_weekday(date_obj):
    weekdays = ["Po", "Ut", "St", "Št", "Pi", "So", "Ne"]
    return weekdays[date_obj.weekday()]

# --- START OF ANDROID-COMPATIBLE I/O FUNCTIONS ---

def load_ops_poruchy():
    path = get_data_path('ops_poruchy.json')
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except json.JSONDecodeError: return {'ops': [], 'poruchy_pre_op': {}}
    return {'ops': [], 'poruchy_pre_op': {}}

def save_ops_poruchy(data):
    path = get_data_path('ops_poruchy.json')
    path.parent.mkdir(parents=True, exist_ok=True) # Ensure directory exists
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_hlasenia():
    path = get_data_path('hlasenia.json')
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except json.JSONDecodeError: return {'hlasenia': []}
    return {'hlasenia': []}

def save_hlasenia(data):
    path = get_data_path('hlasenia.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_settings():
    path = get_data_path('settings.json')
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except json.JSONDecodeError: return {'primary_palette': 'Lightgreen', 'theme_style': 'Dark'}
    # Predvolené nastavenia, ak súbor neexistuje
    return {'primary_palette': 'Lightgreen', 'theme_style': 'Dark'}

def save_settings(data):
    path = get_data_path('settings.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_jph():
    path = get_data_path('jph.json')
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except json.JSONDecodeError: return {}
    return {}

def save_jph(data):
    path = get_data_path('jph.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- END OF ANDROID-COMPATIBLE I/O FUNCTIONS ---


class HlavnaScreen(MDScreen):
    retroactive_fault_target = StringProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.note_dialog = None
        self.duration_menu = None
        self.copy_menu = None

    def on_enter(self, *args):
        app = MDApp.get_running_app()
        if app.fault_in_progress.get('op') and app.fault_in_progress.get('porucha'):
            op = app.fault_in_progress['op']
            porucha = app.fault_in_progress['porucha']
            Clock.schedule_once(lambda dt: self.show_duration_selection_dialog(op, porucha))
        else:
            Clock.schedule_once(self.init_screen_widgets, 0.2)

    def init_screen_widgets(self, *args):
        start_of_shift, _ = get_current_shift_timeframe()
        jph_data = load_jph()
        shift_date_key = start_of_shift.strftime('%d.%m.%y')
        shift_type = get_shift_type(start_of_shift.hour)
        goal_key = f"goal_{shift_date_key}_{shift_type}"
        goal_value = jph_data.get(goal_key)
        if goal_value is not None:
            self.ids.shift_goal_input.text = str(goal_value)
        else:
            self.ids.shift_goal_input.text = ""
        self.update_poruchy_list()

    def open_copy_menu(self):
        menu_items = [
            {
                "text": "Kopírovať súhrn celej smeny",
                "on_release": self.copy_full_shift_summary
            }
        ]

        panels = sorted(
            [child for child in self.ids.poruchy_list.children if isinstance(child, MyExpansionPanel)],
            key=lambda x: x.panel_key
        )

        has_hourly_data = False
        for panel in panels:
            if panel.hour_hlasenia.get('jph', 0) > 0 or panel.hour_hlasenia.get('list'):
                if not has_hourly_data:
                    menu_items.append({"divider": "Full"})
                    has_hourly_data = True

                hour_str = datetime.strptime(panel.panel_key, '%d.%m.%y_%H:00').strftime('%H:00')
                menu_items.append({
                    "text": f"Kopírovať hodinu {hour_str}",
                    "on_release": lambda p=panel: self.copy_and_dismiss_menu(p.copy_hour_summary)
                })

        if hasattr(self, 'copy_menu') and self.copy_menu:
             self.copy_menu.dismiss()

        self.copy_menu = MDDropdownMenu(
            caller=self.ids.copy_button, items=menu_items, width=dp(250)
        )
        self.copy_menu.open()

    def copy_and_dismiss_menu(self, copy_function):
        copy_function()
        if self.copy_menu:
            self.copy_menu.dismiss()

    def copy_full_shift_summary(self):
        if self.copy_menu:
            self.copy_menu.dismiss()

        data = load_hlasenia()
        jph_data = load_jph()
        all_hlasenia = data.get('hlasenia', [])
        start_of_shift, end_of_shift = get_current_shift_timeframe()
        filtered_hlasenia = [
            h for h in all_hlasenia
            if start_of_shift <= datetime.strptime(h['datum_cas'], '%Y-%m-%d %H:%M:%S') <= end_of_shift
        ]
        today = datetime.now()
        shift_type = get_shift_type(today.hour)
        content = f"Súhrn Hlásení Porúch | {today.strftime('%d.%m.%Y')} ({shift_type} Smena)\n"
        content += "=" * 55 + "\n"
        
        # Hlásenia triedime podľa času
        filtered_hlasenia.sort(key=lambda x: datetime.strptime(x['datum_cas'], '%Y-%m-%d %H:%M:%S'))

        jph_summary = {}
        current_time = start_of_shift
        while current_time < end_of_shift:
            panel_key = current_time.strftime('%d.%m.%y_%H:00')
            jph_value = jph_data.get(panel_key, 0)
            if jph_value > 0:
                 jph_summary[current_time.strftime('%H:00')] = jph_value
            current_time += timedelta(hours=1)

        if jph_summary:
            content += "SUMÁR JPH:\n"
            for hour, jph_val in sorted(jph_summary.items()):
                 content += f"- Hodina {hour}: {jph_val} ks\n"
            content += "=" * 55 + "\n"

        # --- ŠTART FORMÁTOVANIA HLÁSENÍ ---
        
        # 1. Zoskupíme hlásenia podľa hodiny
        hlasenia_by_hour = defaultdict(list)
        for hlasenie in filtered_hlasenia:
            hodina_str = datetime.strptime(hlasenie['datum_cas'], '%Y-%m-%d %H:%M:%S').strftime('%H:00')
            hlasenia_by_hour[hodina_str].append(hlasenie)

        # 2. Vytvoríme textový výstup
        if hlasenia_by_hour:
            content += "HLÁSENIA PORÚCH:\n"
            
            # Iterujeme cez hodiny v chronologickom poradí
            for hour_str, hlasenia_in_hour in sorted(hlasenia_by_hour.items()):
                content += f"\n--- Hodina {hour_str} ---\n"
                
                for hlasenie in hlasenia_in_hour:
                    hlasenie_time_str = datetime.strptime(hlasenie['datum_cas'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')
                    duration = hlasenie.get('trvanie_minuty', 0)
                    op = hlasenie.get('op', 'N/A')
                    porucha = hlasenie.get('porucha', 'N/A')

                    # Nový viacriadkový formát s Markdown
                    content += f"\n[{hlasenie_time_str}]\n"
                    content += f"OP: **{op}**\n"
                    content += f"Porucha: **{porucha}**\n"
                    content += f"Trvanie: **{duration} minút**\n"
            
            content += "\n" # Pridá medzeru pred koncovým oddeľovačom
        else:
             content += "ŽIADNE HLÁSENIA PORÚCH ZAZNAMENANÉ.\n"
             
        # --- KONIEC FORMÁTOVANIA HLÁSENÍ ---

        content += "=" * 55 + "\n"

        try:
            Clipboard.copy(content)
            MDSnackbar(MDSnackbarText(text="Súhrn smeny skopírovaný do schránky.")).open()
        except Exception as e:
            print(f"Chyba kopírovania: {e}")
            MDSnackbar(MDSnackbarText(text="Kopírovanie zlyhalo.")).open()

    def share_current_faults(self):
        data = load_hlasenia()
        jph_data = load_jph()
        all_hlasenia = data.get('hlasenia', [])
        start_of_shift, end_of_shift = get_current_shift_timeframe()
        filtered_hlasenia = [
            h for h in all_hlasenia
            if start_of_shift <= datetime.strptime(h['datum_cas'], '%Y-%m-%d %H:%M:%S') <= end_of_shift
        ]
        today = datetime.now()
        shift_type = get_shift_type(today.hour)
        content = f"Súhrn Hlásení Porúch | {today.strftime('%d.%m.%Y')} ({shift_type} Smena)\n"
        content += "=" * 55 + "\n"
        
        # Hlásenia triedime podľa času
        filtered_hlasenia.sort(key=lambda x: datetime.strptime(x['datum_cas'], '%Y-%m-%d %H:%M:%S'))

        jph_summary = {}
        current_time = start_of_shift
        while current_time < end_of_shift:
            panel_key = current_time.strftime('%d.%m.%y_%H:00')
            jph_value = jph_data.get(panel_key, 0)
            if jph_value > 0:
                 jph_summary[current_time.strftime('%H:00')] = jph_value
            current_time += timedelta(hours=1)

        if jph_summary:
            content += "SUMÁR JPH:\n"
            for hour, jph_val in sorted(jph_summary.items()):
                 content += f"- Hodina {hour}: {jph_val} ks\n"
            content += "=" * 55 + "\n"

        # --- ŠTART FORMÁTOVANIA HLÁSENÍ ---
        
        # 1. Zoskupíme hlásenia podľa hodiny
        hlasenia_by_hour = defaultdict(list)
        for hlasenie in filtered_hlasenia:
            hodina_str = datetime.strptime(hlasenie['datum_cas'], '%Y-%m-%d %H:%M:%S').strftime('%H:00')
            hlasenia_by_hour[hodina_str].append(hlasenie)

        # 2. Vytvoríme textový výstup
        if hlasenia_by_hour:
            content += "HLÁSENIA PORÚCH:\n"
            
            # Iterujeme cez hodiny v chronologickom poradí
            for hour_str, hlasenia_in_hour in sorted(hlasenia_by_hour.items()):
                content += f"\n--- Hodina {hour_str} ---\n"
                
                for hlasenie in hlasenia_in_hour:
                    hlasenie_time_str = datetime.strptime(hlasenie['datum_cas'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')
                    duration = hlasenie.get('trvanie_minuty', 0)
                    op = hlasenie.get('op', 'N/A')
                    porucha = hlasenie.get('porucha', 'N/A')

                    # Nový viacriadkový formát s Markdown
                    content += f"\n[{hlasenie_time_str}]\n"
                    content += f"OP: **{op}**\n"
                    content += f"Porucha: **{porucha}**\n"
                    content += f"Trvanie: **{duration} minút**\n"
            
            content += "\n" # Pridá medzeru pred koncovým oddeľovačom
        else:
             content += "ŽIADNE HLÁSENIA PORÚCH ZAZNAMENANÉ.\n"
             
        # --- KONIEC FORMÁTOVANIA HLÁSENÍ ---

        content += "=" * 55 + "\n"

        try:
            share.share(title=f"Poruchy {today.strftime('%d.%m.%Y')} ({shift_type})", text=content)
            MDSnackbar(MDSnackbarText(text="Spustený dialóg zdieľania.")).open()
        except Exception as e:
            print(f"Chyba zdieľania: {e}")
            MDSnackbar(MDSnackbarText(text="Zdieľanie zlyhalo.")).open()

    def delete_hlasenie(self, hlasenie, *args):
        data = load_hlasenia()
        all_hlasenia = data.get('hlasenia', [])
        all_hlasenia = [h for h in all_hlasenia if h.get('datum_cas') != hlasenie.get('datum_cas')]
        data['hlasenia'] = all_hlasenia
        save_hlasenia(data)
        MDSnackbar(MDSnackbarText(text="Hlásenie vymazané!")).open()
        self.update_poruchy_list()

    def show_time_duration_menu(self, hlasenie: dict, item: Factory.MDListItem):
        menu_items = [
            {"text": f"{i} minút", "on_release": lambda x=i: self.save_time_duration_from_menu(hlasenie, item, x)}
            for i in range(1, 61)
        ]

        caller = next((child for child in item.children if isinstance(child, TimeDurationChip)), None)

        if not caller:
             MDSnackbar(MDSnackbarText(text="Chyba: Nepodarilo sa nájsť Caller pre menu trvania.")).open()
             return

        if hasattr(self, 'duration_menu') and self.duration_menu:
            self.duration_menu.dismiss()

        self.duration_menu = MDDropdownMenu(
            caller=caller, items=menu_items, width=dp(150), max_height=dp(400), radius=[7] * 4
        )
        self.duration_menu.open()

    def save_time_duration_from_menu(self, hlasenie: dict, item: Factory.MDListItem, duration_minutes: int):
        if hasattr(self, 'duration_menu') and self.duration_menu:
            self.duration_menu.dismiss()
        data = load_hlasenia()
        for h in data.get('hlasenia', []):
            if h.get('datum_cas') == hlasenie.get('datum_cas'):
                h['trvanie_minuty'] = duration_minutes
                break
        save_hlasenia(data)
        self.update_poruchy_list()
        MDSnackbar(MDSnackbarText(text=f"Trvanie poruchy ({hlasenie['op']}) uložené: {duration_minutes} minút.")).open()

    def update_poruchy_list_height(self, *args):
        self.ids.poruchy_list.height = self.ids.poruchy_list.minimum_height

    def go_to_edit_screen(self, hlasenie, *args):
        edit_screen = self.manager.get_screen('edit_hlasenie')
        edit_screen.set_hlasenie_data(hlasenie)
        self.manager.current = 'edit_hlasenie'

    def update_poruchy_list(self):
        self.ids.poruchy_list.clear_widgets()
        today = datetime.now()
        date_text = f"Dnešné Hlásenia | {get_slovak_weekday(today)} {today.strftime('%d.%m.%Y')}"
        self.ids.date_label_static.text = date_text

        current_hour_key = today.strftime('%d.%m.%y_%H:00')

        start_of_shift, end_of_shift = get_current_shift_timeframe()
        jph_data = load_jph()

        shift_goal = 0
        goal_key = f"goal_{start_of_shift.strftime('%d.%m.%y')}_{get_shift_type(start_of_shift.hour)}"
        try:
            current_goal_text = self.ids.shift_goal_input.text.strip()
            if current_goal_text:
                shift_goal = int(current_goal_text)
                if jph_data.get(goal_key) != shift_goal:
                    jph_data[goal_key] = shift_goal
                    save_jph(jph_data)
            elif goal_key in jph_data:
                del jph_data[goal_key]
                save_jph(jph_data)
        except (ValueError, AttributeError):
            pass

        hourly_goal = float(shift_goal) / 12.0 if shift_goal > 0 else 0
        all_hlasenia = load_hlasenia().get('hlasenia', [])
        filtered_hlasenia = [
            h for h in all_hlasenia
            if start_of_shift <= datetime.strptime(h['datum_cas'], '%Y-%m-%d %H:%M:%S') <= end_of_shift
        ]

        panels = {}
        current_time = start_of_shift
        while current_time < end_of_shift:
            panel_key = current_time.strftime('%d.%m.%y_%H:00')
            panels[panel_key] = {'count': 0, 'list': []}
            current_time += timedelta(hours=1)

        for hlasenie in filtered_hlasenia:
            datum_cas_obj = datetime.strptime(hlasenie['datum_cas'], '%Y-%m-%d %H:%M:%S')
            panel_key = datum_cas_obj.strftime('%d.%m.%y_%H:00')
            if panel_key in panels:
                panels[panel_key]['count'] += 1
                panels[panel_key]['list'].append(hlasenie)

        chronological_panels = sorted(panels.items(), key=lambda item: datetime.strptime(item[0], '%d.%m.%y_%H:00'))
        cumulative_jph = 0
        hours_passed = 0
        calculations = {}
        for panel_key, _ in chronological_panels:
            hours_passed += 1
            current_jph = jph_data.get(panel_key, 0)
            cumulative_jph += current_jph
            cumulative_goal = hourly_goal * hours_passed
            loss = cumulative_jph - cumulative_goal
            calculations[panel_key] = {'cumulative_jph': cumulative_jph, 'loss': int(round(loss))}

        self.ids.total_jph_label.text = f"Celkové JPH smeny: {cumulative_jph} ks"

        sorted_panels = sorted(panels.items(), key=lambda item: datetime.strptime(item[0], '%d.%m.%y_%H:00'), reverse=True)

        if not filtered_hlasenia and all(p['count'] == 0 for p in panels.values()):
             self.ids.poruchy_list.add_widget(
                MDLabel(text="Žiadne hlásenia v aktuálnej smene.", halign="center", adaptive_height=True, padding=[0, "20dp"])
            )
        else:
            for panel_key, panel_data in sorted_panels:
                hodina = datetime.strptime(panel_key, '%d.%m.%y_%H:00').strftime('%H:00')
                count = panel_data['count']

                new_panel = MyExpansionPanel()
                new_panel.panel_key = panel_key
                new_panel.hour_hlasenia = {'jph': jph_data.get(panel_key, 0), 'list': panel_data['list']}

                if panel_key == current_hour_key:
                    new_panel.ids.header_list_item.md_bg_color = self.theme_cls.primaryContainerColor

                panel_calcs = calculations.get(panel_key, {'cumulative_jph': 0, 'loss': 0})
                loss_val = panel_calcs['loss']
                loss_str = f"+{loss_val}" if loss_val >= 0 else str(loss_val)

                base_text = f" | JPH: {panel_calcs['cumulative_jph']} | : {loss_str}"
                headline_text = f"{hodina}: {count}{base_text}" if count > 0 else f"[color=808080]{hodina}: {count}[/color]{base_text}"

                new_panel.ids.headline_text.text = headline_text
                new_panel.ids.jph_button_text.text = str(jph_data.get(panel_key, 0))
                new_panel.ids.jph_button.bind(on_release=lambda _, p=new_panel: self.tap_jph_button(p))

                self.ids.poruchy_list.add_widget(new_panel)
                content_list = new_panel.ids.content_list

                op_groups = {}
                sorted_hlasenia = sorted(panel_data['list'], key=lambda x: x['datum_cas'])
                for hlasenie in sorted_hlasenia:
                    op_key = hlasenie['op']
                    op_groups.setdefault(op_key, []).append(hlasenie)

                farby_pozadia = [
                    "surfaceContainer", "surfaceContainerHigh",
                    "surfaceContainerLow", "surfaceContainerHighest",
                ]
                color_index = 0

                for op, hlasenia_v_skupine in op_groups.items():
                    bg_color_name = farby_pozadia[color_index % len(farby_pozadia)]
                    bg_color = getattr(self.theme_cls, f"{bg_color_name}Color")
                    color_index += 1

                    op_card = MDCard(
                        orientation='vertical',
                        adaptive_height=True,
                        padding="8dp",
                        spacing="8dp",
                        radius=dp(12),
                        md_bg_color=bg_color,
                        style="outlined"
                    )

                    op_card.add_widget(MDLabel(
                        text=f"[{op}]",
                        halign="left",
                        font_style="Body",
                        bold=True,
                        adaptive_height=True,
                        theme_text_color="Secondary"
                    ))

                    for hlasenie in hlasenia_v_skupine:
                        trvanie_minuty = hlasenie.get('trvanie_minuty', 0)
                        poznamka = hlasenie.get('poznamka', '')
                        text_poruchy = hlasenie['porucha']
                        hlasenie_time_str = datetime.strptime(hlasenie['datum_cas'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')
                        cas_a_trvanie_text = f"¦ Čas: {hlasenie_time_str} ¦ | Trvanie: {trvanie_minuty} min |"

                        item_container = MDBoxLayout(
                            orientation='horizontal',
                            adaptive_height=True,
                            padding=("8dp", "4dp"),
                            spacing="8dp"
                        )

                        text_container = MDBoxLayout(
                            orientation='vertical', adaptive_height=True,
                            spacing="4dp", size_hint_x=0.9
                        )

                        text_container.add_widget(MDLabel(
                            text=text_poruchy,
                            font_style="Label",
                            theme_text_color = "Secondary",
                            bold=True,
                            adaptive_height=True,
                        ))

                        text_container.add_widget(MDLabel(
                            text=cas_a_trvanie_text,
                            font_style="Label",
                            text_color = (113, 113, 113, 1),
                            adaptive_height=True,
                        ))

                        if poznamka:
                            text_container.add_widget(MDLabel(
                                text=poznamka,
                                font_style="Label",
                                text_color = (113, 113, 113, 1),
                                adaptive_height=True,
                                padding=(0, "4dp", 0, 0),
                            ))

                        item_container.add_widget(text_container)

                        button_container = MDBoxLayout(
                            orientation='horizontal',
                            adaptive_width=True,
                            spacing="8dp",
                            pos_hint={"center_y": .5}
                        )
                        edit_button = MDIconButton(
                            icon="pencil",
                            on_release=functools.partial(self.go_to_edit_screen, hlasenie)
                        )
                        delete_button = MDIconButton(
                            icon="delete",
                            on_release=functools.partial(self.delete_hlasenie, hlasenie)
                        )
                        button_container.add_widget(edit_button)
                        button_container.add_widget(delete_button)

                        item_container.add_widget(button_container)

                        op_card.add_widget(item_container)

                    content_list.add_widget(op_card)

                # --- NOVÁ LOGIKA PRE TLAČIDLO V OBSAHU ---
                panel_hour_dt = datetime.strptime(panel_key, '%d.%m.%y_%H:00')
                panel_end_time = panel_hour_dt + timedelta(hours=1)

                if panel_end_time < today: # Ak hodina už skončila
                    retro_button = MDButton(
                        MDButtonText(text="+", font_style="Title"),
                        style="text",
                        size_hint_x=1
                    )
                    retro_button.icon = "plus"
                    retro_button.on_release = functools.partial(
                        self.show_op_selection_dialog, new_panel.panel_key
                    )
                    content_list.add_widget(retro_button)
                # --- KONIEC NOVEJ LOGIKY ---

        Clock.schedule_once(self.update_poruchy_list_height)
        Clock.schedule_once(self.force_layout_update)

    def force_layout_update(self, dt):
        self.ids.poruchy_list.do_layout()
        self.ids.main_scroll_view.scroll_y = 1

    def tap_jph_button(self, panel):
        MDApp.get_running_app().show_jph_menu(panel)

    def show_op_selection_dialog(self, target_panel_key=None):
        self.retroactive_fault_target = target_panel_key

        if self.dialog:
            self.dialog.dismiss()

        data = load_ops_poruchy()
        ops = data.get('ops', [])
        if not ops:
            MDSnackbar(MDSnackbarText(text="Najprv pridajte OP v nastaveniach.")).open()
            return

        content_container = MDDialogContentContainer()
        scroll = MDScrollView(size_hint_y=None, height=Window.height / 2.5)

        button_grid = MDGridLayout(
            cols=3,
            adaptive_height=True,
            spacing="8dp",
            padding="8dp",
            row_force_default=True,
            row_default_height=dp(52)
        )

        for op in sorted(ops, key=op_sort_key):
            btn = MDButton(
                MDButtonText(text=op),
                style="tonal",
                on_release=functools.partial(self.show_porucha_selection_dialog, op)
            )
            button_grid.add_widget(btn)

        scroll.add_widget(button_grid)
        content_container.add_widget(scroll)

        dialog_title = "Krok 1: Vyberte OP"
        if target_panel_key:
            hour_str = datetime.strptime(target_panel_key, '%d.%m.%y_%H:00').strftime('%H:00')
            dialog_title = f"Pridať pre {hour_str} | Krok 1: OP"

        self.dialog = MDDialog(
            MDDialogHeadlineText(text=dialog_title),
            content_container,
        )
        self.dialog.open()

    def go_to_settings_for_op(self, op, resume_workflow=False):
        self.dialog.dismiss()
        self.dialog = None
        nastavenie_screen = self.manager.get_screen('nastavenie')
        nastavenie_screen.setup_porucha_mode(op, resume=resume_workflow)
        self.manager.current = 'nastavenie'

    def show_porucha_selection_dialog(self, selected_op, *args):
        if self.dialog:
            self.dialog.dismiss()

        data = load_ops_poruchy()
        poruchy = data.get('poruchy_pre_op', {}).get(selected_op, [])

        content_container = MDDialogContentContainer()
        scroll = MDScrollView(size_hint_y=None, height=Window.height / 2.5)
        button_box = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing="8dp", padding="8dp")

        if not poruchy:
             button_box.add_widget(MDLabel(text="Pre toto OP nie sú definované žiadne poruchy.", adaptive_height=True, halign="center"))
        else:
            for porucha in sorted(poruchy):
                btn = MDButton(
                    MDButtonText(text=porucha),
                    style="tonal",
                    on_release=functools.partial(self.show_duration_selection_dialog, selected_op, porucha)
                )
                button_box.add_widget(btn)

        scroll.add_widget(button_box)
        content_container.add_widget(scroll)

        dialog_title = f"Krok 2: Porucha pre {selected_op}"
        if self.retroactive_fault_target:
            hour_str = datetime.strptime(self.retroactive_fault_target, '%d.%m.%y_%H:00').strftime('%H:00')
            dialog_title = f"Pridať pre {hour_str} | Krok 2: Porucha"

        self.dialog = MDDialog(
            MDDialogHeadlineText(text=dialog_title),
            content_container,
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="PRIDAŤ NOVÚ PORUCHU"), style="text",
                         on_release=lambda x: self.go_to_settings_for_op(selected_op, resume_workflow=True)),
                spacing="8dp",
            ),
        )
        self.dialog.open()

    def show_duration_selection_dialog(self, selected_op, selected_porucha, *args):
        if self.dialog:
            self.dialog.dismiss()

        content_container = MDDialogContentContainer()
        scroll = MDScrollView(size_hint_y=None, height=Window.height / 2.5)
        grid = MDGridLayout(cols=5, adaptive_height=True, spacing="8dp", padding="8dp")

        for i in range(1, 61):
            btn = MDButton(
                MDButtonText(text=str(i)),
                style="tonal",
                on_release=functools.partial(self.show_note_dialog, selected_op, selected_porucha, i)
            )
            grid.add_widget(btn)

        scroll.add_widget(grid)
        content_container.add_widget(scroll)

        dialog_title = "Krok 3: Trvanie v minútach"
        if self.retroactive_fault_target:
            hour_str = datetime.strptime(self.retroactive_fault_target, '%d.%m.%y_%H:00').strftime('%H:00')
            dialog_title = f"Pridať pre {hour_str} | Krok 3: Trvanie"

        self.dialog = MDDialog(
            MDDialogHeadlineText(text=dialog_title),
            content_container,
        )
        self.dialog.open()

    def show_note_dialog(self, op, porucha, duration, *args):
        if self.dialog:
            self.dialog.dismiss()

        note_field = MDTextField(hint_text="Poznámka (voliteľné)", mode="outlined")
        content = MDDialogContentContainer(note_field)

        dialog_title = "Krok 4: Pridať poznámku"
        if self.retroactive_fault_target:
            hour_str = datetime.strptime(self.retroactive_fault_target, '%d.%m.%y_%H:00').strftime('%H:00')
            dialog_title = f"Pridať pre {hour_str} | Krok 4: Poznámka"

        self.note_dialog = MDDialog(
            MDDialogHeadlineText(text=dialog_title),
            content,
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="ULOŽIŤ BEZ POZNÁMKY"),
                    style="text",
                    on_release=lambda x: self.save_new_fault(op, porucha, duration, "")
                ),
                MDButton(
                    MDButtonText(text="ULOŽIŤ"),
                    style="text",
                    on_release=lambda x: self.save_new_fault(op, porucha, duration, note_field.text)
                ),
            ),
        )
        self.note_dialog.open()

    def save_new_fault(self, op, porucha, duration, note="", *args):
        if self.note_dialog and self.note_dialog.parent:
            self.note_dialog.dismiss()

        app = MDApp.get_running_app()
        app.fault_in_progress = {}

        if self.retroactive_fault_target:
            panel_key = self.retroactive_fault_target
            panel_hour_dt = datetime.strptime(panel_key, '%d.%m.%y_%H:00')
            save_time_dt = panel_hour_dt + timedelta(hours=1) - timedelta(seconds=1)
            save_time_str = save_time_dt.strftime('%Y-%m-%d %H:%M:%S')
            self.retroactive_fault_target = None
        else:
            save_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        data = load_hlasenia()
        hlasenie = {
            'datum_cas': save_time_str,
            'op': op,
            'porucha': porucha,
            'trvanie_minuty': duration,
            'poznamka': note.strip()
        }
        data.setdefault('hlasenia', []).append(hlasenie)
        save_hlasenia(data)

        MDSnackbar(MDSnackbarText(text=f"Hlásenie pre {op} uložené!")).open()
        self.update_poruchy_list()


class NastavenieScreen(MDScreen):
    # ... (trieda je nezmenená) ...
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.op_to_save_porucha = None
        self.resume_workflow_on_save = False
        self.available_colors = [color for category in COLOR_CATEGORIES.values() for color in sorted(category)]
        self.current_color_index = 0

    def on_enter(self, *args):
        settings = load_settings()
        current_color = settings.get('primary_palette', 'Lightgreen')

        if current_color in self.available_colors:
            self.current_color_index = self.available_colors.index(current_color)

        self.update_color_button_text()
        theme_style_text = "Svetlá" if settings.get('theme_style') == 'Light' else "Tmavá"
        self.ids.theme_button_text.text = f"Téma: {theme_style_text}"

    def setup_porucha_mode(self, op_value, resume=False):
        self.ids.op_input.text = op_value
        self.ids.op_input.disabled = True
        self.ids.porucha_input.text = ""
        self.ids.porucha_input.focus = True
        self.op_to_save_porucha = op_value
        self.resume_workflow_on_save = resume

    def go_back_to_hlavna(self):
        self.ids.op_input.text = ""
        self.ids.op_input.disabled = False
        self.ids.porucha_input.text = ""
        self.op_to_save_porucha = None
        self.resume_workflow_on_save = False
        self.manager.current = 'hlavna'

    def ulozit_op_a_poruchu(self):
        op = self.ids.op_input.text.strip().upper()
        porucha = self.ids.porucha_input.text.strip()
        if self.op_to_save_porucha:
            op = self.op_to_save_porucha

        if not (op and porucha):
            MDSnackbar(MDSnackbarText(text="Zadajte OP aj Poruchu!")).open()
            return

        data = load_ops_poruchy()
        if op not in data['ops']:
            data['ops'].append(op)

        poruchy_pre_op = data.setdefault('poruchy_pre_op', {})
        op_poruchy = poruchy_pre_op.setdefault(op, [])

        if porucha not in op_poruchy:
            op_poruchy.append(porucha)
            save_ops_poruchy(data)

            if self.resume_workflow_on_save:
                app = MDApp.get_running_app()
                app.fault_in_progress = {'op': op, 'porucha': porucha}
                self.go_back_to_hlavna()
            else:
                MDSnackbar(MDSnackbarText(text=f"Porucha '{porucha}' pre OP '{op}' uložená!")).open()
                self.ids.porucha_input.text = ''
                if not self.op_to_save_porucha:
                    self.ids.op_input.text = ''
        else:
            MDSnackbar(MDSnackbarText(text=f"Porucha '{porucha}' už pre toto OP existuje!")).open()

    def update_color_button_text(self):
        color_name = self.available_colors[self.current_color_index]
        self.ids.color_button_text.text = color_name.capitalize()

    def set_primary_palette(self, color_name):
        app = MDApp.get_running_app()
        app.theme_cls.primary_palette = color_name

        if color_name in self.available_colors:
            self.current_color_index = self.available_colors.index(color_name)

        self.update_color_button_text()

        settings = load_settings()
        settings['primary_palette'] = color_name
        save_settings(settings)

        MDSnackbar(MDSnackbarText(text=f"Farba témy zmenená na {color_name.capitalize()}!")).open()
        if hasattr(self, 'color_menu') and self.color_menu.parent:
            self.color_menu.dismiss()

    def change_color_by_arrow(self, direction: int):
        self.current_color_index = (self.current_color_index + direction) % len(self.available_colors)
        new_color = self.available_colors[self.current_color_index]
        self.set_primary_palette(new_color)

    def show_color_menu(self):
        menu_items = []
        for category_name, colors in COLOR_CATEGORIES.items():
            menu_items.append({"text": f"--- {category_name} ---", "divider": "Full"})
            for color_name in sorted(colors):
                hex_code = COLOR_HEX_MAP.get(color_name, '#000000')
                text_color = get_color_from_hex('#000000') if hex_code.upper() in ['#FFFFFF', '#F0F8FF', '#F0FFFF', '#FFF8DC', '#F8F8FF', '#DCDCDC', '#E6E6FA', '#FFF0F5', '#FFFAF0', '#F0FFF0', '#FFFFF0', '#FAF0E6', '#F5FFFA', '#FFF5EE', '#FFFAFA', '#FFE4E1', '#FFEBCD', '#FFE4C4', '#FAEBD7', '#FFFACD', '#FAFAD2', '#FFFFE0', '#FFEFD5', '#FFDAB9', '#FDF5E6', '#F5DEB3', '#FFE4B5', '#FFDEAD', '#D3D3D3', '#C0C0C0', '#F5F5F5', '#F5F5DC'] else get_color_from_hex(hex_code)
                menu_items.append({
                    "text": color_name.capitalize(),
                    "text_color": text_color,
                    "theme_text_color": "Custom",
                    "on_release": lambda x=color_name: self.set_primary_palette(x),
                })
        self.color_menu = MDDropdownMenu(
            caller=self.ids.color_button, items=menu_items, width=max(self.ids.color_button.width, dp(250)), max_height=dp(600), radius=[20, 7, 20, 7]
        )
        self.color_menu.open()

    def show_theme_menu(self):
        menu_items = [
            {"text": "Svetlá", "on_release": lambda: self.set_theme_style("Light")},
            {"text": "Tmavá", "on_release": lambda: self.set_theme_style("Dark")}
        ]
        self.theme_menu = MDDropdownMenu(
            caller=self.ids.theme_button, items=menu_items, width=self.ids.theme_button.width, radius=[20, 7, 20, 7]
        )
        self.theme_menu.open()

    def set_theme_style(self, theme_style):
        MDApp.get_running_app().theme_cls.theme_style = theme_style
        theme_style_text = "Svetlá" if theme_style == 'Light' else "Tmavá"
        self.ids.theme_button_text.text = f"Téma: {theme_style_text}"
        settings = load_settings()
        settings['theme_style'] = theme_style
        save_settings(settings)
        MDSnackbar(MDSnackbarText(text=f"Téma zmenená na {theme_style_text}!")).open()
        self.theme_menu.dismiss()


class SearchScreen(MDScreen):
    # ... (trieda je nezmenená) ...
    DEFAULT_STATS = {
        "total_faults": 0,
        "total_downtime": 0,
        "avg_downtime": 0.0,
        "total_jph": 0,
        "top_op_freq_str": "-",
        "top_op_time_str": "-",
        "top_porucha_freq_str": "-",
        "top_porucha_time_str": "-",
        "title_text": "Súhrnné štatistiky"
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_date = None
        self.selected_shifts = {"Denná", "Nočná"}
        self.filter_dialog = None
        self.stats_dialog = None
        self.stats_content_obj = None
        self.current_stats = self.DEFAULT_STATS.copy()

    def on_enter(self, *args):
        self.selected_date = None
        self.selected_shifts = {"Denná", "Nočná"}
        Clock.schedule_once(lambda dt: self.search_hlasenia())

    def on_leave(self, *args):
        self.close_filter_dialog()
        self.close_stats_dialog()

        self.selected_date = None
        self.selected_shifts = {"Denná", "Nočná"}
        self.current_stats = self.DEFAULT_STATS.copy()

        self.ids.search_results_list.clear_widgets()
        if not any(isinstance(child, MDLabel) and "kliknite na ikonu filtra" in child.text for child in self.ids.search_results_list.children):
            self.ids.search_results_list.add_widget(
                MDLabel(
                    text="Pre zobrazenie výsledkov kliknite na ikonu filtra vpravo hore.",
                    halign="center",
                    adaptive_height=True,
                    padding=[0, "20dp"]
                )
            )
        super().on_leave(*args)

    def on_filter_dialog_dismiss(self, *args):
        self.filter_dialog = None

    def on_stats_dialog_dismiss(self, *args):
        self.stats_dialog = None

    def close_filter_dialog(self, *args):
        if self.filter_dialog:
            self.filter_dialog.dismiss()

    def close_stats_dialog(self, *args):
         if self.stats_dialog:
             self.stats_dialog.dismiss()

    def open_filter_dialog(self):
        if self.filter_dialog:
            self.filter_dialog.open()
            return

        date_button_text = self.selected_date.strftime('%d.%m.%Y') if self.selected_date else "Vybrať dátum (Všetky)"
        date_button = MDButton(
            MDButtonText(text=date_button_text),
            style="outlined",
        )
        date_button.on_release = lambda btn=date_button: self.show_dialog_date_picker(btn)

        switch_box = MDBoxLayout(orientation='vertical', adaptive_height=True, spacing="8dp")
        denna_row = MDBoxLayout(adaptive_height=True, spacing="8dp")
        denna_row.add_widget(MDLabel(text="Denná", adaptive_size=True, pos_hint={"center_y": 0.5}))
        denna_switch = MDSwitch()
        denna_switch.active = "Denná" in self.selected_shifts
        denna_switch.bind(active=lambda instance, value: self.on_shift_switch_active("Denná", value))
        denna_row.add_widget(denna_switch)
        switch_box.add_widget(denna_row)

        nocna_row = MDBoxLayout(adaptive_height=True, spacing="8dp")
        nocna_row.add_widget(MDLabel(text="Nočná", adaptive_size=True, pos_hint={"center_y": 0.5}))
        nocna_switch = MDSwitch()
        nocna_switch.active = "Nočná" in self.selected_shifts
        nocna_switch.bind(active=lambda instance, value: self.on_shift_switch_active("Nočná", value))
        nocna_row.add_widget(nocna_switch)
        switch_box.add_widget(nocna_row)

        dialog_content = MDDialogContentContainer(
            MDBoxLayout(
                MDLabel(text="Dátum:", adaptive_height=True, font_style="Body"),
                date_button,
                MDLabel(text="Smena:", adaptive_height=True, font_style="Body", padding=[0, "12dp", 0, 0]),
                switch_box,
                orientation="vertical",
                spacing="12dp",
                adaptive_height=True,
            )
        )

        self.filter_dialog = MDDialog(
            MDDialogHeadlineText(text="Filter vyhľadávania"),
            dialog_content,
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="ZRUŠIŤ DÁTUM"), style="text", on_release=self.clear_date_filter_from_dialog),
                MDButton(MDButtonText(text="ZAVRIEŤ"), style="text", on_release=self.close_filter_dialog),
                MDButton(MDButtonText(text="VYHĽADAŤ"), style="text", on_release=self.search_from_dialog),
            ),
        )
        self.filter_dialog.on_dismiss = self.on_filter_dialog_dismiss
        self.filter_dialog.open()

    def clear_date_filter_from_dialog(self, *args):
        self.selected_date = None
        if self.filter_dialog:
             content_box = self.filter_dialog.content_widget.children[0]
             date_button = content_box.children[-2]
             if isinstance(date_button, MDButton):
                 date_button.children[0].text = "Vybrať dátum (Všetky)"

        self.search_hlasenia()
        self.close_filter_dialog()
        MDSnackbar(MDSnackbarText(text="Filter dátumu bol zrušený. Zobrazujú sa všetky dáta.")).open()

    def on_shift_switch_active(self, shift_name: str, is_active: bool):
        if is_active:
            self.selected_shifts.add(shift_name)
        else:
            self.selected_shifts.discard(shift_name)

    def show_dialog_date_picker(self, date_button_in_dialog):
        date_picker = MDDockedDatePicker()

        current_date_to_set = self.selected_date if self.selected_date else datetime.now().date()
        date_picker.year = current_date_to_set.year
        date_picker.month = current_date_to_set.month
        date_picker.day = current_date_to_set.day

        date_picker.bind(
            on_ok=functools.partial(self.on_dialog_date_ok, date_button_in_dialog),
            on_cancel=lambda instance: instance.dismiss()
        )

        date_picker.open()

    def on_dialog_date_ok(self, date_button_in_dialog, instance_date_picker):
        self.selected_date = instance_date_picker.get_date()[0]
        date_button_in_dialog.children[0].text = self.selected_date.strftime('%d.%m.%Y')
        instance_date_picker.dismiss()

    def search_from_dialog(self, *args):
        self.search_hlasenia()
        self.close_filter_dialog()

    def search_hlasenia(self):
        all_hlasenia = load_hlasenia().get('hlasenia', [])
        jph_data = load_jph()

        results = []
        overall_start = None
        overall_end = None

        shift_text = ", ".join(sorted(list(self.selected_shifts))) if self.selected_shifts else "žiadna"

        if self.selected_date:
            title_text = f"Súhrn pre {self.selected_date.strftime('%d.%m.%Y')} ({shift_text})"
            day_start = datetime.combine(self.selected_date, datetime.min.time())

            if "Denná" in self.selected_shifts:
                timeframe_start_d = day_start.replace(hour=6)
                timeframe_end_d = day_start.replace(hour=18)
                results.extend([
                    h for h in all_hlasenia
                    if timeframe_start_d <= datetime.strptime(h['datum_cas'], '%Y-%m-%d %H:%M:%S') < timeframe_end_d
                ])
                if overall_start is None: overall_start = timeframe_start_d
                overall_end = timeframe_end_d

            if "Nočná" in self.selected_shifts:
                timeframe_start_n = day_start.replace(hour=18)
                timeframe_end_n = day_start.replace(hour=6) + timedelta(days=1)
                results.extend([
                    h for h in all_hlasenia
                    if timeframe_start_n <= datetime.strptime(h['datum_cas'], '%Y-%m-%d %H:%M:%S') < timeframe_end_n
                ])
                if overall_start is None: overall_start = timeframe_start_n
                overall_end = timeframe_end_n

            if "Denná" in self.selected_shifts and "Nočná" in self.selected_shifts:
                overall_start = day_start.replace(hour=6)
                overall_end = day_start.replace(hour=6) + timedelta(days=1)

        else:
            title_text = f"Súhrn za celý čas ({shift_text})"
            overall_start = None
            overall_end = None

            for h in all_hlasenia:
                h_dt = datetime.strptime(h['datum_cas'], '%Y-%m-%d %H:%M:%S')
                h_hour = h_dt.hour
                is_denna = 6 <= h_hour < 18
                is_nocna = not is_denna

                if ("Denná" in self.selected_shifts and is_denna) or \
                   ("Nočná" in self.selected_shifts and is_nocna):
                    results.append(h)

        unique_results = list({v['datum_cas']:v for v in results}.values())
        unique_results.sort(key=lambda x: x['datum_cas'])

        total_faults = len(unique_results)
        total_downtime = 0
        avg_downtime = 0.0
        op_freq = Counter()
        porucha_freq = Counter()
        op_time = defaultdict(int)
        porucha_time = defaultdict(int)

        if total_faults > 0:
            for hlasenie in unique_results:
                duration = hlasenie.get('trvanie_minuty', 0)
                op = hlasenie.get('op', 'N/A')
                porucha = hlasenie.get('porucha', 'N/A')

                total_downtime += duration
                op_freq[op] += 1
                porucha_freq[porucha] += 1
                op_time[op] += duration
                porucha_time[porucha] += duration

            avg_downtime = total_downtime / total_faults

        def format_top3(counter_data):
            if not counter_data: return "-"
            sorted_items = sorted(counter_data.items(), key=lambda item: item[1], reverse=True)
            return "\n".join([f"{i+1}. {name}: {value}" for i, (name, value) in enumerate(sorted_items[:3])])

        top_op_freq_str = format_top3(op_freq)
        top_op_time_str = format_top3(op_time)
        top_porucha_freq_str = format_top3(porucha_freq)
        top_porucha_time_str = format_top3(porucha_time)

        total_jph = 0
        all_jph_keys = [k for k in jph_data.keys() if '_' in k] # Filter keys that look like dates/hours

        for key in all_jph_keys:
            try:
                # Key is typically 'dd.mm.yy_HH:00'
                dt_str = key.split(':')[0] # Remove ':00' if present
                dt_obj = datetime.strptime(dt_str, '%d.%m.%y_%H')
            except ValueError: 
                # Skip keys that are goals or plans (e.g. 'goal_...')
                continue

            if self.selected_date and (overall_start is not None and overall_end is not None):
                 if not (overall_start <= dt_obj < overall_end):
                     continue
            elif self.selected_date and (overall_start is None or overall_end is None):
                 continue # Should not happen if selected_date is set

            h_hour = dt_obj.hour
            is_denna = 6 <= h_hour < 18
            is_nocna = not is_denna

            if ("Denná" in self.selected_shifts and is_denna) or \
               ("Nočná" in self.selected_shifts and is_nocna):
                total_jph += jph_data.get(key, 0) # Use .get for robustness

        self.current_stats = {
            "total_faults": total_faults, "total_downtime": total_downtime,
            "avg_downtime": avg_downtime, "total_jph": total_jph,
            "top_op_freq_str": top_op_freq_str, "top_op_time_str": top_op_time_str,
            "top_porucha_freq_str": top_porucha_freq_str, "top_porucha_time_str": top_porucha_time_str,
            "title_text": title_text
        }

        self.display_search_results(unique_results, jph_data, overall_start, overall_end)

    def display_search_results(self, results, jph_data, timeframe_start, timeframe_end):
        self.ids.search_results_list.clear_widgets()

        title_text = self.current_stats['title_text'].replace("Súhrn", "Výsledky")

        self.ids.search_results_list.add_widget(
            MDLabel(text=title_text, halign="center", adaptive_height=True, font_style="Title")
        )

        if not results and self.current_stats['total_jph'] == 0:
            self.ids.search_results_list.add_widget(MDLabel(text="Žiadne dáta na zobrazenie.", halign="center", adaptive_height=True, padding=[0, "16dp"]))
            return

        panels = {}

        if self.selected_date and timeframe_start and timeframe_end:
            current_hour = timeframe_start.replace(minute=0, second=0, microsecond=0)
            while current_hour < timeframe_end:
                panel_key = current_hour.strftime('%d.%m.%y_%H:00')
                panels[panel_key] = {'count': 0, 'list': []}
                current_hour += timedelta(hours=1)

        for hlasenie in results:
            datum_cas_obj = datetime.strptime(hlasenie['datum_cas'], '%Y-%m-%d %H:%M:%S')
            panel_key = datum_cas_obj.strftime('%d.%m.%y_%H:00')

            if self.selected_date:
                if panel_key in panels:
                    panels[panel_key]['count'] += 1
                    panels[panel_key]['list'].append(hlasenie)
            else:
                if panel_key not in panels:
                    panels[panel_key] = {'count': 0, 'list': []}
                panels[panel_key]['count'] += 1
                panels[panel_key]['list'].append(hlasenie)

        sorted_panels = sorted(panels.items(), key=lambda item: datetime.strptime(item[0], '%d.%m.%y_%H:00'), reverse=True)

        has_data_to_show = False
        for panel_key, panel_data in sorted_panels:
            hodina_obj = datetime.strptime(panel_key, '%d.%m.%y_%H:00')
            hodina_num = hodina_obj.hour
            panel_jph = jph_data.get(panel_key, 0)

            is_denna = 6 <= hodina_num < 18
            is_nocna = not is_denna
            if not (("Denná" in self.selected_shifts and is_denna) or \
                    ("Nočná" in self.selected_shifts and is_nocna)):
                continue

            if panel_data['count'] > 0 or panel_jph > 0:
                has_data_to_show = True
                hodina = hodina_obj.strftime('%H:%M')
                if not self.selected_date:
                    hodina = f"{hodina_obj.strftime('%d.%m.%y')} | {hodina}"

                new_panel = MyExpansionPanel()

                headline_text = f"{hodina} | Poruchy: {panel_data['count']}"
                new_panel.ids.headline_text.text = headline_text

                new_panel.ids.jph_button_text.text = str(panel_jph)
                new_panel.ids.jph_button.disabled = True

                panel_data['list'].sort(key=lambda x: x['datum_cas'])
                for hlasenie in panel_data['list']:
                    hlasenie_time = datetime.strptime(hlasenie['datum_cas'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')
                    item = MDListItem(
                        MDListItemHeadlineText(text=f"{hlasenie['op']} ({hlasenie_time})"),
                        MDListItemSupportingText(text=hlasenie['porucha']),
                        MDListItemTertiaryText(text=f"Trvanie: {hlasenie.get('trvanie_minuty', 0)} min"),
                        size_hint_y=None,
                        height=dp(88)
                    )
                    new_panel.ids.content_list.add_widget(item)

                self.ids.search_results_list.add_widget(new_panel)

        if not has_data_to_show:
             self.ids.search_results_list.add_widget(MDLabel(text="Žiadne dáta na zobrazenie pre daný filter.", halign="center", adaptive_height=True, padding=[0, "16dp"]))

    def show_statistics_dialog(self):
        if not self.stats_dialog:
            self.stats_content_obj = StatisticsDialogContent()
            self.stats_dialog = MDDialog(
                MDDialogContentContainer(self.stats_content_obj),
                MDDialogButtonContainer(
                    MDButton(
                        MDButtonText(text="ZAVRIEŤ"),
                        style="text",
                        on_release=self.close_stats_dialog
                    ),
                ),
            )
            self.stats_dialog.on_dismiss = self.on_stats_dialog_dismiss

        stats = self.current_stats
        content_ids = self.stats_content_obj.ids

        content_ids.stats_title.text = stats['title_text']
        content_ids.stats_total_faults.text = f"Celkový počet porúch: {stats['total_faults']}"
        content_ids.stats_total_downtime.text = f"Celkové trvanie porúch: {stats['total_downtime']} min ({stats['total_downtime']/60:.2f} hod)"
        content_ids.stats_avg_downtime.text = f"Priemerné trvanie poruchy: {stats['avg_downtime']:.1f} min"
        content_ids.stats_total_jph.text = f"Celkové JPH: {stats['total_jph']} ks"
        content_ids.stats_top_op_freq_data.text = stats['top_op_freq_str']
        content_ids.stats_top_op_time_data.text = stats['top_op_time_str']
        content_ids.stats_top_porucha_freq_data.text = stats['top_porucha_freq_str']
        content_ids.stats_top_porucha_time_data.text = stats['top_porucha_time_str']

        if self.stats_dialog:
            self.stats_dialog.open()


class JPHScreen(MDScreen):
    # ... (trieda je nezmenená) ...
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.filter_dialog = None
        self.selected_shifts_filter = {"Denná", "Nočná"}
        self.start_date = None
        self.end_date = None
        self.start_date_button = None
        self.end_date_button = None

    def on_enter(self, *args):
        self._reset_filter_data()
        self.load_and_display_shifts()

    def on_leave(self, *args):
        if self.filter_dialog:
            self.filter_dialog.dismiss()
        super().on_leave(*args)

    def on_filter_dialog_dismiss(self, *args):
        self.filter_dialog = None

    def go_back_to_hlavna(self):
        self.manager.current = 'hlavna'

    def show_filter_dialog(self):
        if not self.filter_dialog:
            content_layout = MDBoxLayout(
                orientation="vertical",
                spacing="16dp",
                padding="16dp",
                adaptive_height=True,
            )

            content_layout.add_widget(
                MDLabel(text="Filter podľa obdobia:", adaptive_height=True, font_style="Body")
            )

            date_range_box = MDBoxLayout(adaptive_height=True, spacing="8dp")
            start_date_text = self.start_date.strftime('%d.%m.%y') if self.start_date else "Dátum od"
            end_date_text = self.end_date.strftime('%d.%m.%y') if self.end_date else "Dátum do"

            self.start_date_button = MDButton(MDButtonText(text=start_date_text), style="outlined")
            self.end_date_button = MDButton(MDButtonText(text=end_date_text), style="outlined")

            self.start_date_button.on_release = self.show_start_date_picker
            self.end_date_button.on_release = self.show_end_date_picker

            date_range_box.add_widget(self.start_date_button)
            date_range_box.add_widget(self.end_date_button)
            content_layout.add_widget(date_range_box)

            content_layout.add_widget(
                MDLabel(text="Filter podľa smeny:", adaptive_height=True, font_style="Body", padding=[0,"12dp",0,0])
            )

            switch_box = MDBoxLayout(
                orientation='vertical',
                adaptive_height=True,
                spacing="8dp"
            )

            denna_row = MDBoxLayout(adaptive_height=True, spacing="8dp")
            denna_row.add_widget(MDLabel(text="Denná", adaptive_size=True, pos_hint={"center_y": 0.5}))
            denna_switch = MDSwitch()
            denna_switch.active = "Denná" in self.selected_shifts_filter
            denna_switch.bind(active=lambda instance, value: self.on_shift_switch_active("Denná", value))
            denna_row.add_widget(denna_switch)
            switch_box.add_widget(denna_row)

            nocna_row = MDBoxLayout(adaptive_height=True, spacing="8dp")
            nocna_row.add_widget(MDLabel(text="Nočná", adaptive_size=True, pos_hint={"center_y": 0.5}))
            nocna_switch = MDSwitch()
            nocna_switch.active = "Nočná" in self.selected_shifts_filter
            nocna_switch.bind(active=lambda instance, value: self.on_shift_switch_active("Nočná", value))
            nocna_row.add_widget(nocna_switch)
            switch_box.add_widget(nocna_row)

            content_layout.add_widget(switch_box)

            self.filter_dialog = MDDialog(
                MDDialogHeadlineText(text="Filter"),
                MDDialogContentContainer(content_layout),
                MDDialogButtonContainer(
                    MDButton(MDButtonText(text="ZRUŠIŤ FILTRE"), style="text", on_release=self.clear_all_filters),
                    MDButton(MDButtonText(text="ZAVRIEŤ"), style="text", on_release=lambda x: self.filter_dialog.dismiss()),
                ),
            )
            self.filter_dialog.on_dismiss = self.on_filter_dialog_dismiss

        self.filter_dialog.open()

    def show_start_date_picker(self):
        date_picker = MDDockedDatePicker()
        if self.start_date:
             date_picker.set_date(self.start_date)
        date_picker.bind(on_ok=self.set_start_date)
        date_picker.open()

    def set_start_date(self, picker_instance):
        date_obj = picker_instance.get_date()[0]
        self.start_date = date_obj
        if self.start_date_button:
            self.start_date_button.children[0].text = date_obj.strftime('%d.%m.%y')
        self.load_and_display_shifts()
        picker_instance.dismiss()

    def show_end_date_picker(self):
        date_picker = MDDockedDatePicker()
        if self.end_date:
             date_picker.set_date(self.end_date)
        date_picker.bind(on_ok=self.set_end_date)
        date_picker.open()

    def set_end_date(self, picker_instance):
        date_obj = picker_instance.get_date()[0]
        self.end_date = date_obj
        if self.end_date_button:
            self.end_date_button.children[0].text = date_obj.strftime('%d.%m.%y')
        self.load_and_display_shifts()
        picker_instance.dismiss()

    def on_shift_switch_active(self, shift_name: str, is_active: bool):
        if is_active:
            self.selected_shifts_filter.add(shift_name)
        else:
            self.selected_shifts_filter.discard(shift_name)

        self.load_and_display_shifts()

    def _reset_filter_data(self):
        self.start_date = None
        self.end_date = None
        self.selected_shifts_filter = {"Denná", "Nočná"}

    def clear_all_filters(self, *args, show_snackbar=True):
        self._reset_filter_data()

        if self.start_date_button: self.start_date_button.children[0].text = "Dátum od"
        if self.end_date_button: self.end_date_button.children[0].text = "Dátum do"

        if self.filter_dialog:
            self.filter_dialog.dismiss()

        self.load_and_display_shifts()
        if show_snackbar:
            MDSnackbar(MDSnackbarText(text="Všetky filtre boli zrušené.")).open()

    def save_shift_plan(self):
        MDSnackbar(MDSnackbarText(text="Funkcia ukladania plánu bola odstránená.")).open()

    def confirm_delete_shift(self, shift_key):
        if hasattr(self, 'dialog') and self.dialog:
            self.dialog.dismiss()

        date_obj, shift_type = shift_key
        shift_text = "dennú" if shift_type == "D" else "nočnú"

        self.dialog = MDDialog(
            MDDialogHeadlineText(text="Vymazať smenu?"),
            MDDialogSupportingText(text=f"Naozaj chcete natrvalo vymazať všetky JPH záznamy a plán pre {shift_text} smenu dňa {date_obj.strftime('%d.%m.%Y')}?"),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Zrušiť"), style="text", on_release=lambda x: self.dialog.dismiss()),
                MDButton(MDButtonText(text="Vymazať"), style="text", on_release=lambda x: self.delete_shift(shift_key)),
                spacing="8dp",
            ),
        )
        self.dialog.open()

    def delete_shift(self, shift_key):
        if hasattr(self, 'dialog') and self.dialog:
            self.dialog.dismiss()

        date_obj, shift_type = shift_key
        jph_data = load_jph()
        keys_to_delete = []

        goal_key = f"goal_{date_obj.strftime('%d.%m.%y')}_{shift_type}"
        if goal_key in jph_data:
            keys_to_delete.append(goal_key)

        plan_key = f"plan_{date_obj.strftime('%d.%m.%y')}_{shift_type}"
        # Ponechané pre prípad, že kľúč "plan" bol predtým používaný a je v súbore
        if plan_key in jph_data:
            keys_to_delete.append(plan_key)

        start_date_for_del = date_obj
        start_hour = 6 if shift_type == 'D' else 18

        current_time = datetime.combine(start_date_for_del, datetime.min.time()).replace(hour=start_hour)

        for _ in range(12):
            hour_key = current_time.strftime('%d.%m.%y_%H:00')
            if hour_key in jph_data:
                keys_to_delete.append(hour_key)
            current_time += timedelta(hours=1)

        if not keys_to_delete:
            MDSnackbar(MDSnackbarText(text="Nenašli sa žiadne záznamy na vymazanie.")).open()
            return

        for key in keys_to_delete:
            if key in jph_data:
                del jph_data[key]

        save_jph(jph_data)
        MDSnackbar(MDSnackbarText(text="Smena bola vymazaná.")).open()
        self.load_and_display_shifts()

    @staticmethod
    def get_shift_info_from_datetime(dt_obj):
        if 6 <= dt_obj.hour < 18:
            return dt_obj.date(), 'D'
        effective_date = dt_obj.date() if dt_obj.hour >= 18 else (dt_obj - timedelta(days=1)).date()
        return effective_date, 'N'

    def load_and_display_shifts(self):
        jph_data = load_jph()
        shifts = {}
    
        # 1. Spracovanie všetkých kľúčov z jph.json
        for key, value in jph_data.items():
            try:
                # Value môže byť uložená ako string, musíme konvertovať na int
                if isinstance(value, str) and value.isdigit():
                    value = int(value)
                elif not isinstance(value, int):
                    continue # Skip non-integer or non-digit string values
    
                # Cieľ na smenu: goal_21.11.25_D = 6000 (ks za celú smenu)
                if key.startswith('goal_'):
                    parts = key.split('_')
                    if len(parts) != 3:
                        continue
                    _, date_str, shift_type = parts
                    date_obj = datetime.strptime(date_str, '%d.%m.%y').date()
                    shift_key = (date_obj, shift_type)
    
                    shifts.setdefault(shift_key, {
                        'total_made': 0,
                        'goal_shift': 0,      # celkový cieľ na smenu
                        'goal_jph': 0         # JPH = cieľ / 12
                    })
                    shifts[shift_key]['goal_shift'] = value
                    shifts[shift_key]['goal_jph'] = value // 12
    
                # Hodinové záznamy: dd.mm.yy_HH:00 = 520 (vyrobené v tej hodine)
                elif '_' in key and not key.startswith('goal_') and not key.startswith('plan_'):
                    clean_key = key.split(':')[0]  # pre prípad, že je tam :00
                    dt_obj = datetime.strptime(clean_key, '%d.%m.%y_%H')
                    shift_date, shift_type = self.get_shift_info_from_datetime(dt_obj)
                    shift_key = (shift_date, shift_type)
    
                    shifts.setdefault(shift_key, {
                        'total_made': 0,
                        'goal_shift': 0,
                        'goal_jph': 0
                    })
                    shifts[shift_key]['total_made'] += value
    
                # Starý formát plan_... ignorujeme
                elif key.startswith('plan_'):
                    continue
    
            except (ValueError, IndexError, Exception):
                continue
    
        # 2. Filtrovanie podľa dátumu
        display_data = shifts.copy()
        if self.start_date or self.end_date:
            start = self.start_date or date.min
            end = self.end_date or date.max
            # Ak je dátum "do" menší ako "od", zahoď filter alebo ich vymeň (bezpečne ich vymeníme)
            if start > end:
                start, end = end, start
            display_data = {k: v for k, v in display_data.items() if start <= k[0] <= end}
    
        # 3. Filtrovanie podľa typu smeny (Denná/Nočná)
        if self.selected_shifts_filter: # Kontrola, či je aspoň jeden filter smeny
            display_data = {
                k: v for k, v in display_data.items()
                if (k[1] == 'D' and "Denná" in self.selected_shifts_filter) or
                   (k[1] == 'N' and "Nočná" in self.selected_shifts_filter)
            }
        else:
            # Ak nie je vybraná žiadna smena, nezobrazíme nič
            display_data = {}
    
        # 4. Výpočet súhrnných štatistík
        total_shifts = len(display_data)
        total_pieces = sum(s['total_made'] for s in display_data.values())
        total_hours = total_shifts * 12
    
        avg_per_shift = total_pieces / total_shifts if total_shifts > 0 else 0
        avg_per_hour = total_pieces / total_hours if total_hours > 0 else 0
    
        self.ids.summary_total_shifts.text = f"Počet smien: {total_shifts}"
        # Použitie f-string formátovania pre tisíce (napr. 10 000)
        self.ids.summary_total_pieces.text = f"Celkom vyrobené: {total_pieces:,.0f} ks".replace(",", " ")
        self.ids.summary_avg_per_shift.text = f"Priemer na smenu: {avg_per_shift:,.1f} ks".replace(",", " ")
        self.ids.summary_avg_per_hour.text = f"Priemer na hodinu: {avg_per_hour:.1f} ks"
    
        # Animácia zobrazenia súhrnu
        target_height = self.ids.summary_card.minimum_height if total_shifts > 0 else 0
        target_opacity = 1 if total_shifts > 0 else 0
        if self.ids.summary_card.height != target_height or self.ids.summary_card.opacity != target_opacity:
            Animation(height=target_height, opacity=target_opacity, duration=0.3, t="out_quad").start(self.ids.summary_card)
    
        # 5. Vymazanie starého zoznamu
        self.ids.shift_list.clear_widgets()
    
        if not display_data:
            self.ids.shift_list.add_widget(MDListItem(
                MDListItemHeadlineText(text="Žiadne dáta pre vybraný filter"),
                theme_text_color="Secondary"
            ))
            return
    
        # 6. Zobrazenie jednotlivých smien
        for (shift_date, shift_type), data in sorted(display_data.items(), reverse=True):
            total_made = data['total_made']
            goal_shift = data['goal_shift']
            goal_jph = data['goal_jph']
    
            difference = total_made - goal_shift
            diff_str = f"+{difference:,.0f}".replace(",", " ") if difference >= 0 else f"{difference:,.0f}".replace(",", " ")
    
            # Farba podľa plnenia
            if goal_shift == 0:
                bg_color = self.theme_cls.surfaceContainerColor
            elif difference >= 0:
                # Farba z dokumentácie KivyMD 2.0.1 (Material 3) pre Green - napr. povrchová zelená
                # Použijeme hex kód s priehľadnosťou (30 = cca 18% opacity)
                bg_color = get_color_from_hex("#4CAF5030") 
            else:
                # Červená priehľadná pre chybu
                bg_color = get_color_from_hex("#F4433630")
    
            # Texty
            headline = f"{shift_date.strftime('%d.%m.%Y')} • {shift_type} smena"
            supporting = f"Vyrobené: {total_made:,.0f} ks".replace(",", " ")
            if goal_shift > 0:
                supporting += f"  |  Cieľ: {goal_shift:,.0f} ks ({goal_jph} ks/h)".replace(",", " ")
                tertiary = f"Rozdiel: {diff_str} ks"
            else:
                tertiary = "Cieľ na smenu nie je nastavený"
    
            item = MDListItem(
                theme_bg_color="Custom",
                md_bg_color=bg_color,
                radius=dp(16),
                
                size_hint_y=None,
                height=dp(100)
            )
    
            item.add_widget(MDListItemHeadlineText(text=headline, font_style="Title", theme_text_color="Primary"))
            item.add_widget(MDListItemSupportingText(text=supporting))
            item.add_widget(MDListItemTertiaryText(text=tertiary))
    
            # Tlačidlo na vymazanie celej smeny
            delete_btn = TrailingPressedIconButton(
                icon="delete-outline",
                theme_icon_color="Custom",
                icon_color=self.theme_cls.errorColor,
                on_release=lambda x, k=(shift_date, shift_type): self.confirm_delete_shift(k)
            )
            item.add_widget(delete_btn)
    
            self.ids.shift_list.add_widget(item)


class EditHlasenieScreen(MDScreen):
    # ... (trieda je nezmenená) ...
    original_hlasenie = DictProperty()
    current_op = StringProperty()
    current_porucha = StringProperty()
    current_duration = NumericProperty()

    def set_hlasenie_data(self, hlasenie):
        self.original_hlasenie = hlasenie.copy()
        self.current_op = hlasenie['op']
        self.current_porucha = hlasenie['porucha']
        self.current_duration = hlasenie['trvanie_minuty']

        self.ids.op_button_text.text = self.current_op
        self.ids.porucha_button_text.text = self.current_porucha
        self.ids.duration_button_text.text = f"{self.current_duration} minút"
        self.ids.note_input.text = hlasenie.get('poznamka', '')

    def go_back_to_hlavna(self):
        self.manager.current = 'hlavna'

    def show_op_menu(self):
        data = load_ops_poruchy()
        ops = data.get('ops', [])
        menu_items = [
            {"text": op, "on_release": lambda x=op: self.set_op(x)}
            for op in sorted(ops, key=op_sort_key)
        ]
        MDDropdownMenu(caller=self.ids.op_button, items=menu_items, width_mult=4).open()

    def set_op(self, op):
        self.current_op = op
        self.ids.op_button_text.text = op
        data = load_ops_poruchy()
        poruchy_pre_op = data.get('poruchy_pre_op', {}).get(op, [])
        if poruchy_pre_op:
            self.set_porucha(sorted(poruchy_pre_op)[0])
        else:
            self.set_porucha("Žiadna porucha")

    def show_porucha_menu(self):
        data = load_ops_poruchy()
        poruchy = data.get('poruchy_pre_op', {}).get(self.current_op, [])
        if not poruchy:
            MDSnackbar(MDSnackbarText(text=f"Pre {self.current_op} nie sú definované žiadne poruchy.")).open()
            return

        menu_items = [
            {"text": p, "on_release": lambda x=p: self.set_porucha(x)}
            for p in sorted(poruchy)
        ]
        MDDropdownMenu(caller=self.ids.porucha_button, items=menu_items, width_mult=4).open()

    def set_porucha(self, porucha):
        self.current_porucha = porucha
        self.ids.porucha_button_text.text = porucha

    def show_duration_menu(self):
        menu_items = [
            {"text": f"{i} minút", "on_release": lambda x=i: self.set_duration(x)}
            for i in range(1, 61)
        ]
        MDDropdownMenu(caller=self.ids.duration_button, items=menu_items, max_height=dp(200), width_mult=4).open()

    def set_duration(self, duration):
        self.current_duration = duration
        self.ids.duration_button_text.text = f"{duration} minút"

    def save_changes(self):
        data = load_hlasenia()
        all_hlasenia = data.get('hlasenia', [])

        index_to_update = -1
        for i, h in enumerate(all_hlasenia):
            if h.get('datum_cas') == self.original_hlasenie.get('datum_cas'):
                index_to_update = i
                break

        if index_to_update != -1:
            edited_hlasenie = {
                'datum_cas': self.original_hlasenie['datum_cas'],
                'op': self.current_op,
                'porucha': self.current_porucha,
                'trvanie_minuty': self.current_duration,
                'poznamka': self.ids.note_input.text.strip()
            }
            all_hlasenia[index_to_update] = edited_hlasenie
            data['hlasenia'] = all_hlasenia
            save_hlasenia(data)

            MDSnackbar(MDSnackbarText(text="Hlásenie úspešne upravené!")).open()
            self.go_back_to_hlavna()
        else:
            MDSnackbar(MDSnackbarText(text="Chyba: Pôvodné hlásenie sa nenašlo!")).open()


class MyApp(MDApp):
    fault_in_progress = DictProperty({})

    def show_jph_menu(self, panel: Factory.MyExpansionPanel):
        menu_items = [
            {"text": str(i), "on_release": lambda x=str(i): self.save_jph_from_menu(panel, x)}
            for i in range(66)
        ]
        caller = panel.ids.jph_button
        self.jph_menu = MDDropdownMenu(
            caller=caller, items=menu_items, width=caller.width, max_height=dp(400), radius=[20, 7, 20, 7]
        )
        Clock.schedule_once(lambda dt: self.jph_menu.open(), 0.01)

    def save_jph_from_menu(self, panel: Factory.MyExpansionPanel, jph_str: str):
        if hasattr(self, 'jph_menu'):
            self.jph_menu.dismiss()

        panel_key = panel.panel_key
        jph_data = load_jph()
        jph_data[panel_key] = int(jph_str)
        save_jph(jph_data)

        self.root.get_screen('hlavna').update_poruchy_list()
        MDSnackbar(MDSnackbarText(text=f"JPH pre {datetime.strptime(panel_key, '%d.%m.%y_%H:00').strftime('%H:00')} uložené: {jph_str}")).open()

    def build(self):
        settings = load_settings()
        self.theme_cls.theme_style = settings.get('theme_style', "Dark")
        self.theme_cls.primary_palette = settings.get('primary_palette', "Lightgreen")
        # Overené v dokumentácii KivyMD 2.0.1 (Strana 6 v kivymd-readthedocs-io-en-latest.pdf)
        self.theme_cls.m_version = "3"
        return Builder.load_string(KV)

    def tap_expansion_chevron(self, panel: Factory.MyExpansionPanel, chevron: TrailingPressedIconButton):
        chevron.animate_to(90 if not panel.is_open else 0)
        panel.toggle()

if __name__ == '__main__':
    MyApp().run()
