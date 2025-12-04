"""
Writers Room - Ideenfindung und Ideendiskussion
Streamlit App für writersroom.pro
"""

import streamlit as st
import PyPDF2
from io import BytesIO
import json
import os
from dotenv import load_dotenv
import anthropic

# Lade Umgebungsvariablen aus .env Datei
load_dotenv()

# Seitenkonfiguration
st.set_page_config(
    page_title="Writers Room",
    page_icon="✍️",
    layout="wide"
)

# CSS Styling
st.markdown("""
<style>
    .agent-message {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid;
    }
    .agent-kritiker {
        background-color: #fff3cd;
        border-left-color: #ffc107;
    }
    .agent-gefuehlvolle {
        background-color: #f8d7da;
        border-left-color: #dc3545;
    }
    .agent-action {
        background-color: #d1ecf1;
        border-left-color: #17a2b8;
    }
    .agent-horror {
        background-color: #e2e3e5;
        border-left-color: #6c757d;
    }
    .agent-name {
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 8px;
    }
    .user-message {
        background-color: #e7f3ff;
        padding: 12px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #0066cc;
    }
</style>
""", unsafe_allow_html=True)

# KI-Agenten Definitionen
AGENTS = {
    "Der Kritiker": {
        "emoji": "🎭",
        "color": "kritiker",
        "system_prompt": """Du bist 'Der Kritiker' - ein erfahrener Story-Analyst mit hohen Standards. 
        Du analysierst Handlungsstränge, Charakterentwicklung und Dramaturgie kritisch aber konstruktiv.
        Du lobst nicht, sondern gibst direkte, ehrliche Einschätzungen. Du identifizierst Schwachstellen,
        logische Brüche und Verbesserungspotenzial. Deine Antworten sind präzise und ohne Umschweife.
        Beziehe dich immer auf den gegebenen Kontext."""
    },
    "Die Gefühlvolle": {
        "emoji": "💝",
        "color": "gefuehlvolle",
        "system_prompt": """Du bist 'Die Gefühlvolle' - du fokussierst dich auf emotionale Tiefe,
        Charakterbeziehungen und authentische Gefühle. Du analysierst zwischenmenschliche Dynamiken,
        emotionale Entwicklungen und die Glaubwürdigkeit von Beziehungen. Du lobst nicht, sondern
        stellst fest, wo emotionale Resonanz fehlt oder vorhanden ist. Antworte direkt und ohne Floskeln.
        Beziehe dich immer auf den gegebenen Kontext."""
    },
    "Der Action-Fanatiker": {
        "emoji": "💥",
        "color": "action",
        "system_prompt": """Du bist 'Der Action-Fanatiker' - du bewertest Tempo, Spannung und Action-Sequenzen.
        Du achtest auf Dynamik, Pacing und intensive Momente. Du lobst nicht, sondern sagst direkt,
        wo es zu langsam ist oder wo Action fehlt. Du analysierst Konflikte, Spannungsbögen und
        action-geladene Szenen. Antworte knapp und direkt ohne Umschweife.
        Beziehe dich immer auf den gegebenen Kontext."""
    },
    "Der Horror-Enthusiast": {
        "emoji": "👻",
        "color": "horror",
        "system_prompt": """Du bist 'Der Horror-Enthusiast' - du analysierst atmosphärische Dichte,
        Spannung und das Unheimliche. Du achtest auf Stimmung, psychologischen Horror und bedrohliche
        Elemente. Du lobst nicht, sondern stellst fest, wo Atmosphäre und Spannung fehlen.
        Du identifizierst potenzielle düstere oder unheimliche Aspekte. Antworte direkt ohne Floskeln.
        Beziehe dich immer auf den gegebenen Kontext."""
    }
}

GENRES = ["Romantik", "Krimi", "Action", "Horror", "Drama", "Sci-Fi", "Fantasy"]


def extract_text_from_pdf(pdf_file):
    """Extrahiert Text aus hochgeladener PDF"""
    try:
        # Datei-Inhalt als Bytes lesen
        pdf_bytes = pdf_file.read()

        # PDF Reader mit den Bytes initialisieren
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        text = ""
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

        if not text.strip():
            st.warning("⚠️ PDF enthält keinen extrahierbaren Text.")
            return ""

        return text[:5000]  # Max 5000 Zeichen
    except Exception as e:
        st.error(f"❌ Fehler beim Lesen der PDF: {e}")
        return ""


def generate_agent_response(agent_name, user_question, context, genre, chat_history):
    agent_info = AGENTS[agent_name]

    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        st.error("⚠️ ANTHROPIC_API_KEY nicht gefunden! Bitte .env Datei erstellen.")
        return "Fehler: API-Key nicht konfiguriert."

    try:

        client = anthropic.Anthropic(api_key=api_key)

        # Erstelle Prompt mit Kontext
        prompt = f"""Kontext der Story:
    {context}

    Genre: {genre}

    Frage des Users: {user_question}

    Antworte als {agent_name} direkt und ohne Lobhudelei. Beziehe dich auf den gegebenen Kontext und das Genre. Sei kritisch und konstruktiv, aber komme ohne Umschweife zum Punkt."""

        # API-Call
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            temperature=1.0,
            system=agent_info['system_prompt'],
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        return message.content[0].text

    except ImportError:
        st.error("⚠️ 'anthropic' Paket nicht installiert! Führe aus: pip install anthropic")
        return "Fehler: anthropic Paket fehlt."
    except Exception as e:
        st.error(f"⚠️ API-Fehler: {str(e)}")
        return f"Fehler bei der Antwort-Generierung: {str(e)}"
