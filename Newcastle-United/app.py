import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Newcastle United Explorer", layout="wide")

# ------------------
# Data (sample)
# ------------------
SQUAD = [
    {"name": "Martin Dúbravka", "position": "Goalkeeper", "number": 1, "age": 34, "nationality": "Slovakia"},
    {"name": "Kieran Trippier", "position": "Defender", "number": 2, "age": 33, "nationality": "England"},
    {"name": "Sven Botman", "position": "Defender", "number": 4, "age": 24, "nationality": "Netherlands"},
    {"name": "Kieran Clarke", "position": "Midfielder", "number": 8, "age": 27, "nationality": "England"},
    {"name": "Bruno Guimarães", "position": "Midfielder", "number": 39, "age": 26, "nationality": "Brazil"},
    {"name": "Callum Wilson", "position": "Forward", "number": 9, "age": 31, "nationality": "England"},
    {"name": "Alexander Isak", "position": "Forward", "number": 14, "age": 25, "nationality": "Sweden"},
    {"name": "Miguel Almirón", "position": "Midfielder", "number": 24, "age": 29, "nationality": "Paraguay"},
    {"name": "Elliot Anderson", "position": "Midfielder", "number": 26, "age": 21, "nationality": "Scotland"},
    {"name": "Nick Pope", "position": "Goalkeeper", "number": 22, "age": 31, "nationality": "England"},
]

SEASON_STATS = {
    "season": ["2021/22", "2022/23", "2023/24", "2024/25"],
    "position": [11, 4, 5, 6],
    "points": [50, 71, 68, 63],
    "goals_scored": [46, 68, 62, 59],
    "goals_conceded": [51, 33, 36, 40],
}

df_squad = pd.DataFrame(SQUAD)
df_stats = pd.DataFrame(SEASON_STATS)

