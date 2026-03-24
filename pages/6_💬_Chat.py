import streamlit as st
import openai
from datetime import datetime

st.set_page_config(page_title="Chat with Dutch AI - Netherlands QuizMaster", page_icon="💬", layout="wide")

# Load custom CSS
from pathlib import Path
ROOT = Path(__file__).parent.parent
CSS_FILE = ROOT / "assets" / "styles.css"
if CSS_FILE.exists():
    st.markdown(f"<style>{CSS_FILE.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# Page container for consistent layout
st.markdown('<div class="container">', unsafe_allow_html=True)

def init_chat_session():
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
        # Add initial greeting
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": "Hoi! Ik ben Jan, een echte Nederlandse AI. Lekker om te praten! Wat kan ik voor je doen vandaag? Misschien over kaas, fietsen, of het weer? 😊",
            "timestamp": datetime.now().isoformat()
        })

init_chat_session()

def get_dutch_ai_response(user_message):
    """Get response from OpenAI as stereotypical Dutch person."""
    try:
        client = openai.OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))
        
        system_prompt = """You are Jan, a stereotypical Dutch person from Amsterdam. You speak English with a strong Dutch accent and personality. Be very direct, blunt, and honest. Use lots of Dutch words and expressions like:
- Lekker (delicious, nice, good)
- Gezellig (cozy, fun)
- Goed zo (good job)
- Ach (oh well)
- Nou (well)
- References to cheese, bikes, windmills, tulips, coffee, being thrifty
- Complain about weather, flat landscape, traffic
- Be proud of Dutch culture but also self-deprecating
- Use humor about Dutch stereotypes
- End sentences with 'ja?' or 'nee?' sometimes
Keep responses conversational and friendly, but with that typical Dutch straightforwardness."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.8
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Ach, sorry! Er is iets mis met mijn brein. Probeer het later nog eens. Error: {str(e)}"

# Header
st.markdown(
    '''
    <div class="topbar">
        <div class="brand">
            <div class="logo">🇳🇱</div>
            <div>
                <div class="title">Netherlands QuizMaster</div>
                <div class="subtitle">Chat with Dutch AI</div>
            </div>
        </div>
        <div class="nav-links">
            <button class="nav-link" onclick="window.location.href = window.location.origin + window.location.pathname + '?page=Home'">🏠 Home</button>
            <button class="nav-link" onclick="window.location.href = window.location.origin + window.location.pathname + '?page=1_🎮_Quiz'">🎮 Quiz</button>
            <button class="nav-link" onclick="window.location.href = window.location.origin + window.location.pathname + '?page=2_🏆_Highscores'">🏆 Leaderboard</button>
            <button class="nav-link" onclick="window.location.href = window.location.origin + window.location.pathname + '?page=3_📚_Categories'">📚 Categories</button>
            <button class="nav-link" onclick="window.location.href = window.location.origin + window.location.pathname + '?page=4_⚙️_Settings'">⚙️ Settings</button>
        </div>
    </div>
    <div class="flag-stripe"></div>
    <div style="margin-top:12px; margin-bottom: 16px;">
        <h2 style='margin: 0; font-weight: 600; font-size: 22px;'>💬 Chat with Jan the Dutch AI</h2>
        <p style='margin:6px 0 0 0; color: var(--muted);'>Have a gezellig conversation with a stereotypical Dutch person!</p>
    </div>
    ''',
    unsafe_allow_html=True,
)

# Chat interface
st.markdown("---")

# Display chat messages
chat_container = st.container()
with chat_container:
    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style='text-align: right; margin: 10px 0;'>
                <div style='display: inline-block; background: var(--accent); color: white; padding: 10px 15px; border-radius: 18px 18px 5px 18px; max-width: 70%; word-wrap: break-word;'>
                    <strong>You:</strong> {msg['content']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='text-align: left; margin: 10px 0;'>
                <div style='display: inline-block; background: rgba(255,255,255,0.05); color: #c9d1d9; padding: 10px 15px; border-radius: 18px 18px 18px 5px; max-width: 70%; word-wrap: break-word;'>
                    <strong>Jan:</strong> {msg['content']}
                </div>
            </div>
            """, unsafe_allow_html=True)

# Input area
col1, col2 = st.columns([4, 1])
with col1:
    user_input = st.text_input("Type your message to Jan...", key="user_input", label_visibility="collapsed")
with col2:
    if st.button("Send", use_container_width=True):
        if user_input.strip():
            # Add user message
            st.session_state.chat_messages.append({
                "role": "user",
                "content": user_input.strip(),
                "timestamp": datetime.now().isoformat()
            })
            
            # Get AI response
            with st.spinner("Jan is typing..."):
                ai_response = get_dutch_ai_response(user_input.strip())
            
            # Add AI response
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": ai_response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Clear input and rerun
            st.session_state.user_input = ""
            st.rerun()

# Clear chat button
st.markdown("---")
if st.button("🗑️ Clear Chat", help="Start a new conversation with Jan"):
    st.session_state.chat_messages = []
    init_chat_session()
    st.rerun()

# Footer
st.markdown('<div style="margin-top: 50px; text-align: center; color: #6b7684; font-size: 12px;">Powered by OpenAI • Jan speaks with a Dutch accent! 🇳🇱</div>', unsafe_allow_html=True)

# Close page container
st.markdown('</div>', unsafe_allow_html=True)