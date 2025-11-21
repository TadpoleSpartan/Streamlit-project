import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Newcastle United Explorer", layout="wide")

# --- Sample data (replace with real data/CSV if you want) ---
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

# Simplified season stats (example)
SEASON_STATS = {
    "season": ["2021/22", "2022/23", "2023/24", "2024/25"],
    "position": [11, 4, 5, 6],
    "points": [50, 71, 68, 63],
    "goals_scored": [46, 68, 62, 59],
    "goals_conceded": [51, 33, 36, 40],
}

# Convert to DataFrames
df_squad = pd.DataFrame(SQUAD)
df_stats = pd.DataFrame(SEASON_STATS)

# --- Layout / Navigation ---
st.sidebar.title("Newcastle United Explorer")
page = st.sidebar.radio("Go to", ["Home", "Squad", "Season Stats", "History & Trophies", "About / Run"])

# Helper: simple club info
club_info = {
    "name": "Newcastle United",
    "founded": 1892,
    "nickname": "The Magpies",
    "stadium": "St James' Park",
    "capacity": "≈ 52,000",
    "colors": "Black & White",
    "rival": "Sunderland (Tyne–Wear Derby)"
}

# --- Pages ---
if page == "Home":
    st.title(f"{club_info['name']} ⚫⚪")
    col1, col2 = st.columns([3,2])
    with col1:
        st.header("Club Overview")
        st.markdown(
            f"""
            **Founded:** {club_info['founded']}  
            **Nickname:** {club_info['nickname']}  
            **Stadium:** {club_info['stadium']} ({club_info['capacity']})  
            **Club colours:** {club_info['colors']}  
            **Rivalry:** {club_info['rival']}
            """
        )
        st.write(
            "This small demo app shows a searchable squad, simple season stats and a short history/trophies section. "
            "Replace the sample data with real CSV/JSON or an API to make it production-ready."
        )
    with col2:
        st.metric("Last season league position", df_stats.loc[len(df_stats)-1, "position"])
        st.metric("Last season points", df_stats.loc[len(df_stats)-1, "points"])

elif page == "Squad":
    st.title("Squad — Search & Filter")
    st.write("Search players, filter by position, nationality or sort by age/number.")
    # Filters
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

    st.dataframe(df_filtered.reset_index(drop=True), use_container_width=True)

    # Simple player detail on click (selectbox for demo)
    player = st.selectbox("Show details for", [""] + df_squad["name"].tolist())
    if player:
        p = df_squad[df_squad["name"] == player].iloc[0]
        st.subheader(p["name"])
        st.write(f"**Position:** {p['position']}")
        st.write(f"**Number:** {p['number']}")
        st.write(f"**Age:** {p['age']}")
        st.write(f"**Nationality:** {p['nationality']}")

elif page == "Season Stats":
    st.title("Season stats (example)")
    st.write("Interactive charts for recent seasons (sample data).")
    # Position over time (line)
    fig_pos = px.line(df_stats, x="season", y="position", markers=True, title="League position by season")
    fig_pos.update_yaxes(autorange="reversed", title="Position (lower is better)")
    st.plotly_chart(fig_pos, use_container_width=True)

    # Points and goals bar chart
    df_melt = df_stats.melt(id_vars="season", value_vars=["points", "goals_scored", "goals_conceded"],
                            var_name="metric", value_name="value")
    fig_bar = px.bar(df_melt, x="season", y="value", color="metric", barmode="group",
                     title="Points / Goals (scored & conceded) by season")
    st.plotly_chart(fig_bar, use_container_width=True)

    # Quick KPI row
    col1, col2, col3 = st.columns(3)
    col1.metric("Best finish (sample)", int(df_stats["position"].min()))
    col2.metric("Best points (sample)", int(df_stats["points"].max()))
    col3.metric("Most goals (sample)", int(df_stats["goals_scored"].max()))

elif page == "History & Trophies":
    st.title("History & Major Honours")
    st.write(
        """
        Newcastle United have a long history in English football, founded in 1892. Below is a short list of major honours (historic).
        This is example content — expand with more seasons, managers, and timelines.
        """
    )
    st.subheader("Major Honours (summary)")
    st.markdown(
        """
        - **English League Titles:** 4  
        - **FA Cups:** 6  
        - **Other:** Several lower-division and regional honours historically
        """
    )
    st.subheader("Notable eras")
    st.markdown(
        """
        - Early 1900s: strong side in the original Football League.  
        - 1990s–2000s: multiple Premier League promotions and European appearances.  
        - Recent era: investment and resurgence in the mid-2020s with strong top-table finishes.
        """
    )

elif page == "About / Run":
    st.title("Run & Deployment")
    st.write("How to run this app locally and quick notes for deployment.")
    st.markdown("""
    **Local (recommended)**:
    ```bash
    python -m venv .venv
    # Windows
    .venv\\Scripts\\activate
    # macOS / Linux
    source .venv/bin/activate

    pip install -r requirements.txt
    streamlit run app.py
    ```
    **Requirements**: see `requirements.txt` (example below).  
    For deploy, you can push to GitHub and deploy to Streamlit Community Cloud (streamlit.io) or another host.
    """)

    st.subheader("requirements.txt (suggested)")
    st.code("streamlit\npandas\nplotly", language="bash")

# Footer
st.sidebar.markdown("---")
st.sidebar.write("Demo app • Data: sample only. Replace with your CSV or API for production.")
