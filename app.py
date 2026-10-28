import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

from analyzer import analyze

st.set_page_config(page_title="Password Strength Analyzer", page_icon="🍂", layout="centered")

# colours go from autumn rust (weak) to spring green (strong)
LABEL_COLORS = {
    "Very Weak": "#B5533C",
    "Weak": "#D98B48",
    "Medium": "#D9B44A",
    "Strong": "#8FAE6B",
    "Very Strong": "#5E9B5A",
}

LEAVES = ["🍂", "🍁", "🍂", "🍃", "🍁", "🍂"]


def falling_leaves(count=16):
    """Build slow falling leaves; each gets its own position, speed, size and delay."""
    spans = []
    for i in range(count):
        left = (i * 100 / count) + (i * 37 % 7)
        size = 18 + (i * 13) % 16
        fall = 16 + (i * 7) % 12          # seconds, slow
        delay = -((i * 5) % 20)           # negative so leaves are already mid-air on load
        sway = 5 + (i * 3) % 4
        spans.append(
            f'<span class="leaf" style="left:{left:.0f}%;font-size:{size}px;'
            f'animation-duration:{fall}s,{sway}s;animation-delay:{delay}s,{delay}s;">'
            f'{LEAVES[i % len(LEAVES)]}</span>'
        )
    return '<div class="leaves">' + "".join(spans) + "</div>"


CSS = """
<style>
.stApp { background: linear-gradient(180deg, #FBF6EE 0%, #F3E6D3 100%); }
header[data-testid="stHeader"] { background: transparent; }

.leaves { position: fixed; inset: 0; overflow: hidden; pointer-events: none; z-index: 999; }
.leaf {
  position: absolute; top: -50px; opacity: .75;
  animation-name: fall, sway;
  animation-timing-function: linear, ease-in-out;
  animation-iteration-count: infinite, infinite;
  animation-direction: normal, alternate;
}
@keyframes fall { to { top: 105vh; } }
@keyframes sway { from { transform: translateX(-25px) rotate(-25deg); }
                  to   { transform: translateX(25px)  rotate(30deg); } }

.title { text-align: center; color: #6B4423; font-size: 2.4rem; margin: .5rem 0 0; }
.subtitle { text-align: center; color: #9A7B5F; margin-bottom: 1.5rem; }

div[data-baseweb="input"] { border-radius: 12px; background: #FFFDF9; }

.card { background: #FFFDF9; border: 1px solid #E6D3B8; border-radius: 16px;
        padding: 1.2rem 1.5rem; margin-top: 1rem;
        box-shadow: 0 4px 14px rgba(120, 80, 40, .08); }
.score-row { display: flex; justify-content: space-between; align-items: baseline; }
.score-label { font-size: 1.6rem; font-weight: 700; }
.score-num { color: #9A7B5F; }
.bar { height: 14px; background: #EFE2CE; border-radius: 99px; overflow: hidden; margin-top: .6rem; }
.bar > div { height: 100%; border-radius: 99px; transition: width .6s ease; }
.card h4 { margin: 0 0 .5rem; color: #6B4423; }
.card ul { margin: 0; padding-left: 1.2rem; }
.card li { margin: .25rem 0; }
.tip { color: #6F8F4E; }
.footer { text-align: center; color: #B79F86; font-size: .8rem; margin-top: 2rem; }
</style>
"""

st.markdown(CSS + falling_leaves(), unsafe_allow_html=True)
st.markdown('<h1 class="title">🍂 Password Strength Analyzer 🌱</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">See how strong your password is and how to improve it</p>',
            unsafe_allow_html=True)

password = st.text_input("Password", type="password", placeholder="Type a password to check…",
                         label_visibility="collapsed")

if password:
    result = analyze(password)
    color = LABEL_COLORS[result["label"]]

    st.markdown(
        f'<div class="card"><div class="score-row">'
        f'<span class="score-label" style="color:{color}">{result["label"]}</span>'
        f'<span class="score-num">{result["score"]} / 100</span></div>'
        f'<div class="bar"><div style="width:{result["score"]}%;background:{color}"></div></div></div>',
        unsafe_allow_html=True,
    )

    if result["weaknesses"]:
        left, right = st.columns(2)
        with left:
            items = "".join(f"<li>{w}</li>" for w in result["weaknesses"])
            st.markdown(f'<div class="card"><h4>🍁 Weaknesses</h4><ul>{items}</ul></div>',
                        unsafe_allow_html=True)
        with right:
            items = "".join(f"<li>{s}</li>" for s in result["suggestions"])
            st.markdown(f'<div class="card"><h4>🌱 Suggestions</h4><ul class="tip">{items}</ul></div>',
                        unsafe_allow_html=True)
    else:
        st.markdown('<div class="card"><h4>🌸 No weaknesses found. Nice password!</h4></div>',
                    unsafe_allow_html=True)

st.markdown('<p class="footer">Runs locally. Your password is never saved or sent anywhere.</p>',
            unsafe_allow_html=True)
