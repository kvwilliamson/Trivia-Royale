# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, Toplevel, Label, Entry, Button, Frame, Canvas, Checkbutton, BooleanVar
import pyttsx3
import random
import pygame
import webbrowser
import pyperclip
from PIL import Image, ImageTk
import os
import sys
import json
from dotenv import load_dotenv
import requests
import google.generativeai as genai
from threading import Thread, Event, Lock
# import traceback # No longer needed

# --- Setup Environment and Paths ---

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
os.environ['TK_SILENCE_DEPRECATION'] = '1'

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')

# --- LLM Model Names ---
GEMINI_MODEL = "gemini-2.0-flash" # Or "gemini-1.5-flash", "gemini-2.5-pro-exp-03-25" - MATCH THE ONE IN generate_trivia_questions_gemini
MISTRAL_MODEL = "mistral-large-latest" # MATCH THE ONE IN generate_trivia_questions_mistral

# --- Determine Base Directory for Assets ---
try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    BASE_DIR = sys._MEIPASS
except AttributeError:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Asset Path Helper ---
def get_asset_path(relative_path):
    """Constructs the absolute path for an asset."""
    # Ensure consistent path separators
    normalized_relative_path = os.path.normpath(relative_path)
    # Assuming assets are in an 'assets' subdirectory relative to the script
    full_path = os.path.join(BASE_DIR, "assets", normalized_relative_path)
    if not os.path.exists(full_path):
         print(f"### WARNING: Asset not found at expected path: {full_path}")
    return full_path


