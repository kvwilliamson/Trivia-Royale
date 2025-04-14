# Trivia Royale 🎮

A feature-rich trivia game built with Python and Tkinter that uses AI to generate questions and supports text-to-speech.

## ✨ Features

- **AI-Powered Questions**: Generates unique trivia questions using Gemini and Mistral AI models
- **Text-to-Speech**: Built-in voice narration for questions and answers
- **Multi-Team Support**: Play with multiple teams in tournament style
- **Final Round**: Special final round with wagering system
- **Fact Checking**: Quick Google search integration for verifying answers
- **Difficulty Levels**: Customizable question difficulty
- **Category Selection**: Choose from various trivia categories
- **Score Tracking**: Automatic score management for all teams

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- API Keys:
  - Gemini API key from Google AI Studio
  - Mistral API key from Mistral AI

### Installation

1. Clone the repository:
```bash
git clone https://github.com/kvwilliamson/trivia-royale.git
cd trivia-royale
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key
MISTRAL_API_KEY=your_mistral_api_key
```

### Running the Game

```bash
python TriviaRoyale.py
```

## 🎮 Game Controls

- `Space`: Reveal answer
- `Y`: Mark answer as correct (+10 points)
- `N`: Mark answer as incorrect (no points)
- `G`: Google the current question for fact-checking
- `ESC`: Exit game

## 🏗️ Project Structure

```
TriviaRoyale/
├── assets/               # Game assets (images, sounds)
├── src/                 # Source code
│   ├── __init__.py
│   ├── ui/             # UI-related code
│   ├── ai/             # AI integration code
│   └── utils/          # Utility functions
├── tests/              # Test files
├── requirements.txt    # Project dependencies
├── TriviaRoyale.py    # Main game file
└── README.md          # This file
```

## 🧪 Running Tests

```bash
pytest tests/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Kelly Williamson ([@kvwilliamson](https://github.com/kvwilliamson))

## 🙏 Acknowledgments

- Google AI for Gemini API
- Mistral AI for their language model
- All contributors and testers
