import streamlit as st
import base64
import login
# --- Helper: convert local image to base64 ---
def get_base64_of_image(image_file):
    with open(image_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

img_base64 = get_base64_of_image("img1.jpg")

st.set_page_config(page_title="Incident Management Portal", layout="wide")

# --- CSS styling ---
page_style = f"""
<style>
/* Background image with 50% black overlay */
[data-testid="stAppViewContainer"] {{
  background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)),
              url("data:image/jpg;base64,{img_base64}") no-repeat center center fixed;
  background-size: cover;
}}

.hero {{
  height: 40vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: top center;
  color: white;
  gap: 0.5rem;
  padding: 0.5rem;
  box-sizing: border-box;
}}

.hero h1 {{
  font-size: 3rem;
  margin: 0;
  font-weight: 800;
  letter-spacing: 0.5px;
  color: white;
}}

.hero p.subtitle {{
  margin: 0;
  font-size: 1.25rem;
  opacity: 0.95;
}}

.hero p.small {{
  margin-top: 0.3rem;
  font-size: 0.75rem; /* smaller font size */
  opacity: 0.9;
}}

.btn-group {{
  display: inline-flex;
  gap: 20px;
  margin-top: 1.8rem;
  align-items: center;
  justify-content: center;
}}

/* Base button styling */
.btn {{
  border: none;
  padding: 14px 40px;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  color: white;
  transition: all 0.2s ease-in-out;
  box-shadow: 0 6px 18px rgba(0,0,0,0.25);
  width: 220px;
  background-size: 200% auto; /* smooth gradient hover */
}}

.btn:hover {{
  transform: translateY(-3px);
  box-shadow: 0 10px 24px rgba(0,0,0,0.32);
  background-position: right center; /* animate gradient */
}}

/* Gradient versions */
.btn-report {{
  background-image: linear-gradient(90deg, #1E56A0, #4A90E2);
}}

.btn-resolve {{
  background-image: linear-gradient(90deg, #2E8B57, #7ED957);
}}

@media (max-width: 520px) {{
  .btn-group {{
    flex-direction: column;
    gap: 12px;
    width: 100%;
  }}
  .btn {{
    width: 100%;
    padding: 12px 18px;
  }}
  .hero h1 {{ font-size: 2rem; }}
}}
</style>
"""

st.markdown(page_style, unsafe_allow_html=True)

import streamlit as st

# --- Hero section ---
hero_html = """
<div class="hero">
  <h1>&lt;Name of our Portal&gt;</h1>
  <p class="subtitle">Incident Management Portal</p>
  <p class="small">What would you like to do today?</p>
</div>
"""
st.markdown(hero_html, unsafe_allow_html=True)

# --- CSS for buttons & spacing ---
st.markdown("""
<style>
/* Fixed width for buttons */
div.stButton > button {
    width: 220px;
    padding: 14px 0;
    font-size: 1rem;
}

/* Reduce vertical space between hero and buttons */
.css-1d391kg {  /* Streamlit container class, may vary */
    margin-top: 10px !important;
}

.hero {
    margin-bottom: 0px;  /* remove extra bottom space */
}
</style>
""", unsafe_allow_html=True)

# --- Centered buttons ---
col1, col2, col3 = st.columns([1,2,1])
with col2:
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.button("Report & Track", key="report_button", on_click=lambda: login.show_login(action="Report & Track"))
    with btn_col2:
        st.button("Resolve", key="resolve_button", on_click=lambda: login.show_login(action="Resolve"))