def main():
    # Header
    st.title("✍️ Writers Room")
    st.subheader("Ideenfindung und Ideendiskussion mit KI-Agenten")
    st.markdown("---")

    # Session State initialisieren
    if 'context' not in st.session_state:
        st.session_state.context = ""
    if 'genre' not in st.session_state:
        st.session_state.genre = ""
    if 'selected_agents' not in st.session_state:
        st.session_state.selected_agents = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'setup_complete' not in st.session_state:
        st.session_state.setup_complete = False

    # Setup-Phase
    if not st.session_state.setup_complete:
        st.header("🎬 Setup: Kontext & Einstellungen")

        # Kontext-Eingabe
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📝 Kontext eingeben")
            context_input = st.text_area(
                "Beschreibe deine Story-Idee oder deinen Kontext:",
                height=250,
                max_chars=5000,
                placeholder="Z.B.: Ein Detektiv untersucht mysteriöse Verschwinden in einer Kleinstadt..."
            )
            char_count = len(context_input)
            st.caption(f"Zeichen: {char_count}/5000")

        with col2:
            st.subheader("📄 Oder PDF hochladen")
            pdf_file = st.file_uploader(
                "PDF-Datei hochladen (max. 5000 Zeichen werden extrahiert)",
                type=['pdf']
            )

            if pdf_file:
                extracted_text = extract_text_from_pdf(pdf_file)
                if extracted_text:
                    st.success(f"✅ PDF gelesen: {len(extracted_text)} Zeichen")
                    if st.button("PDF-Text übernehmen"):
                        context_input = extracted_text
                        st.rerun()

        st.markdown("---")

        # Genre-Auswahl
        st.subheader("🎭 Genre wählen")
        selected_genre = st.selectbox(
            "Wähle das Genre deiner Story:",
            options=GENRES,
            index=0
        )

        st.markdown("---")

        # Agenten-Auswahl
        st.subheader("🤖 KI-Agenten auswählen")
        st.write("Wähle einen oder mehrere Agenten für die Diskussion:")

        cols = st.columns(4)
        selected_agents = []

        for idx, (agent_name, agent_data) in enumerate(AGENTS.items()):
            with cols[idx % 4]:
                if st.checkbox(
                        f"{agent_data['emoji']} {agent_name}",
                        key=f"agent_{agent_name}"
                ):
                    selected_agents.append(agent_name)
                st.caption(agent_data['system_prompt'][:100] + "...")

        st.markdown("---")

        # Setup abschließen
        if st.button("🚀 Writers Room starten", type="primary", use_container_width=True):
            if not context_input:
                st.error("⚠️ Bitte gib einen Kontext ein oder lade eine PDF hoch!")
            elif not selected_agents:
                st.error("⚠️ Bitte wähle mindestens einen Agenten aus!")
            else:
                st.session_state.context = context_input
                st.session_state.genre = selected_genre
                st.session_state.selected_agents = selected_agents
                st.session_state.setup_complete = True
                st.rerun()

    # Chat-Phase
    else:
        # Sidebar mit Setup-Info
        with st.sidebar:
            st.header("📋 Session Info")
            st.write(f"**Genre:** {st.session_state.genre}")
            st.write(f"**Aktive Agenten:**")
            for agent in st.session_state.selected_agents:
                st.write(f"{AGENTS[agent]['emoji']} {agent}")

            st.markdown("---")
            st.write("**Kontext:**")
            st.text_area(
                "Dein Kontext",
                value=st.session_state.context[:500] + "..." if len(
                    st.session_state.context) > 500 else st.session_state.context,
                height=200,
                disabled=True
            )

            if st.button("🔄 Neuer Session", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        # Chat-Interface
        st.header("💬 Writers Room Chat")

        # Chat-Verlauf anzeigen
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div class="user-message">
                        <strong>Du:</strong> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    agent = message['agent']
                    agent_data = AGENTS[agent]
                    st.markdown(f"""
                    <div class="agent-message agent-{agent_data['color']}">
                        <div class="agent-name">{agent_data['emoji']} {agent}</div>
                        {message['content']}
                    </div>
                    """, unsafe_allow_html=True)

        # Frage-Eingabe
        st.markdown("---")
        with st.form(key='question_form', clear_on_submit=True):
            user_question = st.text_area(
                "Stelle deine Frage an die Agenten:",
                height=100,
                max_chars=250,
                placeholder="Z.B.: Wie kann ich die Spannung im zweiten Akt erhöhen?"
            )

            col1, col2 = st.columns([3, 1])
            with col1:
                submit_button = st.form_submit_button("📤 Frage senden", use_container_width=True)
            with col2:
                st.caption(f"{len(user_question)}/250")

        if submit_button and user_question:
            # User-Nachricht hinzufügen
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_question
            })

            # Agenten-Antworten generieren
            for agent in st.session_state.selected_agents:
                response = generate_agent_response(
                    agent,
                    user_question,
                    st.session_state.context,
                    st.session_state.genre,
                    st.session_state.chat_history
                )

                st.session_state.chat_history.append({
                    'role': 'agent',
                    'agent': agent,
                    'content': response
                })

            st.rerun()


if __name__ == "__main__":
    main()