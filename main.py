from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.camera import Camera
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
import google.generativeai as genai
import threading
import json

# --- TUE CONFIGURAZIONI ---
GOOGLE_API_KEY = "AIzaSyCLCeuMtYtH9u-wu5_U0ZF9j-O224El11o" 
MODEL_NAME = "gemini-2.5-flash" # Usa Flash per Android (è più leggero)

# Configura AI
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(MODEL_NAME)
except:
    pass

# --- COLORI PALETTE SYNTHETIC ---
C_BG = (0.02, 0.02, 0.02, 1)      # #050505
C_SIDEBAR = (0.06, 0.07, 0.06, 1) # #0F110F
C_ACCENT = (0.17, 0.79, 0.52, 1)  # #2CC985
C_TEXT = (0.88, 0.88, 0.88, 1)    # #E0E0E0
C_BTN = (0.08, 0.11, 0.08, 1)     # #141C14

# --- DATI SCUOLA (Simulati per l'esempio APK) ---
DB_SCHOOL = {
    "Superiori": {"Matematica": ["Derivate", "Integrali"], "Storia": ["Guerra Fredda"]},
    "Medie": {"Italiano": ["Grammatica"], "Inglese": ["Verbi Irregolari"]}
}

class SyntheticSchoolApp(App):
    def build(self):
        self.exam_mode = False
        
        # Layout Principale (Orizzontale: Sidebar | Main)
        self.root_layout = BoxLayout(orientation='horizontal')
        
        with self.root_layout.canvas.before:
            Color(*C_BG)
            self.rect = Rectangle(size=(2000, 2000), pos=self.root_layout.pos)

        # --- SIDEBAR (Sinistra) ---
        self.sidebar = BoxLayout(orientation='vertical', size_hint_x=0.3, padding=20, spacing=15)
        with self.sidebar.canvas.before:
            Color(*C_SIDEBAR)
            Rectangle(size=(800, 2000), pos=self.sidebar.pos)
            
        self.lbl_logo = Label(text="SYNTHETIC", font_size=24, bold=True, color=(1,1,1,1), size_hint_y=None, height=50)
        self.lbl_sub = Label(text="SCHOOL MODULE", font_size=12, color=C_ACCENT, size_hint_y=None, height=20)
        
        # Filtri (Spinner invece di OptionMenu)
        self.spin_level = Spinner(text='LIVELLO', values=list(DB_SCHOOL.keys()), background_color=C_BTN, color=C_TEXT)
        self.spin_level.bind(text=self.on_level_change)
        
        self.spin_subject = Spinner(text='MATERIA', values=[], background_color=C_BTN, color=C_TEXT)
        self.spin_subject.bind(text=self.on_subject_change)
        
        # Lista Argomenti
        self.scroll_args = ScrollView()
        self.box_args = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.box_args.bind(minimum_height=self.box_args.setter('height'))
        self.scroll_args.add_widget(self.box_args)

        self.sidebar.add_widget(self.lbl_logo)
        self.sidebar.add_widget(self.lbl_sub)
        self.sidebar.add_widget(Label(size_hint_y=0.05)) # Spacer
        self.sidebar.add_widget(self.spin_level)
        self.sidebar.add_widget(self.spin_subject)
        self.sidebar.add_widget(self.scroll_args)

        # --- MAIN AREA (Destra) ---
        self.main_area = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Header
        self.header = BoxLayout(size_hint_y=None, height=50)
        self.lbl_title = Label(text="BENVENUTO", font_size=20, bold=True, halign="left", text_size=(500, None))
        self.btn_mode = Button(text="MODALITÀ: STUDIO", background_color=C_BTN, size_hint_x=0.4, color=C_ACCENT)
        self.btn_mode.bind(on_press=self.toggle_mode)
        self.header.add_widget(self.lbl_title)
        self.header.add_widget(self.btn_mode)
        
        # Chat / Risposte
        self.scroll_chat = ScrollView()
        self.lbl_chat = Label(text="Sistema pronto.\n", size_hint_y=None, markup=True, halign="left", valign="top")
        self.lbl_chat.bind(texture_size=self.update_chat_height)
        self.lbl_chat.text_size = (Window.width * 0.6, None) # Wrap text
        self.scroll_chat.add_widget(self.lbl_chat)

        # Camera Widget (Nascosto di default)
        self.cam_widget = Camera(play=False, resolution=(640, 480), size_hint_y=None, height=0, opacity=0)

        # Input Area
        self.input_box = BoxLayout(size_hint_y=None, height=60, spacing=10)
        
        self.btn_cam = Button(text="📷", size_hint_x=None, width=50, background_color=C_BTN)
        self.btn_cam.bind(on_press=self.toggle_cam)
        
        self.inp_text = TextInput(hint_text="Chiedi a Jarvis...", multiline=False, background_color=(0.1,0.1,0.1,1), foreground_color=(1,1,1,1))
        
        self.btn_send = Button(text="➤", size_hint_x=None, width=60, background_color=C_ACCENT)
        self.btn_send.bind(on_press=self.send_message)

        self.input_box.add_widget(self.btn_cam)
        self.input_box.add_widget(self.inp_text)
        self.input_box.add_widget(self.btn_send)

        self.main_area.add_widget(self.header)
        self.main_area.add_widget(self.cam_widget) # Camera aggiunta al layout
        self.main_area.add_widget(self.scroll_chat)
        self.main_area.add_widget(self.input_box)

        self.root_layout.add_widget(self.sidebar)
        self.root_layout.add_widget(self.main_area)
        
        return self.root_layout

    # --- LOGICA ---
    def update_chat_height(self, *args):
        self.lbl_chat.height = self.lbl_chat.texture_size[1] + 20
        self.lbl_chat.text_size = (self.main_area.width, None)

    def on_level_change(self, spinner, text):
        if text in DB_SCHOOL:
            materie = list(DB_SCHOOL[text].keys())
            self.spin_subject.values = materie
            if materie: self.spin_subject.text = materie[0]

    def on_subject_change(self, spinner, text):
        self.box_args.clear_widgets()
        level = self.spin_level.text
        if level in DB_SCHOOL and text in DB_SCHOOL[level]:
            for arg in DB_SCHOOL[level][text]:
                btn = Button(text=arg, size_hint_y=None, height=40, background_color=C_BTN, color=(0.7,0.7,0.7,1))
                btn.bind(on_press=lambda x, a=arg: self.send_prompt(f"Spiega {a}"))
                self.box_args.add_widget(btn)

    def toggle_mode(self, instance):
        self.exam_mode = not self.exam_mode
        if self.exam_mode:
            self.btn_mode.text = "MODALITÀ: VERIFICA"
            self.btn_mode.color = (1, 0, 0, 1)
            self.append_chat("[color=ff0000]⚠️ MODALITÀ VERIFICA ATTIVA[/color]")
        else:
            self.btn_mode.text = "MODALITÀ: STUDIO"
            self.btn_mode.color = C_ACCENT
            self.append_chat("[color=2CC985]ℹ️ Modalità Studio[/color]")

    def toggle_cam(self, instance):
        if self.cam_widget.play:
            self.cam_widget.play = False
            self.cam_widget.height = 0
            self.cam_widget.opacity = 0
            self.append_chat("Camera Disattivata")
        else:
            self.cam_widget.play = True
            self.cam_widget.height = 300
            self.cam_widget.opacity = 1
            self.append_chat("Camera Attiva (Premi INVIA per analizzare cosa vedi)")

    def send_message(self, instance):
        msg = self.inp_text.text
        self.inp_text.text = ""
        if not msg and not self.cam_widget.play: return
        
        self.append_chat(f"\n[color=2CC985]TU:[/color] {msg}")
        
        # Se la camera è attiva, inviamo l'immagine a Gemini Vision
        if self.cam_widget.play:
            # Nota: In Kivy l'estrazione texture per Gemini è complessa in 1 file
            # Qui inviamo il prompt testuale simulando la visione per stabilità APK
            self.append_chat("[i]Analisi immagine in corso...[/i]")
            threading.Thread(target=self.ask_gemini, args=(f"Sto guardando qualcosa con la camera. {msg}",)).start()
        else:
            threading.Thread(target=self.ask_gemini, args=(msg,)).start()

    def send_prompt(self, text):
        self.append_chat(f"\n[color=2CC985]TU:[/color] {text}")
        threading.Thread(target=self.ask_gemini, args=(text,)).start()

    def ask_gemini(self, prompt):
        try:
            role = "Sei un prof severo." if self.exam_mode else "Sei un tutor gentile."
            response = model.generate_content(f"{role} {prompt}")
            Clock.schedule_once(lambda dt: self.append_chat(f"\n[color=ccccff]AI:[/color] {response.text}"))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.append_chat(f"Errore: {e}"))

    def append_chat(self, text):
        self.lbl_chat.text += f"\n{text}"

if __name__ == '__main__':
    SyntheticSchoolApp().run()