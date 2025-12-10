from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDButton, MDButtonText

class ButtonApp(MDApp):
    """
    Hlavná trieda aplikácie.
    """

    def build(self):
        """
        Iniciuje a vracia strom widgetov.
        """
        # 1. Nastavenie Material Design 3 témy (strana 7/8 z KivyMD 2.0.1.dev0)
        # Tieto riadky musíte ponechať čisté, bez akýchkoľvek extra znakov.
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange" # Nastavuje primárnu farebnú paletu

        # 2. Definícia funkcie pre stlačenie tlačidla
        def on_button_release(instance):
            """Akcia, ktorá sa vykoná po uvoľnení tlačidla."""
            # Zmena textu na tlačidle (children[0] je MDButtonText)
            instance.children[0].text = "Tlačidlo bolo stlačené!"
            print("Tlačidlo bolo stlačené! (on_release)")

        # 3. Vytvorenie obrazovky a tlačidla (strana 10 z KivyMD 2.0.1.dev0)
        return MDScreen(
            MDButton(
                MDButtonText(
                    text="Stlač ma!",
                ),
                # Centrovanie tlačidla na obrazovke
                pos_hint={"center_x": 0.5, "center_y": 0.5},
                # Priradenie funkcie k udalosti uvoľnenia tlačidla
                on_release=on_button_release,
            )
        )

# Spustenie aplikácie
if __name__ == '__main__':
    ButtonApp().run()
