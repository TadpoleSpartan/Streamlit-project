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

## More about Newcastle United

Newcastle United Football Club, founded in 1892, has a long and storied history in English football. Known as "The Magpies" because of their black-and-white striped shirts, the club plays at St. James' Park and boasts one of the most passionate fanbases in the country.

Key facts:
- Founded: 1892
- Stadium: St. James' Park — capacity ~52,000
- Nickname: The Magpies

Recent highlights (sample):
- 2022–2025: Club resurgence after investment; higher league finishes and European qualification

Manager & style:
- Manager (example in app): Eddie Howe — pragmatic, possession-based, strong focus on defensive organization and transitions (note: sample info in the app)

Notable current players (sample): Alexander Isak, Bruno Guimarães, Kieran Trippier, Miguel Almirón

Culture & matchday:
- Matchdays at St. James' Park are renowned for atmosphere and vocal local support. The city of Newcastle has deep ties with the club, and local rivalries (notably the Tyne–Wear derby vs Sunderland) are historic and intense.

Data & Sources
- The content in this app is sample-only. To extend to real data, consider using APIs such as `football-data.org`, `api-football.com`, or scraping reliable sources with respect to their terms of service.
- When adding real data, include a `data/` folder with CSV exports or integrate secure API keys using Streamlit secrets (`st.secrets`).

Want more?
- I can add a `data/` import flow, live API integration, or a players detail page with images and advanced stats. Tell me which you'd like next.

## Club Encyclopedia (extended)

Below is an expanded reference you can copy into the app or use as content for the `Encyclopedia` page.

Club Overview
- Full name: Newcastle United Football Club
- Founded: 1892 (merger of Newcastle East End & West End)
- Nickname: The Magpies
- Stadium: St. James' Park — capacity ~52,000
- Motto: "Nil Satis Nisi Optimum"

Honours & Achievements
- English League Titles: 4 (early 1900s)
- FA Cups: 6
- European appearances: UEFA Cup/Europa League entries and historic continental matches

Notable managers (selected)
- Sir Bobby Robson — legendary manager with European success and player development
- Kevin Keegan — defined the 1990s era and high-scoring teams
- Rafa Benítez — led European cup campaigns and tactical structures
- Eddie Howe — modern manager credited with tactical stability and improved league finishes (appointed 2021)

Club records & notable players (summary)
- Record goalscorer and appearance leaders: keep verified sources (club archives / reliable stats websites) to populate exact figures
- Notable present-day players (sample): Alexander Isak, Bruno Guimarães, Kieran Trippier, Miguel Almirón
- Club legends across history: several early- and mid-20th-century stars and modern-era icons

Stadium — St. James' Park
- Key facts: located in Newcastle city centre, home since 1892, capacity ~52,000
- Famous stands and features: Gallowgate End, Leazes End, Milburn Stand (historic names and significance)

Rivalries & culture
- Tyne–Wear derby vs Sunderland — a historic and intense local rivalry
- Supporters: strong local identity, known for passionate matchday atmosphere, chants and tifos

Youth Academy & development
- The academy is a focus for long-term development — add academy graduates and timelines to a `data/` CSV for tracking

Transfers & business
- Transfer strategy blends marquee signings with recruitment from global scouting networks. Use a CSV to track transfer fees and dates.

European & Cup History
- Historic European campaigns and cup runs are best represented season-by-season; consider adding a `seasons.csv` file and an interactive timeline in the app.

Community & Foundation work
- The club engages in community outreach, charity, and youth development programs — include foundation links and local projects when publishing content.

How to enrich this project
- Add `data/players.csv`, `data/seasons.csv`, `data/transfers.csv` and update the app to load these files.  
- Add `images/players/` and show player photos in the squad page.  
- Integrate a football API for live fixtures and up-to-date stats (requires API key and respecting API terms).

If you want, I can now:
- generate sample CSV files and wire an upload flow into the app, or
- add player image placeholders and show richer player cards, or
- scaffold an integration with a free API (you'll provide the key).

## License

Feel free to use and modify as needed.

---

**Howay the Lads!** ⚫⚪
