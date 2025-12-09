# main.py – FUNGUJE NA 100% V PYDROID 3 – FINÁLNA VERZIA!
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.list import MDListItem, MDListItemHeadlineText
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.lang import Builder
import requests
import threading
import os
import hashlib
import webbrowser
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# ==============================================================================
# CACHE - UPRAVENÉ PRE BUILDOZER/ANDROID KOMPATIBILITU
# ==============================================================================

# Pôvodné globálne definície CACHE_DIR boli odstránené.
# Adresár sa bude inicializovať v triede MDApp pomocou self.user_data_dir

def get_cache_done_file(cache_dir):
    """Vráti celú cestu k súboru .cache_done."""
    return os.path.join(cache_dir, ".cache_done")

def cache_complete(cache_dir):
    """Skontroluje, či je cache stiahnutá."""
    return os.path.exists(get_cache_done_file(cache_dir))

def set_cache_done(cache_dir):
    """Vytvorí súbor pre označenie dokončenia cache."""
    # Pre istotu vytvorí adresár predtým, ako doň zapíše
    os.makedirs(cache_dir, exist_ok=True) 
    open(get_cache_done_file(cache_dir), "w").close()

def cache_image(url, cache_dir):
    """Asynchrónne stiahne obrázok do cache_dir."""
    if not url or not url.startswith("http"): return
    name = hashlib.md5(url.encode()).hexdigest() + ".jpg"
    path = os.path.join(cache_dir, name)
    if os.path.exists(path): return
    def dl():
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                # Zabezpečenie, že cache_dir existuje pred zápisom
                os.makedirs(cache_dir, exist_ok=True) 
                open(path, "wb").write(r.content)
        except: pass
    threading.Thread(target=dl, daemon=True).start()

def get_image(url, cache_dir):
    """Vráti cestu k lokálnemu obrázku (ak existuje) alebo URL, pričom spustí sťahovanie."""
    if not url: return "https://via.placeholder.com/500x750/222/fff?text=?"
    name = hashlib.md5(url.encode()).hexdigest() + ".jpg"
    path = os.path.join(cache_dir, name)
    if os.path.exists(path): return path
    cache_image(url, cache_dir)
    return url

# ==============================================================================
# PLUGIN S LOGOM (bezo zmeny)
# ==============================================================================
class StreamPlugin:
# ... (bezo zmeny)
    def __init__(self, app):
        self.app = app

    def log(self, text, color="white"):
        Clock.schedule_once(lambda dt: self.app.add_log(text, color))

    def search(self, movie):
        self.log("Hľadám stream...", "#00ffff")
        title = movie.get("nazov_sk") or movie.get("nazov_en") or "film"
        year = movie.get("rok_vydania", "")
        query = f"{title} {year}".strip()

        try:
            url = f"https://prehraj.to/hledej/{query.replace(' ', '%20')}"
            html = requests.get(url, timeout=15).text
            soup = BeautifulSoup(html, "html.parser")
            links = soup.select("a.video--link")[:6]

            streams = []
            for a in links:
                href = urljoin("https://prehraj.to", a.get("href",""))
                if not href: continue
                try:
                    page = requests.get(href, timeout=12).text
                    mp4 = re.search(r'https?://[^"\']+\.mp4[^"\']*', page)
                    if mp4:
                        streams.append({"názov": a.get("title","Stream"), "link": mp4.group(0)})
                        self.log("Stream nájdený!", "#00ff00")
                except: pass

            Clock.schedule_once(lambda dt: self.app.show_results(streams))
        except:
            self.log("Chyba pri vyhľadávaní", "#ff4444")
            Clock.schedule_once(lambda dt: self.app.show_results([]))

# ==============================================================================
# FilmCard - UPRAVENÉ volanie get_image
# ==============================================================================
class FilmCard(MDCard):
    def __init__(self, film, app, **kwargs):
        super().__init__(**kwargs)
        self.film = film
        self.app = app
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(300)
        self.padding = dp(8)
        self.radius = [16]
        self.md_bg_color = (0.13, 0.13, 0.15, 1)
        self.elevation = 6

        # ÚPRAVA: volanie s app.cache_dir
        img = AsyncImage(source=get_image(
            f"https://image.tmdb.org/t/p/w500{film.get('poster','')}", 
            self.app.cache_dir
        ), size_hint=(1,0.8))
        self.add_widget(img)

        lbl = MDLabel(
            text=f"[b]{film.get('nazov_sk') or film.get('nazov_en')}[/b]\n[color=#00ff99]⭐ {film.get('hodnotenie','N/A')}[/color]",
            markup=True, halign="center", size_hint_y=None, height=dp(70)
        )
        self.add_widget(lbl)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.app.show_detail(self.film)
            return True
        return super().on_touch_down(touch)

