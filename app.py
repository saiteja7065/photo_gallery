
import streamlit as st
import pandas as pd
import re
from readme_api import has_readme_and_url
from contributing_api import has_contributing_and_url
from changelog_api import has_changelog_and_url

st.set_page_config(page_title="Hackathon App Gallery", layout="wide")  # <-- Move here

# ------------------ Set Black + Green Theme ------------------
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            background-color: black;
            color: #ffffff;
        }
        .stButton>button {
            background-color: #1f1f1f;
            color: #90ee90;
            border-radius: 8px;
            padding: 0.4em 1em;
            border: 1px solid #90ee90;
        }
        .stTextInput>div>div>input {
            background-color: #1f1f1f;
            color: #90ee90;
        }
        .stSelectbox>div>div>div>div {
            background-color: #1f1f1f;
            color: #90ee90;
        }
        .stMarkdown {
            color: #90ee90;
        }
        a, a:visited {
            color: #90ee90;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------ Load & Clean CSV Data ------------------
@st.cache_data
def load_data():
    df_raw = pd.read_csv("data.csv", header=2)
    df = df_raw.dropna(subset=["App Name"]).reset_index(drop=True)
    # Filter out placeholder/template rows
    df = df[~df["Short description"].str.contains("Short description of the application", na=False)]
    return df

# ------------------ Topic Classification ------------------
def classify_app_topic(description: str, app_name: str = "") -> str:
    if pd.isna(description): description = ""
    if pd.isna(app_name): app_name = ""
    text = (description + " " + app_name).lower()
    topic_keywords = {
        "Games": ["game", "gaming", "play", "player", "arcade", "puzzle", "quiz", "trivia", "entertainment"],
        "Travel": ["travel", "trip", "journey", "destination", "booking", "hotel", "flight", "vacation"],
        "Finance": ["finance", "money", "payment", "wallet", "budget", "investment", "crypto"],
        "Healthcare": ["health", "medical", "doctor", "patient", "fitness", "hospital"],
        "E-commerce": ["shop", "shopping", "ecommerce", "retail", "buy", "sell"],
        "Education": ["education", "learning", "student", "teacher", "course", "tutorial"],
        "AI/ML": ["ai", "machine learning", "ml", "neural", "chatbot", "automation"],
        "Social": ["social", "chat", "community", "network", "connect"],
        "Business": ["business", "enterprise", "management", "crm", "hr", "workflow"],
        "Analytics": ["data", "analytics", "dashboard", "visualization", "metrics"]
    }
    topic_scores = {topic: sum(1 for keyword in keywords if keyword in text) for topic, keywords in topic_keywords.items()}
    return max(topic_scores, key=topic_scores.get) if topic_scores else "Others"

@st.cache_data
def categorize_apps(df):
    categories = {}
    for idx, row in df.iterrows():
        topic = classify_app_topic(row.get("Short description", ""), row.get("App Name", ""))
        categories.setdefault(topic, []).append({"index": idx, "data": row})
    return categories

# ------------------ Search ------------------
def search_apps(df, query):
    if not query:
        return df
    query = query.lower()
    def create_search_text(row):
        fields = ["App Name", "Short description", "Target User Personas", "Cross-Platform Availability"]
        return ' '.join(str(row.get(f, '')) for f in fields).lower()
    return df[df.apply(lambda row: query in create_search_text(row), axis=1)]

# ------------------ UI: App Card ------------------
def render_app_card(row, card_style):
    repo = row.get("Repo URL", "")
    if not isinstance(repo, str):
        repo = str(repo) if not pd.isna(repo) else ""

    has_readme, readme_url = (False, None)
    has_contrib, contrib_url = (False, None)
    has_changelog, changelog_url = (False, None)
    if repo.strip():
        has_readme, readme_url = has_readme_and_url(repo)
        has_contrib, contrib_url = has_contributing_and_url(repo)
        has_changelog, changelog_url = has_changelog_and_url(repo)

    highlight = not (repo and has_readme)
    card_style_final = card_style
    if highlight:
        card_style_final = card_style + "border: 2px solid #e74c3c; background-color: #fff0f0;"

    with st.container():
        st.markdown(f"<div style='{card_style_final}'>", unsafe_allow_html=True)
        st.subheader(row.get("App Name", "Unnamed App"))
        st.markdown(f"**Team Number**: {row.get('Factor', 'N/A')}")
        st.markdown(f"**Short Description**: {row.get('Short description', 'N/A')}")
        st.markdown(f"**Target Users**: {row.get('Target User Personas', 'N/A')}")
        st.markdown(f"**Current Users**: {row.get('Current Users Count', 'N/A')}")
        st.markdown(f"**AI/ML Innovation**: {row.get('AI/ML Innovation', 'N/A')}")

        prod = row.get("PROD URL", "")

        # 1st row: App and Source Code buttons
        btn_row1 = st.columns(2)
        if isinstance(prod, str) and prod.strip() and re.match(r"https?://", prod):
            btn_row1[0].markdown(
                f"<a href='{prod}' target='_blank'><button style='width:100%'>Open App</button></a>",
                unsafe_allow_html=True
            )
        else:
            btn_row1[0].markdown(
                "<button style='width:100%;background-color:#ff4d4d;color:white;border:none;border-radius:4px;padding:0.5em 0;'>⚠️No Link to App⚠️</button>",
                unsafe_allow_html=True
            )
        if repo and isinstance(repo, str) and re.match(r"https?://", repo):
            btn_row1[1].markdown(
                f"<a href='{repo}' target='_blank'><button style='width:100%'>Source Code</button></a>",
                unsafe_allow_html=True
            )
        else:
            btn_row1[1].markdown(
                "<button style='width:100%;background-color:#ff4d4d;color:white;border:none;border-radius:4px;padding:0.5em 0;'>No Link to Source</button>",
                unsafe_allow_html=True
            )

        # Move documentation buttons into the expander, at the top
        with st.expander("Read More"):
            btn_docs = st.columns(3)
            # README button or warning
            if repo and has_readme and readme_url:
                btn_docs[0].markdown(
                    f"<a href='{readme_url}' target='_blank'><button style='width:100%'>View README.md</button></a>",
                    unsafe_allow_html=True
                )
            elif repo:
                btn_docs[0].markdown(
                    "<button style='width:100%;background-color:#ff4d4d;color:white;border:none;border-radius:4px;padding:0.5em 0;'>❌ No README.md</button>",
                    unsafe_allow_html=True
                )
            else:
                btn_docs[0].markdown(
                    "<button style='width:100%;background-color:#ff4d4d;color:white;border:none;border-radius:4px;padding:0.5em 0;'>❌ No Repo Link</button>",
                    unsafe_allow_html=True
                )

            # CONTRIBUTING button or warning
            if repo and has_contrib and contrib_url:
                btn_docs[1].markdown(
                    f"<a href='{contrib_url}' target='_blank'><button style='width:100%'>View CONTRIBUTING.md</button></a>",
                    unsafe_allow_html=True
                )
            elif repo:
                btn_docs[1].markdown(
                    "<button style='width:100%;background-color:#ff4d4d;color:white;border:none;border-radius:4px;padding:0.5em 0;'>❌ No CONTRIBUTING.md</button>",
                    unsafe_allow_html=True
                )
            else:
                btn_docs[1].markdown(
                    "<button style='width:100%;background-color:#ff4d4d;color:white;border:none;border-radius:4px;padding:0.5em 0;'>❌ No Repo Link</button>",
                    unsafe_allow_html=True
                )

            # CHANGELOG button or warning
            if repo and has_changelog and changelog_url:
                btn_docs[2].markdown(
                    f"<a href='{changelog_url}' target='_blank'><button style='width:100%'>View CHANGELOG</button></a>",
                    unsafe_allow_html=True
                )
            elif repo:
                btn_docs[2].markdown(
                    "<button style='width:100%;background-color:#ff4d4d;color:white;border:none;border-radius:4px;padding:0.5em 0;'>❌ No CHANGELOG</button>",
                    unsafe_allow_html=True
                )
            else:
                btn_docs[2].markdown(
                    "<button style='width:100%;background-color:#ff4d4d;color:white;border:none;border-radius:4px;padding:0.5em 0;'>❌ No Repo Link</button>",
                    unsafe_allow_html=True
                )

            # Now the rest of the text
            st.markdown(f"**Cross-Platform Availability**: {row.get('Cross-Platform Availability', 'N/A')}")
            for col in row.index:
                if col not in [
                    "App Name", "Factor", "Short description", "Target User Personas", "Current Users Count",
                    "Indic Languages support", "AI/ML Innovation", "PROD URL", "Repo URL", "Cross-Platform Availability"
                ]:
                    st.markdown(f"**{col}**: {row[col]}")
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------ Streamlit App ------------------
def main():
    # st.set_page_config(page_title="Hackathon App Gallery", layout="wide")
    st.title("Hackathon Project Gallery")
    df = load_data()

    st.sidebar.header("Controls")
    topic_mode = st.sidebar.toggle("Enable Topic Filters")
    search_query = st.sidebar.text_input("Search Apps")

    card_style = '''
        background-color: #90ee90;
        padding: 1rem;
        border-radius: 1rem;
        box-shadow: 1px 1px 5px rgba(0,255,0,0.2);
        margin-bottom: 1.5rem;
        color: #1a1a1a;
    '''

    filtered_df = search_apps(df, search_query)

    if topic_mode:
        categories = categorize_apps(filtered_df)
        selected_topic = st.sidebar.selectbox("Select Topic", ["All"] + list(categories.keys()))
        if selected_topic == "All":
            apps_to_display = filtered_df.iterrows()
        else:
            apps_to_display = [(app['index'], app['data']) for app in categories[selected_topic]]
    else:
        apps_to_display = filtered_df.iterrows()

    st.subheader(f"Total Apps: {len(filtered_df)}")
    cols = st.columns(3)
    for idx, (_, row) in enumerate(apps_to_display):
        with cols[idx % 3]:
            render_app_card(row, card_style)

if __name__ == "__main__":
    main()