# --- Sound Effect Manager ---
class SoundEffectManager:
    """Manages loading and playing sound effects"""
    def __init__(self):
        self.sounds = {}
        self.enabled = True
        self.volume = 0.7
        self._load_sounds()
    
    def _load_sounds(self):
        """Load all sound effects"""
        sound_files = {
            'button_click': 'audio/sfx/button_click.wav',
            'correct': 'audio/sfx/correct_answer.wav',
            'wrong': 'audio/sfx/wrong_answer.wav',
            'round_transition': 'audio/sfx/round_transition.wav',
            'achievement': 'audio/sfx/achievement.wav',
            'score_change': 'audio/sfx/score_change.wav',
            'timer_tick': 'audio/sfx/timer_tick.wav',
            'timer_warning': 'audio/sfx/timer_warning.wav',
        }
        
        for name, path in sound_files.items():
            try:
                full_path = get_asset_path(path)
                if os.path.exists(full_path):
                    sound = pygame.mixer.Sound(full_path)
                    sound.set_volume(self.volume)
                    self.sounds[name] = sound
                else:
                    print(f"### WARNING: Sound effect not found: {path}")
            except Exception as e:
                print(f"### ERROR: Failed to load sound {name}: {e}")
    
    def play(self, sound_name):
        """Play a sound effect by name"""
        if self.enabled and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                print(f"### ERROR: Failed to play sound {sound_name}: {e}")
    
    def set_volume(self, volume):
        """Set volume for all sound effects (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.volume)
    
    def toggle(self):
        """Toggle sound effects on/off"""
        self.enabled = not self.enabled
        return self.enabled


# --- Visual Feedback Animator ---
class FeedbackAnimator:
    """Handles visual feedback animations"""
    def __init__(self, root):
        self.root = root
        self.current_feedback = None
        self.checkmark_image = None
        self.x_mark_image = None
        self._load_images()
    
    def _load_images(self):
        """Load checkmark and X mark images"""
        try:
            check_path = get_asset_path('images/ui/checkmark.png')
            if os.path.exists(check_path):
                img = Image.open(check_path)
                img = img.resize((100, 100), Image.LANCZOS)
                self.checkmark_image = ImageTk.PhotoImage(img)
            
            x_path = get_asset_path('images/ui/x_mark.png')
            if os.path.exists(x_path):
                img = Image.open(x_path)
                img = img.resize((100, 100), Image.LANCZOS)
                self.x_mark_image = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"### ERROR: Failed to load feedback images: {e}")
    
    def show_feedback(self, is_correct, parent_widget=None):
        """Show checkmark or X mark with fade-in animation"""
        if parent_widget is None:
            parent_widget = self.root
        
        # Clear any existing feedback
        if self.current_feedback and self.current_feedback.winfo_exists():
            self.current_feedback.destroy()
        
        # Choose image
        image = self.checkmark_image if is_correct else self.x_mark_image
        if not image:
            return  # Images not loaded
        
        # Create label with image
        feedback_label = Label(parent_widget, image=image, bg=COLORS["light_blue"], borderwidth=0)
        feedback_label.image = image  # Keep reference
        feedback_label.place(relx=0.5, rely=0.5, anchor='center')
        
        self.current_feedback = feedback_label
        
        # Auto-dismiss after 1.5 seconds
        self.root.after(1500, lambda: self._dismiss_feedback(feedback_label))
    
    def _dismiss_feedback(self, widget):
        """Dismiss the feedback widget"""
        try:
            if widget and widget.winfo_exists():
                widget.destroy()
        except:
            pass



# --- Constants ---
COLORS = {
    "light_blue": "#36a0fe",
    "soft_yellow": "#ffff99",
    "dark_teal": "#9dd8e6",
    "soft_coral": "#deaaef",
    "softer_coral": "#deaF50",
    "black": "#000000",
    "red": "#FF0000"
}

FONTS = {
    "large": ("Helvetica", 60, "bold"),
    "big": ("Helvetica", 40, "bold"),
    "big_italic": ("Helvetica", 40, "bold", "italic"),
    "medium": ("Helvetica", 28),
    "medium_bold": ("Helvetica", 30, "bold", "italic"),
    "small": ("Helvetica", 18),
    "xsmall": ("Helvetica", 14)
}

CATEGORIES = [
    "General Science", "Physics and Astronomy", "Medicine", "Toxicology", "Technology",
    "History", "Geography", "World Capitals", "France", "Famous Landmarks", "Cycling",
    "College Football", "Pro Football", "Knitting", "Gardening", "Equine", "Art and Literature",
    "Music", "Movies",
    "70's", "80's Culture", "90's Culture", "Mythology", "Folklore",
    "TV Shows and Series", "Wine", "Food and Drink", "Famous Inventors",
    "Real Estate", "Nature", "Business and Economics", "Philosophy", "Riddles and Puzzles",
    "Linguistics", "National Parks", "Hiking", "Pets", "Other", "Other", "Other"
]

class TriviaGame:
    def __init__(self, root):
        self.root = root
        # Load API keys
        self._load_api_keys()
        
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=COLORS["light_blue"])
        self.root.title("Trivia Royale")

        self.root.bind("<Escape>", self.quit_game)

        self.question_index = 0

    def _load_api_keys(self):
        """Load API keys from environment and config file."""
        # Try environment first
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        self.mistral_key = os.getenv('MISTRAL_API_KEY')
        
        # Try config file if needed
        if not self.gemini_key or not self.mistral_key:
            config_dir = os.path.expanduser('~/.trivia_royale')
            config_file = os.path.join(config_dir, 'config.json')
            
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        stored_keys = json.load(f)
                        if not self.gemini_key and 'GEMINI_API_KEY' in stored_keys:
                            self.gemini_key = stored_keys['GEMINI_API_KEY'].strip()
                        if not self.mistral_key and 'MISTRAL_API_KEY' in stored_keys:
                            self.mistral_key = stored_keys['MISTRAL_API_KEY'].strip()
                except Exception as e:
                    print(f"### ERROR: Failed to load config file: {e}")

        # If keys are still missing, show dialog
        if not self.gemini_key or not self.mistral_key:
            self._show_api_key_dialog()

        # Debug output
        print(f"### DEBUG: Loaded GEMINI_API_KEY: {bool(self.gemini_key)} (len: {len(self.gemini_key) if self.gemini_key else 0})")
        print(f"### DEBUG: Loaded MISTRAL_API_KEY: {bool(self.mistral_key)} (len: {len(self.mistral_key) if self.mistral_key else 0})")

        # --- Pygame Mixer Initialization ---
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
            pygame.init()
        except pygame.error as e:
            messagebox.showerror("Audio Error", f"Could not initialize audio playback: {e}\nMusic and TTS may not work.")

        # --- Initialize Sound Effects and Visual Feedback ---
        try:
            self.sfx = SoundEffectManager()
            print("✓ Sound effects loaded successfully")
        except Exception as e:
            print(f"### WARNING: Failed to initialize sound effects: {e}")
            self.sfx = None
        
        try:
            self.feedback_animator = FeedbackAnimator(self.root)
            print("✓ Visual feedback system loaded")
        except Exception as e:
            print(f"### WARNING: Failed to initialize feedback animator: {e}")
            self.feedback_animator = None

        # Initialize game state variables
        self.num_rounds = 0
        self.num_teams = 0
        self.team_names = []
        self.scores = []
        self.wagers = {}
        self.collecting_wagers = False
        self.selected_categories = []
        self.selected_difficulties = []
        self.questions = []
        self.current_round = 1
        self.current_team = 0
        self.bg_canvas = None
        self.original_bg_image = None
        self.bg_photo = None

        # Define UI element instance variables early
        self.reveal_prompt_label = None
        self.correctness_prompt_label = None

        # Load background image safely
        try:
            bg_image_path = get_asset_path("images/backgrounds/TriviaRoyaleScene(2).jpg")
            if not os.path.exists(bg_image_path):
                 raise FileNotFoundError(f"Image file not found at {bg_image_path}")
            self.original_bg_image = Image.open(bg_image_path)
        except FileNotFoundError as fnf_error:
            self.original_bg_image = None
            messagebox.showerror("Image Error", f"Background image not found:\n{bg_image_path}\nPlease ensure it's in the 'assets' folder.")
        except Exception as e:
            self.original_bg_image = None
            messagebox.showerror("Image Error", f"Could not load background image: {e}")

        self.title_screen()

    def _show_api_key_dialog(self):
        """Show dialog for API key entry with improved UI"""
        dialog = Toplevel(self.root)
        dialog.title("API Keys Required")
        dialog.configure(bg='white')
        dialog.geometry("400x400")
        
        # Center window
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 400) // 2
        y = (dialog.winfo_screenheight() - 400) // 2
        dialog.geometry(f"+{x}+{y}")
        
        Label(dialog, 
              text="Please enter your API keys:",
              font=("Helvetica", 12, "bold"),
              bg='white').pack(pady=20)

        # Gemini section
        gemini_frame = Frame(dialog, bg='white')
        gemini_frame.pack(pady=5, fill='x', padx=20)
        
        Label(gemini_frame, text="Gemini API Key:", bg='white').pack(side='left')
        get_gemini_btn = Button(
            gemini_frame,
            text="Get Google API Key",
            command=lambda: webbrowser.open('https://makersuite.google.com/app/apikey'),
            bg='#4285F4',
            fg='black',
            font=("Helvetica", 8)
        )
        get_gemini_btn.pack(side='right')
        
        gemini_entry = Entry(dialog, width=50)
        gemini_entry.pack(pady=5)

        # Mistral section
        mistral_frame = Frame(dialog, bg='white')
        mistral_frame.pack(pady=5, fill='x', padx=20)
        
        Label(mistral_frame, text="Mistral API Key:", bg='white').pack(side='left')
        get_mistral_btn = Button(
            mistral_frame,
            text="Get Mistral API Key",
            command=lambda: webbrowser.open('https://console.mistral.ai/api-keys/'),
            bg='#6B4FBB',
            fg='black',
            font=("Helvetica", 8)
        )
        get_mistral_btn.pack(side='right')
        
        mistral_entry = Entry(dialog, width=50)
        mistral_entry.pack(pady=5)

        # Info label
        Label(dialog,
              text="Note: You can continue without API keys.\nThe game will use default questions.",
              font=("Helvetica", 9),
              bg='white',
              fg='#666').pack(pady=20)
        
        def save_and_close():
            gemini_key = gemini_entry.get().strip()
            mistral_key = mistral_entry.get().strip()
            
            # Update instance variables
            if gemini_key:
                self.gemini_key = gemini_key
            if mistral_key:
                self.mistral_key = mistral_key
            
            # Save to config file if keys provided
            if gemini_key or mistral_key:
                config_dir = os.path.expanduser('~/.trivia_royale')
                os.makedirs(config_dir, exist_ok=True)
                config_file = os.path.join(config_dir, 'config.json')
                
                stored_keys = {}
                if gemini_key:
                    stored_keys['GEMINI_API_KEY'] = gemini_key
                if mistral_key:
                    stored_keys['MISTRAL_API_KEY'] = mistral_key
                
                try:
                    with open(config_file, 'w') as f:
                        json.dump(stored_keys, f)
                except Exception as e:
                    print(f"### ERROR: Failed to save config file: {e}")
        
            dialog.destroy()
        
        # Save button with better contrast
        save_button = Button(
            dialog,
            text="Save and Start Game",
            command=save_and_close,
            bg='#2E7D32',
            fg='black',
            font=("Helvetica", 10, "bold"),
            relief="raised",
            padx=20,
            pady=10
        )
        save_button.pack(pady=20)
        
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)

    def quit_game(self, event=None):
        """Safely exits the application."""
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        if pygame.get_init():
            pygame.quit()
        try:
            self.root.destroy()
        except tk.TclError:
            pass
        self.root.quit()


    def clear_screen(self):
        """Clear all widgets from the root window."""
        for widget in self.root.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                pass
        self.reveal_prompt_label = None
        self.correctness_prompt_label = None
        self.root.bind("<Escape>", self.quit_game)

    def _resize_and_display_bg(self):
        """Resizes and displays the background image."""
        self.clear_screen()

        if not self.original_bg_image:
            self.root.configure(bg=COLORS["light_blue"])
            self.bg_canvas = None
            return

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        try:
            resized_bg = self.original_bg_image.resize((screen_width, screen_height), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(resized_bg)
            self.bg_canvas = Canvas(self.root, width=screen_width, height=screen_height, borderwidth=0, highlightthickness=0)
            self.bg_canvas.pack(fill=tk.BOTH, expand=True)
            self.bg_canvas.create_image(0, 0, anchor='nw', image=self.bg_photo)
            self.bg_canvas.image = self.bg_photo
            self.root.update_idletasks()
        except Exception as e:
             print(f"### ERROR: Failed to resize or display background image: {e}")
             self.bg_canvas = None
             self.root.configure(bg=COLORS["light_blue"])


    def title_screen(self):
        self._resize_and_display_bg()

        # Title label commented out
        # title_label = Label(self.root, text="Trivia Royale", font=FONTS["large"], ...)
        # title_label.place(relx=0.5, rely=0.4, anchor='center')

        subtitle_label1 = Label(self.root, text="A more fun Trivia Game", font=FONTS["big_italic"],
                                bg=COLORS["black"], fg=COLORS["soft_coral"], padx=10)

        subtitle_label2 = Label(self.root, text="by K2 and a little bit Deepseek, chatGPT, Gemini, and Mistral",
                                font=("Helvetica", 17), bg=COLORS["black"], fg=COLORS["softer_coral"], padx=10)

        def show_subtitle1():
            # rely moved down
            subtitle_label1.place(relx=0.5, rely=0.58, anchor='center')

        def show_subtitle2():
            # rely moved down
            subtitle_label2.place(relx=0.5, rely=0.64, anchor='center')

        def proceed(event=None):
            self.root.unbind("<Return>")
            self.stop_music()
            self.get_number_of_rounds()

        def start_sequence():
            self.play_intro_theme()
            self.root.after(3750, show_subtitle1)
            self.root.after(5700, show_subtitle2)
            self.root.after(6000, lambda: self.root.bind("<Return>", proceed))

        self.root.after(1500, start_sequence)

    def _load_icon_image(self, parent_frame):
        """Helper to load and display the Trivia Royale icon"""
        try:
            icon_path = get_asset_path("TriviaRoyalIcon(2).png")
            icon_img = Image.open(icon_path)
            icon_img = icon_img.resize((80, 80), Image.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_img)
            icon_label = Label(parent_frame, image=icon_photo, bg=COLORS["light_blue"])
            icon_label.image = icon_photo  # Keep reference
            icon_label.pack()
        except Exception as e:
            # Fallback to crown emoji if image not found
            Label(parent_frame, text="\U0001F451", font=("Helvetica", 50), bg=COLORS["light_blue"]).pack()

    def get_number_of_rounds(self):
        self.clear_screen()
        self.root.configure(bg=COLORS["light_blue"])
        
        # Title with icon
        title_frame = Frame(self.root, bg=COLORS["light_blue"])
        title_frame.pack(pady=30)
        self._load_icon_image(title_frame)
        Label(title_frame, text="Trivia Royale", font=FONTS["big"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack()
        
        # Question
        Label(self.root, text="How many rounds would you like to play?", 
              font=FONTS["medium"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=20)
        
        # Helper text
        Label(self.root, text="(Each round = 1 question per team)", 
              font=FONTS["small"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"]).pack(pady=5)
        
        # Entry field with better styling
        entry_frame = Frame(self.root, bg=COLORS["dark_teal"], padx=2, pady=2)
        entry_frame.pack(pady=20)
        entry = Entry(entry_frame, font=("Helvetica", 36, "bold"), justify="center", 
                      bg=COLORS["light_blue"], fg=COLORS["soft_coral"], 
                      bd=0, highlightthickness=0, width=5)
        entry.pack(padx=10, pady=10)
        entry.focus_set()
        
        # Quick select buttons
        Label(self.root, text="Quick Select:", font=FONTS["small"], 
              fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=(30, 10))
        
        button_frame = Frame(self.root, bg=COLORS["light_blue"])
        button_frame.pack()
        
        def select_rounds(num):
            if self.sfx:
                self.sfx.play('button_click')
            entry.delete(0, tk.END)
            entry.insert(0, str(num))
            self.root.after(200, validate_input)
        
        quick_options = [3, 5, 10, 15]
        for num in quick_options:
            btn = Button(
                button_frame,
                text=str(num),
                font=("Helvetica", 24, "bold"),
                bg=COLORS["dark_teal"],
                fg=COLORS["light_blue"],
                activebackground=COLORS["soft_coral"],
                activeforeground=COLORS["light_blue"],
                padx=20,
                pady=10,
                bd=0,
                command=lambda n=num: select_rounds(n),
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Instructions
        Label(self.root, text="Type a number (1-25) or click a button above, then press ENTER", 
              font=FONTS["xsmall"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"]).pack(pady=(30, 10))
        
        def validate_input(event=None):
            try:
                num = int(entry.get())
                if 1 <= num <= 25:
                    if self.sfx:
                        self.sfx.play('button_click')
                    self.num_rounds = num
                    self.root.unbind("<Return>")
                    self.get_number_of_teams()
                else:
                    if self.sfx:
                        self.sfx.play('wrong')
                    messagebox.showerror("Invalid Input", "Please enter a number between 1 and 25.")
                    entry.delete(0, tk.END)
                    entry.focus_set()
            except ValueError:
                if entry.get():
                    if self.sfx:
                        self.sfx.play('wrong')
                    messagebox.showerror("Invalid Input", "Please enter a valid number.")
                    entry.delete(0, tk.END)
                entry.focus_set()
        
        self.root.bind("<Return>", validate_input)

    def get_number_of_teams(self):
        self.clear_screen()
        self.root.configure(bg=COLORS["light_blue"])
        
        # Title with icon
        title_frame = Frame(self.root, bg=COLORS["light_blue"])
        title_frame.pack(pady=30)
        self._load_icon_image(title_frame)
        Label(title_frame, text="Trivia Royale", font=FONTS["big"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack()
        
        # Question
        Label(self.root, text="How many teams are playing?", 
              font=FONTS["medium"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=20)
        
        # Helper text
        Label(self.root, text="(1-6 teams or individual players)", 
              font=FONTS["small"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"]).pack(pady=5)
        
        # Entry field with better styling
        entry_frame = Frame(self.root, bg=COLORS["dark_teal"], padx=2, pady=2)
        entry_frame.pack(pady=20)
        entry = Entry(entry_frame, font=("Helvetica", 36, "bold"), justify="center", 
                      bg=COLORS["light_blue"], fg=COLORS["soft_coral"], 
                      bd=0, highlightthickness=0, width=5)
        entry.pack(padx=10, pady=10)
        entry.focus_set()
        
        # Quick select buttons
        Label(self.root, text="Quick Select:", font=FONTS["small"], 
              fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=(30, 10))
        
        button_frame = Frame(self.root, bg=COLORS["light_blue"])
        button_frame.pack()
        
        def select_teams(num):
            if self.sfx:
                self.sfx.play('button_click')
            entry.delete(0, tk.END)
            entry.insert(0, str(num))
            self.root.after(200, validate_input)
        
        quick_options = [1, 2, 3, 4]
        labels = ["Solo", "2 Teams", "3 Teams", "4 Teams"]
        for num, label in zip(quick_options, labels):
            btn = Button(
                button_frame,
                text=label,
                font=("Helvetica", 18, "bold"),
                bg=COLORS["dark_teal"],
                fg=COLORS["light_blue"],
                activebackground=COLORS["soft_coral"],
                activeforeground=COLORS["light_blue"],
                padx=15,
                pady=15,
                bd=0,
                command=lambda n=num: select_teams(n),
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Instructions
        Label(self.root, text="Type a number (1-6) or click a button above, then press ENTER", 
              font=FONTS["xsmall"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"]).pack(pady=(30, 10))
        
        def validate_input(event=None):
            try:
                num = int(entry.get())
                if 1 <= num <= 6:
                    if self.sfx:
                        self.sfx.play('button_click')
                    self.num_teams = num
                    self.root.unbind("<Return>")
                    self.get_team_names()
                else:
                    if self.sfx:
                        self.sfx.play('wrong')
                    messagebox.showerror("Invalid Input", "Please enter a number between 1 and 6.")
                    entry.delete(0, tk.END)
                    entry.focus_set()
            except ValueError:
                if entry.get():
                    if self.sfx:
                        self.sfx.play('wrong')
                    messagebox.showerror("Invalid Input", "Please enter a valid number.")
                    entry.delete(0, tk.END)
                entry.focus_set()
        
        self.root.bind("<Return>", validate_input)

    def get_team_names(self):
        """Collect names for all teams."""
        self.clear_screen()
        self.root.configure(bg=COLORS["light_blue"])

        # Title with icon
        title_frame = Frame(self.root, bg=COLORS["light_blue"])
        title_frame.pack(pady=30)
        self._load_icon_image(title_frame)
        Label(title_frame, text="Trivia Royale", font=FONTS["big"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack()
        
        # Instruction
        Label(self.root, text="Enter Team Names", 
              font=FONTS["medium"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=20)
        
        # Helper text
        if self.num_teams == 1:
            helper_text = "(Playing solo - enter your name)"
        else:
            helper_text = f"(Enter a name for each of the {self.num_teams} teams)"
        Label(self.root, text=helper_text, 
              font=FONTS["small"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"]).pack(pady=5)

        self.team_entries = []
        entries_frame = Frame(self.root, bg=COLORS["light_blue"])
        entries_frame.pack(pady=20)

        for i in range(self.num_teams):
            # Container for each team entry
            team_frame = Frame(entries_frame, bg=COLORS["light_blue"])
            team_frame.pack(pady=10, padx=20)
            
            # Progress indicator
            if self.num_teams > 1:
                progress_text = f"Team {i + 1} of {self.num_teams}"
            else:
                progress_text = "Your Name"
            
            Label(team_frame, 
                  text=progress_text, 
                  font=FONTS["small"], 
                  fg=COLORS["soft_coral"], 
                  bg=COLORS["light_blue"]).pack(anchor='w', padx=5, pady=(0, 5))

            # Entry with border
            entry_container = Frame(team_frame, bg=COLORS["dark_teal"], padx=2, pady=2)
            entry_container.pack()
            
            entry = Entry(entry_container,
                          font=("Helvetica", 24, "bold"),
                          justify="center",
                          bg=COLORS["light_blue"],
                          fg=COLORS["soft_coral"],
                          bd=0,
                          highlightthickness=0,
                          width=20)
            entry.pack(padx=8, pady=8)

            self.team_entries.append(entry)
            if i == 0:
                entry.focus_set()

        # Instructions at bottom
        instruction_text = "Press ENTER after each name"
        if self.num_teams > 1:
            instruction_text += f" • {self.num_teams} teams total"
        Label(self.root, text=instruction_text, 
              font=FONTS["xsmall"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"]).pack(pady=(30, 10))

        def handle_team_name_input(event=None):
            current_focus = self.root.focus_get()
            current_index = -1
            if isinstance(current_focus, Entry):
                try:
                    current_index = self.team_entries.index(current_focus)
                except ValueError:
                    pass

            if current_index != -1 and not self.team_entries[current_index].get().strip():
                if self.sfx:
                    self.sfx.play('wrong')
                messagebox.showwarning("Input Required", f"Please enter a name for Team {current_index + 1}.")
                self.team_entries[current_index].focus_set()
                return

            if current_index < self.num_teams - 1:
                # Play sound and move to next
                if self.sfx:
                    self.sfx.play('button_click')
                self.team_entries[current_index + 1].focus_set()
            elif current_index == self.num_teams - 1:
                all_names = [entry.get().strip() for entry in self.team_entries]
                if all(all_names):
                    if self.sfx:
                        self.sfx.play('button_click')
                    self.team_names = all_names
                    self.scores = [0] * self.num_teams
                    self.root.unbind("<Return>")
                    self.select_categories()
                else:
                    if self.sfx:
                        self.sfx.play('wrong')
                    for i, entry in enumerate(self.team_entries):
                        if not entry.get().strip():
                            messagebox.showwarning("Input Required", f"Please enter a name for Team {i + 1}.")
                            entry.focus_set()
                            break

        self.root.bind("<Return>", handle_team_name_input)


    def select_categories(self):
        self.clear_screen()
        self.root.configure(bg=COLORS["light_blue"])

        # Title with icon (restored)
        title_frame = Frame(self.root, bg=COLORS["light_blue"])
        title_frame.pack(pady=10)
        self._load_icon_image(title_frame)
        Label(title_frame, text="Trivia Royale", font=FONTS["big"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack()

        # Instruction labels
        needed_count = 3 * self.num_teams
        Label(self.root, text=f"Select {needed_count} Categories Total", font=FONTS["medium"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"]).pack(pady=5)
        Label(self.root, text="or click 'Use Default'. Double-click 'Other' to customize.", font=FONTS["small"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=(0,10))

        # Category selection area
        outer_frame = Frame(self.root, bg=COLORS["light_blue"])
        outer_frame.place(relx=0.54, rely=0.58, anchor='center') 

        canvas = Canvas(outer_frame, bg=COLORS["light_blue"], borderwidth=0, highlightthickness=0, width=1100, height=600)
        category_frame = Frame(canvas, bg=COLORS["light_blue"], padx=20, pady=0)

        category_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=category_frame, anchor="nw")

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Checkboxes
        self.checkbox_vars = []
        self.checkbox_widgets = []
        num_columns = 4

        for i, category in enumerate(CATEGORIES):
            var = BooleanVar()
            checkbox = Checkbutton(
                category_frame, text=category, variable=var, font=FONTS["xsmall"],
                fg=COLORS["soft_yellow"], bg=COLORS["light_blue"], selectcolor=COLORS["black"],
                activebackground=COLORS["light_blue"], activeforeground=COLORS["soft_coral"],
                anchor="w", justify="left", wraplength=220, padx=5
            )
            row = i // num_columns
            col = i % num_columns
            checkbox.grid(row=row, column=col, sticky="nw", padx=15, pady=3)

            if category == "Other":
                checkbox.bind('<Double-Button-1>', lambda e, idx=i: self.modify_other_label(e, idx))

            self.checkbox_vars.append(var)
            self.checkbox_widgets.append(checkbox)

        # Error label
        error_label = Label(self.root, text="", font=FONTS["small"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"])
        error_label.pack(side=tk.BOTTOM, pady=(0, 60))

        # Buttons at bottom
        button_outer_frame = Frame(self.root, bg=COLORS["light_blue"])
        button_outer_frame.pack(side=tk.BOTTOM, pady=20)

        def submit_categories():
            selected_categories_texts = [self.checkbox_widgets[index].cget("text")
                                    for index, val in enumerate(self.checkbox_vars) if val.get()]
            if len(selected_categories_texts) != needed_count:
                if self.sfx: self.sfx.play('wrong')
                error_label.config(text=f"Selected {len(selected_categories_texts)}. Please select exactly {needed_count}.")
                return
            
            if self.sfx: self.sfx.play('button_click')
            self.selected_categories = selected_categories_texts
            self.select_difficulty()
            
        Button(button_outer_frame, text="Use Selected Categories", font=FONTS["small"], 
               fg=COLORS["light_blue"], bg=COLORS["dark_teal"], 
               command=submit_categories).pack(side=tk.LEFT, padx=10, pady=5)
        
        Button(button_outer_frame, text="Use Default Questions", font=FONTS["small"], 
               fg=COLORS["light_blue"], bg=COLORS["dark_teal"], 
               command=lambda: (self.sfx.play('button_click') if self.sfx else None,
                              setattr(self, "selected_categories", ["default"]), 
                              self.select_difficulty())).pack(side=tk.LEFT, padx=10, pady=5)



    def modify_other_label(self, event, checkbox_index):
        checkbox = self.checkbox_widgets[checkbox_index]
        current_text = checkbox.cget("text")
        popup = Toplevel(self.root)
        popup.title("Edit Category Name")
        popup.configure(bg=COLORS["light_blue"])
        x = self.root.winfo_rootx() + event.x + 20
        y = self.root.winfo_rooty() + event.y - 10
        popup.geometry(f"300x100+{x}+{y}")
        popup.transient(self.root)
        popup.grab_set()
        Label(popup, text="Enter new category name:", font=FONTS["small"], bg=COLORS["light_blue"], fg=COLORS["soft_yellow"]).pack(pady=(10,5))
        input_box = Entry(popup, font=FONTS["small"], fg=COLORS["black"], bg=COLORS["soft_yellow"])
        input_box.pack(pady=5, padx=10, fill='x')
        input_box.insert(0, current_text if current_text != "Other" else "")
        input_box.focus_set()
        def save_label(event=None):
            new_label = input_box.get().strip()
            if new_label:
                checkbox.config(text=new_label)
            popup.destroy()
        input_box.bind("<Return>", save_label)
        Button(popup, text="Save", command=save_label, font=FONTS["small"], bg=COLORS["dark_teal"], fg=COLORS["light_blue"]).pack(pady=5)
        popup.wait_window()

    def select_difficulty(self):
        self.clear_screen()
        self.root.configure(bg=COLORS["light_blue"])
        
        # Title with icon
        title_frame = Frame(self.root, bg=COLORS["light_blue"])
        title_frame.pack(pady=30)
        self._load_icon_image(title_frame)
        Label(title_frame, text="Trivia Royale", font=FONTS["big"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack()
        
        # Main question
        Label(self.root, text="Select Difficulty Levels", 
              font=FONTS["medium"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=20)
        
        # Helper text
        Label(self.root, text="(Choose one or more difficulty levels)", 
              font=FONTS["small"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"]).pack(pady=5)
        
        # Difficulty checkboxes with visual indicators
        diff_frame = Frame(self.root, bg=COLORS["light_blue"])
        diff_frame.pack(pady=30)
        
        self.diff_vars = {"Easy": BooleanVar(), "Medium": BooleanVar(), "Hard": BooleanVar()}
        
        difficulty_info = {
            "Easy": ("⭐", "Basic questions"),
            "Medium": ("⭐⭐", "Moderate challenge"),
            "Hard": ("⭐⭐⭐", "Expert level")
        }
        
        for i, (level, var) in enumerate(self.diff_vars.items()):
            # Container for each difficulty option
            container = Frame(diff_frame, bg=COLORS["light_blue"])
            container.grid(row=0, column=i, padx=20, pady=10)
            
            # Stars and label
            stars, description = difficulty_info[level]
            Label(container, text=stars, font=("Helvetica", 24), 
                  bg=COLORS["light_blue"]).pack()
            
            # Checkbox with better styling
            cb = Checkbutton(container, text=level, variable=var, 
                            font=("Helvetica", 18, "bold"), 
                            fg=COLORS["soft_yellow"], 
                            bg=COLORS["light_blue"], 
                            selectcolor=COLORS["dark_teal"], 
                            activebackground=COLORS["light_blue"], 
                            activeforeground=COLORS["soft_coral"],
                            padx=15, pady=10,
                            command=lambda: self.sfx.play('button_click') if self.sfx else None)
            cb.pack()
            
            # Description
            Label(container, text=description, font=FONTS["xsmall"],
                  fg=COLORS["soft_coral"], bg=COLORS["light_blue"]).pack()
        
        # Quick preset buttons
        Label(self.root, text="Quick Presets:", font=FONTS["small"], 
              fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=(30, 10))
        
        preset_frame = Frame(self.root, bg=COLORS["light_blue"])
        preset_frame.pack()
        
        def apply_preset(preset_name, levels):
            if self.sfx:
                self.sfx.play('button_click')
            # Clear all
            for var in self.diff_vars.values():
                var.set(False)
            # Set selected
            for level in levels:
                self.diff_vars[level].set(True)
        
        presets = [
            ("Beginner Friendly", ["Easy"]),
            ("Balanced Mix", ["Easy", "Medium", "Hard"]),
            ("Challenge Mode", ["Hard"])
        ]
        
        for name, levels in presets:
            btn = Button(preset_frame, text=name, 
                        font=("Helvetica", 14, "bold"),
                        bg=COLORS["dark_teal"], fg=COLORS["light_blue"],
                        activebackground=COLORS["soft_coral"],
                        activeforeground=COLORS["light_blue"],
                        padx=15, pady=8, bd=0,
                        command=lambda l=levels: apply_preset(name, l),
                        cursor="hand2")
            btn.pack(side=tk.LEFT, padx=5)
        
        # Continue button
        def continue_click():
            if self.sfx:
                self.sfx.play('button_click')
            self.process_difficulty_selection()
        
        Button(self.root, text="Continue", 
               font=("Helvetica", 18, "bold"), 
               fg=COLORS["light_blue"], 
               bg=COLORS["dark_teal"],
               activebackground=COLORS["soft_coral"],
               padx=30, pady=12, bd=0,
               command=continue_click,
               cursor="hand2").pack(pady=40)

    def process_difficulty_selection(self):
        selected_difficulties = [level for level, var in self.diff_vars.items() if var.get()]
        if not selected_difficulties:
            selected_difficulties = ["Medium"]
            self.diff_vars["Medium"].set(True)
        self.selected_difficulties = selected_difficulties
        self.generate_and_load_questions()

    def generate_and_load_questions(self):
        prompt = ""
        is_default = self.selected_categories == ["default"]
        if is_default:
            prompt = "default"
        else:
            categories_list = ", ".join(self.selected_categories)
            order = {"Easy": 1, "Medium": 2, "Hard": 3}
            sorted_difficulties = sorted(self.selected_difficulties, key=lambda x: order.get(x, 99))
            if len(sorted_difficulties) == 1: diff_clause = f"The questions should be primarily {sorted_difficulties[0].lower()} difficulty."
            elif len(sorted_difficulties) == 2: diff_clause = f"Include a mix of {sorted_difficulties[0].lower()} and {sorted_difficulties[1].lower()} difficulty questions."
            else: diff_clause = "Include a mix of easy, medium, and hard difficulty questions."
            num_questions_needed = self.num_rounds * self.num_teams + 1
            if num_questions_needed < 10: num_questions_needed = 10
            prompt = (f"Generate {num_questions_needed} unique trivia questions randomly selected from the following topics: {categories_list}. {diff_clause} Ensure that all answers are factually correct and concise. Output the results STRICTLY as a JSON array where each element is a JSON object containing ONLY two keys: \"question\" and \"answer\". Do NOT include any introductory text, explanations, markdown formatting (like ```json or ```), or comments outside the JSON structure.")

        wait_window = None
        if not is_default:
            # --- More Generic Initial Message ---
            wait_message = "One Moment Please...\n\nConnecting to Language Model..."
            # ----------------------------------
            wait_window = self.show_wait_message(wait_message)

        # Pass the wait_window object to the thread
        loading_thread = Thread(target=self._load_questions_thread, args=(prompt, wait_window), daemon=True)
        loading_thread.start()

    def _load_questions_thread(self, prompt, wait_window=None):
        """Thread for loading questions with LLM fallback logic"""
        loaded_questions = []
        llm_tried = False  # Track if we attempted any LLM

        if prompt == "default":
            # Load default questions logic here...
            if wait_window:
                self.root.after(0, self.update_wait_label, wait_window, "Default Files")
            # ... existing default loading code ...
        else:
            # Debug logging with instance variables
            print(f"### DEBUG: Attempting LLM generation with GEMINI_API_KEY present: {bool(self.gemini_key)}")
            print(f"### DEBUG: GEMINI_API_KEY length: {len(self.gemini_key) if self.gemini_key else 0}")
            print(f"### DEBUG: Attempting LLM generation with MISTRAL_API_KEY present: {bool(self.mistral_key)}")
            print(f"### DEBUG: MISTRAL_API_KEY length: {len(self.mistral_key) if self.mistral_key else 0}")

            # --- LLM Generation Logic ---
            raw_json_text = None # Initialize raw_json_text

            # --- Attempt Gemini ---
            if self.gemini_key:
                llm_tried = True
                print("### INFO: Attempting Gemini...")
                # Schedule update for Gemini model name
                if wait_window:
                    self.root.after(0, self.update_wait_label, wait_window, GEMINI_MODEL)
                # Make the actual call
                raw_json_text = self.generate_trivia_questions_gemini(prompt)
            else:
                print("### INFO: Gemini API Key not found, skipping Gemini.")
                raw_json_text = None # Ensure it's None if key is missing

            # --- Attempt Mistral (if Gemini failed/skipped and key exists) ---
            if raw_json_text is None and self.mistral_key:
                llm_tried = True
                print("### INFO: Gemini failed or key missing, attempting Mistral...")
                # Schedule update for Mistral model name
                if wait_window:
                    self.root.after(0, self.update_wait_label, wait_window, MISTRAL_MODEL)
                # Make the actual call
                raw_json_text = self.generate_trivia_questions_mistral(prompt)
            elif raw_json_text is None and not self.mistral_key:
                print("### INFO: Mistral API Key not found, skipping Mistral.")

            # --- Process Result (if any LLM was attempted and returned something) ---
            if raw_json_text:
                print("### INFO: Received response from LLM, attempting to parse...")
                try:
                    # Clean potential markdown formatting
                    cleaned_json = raw_json_text.strip().lstrip('```json').rstrip('```').strip()
                    # Be more robust finding the start/end of the list/object
                    list_start = cleaned_json.find('[')
                    obj_start = cleaned_json.find('{')

                    if list_start != -1 and (obj_start == -1 or list_start < obj_start):
                        # Looks like a list is intended
                        if not cleaned_json.startswith('['): cleaned_json = cleaned_json[list_start:]
                        list_end = cleaned_json.rfind(']')
                        if list_end != -1: cleaned_json = cleaned_json[:list_end+1]
                    elif obj_start != -1:
                         # Might be a single object or object containing a list
                         if not cleaned_json.startswith('{'): cleaned_json = cleaned_json[obj_start:]
                         obj_end = cleaned_json.rfind('}')
                         if obj_end != -1: cleaned_json = cleaned_json[:obj_end+1]
                    else:
                         # If neither [ nor { are found, assume it might be a raw list/object without them
                         pass # Keep cleaned_json as is for the json.loads attempt


                    parsed_data = json.loads(cleaned_json)

                    # Handle potential structure variations (e.g., object with a 'questions' key)
                    potential_list = None
                    if isinstance(parsed_data, list):
                        potential_list = parsed_data
                    elif isinstance(parsed_data, dict):
                        # Look for common key names that might contain the list
                        for key in ['questions', 'trivia', 'data', 'results']:
                             if key in parsed_data and isinstance(parsed_data[key], list):
                                 potential_list = parsed_data[key]
                                 break
                        # If no common key found, but it's a dict, maybe it's just one question/answer pair? Unlikely but possible.
                        # We primarily expect a list.
                    else:
                         print("### ERROR: LLM JSON was neither a list nor a recognized dictionary structure.")


                    # Validate the structure of the final list
                    if potential_list and all(isinstance(item, dict) and 'question' in item and 'answer' in item for item in potential_list):
                        loaded_questions = potential_list # Assign successfully parsed questions
                        print(f"### INFO: Successfully parsed {len(loaded_questions)} questions from LLM.")
                    else:
                        print("### ERROR: Parsed LLM JSON has unexpected structure or missing keys (question/answer).")
                        loaded_questions = [] # Ensure it's empty if parsing/validation fails

                except json.JSONDecodeError as e:
                    print(f"### ERROR: Failed to decode LLM JSON: {e}")
                    print(f"--- Start Raw LLM Response ---\n{raw_json_text}\n--- End Raw LLM Response ---")
                    loaded_questions = [] # Ensure empty on decode error
                except Exception as e:
                    print(f"### ERROR: Unexpected error processing LLM response: {e}")
                    loaded_questions = [] # Ensure empty on other errors

            # --- Fallback to Default (if LLMs were tried but failed/yielded no questions, or keys were missing) ---
            # Use the llm_tried flag here
            if not loaded_questions and (llm_tried or (not self.gemini_key and not self.mistral_key)):
                # Only print fallback message if an LLM was actually attempted or if no keys existed at all
                print("### WARNING: LLM generation failed or produced invalid data. Falling back to default questions.")
                # Schedule update for Default Files message
                if wait_window:
                    self.root.after(0, self.update_wait_label, wait_window, "Default Files")

                # --- Load from Default Files (Fallback Logic) ---
                files_to_load = []
                difficulty_map = {"Easy": "questions_easy.json", "Medium": "questions_medium.json", "Hard": "questions_hard.json"}
                for diff in self.selected_difficulties:
                    filename = difficulty_map.get(diff)
                    if filename:
                        files_to_load.append(get_asset_path(filename))
                if not files_to_load:
                    files_to_load.append(get_asset_path("questions_medium.json"))

                for fname in files_to_load:
                    try:
                        with open(fname, 'r', encoding='utf-8') as file:
                            data = json.load(file)
                            loaded_questions.extend(data)
                    except FileNotFoundError: print(f"### ERROR: Default file (fallback) not found: {fname}")
                    except json.JSONDecodeError as e: print(f"### ERROR: JSON decode error in {os.path.basename(fname)} (fallback): {e}")
                    except Exception as e: print(f"### ERROR: Error reading {os.path.basename(fname)} (fallback): {e}")

                if loaded_questions:
                    random.shuffle(loaded_questions)
                    num_needed = self.num_rounds * self.num_teams + 1
                    if len(loaded_questions) > num_needed + 20:
                        loaded_questions = loaded_questions[:num_needed + 20]
                else:
                     print("### CRITICAL ERROR: Failed to load ANY questions (LLM and Default fallback failed).")


        # --- Nested Function to Finalize Loading on Main Thread ---
        def finish_loading():
            """Runs on the main thread to update UI after loading."""
            # --- Reset Cursor FIRST (on root) ---
            try:
                # Only reset the root window's cursor
                self.root.config(cursor="")
                self.root.update_idletasks() # Optional: ensure reset is processed
                print("### DEBUG: Root cursor reset to default")
            except tk.TclError as e:
                 print(f"### WARNING: Could not reset root cursor: {e}")
            except Exception as e:
                 print(f"### ERROR: Unexpected error resetting cursor: {e}")
            # ------------------------------------

            # --- Destroy Wait Window ---
            if wait_window:
                try:
                    if wait_window.winfo_exists():
                        # No need to reset wait_window cursor as we didn't set it
                        wait_window.destroy()
                except tk.TclError:
                    pass # Window might already be gone
                except Exception as e:
                    print(f"### ERROR: Unexpected error destroying wait window: {e}")

            # --- Process Loaded Questions ---
            if loaded_questions:
                # ... (process questions and start game) ...
                self.questions = loaded_questions
                num_needed = self.num_rounds * self.num_teams + 1
                if len(self.questions) < num_needed:
                     messagebox.showwarning("Question Shortage", f"Warning: Only {len(self.questions)} questions loaded (needed {num_needed}). Game may end early or repeat questions if defaults were limited.")
                print(f"--- Question Loading Complete: {len(self.questions)} questions ready. ---")
                self.game_play() # Start the game
            else:
                # ... (handle critical loading error) ...
                messagebox.showerror("Loading Error", "CRITICAL: Failed to load any trivia questions from LLM or default files. Cannot start the game.")
                self.title_screen() # Go back to title screen

        # --- Schedule finish_loading to run on the main thread ---
        self.root.after(0, finish_loading)

    def update_wait_label(self, wait_window, model_name):
        """Safely updates the label text in the wait_window."""
        try:
            # Check if the window still exists
            if wait_window and wait_window.winfo_exists():
                # Find the Label widget within the window
                # Assumes the Label is the first/primary child widget
                for widget in wait_window.winfo_children():
                    if isinstance(widget, Label):
                        new_text = f"One Moment Please...\nGenerating questions from\n {model_name}"
                        widget.config(text=new_text)
                        # print(f"### DEBUG: Updated wait label to use {model_name}") # Optional debug
                        break # Stop after finding the first label
        except tk.TclError as e:
            # Handle cases where the window might be destroyed between check and config
            print(f"### INFO: Could not update wait label (window likely closed): {e}")
        except Exception as e:
            print(f"### ERROR: Unexpected error updating wait label: {e}")

    def show_wait_message(self, message="Please wait..."):
        wait_window = Toplevel(self.root)
        wait_window.title("Loading")
        # --- Center the window ---
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        # Use self.root dimensions if available, otherwise screen dimensions as fallback
        if root_width <= 1 or root_height <= 1: # Check if root window size is valid
            root_width = self.root.winfo_screenwidth()
            root_height = self.root.winfo_screenheight()
            root_x = 0
            root_y = 0

        win_width = 350 # Slightly wider for potentially longer messages
        win_height = 150 # Slightly taller
        x = root_x + (root_width // 2) - (win_width // 2)
        y = root_y + (root_height // 2) - (win_height // 2)
        wait_window.geometry(f"{win_width}x{win_height}+{x}+{y}")
        # --------------------------
        wait_window.configure(bg=COLORS["light_blue"])
        Label(wait_window, text=message, font=FONTS["small"], bg=COLORS["light_blue"], fg=COLORS["soft_yellow"], justify="center", wraplength=win_width - 40).pack(pady=20, padx=20, expand=True, fill=tk.BOTH)
        wait_window.transient(self.root)
        wait_window.grab_set()
        wait_window.resizable(False, False) # Prevent resizing

        # --- Cursor Change: Apply ONLY to root window ---
        try:
            self.root.config(cursor="watch")
            # Force the root window to process idle tasks, including cursor change
            self.root.update_idletasks()
            print("### DEBUG: Root cursor set to 'watch'")
        except tk.TclError as e:
            print(f"### WARNING: Could not set 'watch' cursor on root: {e}")
        except Exception as e:
            print(f"### ERROR: Unexpected error setting root cursor: {e}")
        # --- Do NOT set cursor on wait_window ---
        # try:
        #     wait_window.config(cursor="watch") # REMOVED/COMMENTED OUT
        # except: pass # Ignore errors here

        # wait_window.update_idletasks() # Update the wait window itself (already done essentially by pack/geometry)
        return wait_window

    # --- LLM Interaction ---
    def generate_trivia_questions_gemini(self, prompt):
        if not self.gemini_key:
            print("### ERROR: Gemini API Key not found.")
            return None
            
        genai.configure(api_key=self.gemini_key)
        # Use the constant here:
        model = genai.GenerativeModel(GEMINI_MODEL)
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"### ERROR: Gemini API Exception: {e}")
            return None

    def generate_trivia_questions_mistral(self, prompt):
        if not self.mistral_key:
            print("### ERROR: Mistral API Key not found.")
            return None

        try:
            headers = {
                "Authorization": f"Bearer {self.mistral_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": MISTRAL_MODEL,
                "messages": [{"role": "user", "content": prompt}]
            }
            response = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers=headers,
                json=data
            )
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                print(f"### ERROR: Mistral API Error: {response.status_code}")
                return None
        except Exception as e:
            print(f"### ERROR: Mistral API Exception: {e}")
            return None

    def get_trivia_questions_from_llm(self, prompt):
        raw_json_text = self.generate_trivia_questions_gemini(prompt)
        if raw_json_text is None:
            raw_json_text = self.generate_trivia_questions_mistral(prompt)
        if raw_json_text:
            try:
                cleaned_json = raw_json_text.strip().lstrip('```json').rstrip('```').strip()
                if not cleaned_json.startswith('['): list_start = cleaned_json.find('['); cleaned_json = cleaned_json[list_start:] if list_start != -1 else cleaned_json
                if not cleaned_json.endswith(']'): list_end = cleaned_json.rfind(']'); cleaned_json = cleaned_json[:list_end+1] if list_end != -1 else cleaned_json
                parsed_questions = json.loads(cleaned_json)
                if isinstance(parsed_questions, list) and all(isinstance(item, dict) and 'question' in item and 'answer' in item for item in parsed_questions):
                    return parsed_questions
                else: print("### ERROR: Parsed LLM JSON has unexpected structure."); return None
            except json.JSONDecodeError as e: print(f"### ERROR: Failed to decode LLM JSON: {e}\n--- Start Raw ---\n{raw_json_text}\n--- End Raw ---"); return None
            except Exception as e: print(f"### ERROR: Error processing LLM response: {e}"); return None
        else: print("### ERROR: Both LLMs failed."); return None

     # --- Text-to-Speech (IMPROVED WITH gTTS) ---
    def speak_text(self, text):
        """Speak text using gTTS (Google Text-to-Speech) for high-quality natural voice."""
        if not text:
            return

        try:
            from gtts import gTTS
            import tempfile
            
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_file = fp.name
            
            # Generate speech using Google's TTS (much more natural than pyttsx3)
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_file)
            
            # Play the audio using pygame
            try:
                pygame.mixer.music.load(temp_file)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                    
            finally:
                # Clean up temporary file
                try:
                    os.remove(temp_file)
                except:
                    pass
                    
        except ImportError:
            print("### WARNING: gTTS not available, falling back to pyttsx3")
            self._speak_text_fallback(text)
        except Exception as e:
            print(f"### ERROR: gTTS failed ({e}), falling back to pyttsx3")
            self._speak_text_fallback(text)
    
    def _speak_text_fallback(self, text):
        """Fallback TTS using pyttsx3 if gTTS fails."""
        engine = None
        try:
            try:
                engine = pyttsx3.init(driverName='nsss')
            except Exception:
                engine = pyttsx3.init()
            
            try:
                voices = engine.getProperty('voices')
                if voices:
                    # Try to use Samantha (better than Daniel)
                    desired_voice_id = "com.apple.speech.synthesis.voice.samantha"
                    try:
                        engine.setProperty('voice', desired_voice_id)
                    except:
                        pass  # Use default if not available
            except:
                pass
            
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.9)
            engine.say(text)
            engine.runAndWait()
            
        except Exception as e:
            print(f"### ERROR: Fallback TTS also failed: {e}")
        finally:
            if engine is not None:
                del engine


    # --- Music Control ---
    def stop_music(self):
        if pygame.mixer.get_init():
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            except pygame.error as e:
                print(f"### ERROR: Error stopping music: {e}")

    def play_music(self, filename, loops=-1):
        if not pygame.mixer.get_init():
             print("### ERROR: Audio mixer not initialized, cannot play music.")
             return
        try:
            music_path = get_asset_path(filename)
            if not os.path.exists(music_path):
                print(f"### WARNING: Music file not found at {music_path}")
                return

            self.stop_music()
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(loops=loops)
        except pygame.error as e:
            print(f"### ERROR: Pygame error playing music file {filename}: {e}")
        except Exception as e:
             print(f"### ERROR: General error playing music {filename}: {e}")


    def play_intro_theme(self):
        self.play_music("audio/TriviaRoyaleTheme(2).mp3", loops=0)

    def play_thinking_theme(self):
        random_number = random.randint(1, 7)
        theme_file = f"audio/TQ_music_{random_number}.mp3"
        self.play_music(theme_file, loops=-1)

    def play_winner_music(self):
        self.play_music("audio/TriviaChampion.mp3", loops=0)

    # --- Game Flow ---
    def game_play(self):
        if not self.questions:
             messagebox.showerror("Game Error", "No questions loaded!")
             self.title_screen(); return
        self.question_index = 0; self.current_round = 1; self.current_team = 0
        self.scores = [0] * self.num_teams; self.wagers = {}; self.collecting_wagers = False
        self.show_question()

    def display_scoreboard(self):
        """Displays a polished scoreboard at the top of the game screen."""
        score_container = Frame(self.root, bg=COLORS["dark_teal"], padx=2, pady=2)
        score_container.pack(pady=10, padx=40, fill=tk.X)
        
        score_frame = Frame(score_container, bg=COLORS["light_blue"], padx=10, pady=5)
        score_frame.pack(fill=tk.X)
        
        for i, (name, score) in enumerate(zip(self.team_names, self.scores)):
            team_container = Frame(score_frame, bg=COLORS["light_blue"])
            team_container.pack(side=tk.LEFT, expand=True, padx=10)
            
            # Highlight current team
            is_current = (i == self.current_team)
            fg_color = COLORS["soft_yellow"] if is_current else COLORS["soft_coral"]
            font_style = ("Helvetica", 14, "bold") if not is_current else ("Helvetica", 16, "bold")
            
            Label(team_container, text=f"{name}", font=font_style, fg=fg_color, bg=COLORS["light_blue"]).pack(side=tk.TOP)
            Label(team_container, text=f"{score} pts", font=("Helvetica", 18, "bold"), fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(side=tk.TOP)
        return score_container

    def show_progress_bar(self):
        """Displays a visual progress bar indicating game completion."""
        if self.num_rounds == 0: return
        
        progress_container = Frame(self.root, bg=COLORS["light_blue"])
        progress_container.pack(fill=tk.X, padx=100, pady=(0, 20))
        
        # Calculate progress Percentage (total rounds * total teams)
        total_questions = self.num_rounds * self.num_teams
        current_question_num = ((self.current_round - 1) * self.num_teams) + self.current_team + 1
        progress_percent = min(1.0, current_question_num / total_questions) if total_questions > 0 else 0
        
        # Background bar
        bar_bg = Frame(progress_container, bg=COLORS["dark_teal"], height=10)
        bar_bg.pack(fill=tk.X, pady=5)
        bar_bg.pack_propagate(False)
        
        # Foreground bar (filled)
        bar_fg = Frame(bar_bg, bg=COLORS["soft_yellow"], height=10)
        bar_fg.place(relx=0, rely=0, relwidth=progress_percent)
        
        # Text indicator
        Label(progress_container, 
              text=f"Question {current_question_num} of {total_questions}", 
              font=FONTS["xsmall"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"]).pack()


    # Callback function for root.after (for UI updates/key bindings)
    def setup_reveal_prompt(self):
             try:
                 self.play_thinking_theme()

                 if self.reveal_prompt_label and self.reveal_prompt_label.winfo_exists():
                     self.reveal_prompt_label.config(text="Press 'Enter' to reveal Answer")
                 else:
                     print("### ERROR: self.reveal_prompt_label is None or destroyed, cannot config!")

                 self.unbind_key("<Return>")
                 self.unbind_key("<Key-x>")
                 self.unbind_key("<Key-X>")

                 if self.question_index < len(self.questions):
                    current_q_data = self.questions[self.question_index]
                    self.bind_key("<Return>", lambda e, data=current_q_data: self.handle_reveal_answer(data))
                 else:
                     print("### ERROR: Cannot bind Return, question index out of bounds!")
                 self.bind_key("<Key-x>", self.handle_skip_question)
                 self.bind_key("<Key-X>", self.handle_skip_question)

             except Exception as e:
                  print(f"### ERROR in setup_reveal_prompt: {e}")


    def show_question(self):
        if self.question_index >= len(self.questions):
            messagebox.showinfo("Game End", "No more questions available.")
            self.determine_final_round_or_winner(); return

        self.clear_screen(); self.root.configure(bg=COLORS["light_blue"])
        
        # Title with icon
        title_frame = Frame(self.root, bg=COLORS["light_blue"])
        title_frame.pack(pady=(10, 5))
        self._load_icon_image(title_frame)
        Label(title_frame, text="Trivia Royale", font=FONTS["big"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack()
        
        self.display_scoreboard()
        self.show_progress_bar()

        if self.current_round > self.num_rounds:
             self.final_question_round(); return

        # Current Turn Indicator
        turn_frame = Frame(self.root, bg=COLORS["dark_teal"], padx=2, pady=2)
        turn_frame.pack(pady=10)
        Label(turn_frame, text=f" Round {self.current_round}/{self.num_rounds} • {self.team_names[self.current_team]}'s Turn ", 
              font=FONTS["big_italic"], fg=COLORS["light_blue"], bg=COLORS["dark_teal"]).pack()

        if self.question_index < len(self.questions):
            current_q_data = self.questions[self.question_index]
            current_question = current_q_data["question"]
        else:
            print("### ERROR: question_index out of bounds in show_question!")
            self.determine_final_round_or_winner(); return

        # Question text with better spacing
        question_label = Label(self.root, text=current_question, 
                               font=FONTS["medium"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"], 
                               wraplength=self.root.winfo_screenwidth() * 0.8, justify="center")
        question_label.pack(pady=30)

        # Trigger TTS Synchronously via root.after
        tts_delay_ms = 10
        self.root.after(tts_delay_ms, self.speak_text, current_question)

        # UI Update / Key Binding Setup
        self.reveal_prompt_label = Label(self.root, text="", font=FONTS["medium_bold"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"])
        self.reveal_prompt_label.pack(pady=40)

        # Schedule the UI update/bindings using a SEPARATE `after` call
        ui_setup_delay_ms = 2500
        self.root.after(ui_setup_delay_ms, self.setup_reveal_prompt)


    def handle_reveal_answer(self, question_data, event=None):
        self.stop_music()
        self.unbind_keys_for_reveal()
        self.show_answer(question_data["question"], question_data["answer"])


    def handle_skip_question(self, event=None):
        self.stop_music()
        self.unbind_keys_for_reveal()
        self.next_turn_logic()
        if self.current_round > self.num_rounds:
             self.final_question_round()
        else:
             self.show_question()

    def unbind_keys_for_reveal(self):
        self.unbind_key("<Return>")
        self.unbind_key("<Key-x>")
        self.unbind_key("<Key-X>")


    def show_answer(self, question_text, answer_text):
        self.clear_screen(); self.root.configure(bg=COLORS["light_blue"])
        
        # Title with icon
        title_frame = Frame(self.root, bg=COLORS["light_blue"])
        title_frame.pack(pady=(10, 5))
        self._load_icon_image(title_frame)
        Label(title_frame, text="Trivia Royale", font=FONTS["big"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack()
        
        self.display_scoreboard()
        self.show_progress_bar()

        Label(self.root, text="Answer", font=FONTS["big_italic"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=40)
        
        # Answer container for emphasis
        answer_container = Frame(self.root, bg=COLORS["dark_teal"], padx=3, pady=3)
        answer_container.pack(pady=20)
        
        answer_label = Label(answer_container, text=answer_text, 
                             font=("Helvetica", 28, "bold"), 
                             fg=COLORS["soft_yellow"], bg=COLORS["light_blue"], 
                             wraplength=self.root.winfo_screenwidth() * 0.8,
                             padx=40, pady=20)
        answer_label.pack()


        # Trigger Answer TTS Synchronously via root.after
        tts_delay_ms = 10
        self.root.after(tts_delay_ms, self.speak_text, answer_text)

        # Create correctness prompt label
        self.correctness_prompt_label = Label(self.root, text=f"Team {self.team_names[self.current_team]} was your answer correct?\n(Y)es  (N)o  (G)oogle it", font=FONTS["medium_bold"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"])
        self.correctness_prompt_label.pack(pady=60)

        # Bind keys for correctness - Schedule this after a longer delay
        bind_delay_ms = 2500
        def bind_correctness_keys():
             self.unbind_keys_for_correctness() # Unbind first
             self.bind_key("<Key-y>", lambda e: self.handle_correctness_input("y", question_text))
             self.bind_key("<Key-Y>", lambda e: self.handle_correctness_input("y", question_text))
             self.bind_key("<Key-n>", lambda e: self.handle_correctness_input("n", question_text))
             self.bind_key("<Key-N>", lambda e: self.handle_correctness_input("n", question_text))
             self.bind_key("<Key-g>", lambda e: self.handle_correctness_input("g", question_text))
             self.bind_key("<Key-G>", lambda e: self.handle_correctness_input("g", question_text))
        self.root.after(bind_delay_ms, bind_correctness_keys)


    def handle_correctness_input(self, key_char, question_text):
        """Process Y/N/G input after answer reveal."""
        self.unbind_keys_for_correctness()

        if key_char == "y":
            self.scores[self.current_team] += 10
            self.next_turn()
        elif key_char == "n":
            self.next_turn()
        elif key_char == "g":
            try:
                 pyperclip.copy(question_text)
                 webbrowser.open(f"https://www.google.com/search?q={requests.utils.quote(question_text)}")
            except Exception as e: print(f"### ERROR: Google/Copy failed: {e}"); messagebox.showerror("Error", f"Google/Copy failed:\n{e}")

            # Re-prompt for Y/N *only*
            if self.correctness_prompt_label and self.correctness_prompt_label.winfo_exists():
                self.correctness_prompt_label.config(text=f"After checking... Team {self.team_names[self.current_team]}, correct?\n(Y = Yes / N = No)")
                # Re-bind *only* Y and N
                self.bind_key("<Key-y>", lambda e: self.handle_correctness_input("y", question_text))
                self.bind_key("<Key-Y>", lambda e: self.handle_correctness_input("y", question_text))
                self.bind_key("<Key-n>", lambda e: self.handle_correctness_input("n", question_text))
                self.bind_key("<Key-N>", lambda e: self.handle_correctness_input("n", question_text))
            else:
                 print("### ERROR: Cannot re-prompt for Y/N, correctness_prompt_label is None or destroyed.")
            # Do NOT call next_turn() here


    def unbind_keys_for_correctness(self):
        self.unbind_key("<Key-y>")
        self.unbind_key("<Key-Y>")
        self.unbind_key("<Key-n>")
        self.unbind_key("<Key-N>")
        self.unbind_key("<Key-g>")
        self.unbind_key("<Key-G>")


    def next_turn(self):
        """Advances the game state AFTER a correct/incorrect decision."""
        self.next_turn_logic()
        if self.current_round > self.num_rounds:
            if not self.collecting_wagers:
                 self.final_question_round()
        else:
             self.show_question()


    def next_turn_logic(self):
         """Handles the logic of incrementing team, round, and question index."""
         self.current_team = (self.current_team + 1) % self.num_teams
         if self.current_team == 0:
             self.current_round += 1
         self.question_index += 1


    def bind_key(self, key, func):
        self.root.bind(key, func)

    def unbind_key(self, key):
        self.root.unbind(key)

    # --- Final Question Round ---
    # Apply similar synchronous TTS scheduling via root.after

    def final_question_round(self):
        if self.question_index >= len(self.questions):
             messagebox.showinfo("Game End", "No question left for final round!")
             self.show_winner(); return
        if self.collecting_wagers: return
        self.clear_screen(); self.root.configure(bg=COLORS["light_blue"])
        self.display_title_and_scoreboard()
        Label(self.root, text="Final Question Round!", font=FONTS["large"], bg=COLORS["light_blue"], fg=COLORS["soft_coral"]).pack(pady=20)
        Label(self.root, text="Teams, prepare your wagers.", font=FONTS["medium"], bg=COLORS["light_blue"], fg=COLORS["soft_yellow"]).pack(pady=10)
        self.play_music("audio/FinalQuestionRound.mp3", loops=-1)
        self.wagers = {}; self.collecting_wagers = True
        self.collect_wager_for_team(0)

    def display_title_and_scoreboard(self):
        """Displays consistent title with icon and scoreboard."""
        title_frame = Frame(self.root, bg=COLORS["light_blue"])
        title_frame.pack(pady=(10, 5))
        self._load_icon_image(title_frame)
        Label(title_frame, text="Trivia Royale", font=FONTS["big"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack()
        self.display_scoreboard()

    def collect_wager_for_team(self, team_index):
        if team_index >= self.num_teams:
            self.collecting_wagers = False; self.display_final_question(); return
        team_name = self.team_names[team_index]; team_score = self.scores[team_index]; max_wager = max(0, team_score)
        wager_frame = Frame(self.root, bg=COLORS["light_blue"]); wager_frame.pack(pady=20, fill='x')
        wager_label = Label(wager_frame, text=f"{team_name}, enter wager (0-{max_wager}):", font=FONTS["medium_bold"], bg=COLORS["light_blue"], fg=COLORS["soft_yellow"]); wager_label.pack(pady=(10, 5))

        # Ensure wager entry has bd=0 and highlightthickness=0
        wager_entry = Entry(wager_frame,
                            font=FONTS["medium_bold"],
                            fg=COLORS["soft_coral"],
                            bg=COLORS["light_blue"],
                            justify="center",
                            bd=0, # Explicitly 0
                            highlightthickness=0, # Remove highlight
                            width=10)
        wager_entry.pack(pady=5)
        wager_entry.focus_set()

        error_label = Label(wager_frame, text="", font=FONTS["small"], bg=COLORS["light_blue"], fg=COLORS["red"]); error_label.pack(pady=(0, 10))
        def submit_wager(event=None):
            try:
                wager_input = wager_entry.get(); wager = int(wager_input) if wager_input else -1 # Handle empty
                if 0 <= wager <= max_wager:
                    self.wagers[team_name] = wager
                    self.unbind_key("<Return>"); wager_frame.destroy(); self.collect_wager_for_team(team_index + 1)
                else: error_label.config(text=f"Invalid! Enter 0 to {max_wager}."); wager_entry.select_range(0, tk.END)
            except ValueError: error_label.config(text="Invalid! Enter a number."); wager_entry.select_range(0, tk.END)
        self.bind_key("<Return>", submit_wager)


    def display_final_question(self):
        self.stop_music()
        self.clear_screen(); self.root.configure(bg=COLORS["light_blue"])
        self.display_title_and_scoreboard()
        if self.question_index >= len(self.questions): print("### ERROR: No final question index available!"); self.show_winner(); return

        if self.question_index < len(self.questions):
            current_q_data = self.questions[self.question_index]
            current_question = current_q_data["question"]
        else: print("### ERROR: Final question index out of bounds!"); self.show_winner(); return

        Label(self.root, text="Final Question!", font=FONTS["large"], bg=COLORS["light_blue"], fg=COLORS["soft_coral"]).pack(pady=20)
        Label(self.root, text=current_question, font=FONTS["medium"], bg=COLORS["light_blue"], fg=COLORS["soft_yellow"], wraplength=self.root.winfo_screenwidth() * 0.7).pack(pady=20)

        # Schedule Final Question TTS
        tts_delay_ms = 10
        self.root.after(tts_delay_ms, self.speak_text, current_question)

        # Setup Reveal Prompt
        self.reveal_prompt_label = Label(self.root, text="", font=FONTS["medium_bold"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"]); self.reveal_prompt_label.pack(pady=60)

        def setup_final_reveal_prompt():
             # Music call RESTORED
             self.play_thinking_theme()

             if self.reveal_prompt_label and self.reveal_prompt_label.winfo_exists():
                 self.reveal_prompt_label.config(text="Press 'Enter' for Final Answer")
             else: print("### ERROR: reveal_prompt_label is None or destroyed in final setup!")

             self.unbind_key("<Return>") # Ensure clean bind
             self.bind_key("<Return>", lambda e, data=current_q_data: self.handle_final_reveal(data))

        # Schedule UI update after a longer delay
        ui_setup_delay_ms = 2500
        self.root.after(ui_setup_delay_ms, setup_final_reveal_prompt)

    def handle_final_reveal(self, question_data, event=None):
         self.stop_music(); self.unbind_key("<Return>")
         self.show_final_answer(question_data["question"], question_data["answer"])

    def show_final_answer(self, question_text, answer_text):
        self.clear_screen(); self.root.configure(bg=COLORS["light_blue"])
        self.display_title_and_scoreboard()
        Label(self.root, text="Final Answer", font=FONTS["large"], bg=COLORS["light_blue"], fg=COLORS["soft_coral"]).pack(pady=20)
        Label(self.root, text=answer_text, font=FONTS["medium"], bg=COLORS["light_blue"], fg=COLORS["soft_yellow"], wraplength=self.root.winfo_screenwidth() * 0.7).pack(pady=20)

        # Schedule Final Answer TTS
        tts_delay_ms = 10
        self.root.after(tts_delay_ms, self.speak_text, answer_text)

        # Schedule the prompt check slightly later to ensure TTS has started blocking
        prompt_delay_ms = 500
        self.root.after(prompt_delay_ms, self.prompt_final_correctness, question_text, 0)


    def prompt_final_correctness(self, question_text, team_index):
        if team_index >= self.num_teams: self.show_winner(); return
        team_name = self.team_names[team_index]
        prompt_frame = Frame(self.root, bg=COLORS["light_blue"]); prompt_frame.pack(pady=30, fill='x')
        correctness_label = Label(prompt_frame, text=f"{team_name}, correct? (Y/N/G)", font=FONTS["medium_bold"], bg=COLORS["light_blue"], fg=COLORS["soft_coral"]); correctness_label.pack()

        def handle_final_correctness_input(key_char):
             self.unbind_keys_for_final_correctness()
             wager = self.wagers.get(team_name, 0)
             if key_char == "y": self.scores[team_index] += wager
             elif key_char == "n": self.scores[team_index] -= wager
             elif key_char == "g":
                 try: pyperclip.copy(question_text); webbrowser.open(f"https://www.google.com/search?q={requests.utils.quote(question_text)}")
                 except Exception as e: print(f"### ERROR: Final Google failed: {e}")

                 if correctness_label.winfo_exists():
                     correctness_label.config(text=f"After checking... {team_name}, correct? (Y/N)")
                     self.bind_key("<Key-y>", lambda e: handle_final_correctness_input("y"))
                     self.bind_key("<Key-Y>", lambda e: handle_final_correctness_input("y"))
                     self.bind_key("<Key-n>", lambda e: handle_final_correctness_input("n"))
                     self.bind_key("<Key-N>", lambda e: handle_final_correctness_input("n"))
                 else:
                      print("### ERROR: Cannot re-prompt final correctness, label destroyed.")
                 return # Wait for Y/N
             if prompt_frame.winfo_exists():
                 prompt_frame.destroy()
             self.prompt_final_correctness(question_text, team_index + 1)

        self.unbind_keys_for_final_correctness() # Unbind before binding new ones
        self.bind_key("<Key-y>", lambda e: handle_final_correctness_input("y"))
        self.bind_key("<Key-Y>", lambda e: handle_final_correctness_input("y"))
        self.bind_key("<Key-n>", lambda e: handle_final_correctness_input("n"))
        self.bind_key("<Key-N>", lambda e: handle_final_correctness_input("n"))
        self.bind_key("<Key-g>", lambda e: handle_final_correctness_input("g"))
        self.bind_key("<Key-G>", lambda e: handle_final_correctness_input("g"))


    def unbind_keys_for_final_correctness(self):
        self.unbind_key("<Key-y>"); self.unbind_key("<Key-Y>")
        self.unbind_key("<Key-n>"); self.unbind_key("<Key-N>")
        self.unbind_key("<Key-g>"); self.unbind_key("<Key-G>")


    def determine_final_round_or_winner(self):
         if self.current_round > self.num_rounds and not self.collecting_wagers:
             self.final_question_round()
         else:
             self.show_winner()

    def show_winner(self):
        self.stop_music()
        self.clear_screen(); self.root.configure(bg=COLORS["light_blue"])
        self.display_title_and_scoreboard()
        if not self.scores: Label(self.root, text="Game Over!", font=FONTS["large"], bg=COLORS["light_blue"], fg=COLORS["soft_coral"]).pack(pady=100); return
        if not self.scores:
            max_score = 0; winners = []
        else:
            try:
                 max_score = max(self.scores)
                 winners = [(self.team_names[i], score) for i, score in enumerate(self.scores) if score == max_score]
            except ValueError:
                 max_score = 0; winners = []

        if len(winners) == 1: win_text = f"Winner: {winners[0][0]} ({winners[0][1]} pts)!"
        elif len(winners) > 1: win_text = f"Tie: {', '.join([w[0] for w in winners])} ({max_score} pts)!"
        else: win_text = "Game Over!"
        Label(self.root, text=win_text, font=FONTS["big_italic"], bg=COLORS["light_blue"], fg=COLORS["soft_coral"], wraplength=self.root.winfo_screenwidth()*0.8).pack(pady=80)

        # Music call RESTORED
        self.play_winner_music()

        Label(self.root, text="Press ESC to Exit", font=FONTS["medium"], bg=COLORS["light_blue"], fg=COLORS["soft_yellow"]).pack(pady=20)


# --- Main Execution ---
if __name__ == "__main__":
    try:
        root = tk.Tk()
        game = TriviaGame(root)
        root.mainloop()
    except Exception as main_e:
        print(f"### FATAL ERROR: An unexpected error occurred: {main_e}")
        # traceback.print_exc() # Can remove traceback
        if pygame.get_init(): pygame.quit()
        try: messagebox.showerror("Fatal Error", f"An unexpected error occurred:\n{main_e}\n\nApplication will close.")
        except: pass
        sys.exit(1)
