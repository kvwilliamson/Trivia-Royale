# Trivia Royale

A feature-rich trivia game built with Python and Tkinter that uses AI to generate questions and supports text-to-speech.

## Features

- **AI-Powered Questions**: Generates unique trivia questions using Gemini and Mistral AI models
- **Text-to-Speech**: Built-in voice narration for questions and answers
- **Multi-Team Support**: Play with multiple teams in tournament style
- **Final Round**: Special final round with wagering system
- **Fact Checking**: Quick Google search integration for verifying answers
- **Difficulty Levels**: Customizable question difficulty
- **Category Selection**: Choose from various trivia categories
- **Score Tracking**: Automatic score management for all teams

## Requirements

- Python 3.11+
- Required Python packages:
  - tkinter
  - pyttsx3
  - pygame
  - PIL (Pillow)
  - google.generativeai
  - python-dotenv
  - requests
  - pyperclip

## Setup

1. Clone the repository
2. Install required packages:
```bash
pip install -r requirements.txt
```
3. Create a `.env` file in the project root with your API keys:
```
GEMINI_API_KEY=your_gemini_api_key
MISTRAL_API_KEY=your_mistral_api_key
```

## Usage

1. Run the game:
```bash
python TriviaRoyale.py
```

2. Game Controls:
- `Y`: Mark answer as correct (+10 points)
- `N`: Mark answer as incorrect (no points)
- `G`: Google the current question for fact-checking
- `Space`: Reveal answer
- `ESC`: Exit game

## Features in Detail

### Question Generation
- Uses both Gemini and Mistral AI models with automatic fallback
- Customizable categories and difficulty levels
- JSON-formatted question structure for consistency

### Text-to-Speech
- Synchronized voice narration
- Compatible with system voices
- Adjustable speech settings

### Final Round
- Special wagering system
- Teams can bet their points
- High-stakes final question

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

[Your chosen license]

## Credits

Created by [Your Name]