# ------------------
# Styling (CSS)
# ------------------
st.markdown(
    """
    <style>
    /* Page background */
    .stApp {
        background: linear-gradient(180deg, #ffffff 0%, #f6f6f6 100%);
    }

    /* Top banner with subtle magpie stripes */
    .banner {
        background: repeating-linear-gradient(90deg, #000000 0px, #000000 6px, #ffffff 6px, #ffffff 12px);
        padding: 18px 24px;
        border-radius: 8px;
        color: #ffffff;
        margin-bottom: 18px;
    }

    .title-large {
        font-size: 30px;
        font-weight: 700;
        color: #ffffff;
        text-shadow: 1px 1px 0 rgba(0,0,0,0.4);
    }

    .subtitle {
        font-size: 14px;
        color: #ffffff;
        opacity: 0.9;
    }

    /* Card style */
    .card {
        background: #ffffff;
        padding: 14px;
        border-radius: 10px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.06);
        margin-bottom: 12px;
    }

    /* Tighter table */
    .stDataFrame table {
        border-collapse: collapse;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------
# Sidebar
# ------------------
st.sidebar.markdown("# ⚫⚪ Newcastle Explorer")
st.sidebar.write("A small demo app — replace sample data with your CSV/API")
page = st.sidebar.radio("Navigate", ["Home", "Squad", "Season Stats", "History & Trophies", "Encyclopedia", "About / Run"])
st.sidebar.markdown("---")

# Club info helper
club_info = {
    "name": "Newcastle United",
    "founded": 1892,
    "nickname": "The Magpies",
    "stadium": "St James' Park",
    "capacity": "≈ 52,000",
    "colors": "Black & White",
}

# ------------------
# Pages
# ------------------
if page == "Home":
    st.markdown('<div class="banner"><div class="title-large">Newcastle United Explorer</div><div class="subtitle">Club overview, squad browser and season analytics</div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(f"{club_info['name']} — {club_info['nickname']}")
        st.markdown(
            f"**Founded:** {club_info['founded']}  \n**Stadium:** {club_info['stadium']} ({club_info['capacity']})  ")
        st.write("This demo uses sample data. Connect an API or CSV to power the app with real data.")
        st.markdown("**Manager:** Eddie Howe — Appointed in 2021, led the club through tactical stability and European qualification in recent seasons.")
        st.markdown("**Club Vision:** Focus on sustainable growth, academy development and competing at the top of the Premier League.")
        st.markdown("**Notable Players (sample):** Alexander Isak, Bruno Guimarães, Kieran Trippier, Miguel Almirón")
        st.markdown("\n**Stadium Facts:** St. James' Park is one of the oldest professional football grounds, centrally located in Newcastle; matchday atmosphere is famed for its vocal support.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("Last season position", df_stats.loc[len(df_stats)-1, "position"])
        st.metric("Last season points", df_stats.loc[len(df_stats)-1, "points"])
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "Squad":
    st.markdown('<div class="banner"><div class="title-large">Squad — Search & Filter</div></div>', unsafe_allow_html=True)
    st.write('Search players, filter by position and nationality, or sort the roster.')

    pos_options = ["All"] + sorted(df_squad["position"].unique().tolist())
    nat_options = ["All"] + sorted(df_squad["nationality"].unique().tolist())

    cols = st.columns(3)
    with cols[0]:
        name_search = st.text_input("Search name (contains)")
    with cols[1]:
        pos_filter = st.selectbox("Position", pos_options)
    with cols[2]:
        nat_filter = st.selectbox("Nationality", nat_options)

    df_filtered = df_squad.copy()
    if name_search:
        df_filtered = df_filtered[df_filtered["name"].str.contains(name_search, case=False, na=False)]
    if pos_filter != "All":
        df_filtered = df_filtered[df_filtered["position"] == pos_filter]
    if nat_filter != "All":
        df_filtered = df_filtered[df_filtered["nationality"] == nat_filter]

    sort_by = st.radio("Sort by", ["number", "age", "name"])
    df_filtered = df_filtered.sort_values(by=sort_by)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.dataframe(df_filtered.reset_index(drop=True), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    player = st.selectbox("Show details for", [""] + df_squad["name"].tolist())
    if player:
        p = df_squad[df_squad["name"] == player].iloc[0]
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(p["name"])
        st.markdown(f"**Position:** {p['position']}  \n**Number:** {p['number']}  \n**Age:** {p['age']}  \n**Nationality:** {p['nationality']}")
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "Season Stats":
    st.markdown('<div class="banner"><div class="title-large">Season Statistics</div></div>', unsafe_allow_html=True)
    st.write('Interactive charts for recent seasons (sample data).')

    # nicer palette: black + grays
    palette = ['#000000', '#555555', '#bdbdbd']

    fig_pos = px.line(df_stats, x="season", y="position", markers=True, title="League position by season")
    fig_pos.update_traces(line=dict(color=palette[0], width=3), marker=dict(color=palette[1]))
    fig_pos.update_yaxes(autorange="reversed", title="Position (lower is better)")
    st.plotly_chart(fig_pos, use_container_width=True)

    df_melt = df_stats.melt(id_vars="season", value_vars=["points", "goals_scored", "goals_conceded"], var_name="metric", value_name="value")
    fig_bar = px.bar(df_melt, x="season", y="value", color="metric", barmode="group", title="Points / Goals by season",
                     color_discrete_sequence=palette)
    st.plotly_chart(fig_bar, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Best finish (sample)", int(df_stats["position"].min()))
    c2.metric("Best points (sample)", int(df_stats["points"].max()))
    c3.metric("Most goals (sample)", int(df_stats["goals_scored"].max()))

elif page == "History & Trophies":
    st.markdown('<div class="banner"><div class="title-large">History & Major Honours</div></div>', unsafe_allow_html=True)
    st.write('A short summary of the club history and honours (example).')
    st.markdown('''
    Newcastle United were formed in 1892 following the merger of Newcastle East End and Newcastle West End. The club quickly established itself in English football, winning multiple league titles in the early 20th century. After periods of ups and downs, including relegations and promotions, the club re-emerged as a stable top-flight team in the 1990s and enjoyed renewed success in the 2020s following new investment.

    **Major honours:**
    - **English League Titles:** 4  
    - **FA Cups:** 6  
    - **Community/League Cups & other honours:** several regional and lower-division trophies

    **Recent era (2020s):** Investment in the mid-2020s helped the club rebuild the squad, finish high in the league standings and qualify for European competitions. The club has placed emphasis on modern scouting and youth development.
    ''')

    st.subheader('Timeline — Selected highlights')
    st.markdown('''
    - 1892: Club founded (merger)
    - 1905, 1907, 1909: Early top-flight success
    - 1950s–1990s: Mixed results and cup runs
    - 1993–1996: Promotion to Premier League and consolidation
    - 2020s: New ownership and resurgence, stronger league finishes
    ''')

    st.subheader('Club culture & fanbase')
    st.write('Newcastle supporters are known for their loyalty and matchday atmosphere. The city has strong community ties to the club and a proud local identity.')

elif page == "Encyclopedia":
    st.markdown('<div class="banner"><div class="title-large">Club Encyclopedia</div></div>', unsafe_allow_html=True)
    st.write('A deep-dive reference about Newcastle United — history, records, stadium, managers, academy and culture.')

    with st.expander('Club Overview (quick facts)', expanded=True):
        st.markdown(
            '''
            - Full name: Newcastle United Football Club
            - Founded: 1892 (merger of Newcastle East End & West End)
            - Nickname: The Magpies
            - Stadium: St. James' Park (capacity ≈ 52,000)
            - Club motto: "Nil Satis Nisi Optimum" (Nothing but the best is good enough)
            - Colours: Black & White striped shirts
            - Owner (example in app): Public Investment Fund (PIF) consortium
            ''')

    with st.expander('Honours & Achievements'):
        st.markdown(
            '''
            - English League Titles: 4 (early 1900s)
            - FA Cups: 6
            - European appearances: multiple UEFA Cup/Europa League entries
            - Numerous regional and lower-division trophies across the club's history
            ''')

    with st.expander('Managers (selected notable)', expanded=False):
        st.markdown(
            '''
            - Sir Bobby Robson — led the club in multiple successful periods and European competition
            - Kevin Keegan — influential in 1990s era and promotion seasons
            - Rafa Benítez — notable European and cup campaigns
            - Eddie Howe — modern-era manager (appointed 2021), led tactical improvements and strong league finishes
            ''')

    with st.expander('Club Records & Statistics'):
        st.markdown(
            '''
            - Most appearances (club legend): (varies historically) — consider adding exact numbers from reliable sources
            - Record goalscorer: (historical record holders exist; add verified figures when integrating data)
            - Biggest win / heaviest defeat: historic match results are part of the club archives
            ''')

    with st.expander('Stadium — St. James\' Park', expanded=False):
        st.write('St. James\' Park is the club\'s home since 1892. Located in Newcastle city centre, it combines historic features with modern hospitality suites and fan zones. The stadium hosts club matches, events and has been upgraded across multiple eras.')
        st.markdown('- Capacity: ~52,000  \n- Notable features: Gallowgate End, Leazes End, Milburn Stand (site names and history)')

    with st.expander('Rivalries & Derbies'):
        st.markdown(
            '''
            - Tyne–Wear derby: fierce local rivalry with Sunderland (historic and culturally significant)
            - Regional rivalries: matches with nearby or historically significant clubs evoke strong local interest
            ''')

    with st.expander('Supporters, Culture & Chants'):
        st.write('Newcastle fans are widely known for their passion. Common features include matchday chants, tifos, and strong community identity. Songs and chants are an important part of the matchday experience.')

    with st.expander('Crest, Kits and Colours'):
        st.markdown('The black-and-white stripes are traditional. The club crest has evolved; modern variations retain magpie imagery, castle elements and symbolic references to the city.')

    with st.expander('Youth Academy & Development'):
        st.write('Newcastle\'s academy has produced notable graduates and remains a focus for long-term club sustainability. Investing in young talent is a club priority in scouting and development.')

    with st.expander('Transfer Records & Business'):
        st.markdown('''
        - Transfer strategy: the club has combined marquee signings with strategic scouting in recent seasons.
        - Transfer fees and records change over time; keep a `data/` CSV to track transfers and fees.
        ''')

    with st.expander('European & Cup History'):
        st.write('Newcastle have a history of European appearances in UEFA competitions and multiple cup runs; consult season-by-season data to populate a full timelines table.')

    with st.expander('Community & Foundation Work'):
        st.write('The club and its foundation engage in community programs, youth outreach, charity matches and local partnerships — an important part of the club\'s impact off the pitch.')

    with st.expander('How to extend this section'):
        st.markdown('''
        - Add a `data/` folder with CSVs for seasons, players, managers, and transfers.  
        - Add images to an `images/players/` folder and show player cards with photos.  
        - Pull verified statistics from `football-data.org` or other licensed APIs and map them to the pages.
        ''')

elif page == "About / Run":
    st.markdown('<div class="banner"><div class="title-large">Run & Deployment</div></div>', unsafe_allow_html=True)
    st.write('How to run locally and tips for deployment.')
    st.code('''python -m venv .venv
.venv\\Scripts\\activate  # Windows
# pip install -r requirements.txt
# streamlit run app.py
''')

# Sidebar footer
st.sidebar.markdown('---')
st.sidebar.write('Demo • Sample data only — replace with CSV/API for real app')
