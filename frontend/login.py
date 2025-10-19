import streamlit as st
import base64
import streamlit_authenticator as stauth
# -----------------------------
# 1️⃣ Page config (must be first)
# -----------------------------
st.set_page_config(page_title="Incident", layout="wide")

# -----------------------------
# 2️⃣ Helper: convert local image to base64
# -----------------------------
def get_base64_of_image(image_file):
    with open(image_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

img_base64 = get_base64_of_image("img1.jpg")

def show_login():
    st.markdown("<div class='login'>", unsafe_allow_html=True)
    st.text_input("Username", key="username")
    st.text_input("Password", type="password", key="password")
    if st.button("Submit"):
        st.success("Login successful!")
    if st.button("Back to Home"):
        st.session_state.page = "home"
        st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# 3️⃣ CSS Styling
# -----------------------------
page_style = f"""
<style>
[data-testid="stAppViewContainer"] {{
  background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)),
              url("data:image/jpg;base64,{img_base64}") no-repeat center center fixed;
  background-size: cover;
}}

.hero {{
  height: 60vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
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
}}

.hero p.subtitle {{
  margin: 0;
  font-size: 1.25rem;
  opacity: 0.95;
}}

.hero p.small {{
  margin-top: 0.3rem;
  font-size: 0.75rem;
  opacity: 0.9;
}}

.st-key-login {{
  background-color: rgba(255, 255, 255, 0.3); /* white with 30% opacity */
  border-radius: 15px; /* rounded edges */
  padding: 20px; /* optional: adds spacing inside */
  width: fit-content; /* adjusts to content size */
  margin: auto; /* centers it */
  color: white;
  align-items: center;
  box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
}}

.st-key-submit button {{
  background-image: linear-gradient(90deg, Indigo , brown); /* gradient background */
  border-radius: 10px;
  font-size: 1rem;
 
}}

/* Style Streamlit buttons to match gradient CSS */
div.stButton > button {{
    border: none;
    padding: 14px 40px;
    border-radius: 10px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    color: white;
    width: 220px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.25);
    transition: all 0.2s ease-in-out;
    background-size: 200% auto;
}}

div.stButton > button:hover {{
    transform: translateY(-3px);
    box-shadow: 0 10px 24px rgba(0,0,0,0.32);
}}
label[data-testid="stWidgetLabel"] > div {{
    color: white !important;
    font-weight: bold !important;
    font-size: 16px !important;
}}
/* Specific gradients */
#report_button {{
    background-image: linear-gradient(90deg, #1E56A0, #4A90E2);
}}

#resolve_button {{
    background-image: linear-gradient(90deg, #2E8B57, #7ED957);
}}

@media (max-width: 520px) {{
  div.stButton > button {{
    width: 100%;
    padding: 12px 18px;
  }}
  .hero h1 {{ font-size: 2rem; }}
}}

</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

# -----------------------------
# 4️⃣ Hero section
# -----------------------------





st.markdown(
    """
    <style>
    .card {
        background-color: rgba(255, 255, 255, 0.3);
        padding: 20px;
        width: 300px;
        border-radius: 10px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

main_container = st.container(
    horizontal_alignment="center",
    vertical_alignment="center",
    key="login"
)

with main_container:
  st.header(" Login " , width=200)
  st.text_input("Username", key="username", width=200 )
  st.text_input("Password", type="password", key="password" , width=200)
  st.button("Submit" , key="submit")



