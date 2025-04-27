import streamlit as st
import random
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
import requests

# Load environment variables (as fallback)
load_dotenv()

# Function to handle API keys
def get_api_keys():
    # Check if API keys are already in session state
    if 'GEMINI_API_KEY' not in st.session_state or 'MISTRAL_API_KEY' not in st.session_state:
        st.title("🔑 API Key Setup")
        
        # Create two columns for the API key sections
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Google Gemini API Key")
            st.markdown("[Get Gemini API Key](https://makersuite.google.com/app/apikey)")
            gemini_key = st.text_input(
                "Enter Gemini API Key",
                type="password",
                key="gemini_input"
            )
        
        with col2:
            st.subheader("Mistral API Key")
            st.markdown("[Get Mistral API Key](https://console.mistral.ai/api-keys/)")
            mistral_key = st.text_input(
                "Enter Mistral API Key",
                type="password",
                key="mistral_input"
            )

        # Info message
        st.info("You need at least one API key to generate custom questions. Without keys, the game will use default questions.")
        
        if st.button("Save API Keys"):
            if gemini_key or mistral_key:
                st.session_state.GEMINI_API_KEY = gemini_key
                st.session_state.MISTRAL_API_KEY = mistral_key
                st.success("API Keys saved successfully!")
                st.experimental_rerun()
            else:
                st.warning("Please enter at least one API key or close this dialog to use default questions.")
        
        # Add a skip button
        if st.button("Skip (Use Default Questions)"):
            st.session_state.GEMINI_API_KEY = None
            st.session_state.MISTRAL_API_KEY = None
            st.experimental_rerun()
            
        # Stop further execution until keys are provided or skipped
        st.stop()
    
    return st.session_state.GEMINI_API_KEY, st.session_state.MISTRAL_API_KEY

# Get API keys before proceeding
GEMINI_API_KEY, MISTRAL_API_KEY = get_api_keys()

# Initialize Gemini if key is available
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Session state initialization
if 'game_state' not in st.session_state:
    st.session_state.game_state = 'title'
if 'scores' not in st.session_state:
    st.session_state.scores = []
if 'team_names' not in st.session_state:
    st.session_state.team_names = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_team' not in st.session_state:
    st.session_state.current_team = 0
if 'current_round' not in st.session_state:
    st.session_state.current_round = 1
if 'wagers' not in st.session_state:
    st.session_state.wagers = {}

def generate_trivia_questions_gemini(prompt):
    if not GEMINI_API_KEY:
        return None
        
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(
            f"""Generate 5 trivia questions with answers in this exact JSON format:
            [{{"question": "Q1", "answer": "A1"}}, {{"question": "Q2", "answer": "A2"}}]
            Make them {prompt} difficulty."""
        )
        return response.text
    except Exception as e:
        st.error(f"Error generating questions: {e}")
        return None

# Update get_trivia_questions to handle missing API keys
def get_trivia_questions(prompt):
    if not GEMINI_API_KEY and not MISTRAL_API_KEY:
        st.warning("Using default questions (no API keys provided)")
        return load_default_questions()
        
    questions = generate_trivia_questions_gemini(prompt)
    if questions:
        try:
            cleaned_questions = questions.strip().replace('```json', '').replace('```', '')
            return json.loads(cleaned_questions)
        except json.JSONDecodeError as e:
            st.error(f"Error parsing questions: {e}")
    return load_default_questions()

def load_default_questions():
    # Add your default questions here
    return [
        {"question": "What is the capital of France?", "answer": "Paris"},
        {"question": "Who painted the Mona Lisa?", "answer": "Leonardo da Vinci"},
        {"question": "What is the largest planet in our solar system?", "answer": "Jupiter"},
        {"question": "What is the chemical symbol for gold?", "answer": "Au"},
        {"question": "Who wrote 'Romeo and Juliet'?", "answer": "William Shakespeare"}
    ]

def title_screen():
    st.title("🎮 Trivia Royale")
    st.markdown("### Welcome to the Ultimate Trivia Experience!")
    
    if st.button("Start Game"):
        st.session_state.game_state = 'setup_teams'
        st.experimental_rerun()

def setup_teams():
    st.title("Team Setup")
    
    num_teams = st.number_input("Number of Teams", min_value=1, max_value=6, value=2)
    num_rounds = st.number_input("Number of Rounds", min_value=1, max_value=10, value=5)
    
    team_names = []
    for i in range(num_teams):
        team_name = st.text_input(f"Team {i+1} Name", value=f"Team {i+1}")
        team_names.append(team_name)
    
    if st.button("Start Game"):
        st.session_state.team_names = team_names
        st.session_state.scores = [0] * num_teams
        st.session_state.num_rounds = num_rounds
        
        # Generate questions
        questions = get_trivia_questions("medium")
        if questions:
            st.session_state.questions = questions
            st.session_state.game_state = 'game_play'
            st.experimental_rerun()
        else:
            st.error("Failed to generate questions. Please try again.")

def show_scoreboard():
    st.sidebar.title("Scoreboard")
    for name, score in zip(st.session_state.team_names, st.session_state.scores):
        st.sidebar.markdown(f"**{name}**: {score}")

def game_play():
    show_scoreboard()
    
    if st.session_state.current_question >= len(st.session_state.questions):
        st.session_state.game_state = 'game_over'
        st.experimental_rerun()
        return

    st.title(f"Round {st.session_state.current_round}")
    st.subheader(f"{st.session_state.team_names[st.session_state.current_team]}'s Turn")
    
    current_q = st.session_state.questions[st.session_state.current_question]
    st.markdown(f"### Question:\n{current_q['question']}")
    
    if st.button("Show Answer"):
        st.markdown(f"### Answer:\n{current_q['answer']}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Correct ✅"):
                st.session_state.scores[st.session_state.current_team] += 10
                next_turn()
                st.experimental_rerun()
        with col2:
            if st.button("Incorrect ❌"):
                next_turn()
                st.experimental_rerun()
        with col3:
            if st.button("Google It 🔍"):
                st.markdown(f"[Search on Google](https://www.google.com/search?q={current_q['question']})")

def next_turn():
    st.session_state.current_team = (st.session_state.current_team + 1) % len(st.session_state.team_names)
    if st.session_state.current_team == 0:
        st.session_state.current_round += 1
    st.session_state.current_question += 1

def game_over():
    st.title("🎉 Game Over!")
    
    winner_idx = st.session_state.scores.index(max(st.session_state.scores))
    winner_name = st.session_state.team_names[winner_idx]
    winner_score = st.session_state.scores[winner_idx]
    
    st.markdown(f"## 🏆 The winner is {winner_name} with {winner_score} points!")
    
    show_scoreboard()
    
    if st.button("Play Again"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.experimental_rerun()

# Main game flow
def main():
    if st.session_state.game_state == 'title':
        title_screen()
    elif st.session_state.game_state == 'setup_teams':
        setup_teams()
    elif st.session_state.game_state == 'game_play':
        game_play()
    elif st.session_state.game_state == 'game_over':
        game_over()

if __name__ == "__main__":
    st.set_page_config(
        page_title="Trivia Royale",
        page_icon="🎮",
        layout="wide"
    )
    main()
