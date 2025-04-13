import tkinter as tk
from tkinter import messagebox
import pyttsx3
import threading
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
from threading import Thread, Event
import speech_recognition as sr
import re

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')

# Constants for colors and fonts
COLORS = {
    "light_blue": "#36a0fe",
    "soft_yellow": "#ffff99",
    "dark_teal": "#9dd8e6",
    "soft_coral": "#deaaef",
    "softer_coral": "#deaF50"
}

FONTS = {
    "large": ("Helvetica", 60, "bold"),
    "big": ("Helvetica", 40, "bold"),
    "big_italic": ("Helvetica", 40, "bold", "italic"),
    "medium": ("Helvetica", 28),
    "medium_bold": ("Helvetica", 30, "bold", "italic"),
    "small": ("Helvetica", 18)
}

CATEGORIES = [
    "General Science", "Physics and Astronomy", "Medicine", "Toxicology", "Technology", 
    "History", "Geography", "World Capitals", "All about France", "Famous Landmarks", "Cycling", 
    "College Football", "Pro Football", "Knitting", "Gardening", "Equine Topics", "Art and Literature",
    "Music", "Movies", "The 70's", "The 80's", "The 90's", "Mythology", "Home Improvements", 
    "TV Shows", "All about Wine", "Food and Restaurants", "Famous Inventors", 
    "Real Estate", "The Natural World", "Business and Economics", "Philosophy", "Riddles and Puzzles", 
    "Linguistics", "National Parks", "Hiking related", "Our Pets", "Other", "Other", "Other"
]

