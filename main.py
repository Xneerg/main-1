# KivyMD App demonstrating a simple button interaction and toast notification.
# Requires kivy and kivymd to be installed (pip install kivy kivymd).

from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.toast import toast

# The KV language definition for the UI
KV = '''
MDScreen:
    # Light gray background for the screen
    md_bg_color: 0.95, 0.95, 0.95, 1

    MDButton:
        # Button text (Slovak: "Click on me!")
        text: "Klikni na mňa!"
        style: "filled"          # The button has a solid background fill
        # FIX: The value must be capitalized to 'Custom'
        theme_width: "Custom"
        # Since theme_width is 'Custom', the width property is respected
        width: 300
        height: 100
        # Center the button on the screen
        pos_hint: {"center_x": .5, "center_y": .5}
        # Action to call when the button is released
        on_release: app.zobraz_pozdrav()
'''

class MojaApp(MDApp):
    def build(self):
        # Set the overall app theme
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(KV)

    # Function called by the button
    def zobraz_pozdrav(self):
        # Show a toast notification (Slovak: "hello, I work")
        toast("ahoj fungujem")

if __name__ == '__main__':
    MojaApp().run()
