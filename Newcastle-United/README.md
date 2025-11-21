# Newcastle United Explorer

A lightweight Streamlit web app dedicated to Newcastle United FC with squad search, season statistics, and club history.

## Features

✨ **Interactive Navigation**
- Home: Club overview with key metrics
- Squad: Searchable & filterable player roster
- Season Stats: Historical performance charts and analytics
- History & Trophies: Club honours and notable eras
- About / Run: Setup and deployment instructions

🔍 **Squad Management**
- Search players by name
- Filter by position and nationality
- Sort by number, age, or name
- View detailed player information

📊 **Analytics**
- Interactive charts for league position trends
- Points, goals scored, and goals conceded analysis
- Season-by-season performance comparison
- Key performance indicators (KPIs)

## Installation

### 1. Clone or download the project
```bash
cd Newcastle-United
```

### 2. Create a virtual environment (optional but recommended)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Requirements

- Python 3.7 or higher
- streamlit
- pandas
- plotly

See `requirements.txt` for full dependency list.

## Project Structure

```
Newcastle-United/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Data

The app currently uses **sample data**. To make it production-ready:

1. **CSV file**: Load player/stats data from a CSV
2. **API**: Connect to a football data API (e.g., football-data.org)
3. **Database**: Store data in a database and query it

Example (CSV):
```python
df_squad = pd.read_csv("squad.csv")
```

## Deployment

### Streamlit Community Cloud (free)
1. Push your code to GitHub
2. Visit [streamlit.io](https://streamlit.io)
3. Deploy directly from your repo

### Other Hosting
- Heroku
- PythonAnywhere
- AWS / Azure / GCP
- Docker container

## Notes

- Data is sample only for demonstration
- Easily extensible for real-time data updates
- Responsive design works on desktop and mobile
- Black & white (Magpie) themed styling

## License

Feel free to use and modify as needed.

---

**Howay the Lads!** ⚫⚪