# ==============================================================================
# KatalogApp - UPRAVENÁ inicializácia cache a volania funkcií
# ==============================================================================
class KatalogApp(MDApp):
    # NOVÁ VLASTNOSŤ: cache_dir bude definovaná v on_start
    cache_dir = None 

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.title = "Stream Katalóg"
        # ... (zvyšok build metódy)
        self.sm = ScreenManager()

        # HLAVNÁ
        main = MDScreen(name="main")
        root = MDBoxLayout(orientation="vertical")
        menu_scroll = ScrollView(size_hint_y=None, height=dp(70), do_scroll_y=False)
        self.menu_box = MDBoxLayout(orientation="horizontal", size_hint_x=None, width=dp(2500), height=dp(70), padding=dp(15), spacing=dp(15))
        menu_scroll.add_widget(self.menu_box)

        self.grid = GridLayout(cols=3, spacing=dp(12), padding=dp(12), size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        grid_scroll = ScrollView()
        grid_scroll.add_widget(self.grid)

        root.add_widget(menu_scroll)
        root.add_widget(grid_scroll)
        main.add_widget(root)
        self.sm.add_widget(main)

        # DETAIL
        detail = MDScreen(name="detail")
        detail.add_widget(Builder.load_string('''
MDBoxLayout:
    orientation: "vertical"
    MDScrollView:
        MDBoxLayout:
            id: content
            orientation: "vertical"
            adaptive_height: True
            padding: dp(20)
            spacing: dp(15)
    Button:
        text: "Späť"
        background_color: 0.2, 0.5, 0.9, 1
        size_hint_y: None
        height: dp(50)
        on_release: app.sm.current = "main"
'''))
        self.sm.add_widget(detail)

        # LOG + VÝSLEDKY
        log = MDScreen(name="log")
        log.add_widget(Builder.load_string('''
MDBoxLayout:
    orientation: "vertical"
    MDBoxLayout:
        orientation: "vertical"
        size_hint_y: None
        height: dp(60)
        md_bg_color: 0.1, 0.1, 0.1, 1
        padding: [dp(15), dp(10)]
        MDLabel:
            text: "Vyhľadávanie streamov"
            halign: "center"
            font_size: sp(20)
            bold: True
        Button:
            text: "Späť"
            pos_hint: {"center_y": .5}
            size_hint_x: None
            width: dp(100)
            on_release: app.sm.current = "detail"
    ScrollView:
        id: scroll
        MDList:
            id: log_list
'''))
        self.sm.add_widget(log)

        self.plugin = StreamPlugin(self)
        return self.sm

    def on_start(self):
        # NOVÁ DÔLEŽITÁ ČASŤ:
        # Použitie MDApp.user_data_dir, ktoré odkazuje na privátnu aplikačnú cache
        # cestu (napr. /data/data/org.test.myapp/files/thumbnails na Androide)
        self.cache_dir = os.path.join(self.user_data_dir, "thumbnails")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Volania cache funkcií s novým argumentom self.cache_dir
        if cache_complete(self.cache_dir):
            Clock.schedule_once(lambda dt: self.setup_main(), 0.5)
        else:
            threading.Thread(target=self.cache_all, daemon=True).start()
            Clock.schedule_once(lambda dt: self.setup_main(), 0.5)

    def cache_all(self):
        urls = set()
        files = ["netflix_movies.json","disney_movies.json","amazon_movies.json","top_movies.json","popular_movies.json"]
        for f in files:
            try:
                data = requests.get(f"https://raw.githubusercontent.com/Xneerg/json/main/tmdb_zoznam/{f}", timeout=15).json()
                for film in data:
                    if film.get("poster"): urls.add(f"https://image.tmdb.org/t/p/w500{film['poster']}")
                    if film.get("fanart_backdrop"): urls.add(film["fanart_backdrop"])
            except: pass
            
        # ÚPRAVA: volanie s self.cache_dir
        for u in urls: cache_image(u, self.cache_dir)
        set_cache_done(self.cache_dir)

    def setup_main(self):
        self.sm.current = "main"
        cats = [("Netflix","netflix_movies.json"),("Disney+","disney_movies.json"),("Amazon","amazon_movies.json"),
                ("Top","top_movies.json"),("Populárne","popular_movies.json")]
        for name,file in cats:
            b = Button(text=name, background_normal='', background_color=(0.2,0.5,0.9,1) if "Netflix" in name else (0.18,0.18,0.25,1),
                       color=(1,1,1,1), size_hint=(None,None), size=(dp(160),dp(50)))
            b.bind(on_release=lambda x,f=file: self.load(f))
            self.menu_box.add_widget(b)
        self.load("netflix_movies.json")

    def load(self, file):
        for b in self.menu_box.children:
            if isinstance(b,Button): b.background_color = (0.18,0.18,0.25,1)
        for b in self.menu_box.children:
            if isinstance(b,Button) and file.replace("_movies.json","") in b.text.lower():
                b.background_color = (0.2,0.5,0.9,1)

        self.grid.clear_widgets()
        self.grid.add_widget(MDLabel(text="Načítavam...", halign="center", size_hint_y=None, height=dp(200)))

        def dl():
            try:
                d = requests.get(f"https://raw.githubusercontent.com/Xneerg/json/main/tmdb_zoznam/{file}", timeout=20).json()
                Clock.schedule_once(lambda dt: self.show_films(d))
            except:
                Clock.schedule_once(lambda dt: self.grid.clear_widgets() or self.grid.add_widget(MDLabel(text="Bez internetu")))
        threading.Thread(target=dl, daemon=True).start()

    def show_films(self, films):
        self.grid.clear_widgets()
        for f in films[:120]:
            # Odovzdanie self (aplikácie) FilmCard, aby mala prístup k self.cache_dir
            self.grid.add_widget(FilmCard(f, self))

    def show_detail(self, film):
        self.current_film = film
        s = self.sm.get_screen("detail")
        box = s.children[0].ids.content
        box.clear_widgets()

        # ÚPRAVA: volanie get_image s self.cache_dir
        if film.get("fanart_backdrop"):
            box.add_widget(AsyncImage(source=get_image(film["fanart_backdrop"], self.cache_dir), allow_stretch=True, keep_ratio=False, opacity=0.3))

        h = MDBoxLayout(orientation="horizontal", spacing=dp(20), size_hint_y=None, height=dp(220))
        # ÚPRAVA: volanie get_image s self.cache_dir
        p = AsyncImage(source=get_image(f"https://image.tmdb.org/t/p/w500{film.get('poster','')}", self.cache_dir), size_hint_x=None, width=dp(140))
        i = MDBoxLayout(orientation="vertical")
        i.add_widget(MDLabel(text=f"[b][size=28]{film.get('nazov_sk','Neznámy')}[/size][/b]", markup=True))
        i.add_widget(MDLabel(text=f"{film.get('nazov_en','')} ({film.get('rok_vydania','')})"))
        i.add_widget(MDLabel(text=f"{film.get('hodnotenie','N/A')} | {film.get('stopaz_min','N/A')} min"))
        h.add_widget(p)
        h.add_widget(i)
        box.add_widget(h)

        for l,k in [("Žáner","žáner"),("Réžia","réžia"),("Herci","herci"),("Štúdiá","štúdiá")]:
            if film.get(k):
                box.add_widget(MDLabel(text=f"[b]{l}:[/b] {film[k]}", markup=True, halign="left", size_hint_y=None, height=dp(80)))

        # OPRAVENÉ – odstránená prebytočná zátvorka!
        kde = film.get("kde_pozriet_sk", {})
        if kde:
            t = ""
            if kde.get("stream"): t += f"Stream: {kde['stream']}\n"
            if kde.get("kúpiť"): t += f"Kúpiť: {kde['kúpiť']}\n"
            if kde.get("prenajať"): t += f"Prenájom: {kde['prenajať']}"
            if t: box.add_widget(MDLabel(text=f"[b]Kde pozrieť:[/b]\n{t}", markup=True, size_hint_y=None, height=dp(120)))

        box.add_widget(MDLabel(text="[b]Obsah:[/b]", markup=True, size_hint_y=None, height=dp(40)))
        box.add_widget(MDLabel(text=film.get("obsah","Žiadny popis."), halign="left", text_size=(None,None), size_hint_y=None, height=dp(600)))

        btn = Button(text="Hľadať stream na prehraj.to", background_color=(0,0.7,0,1), size_hint_y=None, height=dp(60))
        btn.bind(on_release=lambda x: self.search_stream(film))
        box.add_widget(btn)

        self.sm.current = "detail"

    def search_stream(self, film):
        screen = self.sm.get_screen("log")
        log_list = getattr(screen.ids, "log_list", None)
        if log_list:
            log_list.clear_widgets()
        self.plugin.log("Spúšťam vyhľadávanie...", "#00ffff")
        self.plugin.search(film)
        self.sm.current = "log"

    def add_log(self, text, color="white"):
        screen = self.sm.get_screen("log")
        log_list = getattr(screen.ids, "log_list", None)
        if not log_list: return
        item = MDListItem()
        item.add_widget(MDListItemHeadlineText(text=f"[color={color}]{text}[/color]", markup=True))
        log_list.add_widget(item)
        scroll = getattr(screen.ids, "scroll", None)
        if scroll:
            Clock.schedule_once(lambda dt: setattr(scroll, "scroll_y", 0), 0.1)

    def show_results(self, streams):
        screen = self.sm.get_screen("log")
        log_list = getattr(screen.ids, "log_list", None)
        if not log_list: return
        if not streams:
            self.add_log("Žiadne streamy nenájdené", "#ff4444")
        for s in streams:
            item = MDListItem(
                MDListItemHeadlineText(text=s.get("názov", "Stream")),
                on_release=lambda x, l=s.get("link"): webbrowser.open(l) if l else None
            )
            log_list.add_widget(item)

KatalogApp().run()