class TriviaGame:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=COLORS["light_blue"])
        
        self.engine_lock = threading.Lock()
        self.tts_thread = None
        self.question_index = 0

        pygame.mixer.init()
        pygame.init()

        self.num_rounds = 0
        self.num_teams = 0
        self.team_names = []
        self.scores = []
        self.wagers = {}
        self.collecting_wagers = False


        self.bg_image = Image.open(os.path.abspath("/Users/Owner/Projects/Python/Trivia Royal/TriviaRoyaleScene(2).jpg"))
        self.bg_image = self.bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()), Image.LANCZOS)
        
        self.recognizer = sr.Recognizer()
        self.mic_lock = threading.Lock()
        
        self.title_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def title_screen(self):
        self.clear_screen()
        canvas = tk.Canvas(self.root, width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight(), bg=COLORS["light_blue"])
        canvas.pack(fill=tk.BOTH, expand=True)
        
        self.bg_image = Image.open(os.path.abspath("/Users/Owner/Projects/Python/Trivia Royal/TriviaRoyaleScene(2).jpg"))
        bg_photo = ImageTk.PhotoImage(self.bg_image)
    
        canvas.create_image(180, 0, anchor='nw', image=bg_photo)
        canvas.image = bg_photo

        subtitle_label1 = tk.Label(canvas, text="A more fun Trivia Game", font=FONTS["big_italic"], bg="black", fg=COLORS["soft_coral"])
        subtitle_label2 = tk.Label(canvas, text="by K2 and a little bit Deepseek, chatGPT, Gemini, and Mistral", font=("Helvetica", 17), bg="black", fg=COLORS["softer_coral"])
        
        def show_subtitle1():
            subtitle_label1.place(relx=0.5, rely=0.53, anchor='center')
        
        def show_subtitle2():
            subtitle_label2.place(relx=0.5, rely=0.59, anchor='center')
        
        def proceed(event):
            self.stop_music()
            self.get_number_of_rounds()
        
        def music_thread():
            self.play_intro_theme()
        
        def start_sequence():
            thread = threading.Thread(target=music_thread)
            thread.daemon = True
            thread.start()
            
            self.root.after(3750, show_subtitle1)
            self.root.after(5700, show_subtitle2)
            self.root.bind("<Return>", proceed)
        
        self.root.after(1000, start_sequence)

    def listen_for_input(self, prompt_text, entry_widget, callback, number_mode=False, category_mode=False):
        """Basic speech recognition without manual fallback."""
        # Speak the prompt first
        def speak_prompt():
            self.speak_text(prompt_text)
        
        # Run speech in background thread to not block
        speech_thread = threading.Thread(target=speak_prompt, daemon=True)
        speech_thread.start()
        speech_thread.join()  # Wait for speech to finish before listening
        
        # Create status label for listening feedback
        status_label = tk.Label(self.root, text="Listening...", 
                               font=FONTS["medium"], 
                               fg=COLORS["soft_coral"], 
                               bg=COLORS["light_blue"])
        status_label.pack(pady=10)
        
        with self.mic_lock:
            mic = sr.Microphone()
            with mic as source:
                try:
                    # Adjust for ambient noise and show we're listening
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=5)
                    
                    # Remove listening status
                    status_label.destroy()
                    
                    text = self.recognizer.recognize_google(audio).lower()
                    
                    if number_mode:
                        processed_text = self.process_number_input(text)
                    elif category_mode:
                        processed_text = self.process_category_input(text)
                    else:
                        processed_text = text
                    
                    if processed_text:
                        entry_widget.delete(0, tk.END)
                        entry_widget.insert(0, processed_text)
                        # Add 2-second delay before calling callback
                        self.root.after(2000, lambda: callback(processed_text))
                        return True
                    
                except (sr.WaitTimeoutError, sr.UnknownValueError):
                    status_label.destroy()
                    self.root.after(1500, lambda: self.listen_for_input(prompt_text, entry_widget, callback, number_mode, category_mode))
                except sr.RequestError as e:
                    status_label.destroy()
                    print(f"Could not request results; {e}")
                    return False

    def process_number_input(self, text):
        """Convert spoken number words to digits."""
        # Dictionary for number words
        number_words = {
            'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
            'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10',
            'eleven': '11', 'twelve': '12'
            }
        
        # Remove words like "rounds" or "teams" and clean up the text
        text = text.lower()
        text = text.replace('rounds', '').replace('round', '')
        text = text.replace('teams', '').replace('team', '')
        text = text.replace('players', '').replace('player', '')
        text = text.strip()
        
        # Check if text is already a number
        if text.isdigit():
            return text
            
        # Try to convert word to number
        return number_words.get(text)

    def process_category_input(self, text):
        """Process spoken category input."""
        # Convert to lowercase for matching
        text = text.lower()
        
        # List to store matched categories
        matched_categories = []
        
        # Check each category for a match
        for category in CATEGORIES:
            if category.lower() in text:
                matched_categories.append(category)
        
        return matched_categories if matched_categories else None

    def get_number_of_rounds(self):
        self.clear_screen()
        self.root.title("Number of Rounds")
        
        tk.Label(self.root, text="Trivia Royale", font=FONTS["big"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=20)
        tk.Label(self.root, text="Enter Number of Rounds (1-25):", font=FONTS["big"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=20)

        entry = tk.Entry(self.root, font=FONTS["big_italic"], justify="center", bg=COLORS["light_blue"], fg=COLORS["soft_coral"], bd=0)
        entry.pack(pady=20)
        entry.focus_set()

        def validate_input(event=None):
            try:
                num = int(entry.get())
                if 1 <= num <= 25:
                    self.num_rounds = num
                    self.get_number_of_teams()
                else:
                    messagebox.showerror("Invalid Input", "Please enter a number between 1 and 25.")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number.")

        self.root.bind("<Return>", validate_input)

        def start_speech():
            self.listen_for_input("How many rounds?", entry, validate_input, number_mode=True)
        threading.Thread(target=start_speech, daemon=True).start()

    def get_number_of_teams(self):
        self.clear_screen()
        self.root.title("Number of Teams")
        
        tk.Label(self.root, text="Trivia Royale", font=FONTS["big"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=20)
        tk.Label(self.root, text="Enter Number of Teams/Players (1-6):", font=FONTS["big"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=20)

        entry = tk.Entry(self.root, font=FONTS["big_italic"], justify="center", bg=COLORS["light_blue"], fg=COLORS["soft_coral"], bd=0)
        entry.pack(pady=20)
        entry.focus_set()

        def validate_input(event=None):
            try:
                num = int(entry.get())
                if 1 <= num <= 6:
                    self.num_teams = num
                    self.get_team_names()
                else:
                    messagebox.showerror("Invalid Input", "Please enter a number between 1 and 6.")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number.")

        self.root.bind("<Return>", validate_input)

        def start_speech():
            self.listen_for_input("How many teams or players?", entry, validate_input, number_mode=True)
        threading.Thread(target=start_speech, daemon=True).start()

    def get_team_names(self):
        self.clear_screen()
        self.root.title("Team Names")
        
        tk.Label(self.root, text="Trivia Royale", font=FONTS["big"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=20)
        tk.Label(self.root, text="Enter Team/Player Names:", font=FONTS["big"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=20)

        self.team_entries = []
        for i in range(self.num_teams):
            frame = tk.Frame(self.root, bg=COLORS["light_blue"])
            frame.pack(pady=10)
            tk.Label(frame, text=f"Team/Player {i + 1}", font=FONTS["big_italic"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(side=tk.LEFT, padx=10)
            entry = tk.Entry(frame, font=FONTS["big_italic"], justify="center", bg=COLORS["light_blue"], fg=COLORS["soft_coral"], bd=0)
            entry.pack(side=tk.LEFT, padx=1)
            self.team_entries.append(entry)
            if i == 0:
                entry.focus_set()

        def handle_team_name(event=None):
            for entry in self.team_entries:
                if not entry.get():
                    entry.focus_set()
                    return
            self.team_names = [entry.get().capitalize() for entry in self.team_entries]
            self.scores = [0] * self.num_teams
            self.select_categories()

        self.root.bind("<Return>", handle_team_name)

        def start_speech_for_team(index=0):
            if index >= len(self.team_entries):
                handle_team_name()
                return
            entry = self.team_entries[index]
            def next_team():
                # Add delay before moving to next team
                self.root.after(2000, lambda: start_speech_for_team(index + 1))
            def handle_speech_input(text):
                # Capitalize first letter of each word
                capitalized_text = ' '.join(word.capitalize() for word in text.split())
                entry.delete(0, tk.END)
                entry.insert(0, capitalized_text)
                next_team()
                return True
            def retry_speech():
                self.listen_for_input(f"What's the name for team {index + 1}?", entry, handle_speech_input, number_mode=False)
            threading.Thread(target=retry_speech, daemon=True).start()

        start_speech_for_team(0)

    def select_categories(self):
        self.clear_screen()
        self.root.title("Select Categories")
        
        tk.Label(self.root, text="Select Categories", font=FONTS["big"], 
                 fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=20)
        
        # Create scrollable frame for categories
        categories_frame = tk.Frame(self.root, bg=COLORS["light_blue"])
        categories_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        # Dictionary to store category checkboxes
        self.category_vars = {}
        
        # Create checkboxes for categories
        for i, category in enumerate(CATEGORIES):
            row = i // 4  # 4 categories per row
            col = i % 4
            var = tk.BooleanVar()
            self.category_vars[category] = var
            tk.Checkbutton(categories_frame, text=category, variable=var,
                          font=FONTS["small"], fg=COLORS["soft_yellow"],
                          bg=COLORS["light_blue"], selectcolor=COLORS["soft_coral"]).grid(
                              row=row, column=col, padx=10, pady=5, sticky='w')
        
        # Buttons frame
        button_frame = tk.Frame(self.root, bg=COLORS["light_blue"])
        button_frame.pack(pady=20)
        
        submit_button = tk.Button(button_frame, text="Submit", font=FONTS["small"],
                                 fg=COLORS["light_blue"], bg=COLORS["dark_teal"])
        submit_button.pack(side=tk.LEFT, padx=10)
        
        default_button = tk.Button(button_frame, text="Use Default Categories",
                                  font=FONTS["small"], fg=COLORS["light_blue"],
                                  bg=COLORS["dark_teal"])
        default_button.pack(side=tk.LEFT, padx=10)

        # Define category selection methods
        def process_category_selection():
            selected = [cat for cat, var in self.category_vars.items() if var.get()]
            if len(selected) < 3:
                messagebox.showwarning("Warning", "Please select at least 3 categories")
                return
            self.selected_categories = selected
            self.select_difficulty()

        def use_default_categories():
            self.selected_categories = ["default"]
            self.select_difficulty()

        # Configure button commands
        submit_button.config(command=process_category_selection)
        default_button.config(command=use_default_categories)
        
        # Allow manual selection with Enter key
        self.root.bind("<Return>", lambda e: process_category_selection())
        
        # Start speech prompt for categories
        def start_speech():
            self.speak_text("Please select at least three categories for your trivia game, or choose default categories.")
        threading.Thread(target=start_speech, daemon=True).start()

    def select_difficulty(self):
        self.clear_screen()
        self.root.title("Select Difficulty")
        
        tk.Label(self.root, text="Select Difficulty Levels", font=FONTS["big"], 
                 fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=20)
        
        diff_frame = tk.Frame(self.root, bg=COLORS["light_blue"])
        diff_frame.pack(pady=10)
        
        self.diff_vars = {
            "Easy": tk.BooleanVar(),
            "Medium": tk.BooleanVar(),
            "Hard": tk.BooleanVar()
        }
        
        # Create checkbuttons
        for i, (diff, var) in enumerate(self.diff_vars.items()):
            tk.Checkbutton(diff_frame, text=diff, variable=var, font=FONTS["small"], 
                          fg=COLORS["soft_yellow"], bg=COLORS["light_blue"], 
                          selectcolor=COLORS["soft_coral"]).grid(row=0, column=i, padx=10, pady=5)
        
        continue_button = tk.Button(self.root, text="Continue", font=FONTS["small"], 
                                  fg=COLORS["light_blue"], bg=COLORS["dark_teal"], 
                                  command=self.after_difficulty_selection)
        continue_button.pack(pady=20)

        def process_difficulties(text):
            # Convert text to lowercase
            text = text.lower()
            
            # Check if user wants to continue
            if "continue" in text:
                return "continue"
                
            difficulties = []
            # Remove the word 'difficulty' and clean the text
            text = text.replace('difficulty', '').strip()
            
            # Check for each difficulty level
            if "easy" in text:
                self.diff_vars["Easy"].set(True)
                difficulties.append("Easy")
            if "medium" in text:
                self.diff_vars["Medium"].set(True)
                difficulties.append("Medium")
            if "hard" in text:
                self.diff_vars["Hard"].set(True)
                difficulties.append("Hard")
                
            return difficulties

        def handle_speech_input(text):
            result = process_difficulties(text)
            if result == "continue":
                self.root.after(500, self.after_difficulty_selection)
                return True
            elif result:
                # Continue listening for more selections
                self.root.after(500, lambda: self.listen_for_input(
                    "Say another difficulty or say continue", 
                    dummy_entry,
                    handle_speech_input,
                    number_mode=False
                ))
            return False

        dummy_entry = tk.Entry(self.root)  # Hidden entry for speech interface
        threading.Thread(
            target=lambda: self.listen_for_input(
                "What difficulty you want? Say continue when done.", 
                dummy_entry,
                handle_speech_input,
                number_mode=False
            ),
            daemon=True
        ).start()

        # Allow manual selection with Enter key
        self.root.bind("<Return>", lambda e: self.after_difficulty_selection())

    def after_difficulty_selection(self):
        selected_difficulties = [level for level, var in self.diff_vars.items() if var.get()]
        if not selected_difficulties:
            selected_difficulties = ["Medium"]
        self.selected_difficulties = selected_difficulties
        self.generate_prompt(self.selected_categories, self.selected_difficulties)

    def generate_prompt(self, selected_categories, selected_difficulties):
        if selected_categories == ["default"]:
            prompt = "default"
        else:
            categories_list = ", ".join(selected_categories)
            order = {"Easy": 1, "Medium": 2, "Hard": 3}
            sorted_difficulties = sorted(selected_difficulties, key=lambda x: order.get(x, 99))
            
            if len(sorted_difficulties) == 1:
                diff_clause = f"Focus on {sorted_difficulties[0].lower()} questions."
            elif len(sorted_difficulties) == 2:
                diff_clause = f"Balance {sorted_difficulties[0].lower()} and {sorted_difficulties[1].lower()} questions."
            else:
                diff_clause = "Balance easy, medium, and hard questions."
            
            prompt = (
                f"Generate 10 trivia questions randomly selected from the following topics: {categories_list}. {diff_clause}. Ensure that all answers are fact-checked. Output the results as a JSON array where each element is a JSON object containing only two keys: question and answer. Do not include any extra text, formatting, or commentary."
            )
        self.load_questions(prompt)

    def generate_trivia_questions_gemini(self, prompt):
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini Exception: {e}")
            return None
        
    def generate_trivia_questions_mistral(self, prompt):
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "mistral-tiny",
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            response = requests.post(
                url, 
                headers=headers, 
                json=data,  # Fixed: using json as keyword argument
                timeout=30
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.RequestException as e:
            print(f"Mistral Error: {e}")
            return None

    def get_trivia_questions(self, prompt):
        questions = self.generate_trivia_questions_gemini(prompt)
        if questions is None:
            questions = self.generate_trivia_questions_mistral(prompt)
        if questions:
            try:
                cleaned_questions = questions.strip().replace('```json', '').replace('```', '')
                parsed_questions = json.loads(cleaned_questions)
                return parsed_questions
            except json.JSONDecodeError as e:
                return None
        return None

    def load_questions(self, prompt):
        questions = []
        if (prompt == "default"):
            if not hasattr(self, "selected_difficulties") or not self.selected_difficulties:
                self.selected_difficulties = ["Medium"]
            files = []
            if "Easy" in self.selected_difficulties:
                files.append('/Users/Owner/Projects/Python/Trivia Royal/questions_easy.json')
            if "Medium" in self.selected_difficulties:
                files.append('/Users/Owner/Projects/Python/Trivia Royal/questions_medium.json')
            if "Hard" in self.selected_difficulties:
                files.append('/Users/Owner/Projects/Python/Trivia Royal/questions_hard.json')
            for fname in files:
                try:
                    with open(fname, 'r', encoding='utf-8') as file:
                        questions.extend(json.load(file))
                except FileNotFoundError:
                    print(f"Error: The questions file {fname} was not found.")
            random.shuffle(questions)
        else:
            wait_window = self.get_question_from_LLM()
            try:
                trivia_data = self.get_trivia_questions(prompt)
                if trivia_data:
                    questions = [{"question": item['question'], "answer": item['answer']} for item in trivia_data]
                else:
                    print("Failed to generate questions from LLM. Falling back to default.")
                    questions = self.load_questions("default")
            except Exception as e:
                print(f"Error fetching questions: {e}")
                questions = self.load_questions("default")
            finally:
                wait_window.destroy()

        if questions:
            self.game_play(questions)
        else:
            messagebox.showerror("Error", "No questions loaded. Game cannot proceed.")
            self.root.destroy()

    def get_question_from_LLM(self):
        wait_window = tk.Toplevel(self.root)
        wait_window.title("Getting Questions from LLM")
        wait_window.geometry("+%d+%d" % (self.root.winfo_rootx()+60, self.root.winfo_rooty()+70))
        instruction = (
            "Fetching trivia questions from an LLM.\n\n"
            "Please wait while the questions are being generated.\n\n"
            "This might take a moment."
        )
        tk.Label(wait_window, text=instruction, font=FONTS["medium"], bg=COLORS["light_blue"], fg=COLORS["soft_yellow"], justify="center").pack(pady=20, padx=20)
        wait_window.transient(self.root)
        wait_window.grab_set()
        return wait_window

    def speak_text(self, text):
        with self.engine_lock:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 1)
            engine.say(text)
            engine.runAndWait()

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
        except Exception as e:
            print(f"Error stopping music: {e}")

    def play_theme(self):
        random_number = random.randint(1, 7)
        music_file = f"/Users/Owner/Projects/Python/Trivia Royal/TQ_music_{random_number}.mp3"
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play(-1, 0.0)

    def play_intro_theme(self):
        music_file = "/Users/Owner/Projects/Python/Trivia Royal/TriviaRoyaleTheme(2).mp3"
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    def play_winner_music(self):
        music_file = "/Users/Owner/Projects/Python/Trivia Royal/TriviaChampion.mp3"
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play()

    def game_play(self, questions):
        self.questions = questions
        self.current_round = 1
        self.current_team = 0
        self.show_question()

    def show_question(self):
        if self.question_index >= len(self.questions):
            print("No more questions available. Game over.")
            return

        self.clear_screen()
        
        tk.Label(self.root, text="Trivia Royale", font=FONTS["big"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=20)
        score_frame = tk.Frame(self.root, bg=COLORS["light_blue"], relief=tk.RIDGE, bd=2)
        score_frame.pack(pady=10, padx=20, fill=tk.X)
        for name, score in zip(self.team_names, self.scores):
            tk.Label(score_frame, text=f"{name}: {score}", font=FONTS["medium_bold"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"]).pack(side=tk.LEFT, expand=True)

        tk.Label(self.root, text=f"Round {self.current_round} - {self.team_names[self.current_team]}'s Turn",
                 font=FONTS["big_italic"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=60)

        current_question = self.questions[self.question_index]["question"]
        question_label = tk.Label(self.root, text=current_question, font=FONTS["medium"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"], wraplength=700)
        question_label.pack(pady=10)

        def speak_in_background():
            self.speak_text(current_question)
        speech_thread = threading.Thread(target=speak_in_background, daemon=True)
        speech_thread.start()

        def start_music_after_speech():
            speech_thread.join()
            self.play_theme()
            reveal_label = tk.Label(self.root, text="Press 'Enter' to reveal the Answer", font=FONTS["medium_bold"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"])
            reveal_label.pack(pady=80)
            
            def on_enter(event):
                pygame.mixer.music.stop()
                self.show_answer(current_question, self.questions[self.question_index]["answer"], self.show_question)
            self.root.bind("<Return>", on_enter)
            self.root.bind("<Key>", lambda event: self.handle_key(event, self.show_question))
        music_thread = threading.Thread(target=start_music_after_speech, daemon=True)
        music_thread.start()

    def show_answer(self, question, answer, next_action):
        if self.question_index >= len(self.questions):
            self.game_over()
            return

        self.clear_screen()
        
        tk.Label(self.root, text="Trivia Royale", font=FONTS["big"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=20)
        score_frame = tk.Frame(self.root, bg=COLORS["light_blue"], relief=tk.RIDGE, bd=2)
        score_frame.pack(pady=10, padx=20, fill=tk.X)
        for name, score in zip(self.team_names, self.scores):
            tk.Label(score_frame, text=f"{name}: {score}", font=FONTS["medium_bold"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"]).pack(side=tk.LEFT, expand=True)

        tk.Label(self.root, text="Answer", font=FONTS["big_italic"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=60)
        answer_label = tk.Label(self.root, text=answer, font=FONTS["medium"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"], wraplength=700)
        answer_label.pack(pady=10)

        def speak_in_background():
            self.speak_text(answer)
        speech_thread = threading.Thread(target=speak_in_background, daemon=True)
        speech_thread.start()

        tk.Label(self.root, text="Was the answer correct? (Y/N) or (G) to Google it",
                font=FONTS["medium_bold"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"]).pack(pady=80)

        def handle_answer(event):
            if event.char.lower() == "y":
                self.scores[self.current_team] += 10
            elif event.char.lower() == "n":
                pass
            elif event.char.lower() == "g":
                webbrowser.open(f"https://www.google.com/search?q={question}")
                return

            self.unbind_key("<Key>")
            self.next_turn(next_action)
        self.root.bind("<Key>", handle_answer)

    def next_turn(self, next_action):
        self.current_team = (self.current_team + 1) % self.num_teams
        if self.current_team == 0:
            self.current_round += 1
        self.question_index += 1
        if self.current_round > self.num_rounds:
            if not self.collecting_wagers:
                self.wagers = {}
                self.final_question_round()
        else:
            next_action()

    def handle_key(self, event, show_question):
        if event.char.lower() == "x":
            if self.question_index < len(self.questions) - 1:
                self.question_index += 1
                pygame.mixer.music.stop()
                show_question()
            else:
                print("No more questions available.")

    def bind_key(self, key, func):
        self.root.bind(key, func)

    def unbind_key(self, key):
        self.root.unbind(key)

    def final_question_round(self):
        if self.collecting_wagers:
            return
        self.clear_screen()
        self.display_title_and_scoreboard()
        self.collect_wagers(team_index=0)

    def display_title_and_scoreboard(self):
        tk.Label(self.root, text="Trivia Royale", font=FONTS["big"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=20)
        score_frame = tk.Frame(self.root, bg=COLORS["light_blue"], relief=tk.RIDGE, bd=2)
        score_frame.pack(pady=10, padx=20, fill=tk.X)
        for name, score in zip(self.team_names, self.scores):
            tk.Label(score_frame, text=f"{name}: {score}", font=FONTS["medium_bold"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"]).pack(side=tk.LEFT, expand=True)

    def collect_wagers(self, team_index):
        if self.collecting_wagers:
            return
        self.collecting_wagers = True
        self.unbind_key("<Return>")

        if team_index >= len(self.team_names):
            self.collecting_wagers = False
            self.display_final_question()
            return

        team_name = self.team_names[team_index]
        team_score = self.scores[team_index]

        if team_index == 0:
            tk.Label(self.root, text="Final Question Round", font=FONTS["large"], bg=COLORS["light_blue"], fg=COLORS["soft_coral"]).pack(pady=20)

        wager_label = tk.Label(self.root, text=f"Team {team_name}, enter your wager (≤ {team_score}):", font=FONTS["medium_bold"], bg=COLORS["light_blue"], fg=COLORS["soft_yellow"])
        wager_label.pack(pady=30)

        wager_entry = tk.Entry(self.root, font=FONTS["medium_bold"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"], justify="center", bd=0)
        wager_entry.pack(pady=10)
        wager_entry.focus_set()

        error_label = tk.Label(self.root, text="", font=FONTS["small"], bg=COLORS["light_blue"], fg="red")
        error_label.pack()

        def submit_wager(event=None):
            try:
                wager = int(wager_entry.get())
                if wager < 0 or wager > team_score:
                    error_label.config(text=f"Invalid wager! Enter a value ≤ {team_score}.")
                else:
                    self.wagers[team_name] = wager
                    wager_label.destroy()
                    wager_entry.destroy()
                    error_label.destroy()
                    self.collecting_wagers = False
                    self.root.unbind("<Return>")
                    self.collect_wagers(team_index + 1)
            except ValueError:
                error_label.config(text="Invalid input! Please enter a number.")
                self.collecting_wagers = False

        self.root.bind("<Return>", submit_wager)

    def display_final_question(self):
        self.clear_screen()
        self.display_title_and_scoreboard()

        if self.question_index < len(self.questions):
            current_question = self.questions[self.question_index]["question"]
            question_label = tk.Label(self.root, text=f"Final Question:\n\n\n{current_question}", font=FONTS["medium"], bg=COLORS["light_blue"], fg=COLORS["soft_yellow"], wraplength=500)
            question_label.pack(pady=20)
    
            def speak_in_background():
                self.speak_text(current_question)
            speech_thread = threading.Thread(target=speak_in_background, daemon=True)
            speech_thread.start()

            def start_music_after_speech():
                speech_thread.join()
                self.play_theme()
                reveal_label = tk.Label(self.root, text="Press 'Enter' to reveal the Answer", font=FONTS["medium_bold"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"])
                reveal_label.pack(pady=80)
                
                def on_enter(event):
                    pygame.mixer.music.stop()
                    self.show_final_answer(current_question, self.questions[self.question_index]["answer"])
                self.root.bind("<Return>", on_enter)
                self.root.bind("<Key>", lambda event: self.handle_key(event, self.display_final_question))
            music_thread = threading.Thread(target=start_music_after_speech, daemon=True)
            music_thread.start()
        else:
            print("No question available for final round.")
            self.show_winner()

    def show_final_answer(self, question, answer):
        self.clear_screen()
        self.display_title_and_scoreboard()

        answer_label = tk.Label(self.root, text=f"Answer:\n\n\n{answer}", font=FONTS["medium"], bg=COLORS["light_blue"], fg=COLORS["soft_yellow"], wraplength=500)
        answer_label.pack(pady=20)

        speech_thread = threading.Thread(target=lambda: self.speak_text(answer), daemon=True)
        speech_thread.start()

        self.prompt_correctness(question, team_index=0)

    def prompt_correctness(self, question, team_index):
        if team_index >= len(self.team_names):
            self.show_winner()
            return

        team_name = self.team_names[team_index]
        wager = self.wagers.get(team_name, 0)

        correctness_label = tk.Label(self.root, text=f"Team {team_name}, did you get it correct? (Y/N/G)", font=FONTS["medium_bold"], bg=COLORS["light_blue"], fg=COLORS["soft_coral"])
        correctness_label.pack(pady=80)

        def handle_answer(event):
            if event.char.lower() == "y":
                self.scores[team_index] += wager
            elif event.char.lower() == "n":
                self.scores[team_index] -= wager
            elif event.char.lower() == "g":
                webbrowser.open(f"https://www.google.com/search?q={question}")
                return

            correctness_label.destroy()
            self.unbind_key("<Key>")
            self.prompt_correctness(question, team_index + 1)

        self.root.bind("<Key>", handle_answer)

    def show_winner(self):
        self.clear_screen()
        self.display_title_and_scoreboard()

        winner = max(zip(self.team_names, self.scores), key=lambda x: x[1])
        winner_label = tk.Label(self.root, text=f"The winner is {winner[0]} with {winner[1]} points!", font=FONTS["big_italic"], bg=COLORS["light_blue"], fg=COLORS["soft_coral"])
        winner_label.pack(pady=100)
        self.play_winner_music()

        def exit_program(event):
            self.root.destroy()
        self.root.bind("<Escape>", exit_program)

    def game_over(self):
        self.clear_screen()
        winner = max(zip(self.team_names, self.scores), key=lambda x: x[1])
        tk.Label(self.root, text=f"The winner is {winner[0]} with {winner[1]} points!", font=FONTS["big_italic"], bg=COLORS["light_blue"], fg=COLORS["soft_coral"]).pack(pady=100)
        self.play_winner_music()
        self.root.bind("<Escape>", lambda e: self.root.destroy())

if __name__ == "__main__":
    root = tk.Tk()
    game = TriviaGame(root)
    root.mainloop()