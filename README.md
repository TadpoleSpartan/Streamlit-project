# 🎯 Netherlands QuizMaster - Interactive Quiz Application

A complete Streamlit-based quiz application all about the Netherlands! This interactive quiz covers Dutch geography, culture, history, and famous Dutch people. Built for S6 Informatics students to demonstrate modern web development concepts including session state management, data persistence, and interactive UI design.

## Features

- 🏠 **Home Page**: Player registration and category selection
- 🎮 **Quiz Engine**: Randomized questions with immediate feedback about the Netherlands
- 🏆 **Leaderboard**: Top 10 highest scores with statistics
- 📚 **Categories**: 
  - Netherlands Geography (capital, borders, geography facts)
  - Dutch Culture & History (traditions, famous foods, historical events)
  - Famous Dutch People (artists, philosophers, explorers, athletes)
- 💾 **Data Persistence**: JSON-based storage (Phase 1) and SQLite database (Phase 2)
- 🎨 **Beautiful UI**: Custom Streamlit theming with emojis and responsive layout
- 🇳🇱 **Netherlands Focus**: Learn fascinating facts about the Dutch culture and history

## Project Structure

```
s6-quizmaster-yourname/
├── .streamlit/
│   └── config.toml              # Streamlit configuration
├── data/
│   ├── questions.json           # Quiz questions database
│   ├── highscores.json          # Player scores
│   └── quizmaster.db            # SQLite database (Phase 2)
├── pages/
│   ├── 1_🎮_Quiz.py             # Main quiz game
│   ├── 2_🏆_Highscores.py       # Leaderboard
│   └── 3_📚_Categories.py       # Category overview
├── Home.py                       # Entry point
├── database.py                   # Database operations (Phase 2)
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── .gitignore                    # Git ignore rules
```

## Installation

### Prerequisites
- Python 3.10+
- Git
- VS Code (recommended)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/s6-quizmaster-yourname.git
   cd s6-quizmaster-yourname
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Activate (Windows):
   venv\Scripts\activate
   
   # Activate (Mac/Linux):
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run Home.py
   ```

The app will open in your browser at `http://localhost:8501`

## How to Use

### Playing a Quiz

1. **Home Page**: Enter your name and select a quiz category
2. **Quiz Page**: Answer questions and see immediate feedback
3. **Results**: View your score and accuracy percentage
4. **Leaderboard**: Check your position on the Hall of Fame

### Quiz Features

- **Questions**: Multiple choice questions with 4 options
- **Difficulty Levels**: Easy (🟢), Medium (🟡), Hard (🔴)
- **Points System**: Earn points based on difficulty and correctness
- **Feedback**: Instant visual feedback with balloons on correct answers
- **Progress Tracking**: See current question number and score in real-time

## Key Concepts Explained

### Streamlit Execution Model
Streamlit re-runs your entire script from top to bottom on every user interaction. This is why we use session state to persist data across reruns.

### Session State
Session state variables persist across script reruns, allowing us to maintain game state, player information, and progress.

```python
if "player_name" not in st.session_state:
    st.session_state.player_name = ""
```

### JSON Structure
Questions are stored in a hierarchical JSON structure:

```json
{
    "categories": {
        "Category Name": [
            {
                "question": "...",
                "options": [...],
                "correct": 1,
                "difficulty": "easy",
                "points": 10
            }
        ]
    }
}
```

### Data Persistence
- **Phase 1**: JSON files (questions.json, highscores.json)
- **Phase 2**: SQLite database with user authentication

## Development Notes

### Adding New Questions

Edit `data/questions.json` and add questions in this format:

```json
{
    "id": 6,
    "question": "Name a famous Dutch city?",
    "options": ["Amsterdam", "Option 2", "Option 3", "Option 4"],
    "correct": 0,
    "difficulty": "easy",
    "points": 10
}
```

Available categories:
- **Netherlands Geography** - Questions about Dutch cities, borders, and geography
- **Dutch Culture & History** - Questions about Dutch traditions, food, and historical events
- **Famous Dutch People** - Questions about renowned Dutch artists, philosophers, athletes, and explorers

### Customizing Appearance

Edit `.streamlit/config.toml` to change:
- Primary color
- Background color
- Font
- Layout type

### Git Workflow

```bash
# Check status
git status

# Stage changes
git add .

# Commit
git commit -m "Descriptive message about changes"

# Push to GitHub
git push origin main
```

## Troubleshooting

### Port Already in Use
```bash
streamlit run Home.py --server.port 8502
```

### Virtual Environment Issues
```bash
# On Windows:
python -m venv venv
venv\Scripts\activate

# On Mac/Linux:
python3 -m venv venv
source venv/bin/activate
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

## Learning Outcomes

Through this project, you'll learn:

- ✅ How web applications work (client-server model)
- ✅ Python web development with Streamlit
- ✅ Session state management for interactive apps
- ✅ JSON data format and manipulation
- ✅ SQLite database basics
- ✅ Git version control workflows
- ✅ Python best practices (functions, error handling, documentation)
- ✅ UI/UX design principles

## Phase 2: Database Integration

The `database.py` module provides SQLite integration with features like:

- User authentication with password hashing
- Database initialization with schema creation
- CRUD operations for questions and scores
- Query functions for retrieving data efficiently

To use Phase 2:

```python
from database import create_user, verify_user, save_score

# Create a user
create_user("alice", "password123")

# Verify credentials
user = verify_user("alice", "password123")

# Save a score
save_score(user_id=1, category="Math", score=85, correct=4, total=5)
```

## Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Python Documentation](https://docs.python.org/3/)
- [Git Documentation](https://git-scm.com/doc)
- [JSON Format](https://www.json.org/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

## Author

Created for S6 Informatics students at European School Karlsruhe

## License

This project is open source and available for educational purposes.

---

**Happy coding!** 🚀

Remember: Start small, test frequently, commit regularly!
