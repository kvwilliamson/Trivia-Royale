import tkinter as tk
from tkinter import messagebox
import pyttsx3
import threading
import random
import pygame
import webbrowser
import pyperclip
import os
import sys

def get_resource_path(filename):
    """Get the correct path for bundled files when running as an executable."""
    if getattr(sys, 'frozen', False):  # Running as a PyInstaller bundle
        return os.path.join(sys._MEIPASS, filename)
    else:  # Running as a normal script
        return filename
    
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

# Categories for trivia questions
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
        
        self.title_screen()

    def clear_screen(self):
        """Clear all widgets from the root window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def title_screen(self):
        """Display the title screen of the game."""
        self.clear_screen()
        
        # Create and display "Trivia Royale"
        title_label = tk.Label(self.root, text="Trivia Royale", font=FONTS["large"], bg=COLORS["light_blue"], fg=COLORS["soft_yellow"])
        title_label.pack(pady=(200, 0))  # Centered on the screen
        
        # Create the subtitle labels but don't pack them yet
        subtitle_label1 = tk.Label(self.root, text="A more fun Trivia Game", font=FONTS["big_italic"], 
                                   bg=COLORS["light_blue"], fg=COLORS["soft_coral"])
        subtitle_label2 = tk.Label(self.root, text="by K2 and a little bit Deepseek, chatGPT, Gemini, and Claude", font=("Helvetica", 17), 
                                   bg=COLORS["light_blue"], fg=COLORS["softer_coral"])
        
        def show_subtitle1():
            subtitle_label1.pack(pady=(15, 0))
        
        def show_subtitle2():
            subtitle_label2.pack(pady=(15, 0))
        
        def proceed(event):
            self.stop_music()
            self.get_number_of_rounds()  # Move to the next function
        
        def music_thread():
            self.play_intro_theme()
        
        # Start everything in sequence
        def start_sequence():
            # Start music in a separate thread
            thread = threading.Thread(target=music_thread)
            thread.daemon = True  # Set as daemon so it ends when main program ends
            thread.start()
            
            # Show subtitles after delays
            self.root.after(3750, show_subtitle1)
            self.root.after(5700, show_subtitle2)

            # Enable the Enter key to proceed
            self.root.bind("<Return>", proceed)
        
        # Start the sequence immediately after the window appears
        self.root.after(100, start_sequence)

    def get_number_of_rounds(self):
        """Ask for the number of rounds to play."""
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

    def get_number_of_teams(self):
        """Ask for the number of teams."""
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

    def get_team_names(self):
        """Collect names for all teams."""
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
            self.team_names = [entry.get() for entry in self.team_entries]
            self.scores = [0] * self.num_teams
            self.select_difficulties()

        self.root.bind("<Return>", handle_team_name)

    def select_difficulties(self):
        """Allow teams to select difficulty levels for trivia questions."""
        self.clear_screen()
        self.root.title("Select Difficulties")

        tk.Label(self.root, text="Trivia Royale", font=FONTS["big"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=10)
        tk.Label(self.root, text="Select Difficulty Levels:", font=FONTS["medium"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"]).pack(pady=5)

        difficulties_frame = tk.Frame(self.root, bg=COLORS["light_blue"])
        difficulties_frame.pack(pady=5)

        self.difficulty_vars = []
        difficulties = ["Easy", "Medium", "Hard"]

        for difficulty in difficulties:
            var = tk.BooleanVar()
            checkbox = tk.Checkbutton(difficulties_frame, text=difficulty, variable=var, font=FONTS["small"],
                                    fg=COLORS["soft_yellow"], bg=COLORS["light_blue"], selectcolor=COLORS["light_blue"], anchor="w")
            checkbox.pack(side=tk.TOP, padx=10, pady=2)
            self.difficulty_vars.append(var)

        def submit_difficulties():
            selected_difficulties = [difficulties[i] for i, var in enumerate(self.difficulty_vars) if var.get()]
            if not selected_difficulties:
                tk.messagebox.showerror("Error", "Please select at least one difficulty level.")
                return
            self.generate_prompt(selected_difficulties)

        tk.Button(self.root, text="Submit", font=FONTS["small"], fg=COLORS["light_blue"], bg=COLORS["dark_teal"], command=submit_difficulties).pack(pady=10)

    def generate_prompt(self, selected_difficulties):
        """Generate a prompt for trivia questions based on selected difficulties."""
        questions = []
        for difficulty in selected_difficulties:
            questions.extend(self.load_questions(difficulty.lower()))
        
        if questions:
            random.shuffle(questions)
            self.game_play(questions)
        else:
            print("Failed to load questions. Game cannot proceed.")

    def load_questions(self, difficulty):
        """Load trivia questions from a file based on difficulty."""
        try:
            with open(get_resource_path(f'questions_{difficulty}.txt'), 'r', encoding='utf-8') as file:
                questions = []
                for line in file:
                    question, answer = line.strip().split('|')
                    questions.append({"question": question, "answer": answer})
                return questions
        except FileNotFoundError:
            print(f"Error: The questions file for {difficulty} was not found.")
            return []

    def wait_for_user(self):
        """Wait for the user to confirm they've saved the file."""
        def proceed():
            wait_window.destroy()  # Close the dialog when the button is clicked

        wait_window = tk.Toplevel(self.root)
        wait_window.title("Get Trivia Questions")
        tk.Label(wait_window, text="Press the button after saving questions .txt file.").pack(pady=10)
        tk.Button(wait_window, text="Continue", command=proceed).pack(pady=5)
        wait_window.transient(self.root)  # Make this window appear above the main window
        wait_window.grab_set()  # Block interaction with the main window
        self.root.wait_window(wait_window)  # Pause the program until this window is closed

    def speak_text(self, text):
        """Speak text using text-to-speech in a thread-safe manner."""
        with self.engine_lock:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 1)
            engine.say(text)
            engine.runAndWait()

    def speak_question(self, question):
        """Speak the question in the background."""
        def speak_in_background():
            self.speak_text(question)

        speech_thread = threading.Thread(target=speak_in_background, daemon=True)
        speech_thread.start()

    def stop_music(self):
        """Stop the currently playing music."""
        try:
            pygame.mixer.music.stop()
        except Exception as e:
            print(f"Error stopping music: {e}")

    def play_theme(self):
        """Play a random theme song."""
        random_number = random.randint(1, 3)
        music_file = get_resource_path(f"TQ_music_{random_number}.mp3")

        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play(-1, 0.0)

    def play_intro_theme(self):
        """Play the intro theme for the game."""
        music_file = get_resource_path("TriviaRoyaleTheme.mp3")
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    def play_winner_music(self):
        """Play music for the winner."""
        music_file = get_resource_path("TriviaChampion.mp3")

        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play()

    def game_play(self, questions):
        """Main gameplay loop to display questions and handle answers."""
        self.questions = questions
        self.current_round = 1
        self.current_team = 0
        self.show_question()

    def show_question(self):
        """Display the question for the current team and round with specific timing."""
        if self.question_index >= len(self.questions):
            print("No more questions available. Game over.")
            return

        self.clear_screen()
        
        # Display game title and scoreboard
        tk.Label(self.root, text="Trivia Royale", font=FONTS["big"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=20)
        score_frame = tk.Frame(self.root, bg=COLORS["light_blue"], relief=tk.RIDGE, bd=2)
        score_frame.pack(pady=10, padx=20, fill=tk.X)
        for name, score in zip(self.team_names, self.scores):
            tk.Label(score_frame, text=f"{name}: {score}", font=FONTS["medium_bold"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"]).pack(side=tk.LEFT, expand=True)

        # Display round and team turn
        tk.Label(self.root, text=f"Round {self.current_round} - {self.team_names[self.current_team]}'s Turn",
                 font=FONTS["big_italic"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=60)

        current_question = self.questions[self.question_index]["question"]
        question_label = tk.Label(self.root, text=current_question, font=FONTS["medium"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"], wraplength=700)
        question_label.pack(pady=10)

        # Speak the question
        def speak_in_background():
            self.speak_text(current_question)

        # Start speech thread
        speech_thread = threading.Thread(target=speak_in_background, daemon=True)
        speech_thread.start()

        # Wait for speech to finish before starting music
        def start_music_after_speech():
            speech_thread.join()  # Ensures speech finishes before starting music
            self.play_theme()  # Replace with your music-playing function

            reveal_label = tk.Label(self.root, text="Press 'Enter' to reveal the Answer", font=FONTS["medium_bold"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"])
            reveal_label.pack(pady=80)
            
            def on_enter(event):
                pygame.mixer.music.stop()
                self.show_answer(current_question, self.questions[self.question_index]["answer"], self.show_question)

            self.root.bind("<Return>", on_enter)
            self.root.bind("<Key>", lambda event: self.handle_key(event, self.show_question))

        # Start music thread after speech
        music_thread = threading.Thread(target=start_music_after_speech, daemon=True)
        music_thread.start()

    def show_answer(self, question, answer, next_action):
        """Display the answer and handle user input for correctness."""
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
            self.speak_text(answer) # Speak the answer after it's displayed
        # Start speech thread

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

            # Clear the current key binding to prevent multiple triggers
            self.unbind_key("<Key>")

            # Move to the next turn or final question round
            self.next_turn(next_action)

        self.root.bind("<Key>", handle_answer)

    def next_turn(self, next_action):
        """Move to the next team or round."""
        self.current_team = (self.current_team + 1) % self.num_teams
        if self.current_team == 0:
            self.current_round += 1
        self.question_index += 1
        if self.current_round > self.num_rounds:
            if not self.collecting_wagers:  # Ensure we're not already collecting wagers
                self.wagers = {}  # Reset wagers for the final round
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
        """Handle the final question round, including wagers."""
        if self.collecting_wagers:
            
            return
        self.clear_screen()
        
        # Display title and scoreboard
        self.display_title_and_scoreboard()

        # Step 1: Wager Collection
        self.collect_wagers(team_index=0)

    def display_title_and_scoreboard(self):
        """Display game title and current scoreboard."""
        tk.Label(self.root, text="Trivia Royale", font=FONTS["big"], fg=COLORS["soft_yellow"], bg=COLORS["light_blue"]).pack(pady=20)
        score_frame = tk.Frame(self.root, bg=COLORS["light_blue"], relief=tk.RIDGE, bd=2)
        score_frame.pack(pady=10, padx=20, fill=tk.X)
        for name, score in zip(self.team_names, self.scores):
            tk.Label(score_frame, text=f"{name}: {score}", font=FONTS["medium_bold"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"]).pack(side=tk.LEFT, expand=True)

    def collect_wagers(self, team_index):
        """Collect wagers from each team."""
        import traceback
        if self.collecting_wagers:  
            return
        self.collecting_wagers = True
        self.unbind_key("<Return>")  # Clear previous bindings at the start

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
                    
                    self.collecting_wagers = False  # Reset flag before moving to next team
                    self.unbind_key("<Return>")  # Clear binding
                    self.collect_wagers(team_index + 1)  # Move to next team or final question
            except ValueError:
                error_label.config(text="Invalid input! Please enter a number.")
                self.collecting_wagers = False  # Reset flag even on error

        # Delay binding to ensure setup is complete
        self.root.after(100, lambda: self.bind_key("<Return>", submit_wager))

    def display_final_question(self):
        """Display the final question and manage its presentation."""
        self.clear_screen()
        self.display_title_and_scoreboard()

        current_question = self.questions[self.question_index]["question"]
        question_label = tk.Label(self.root, text=f"Final Question:\n\n\n{current_question}", font=FONTS["medium"], bg=COLORS["light_blue"], fg=COLORS["soft_yellow"], wraplength=500)
        question_label.pack(pady=20)
 
        # Speak the question
        def speak_in_background():
            self.speak_text(current_question)

        # Start speech thread
        speech_thread = threading.Thread(target=speak_in_background, daemon=True)
        speech_thread.start()

        # Wait for speech to finish before starting music
        def start_music_after_speech():
            speech_thread.join()  # Ensures speech finishes before starting music
            self.play_theme()  # Replace with your music-playing function

            reveal_label = tk.Label(self.root, text="Press 'Enter' to reveal the Answer", font=FONTS["medium_bold"], fg=COLORS["soft_coral"], bg=COLORS["light_blue"])
            reveal_label.pack(pady=80)
            
            def on_enter(event):
                pygame.mixer.music.stop()
                self.show_final_answer(current_question, self.questions[self.question_index]["answer"])

            self.root.bind("<Return>", on_enter)
            self.root.bind("<Key>", lambda event: self.handle_key(event, self.display_final_question))

        # Start music thread after speech
        music_thread = threading.Thread(target=start_music_after_speech, daemon=True)
        music_thread.start()

    def show_final_answer(self, question, answer):
        self.clear_screen()
        self.display_title_and_scoreboard()

        answer_label = tk.Label(self.root, text=f"Answer:\n\n\n{answer}", font=FONTS["medium"], bg=COLORS["light_blue"], fg=COLORS["soft_yellow"], wraplength=500)
        answer_label.pack(pady=20)

        # Speak the answer
        speech_thread = threading.Thread(target=lambda: self.speak_text(answer), daemon=True)
        speech_thread.start()

        # Prompt for correctness check
        self.prompt_correctness(question, team_index=0)

    def prompt_correctness(self, question, team_index):
        """Prompt each team to check if their answer was correct for the final question."""
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
        """Display the winner of the game."""
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
        """Handle the end of the game."""
        self.clear_screen()
        winner = max(zip(self.team_names, self.scores), key=lambda x: x[1])
        tk.Label(self.root, text=f"The winner is {winner[0]} with {winner[1]} points!", font=FONTS["big_italic"], bg=COLORS["light_blue"], fg=COLORS["soft_coral"]).pack(pady=100)
        self.play_winner_music()
        self.root.bind("<Escape>", lambda e: self.root.destroy())

# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    game = TriviaGame(root)
    root.mainloop()