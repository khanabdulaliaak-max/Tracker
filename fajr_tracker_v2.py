import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
from pathlib import Path

# --- Config ---
DATA_FILE = "data.csv"
MEMBERS = ["Shaheer", "MSN", "Ali"]
OPTIONS = {
    "Fajr with Jamaat (+5)": 5,
    "Fajr prayed alone (+2)": 2,
    "Fajr Qaza (-1)": -1
}
DAYS_LIMIT = 30

# Ensure data file exists
def ensure_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["date","name","status","points"])
        df.to_csv(DATA_FILE, index=False)

def load_data():
    ensure_data()
    return pd.read_csv(DATA_FILE, parse_dates=["date"])

def save_entry(name, status):
    df = load_data()
    today = pd.to_datetime(date.today())
    # remove any existing entry for this name & date (shouldn't be present, but safe)
    df = df[~((df["name"]==name) & (df["date"]==today))]
    points = OPTIONS.get(status, 0)
    new = {"date": today, "name": name, "status": status, "points": points}
    df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

def remove_entry(name):
    df = load_data()
    today = pd.to_datetime(date.today())
    df = df[~((df["name"]==name) & (df["date"]==today))]
    df.to_csv(DATA_FILE, index=False)

def compute_scores(df):
    # consider only last 30 days from most recent record
    if df.empty:
        return {m:0 for m in MEMBERS}
    latest = pd.to_datetime(df["date"].max())
    window_start = latest - pd.Timedelta(days=DAYS_LIMIT-1)
    window_df = df[df["date"] >= window_start]
    scores = {m:0 for m in MEMBERS}
    for _, row in window_df.iterrows():
        scores[row["name"]] += int(row["points"])
    return scores

def build_cumulative_df(df):
    if df.empty:
        return pd.DataFrame(columns=["date"]+MEMBERS)
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    latest = df["date"].max()
    window_start = latest - pd.Timedelta(days=DAYS_LIMIT-1)
    dates = pd.date_range(start=window_start.normalize(), end=latest.normalize(), freq="D")
    pivot = df.pivot_table(index="date", columns="name", values="points", aggfunc="sum").reindex(dates, fill_value=0).reset_index()
    pivot.columns.name = None
    for m in MEMBERS:
        if m not in pivot.columns:
            pivot[m] = 0
    pivot = pivot.sort_values("date")
    cum = pivot.copy()
    cum[MEMBERS] = cum[MEMBERS].cumsum()
    cum = cum.set_index("date")
    return cum

# --- UI ---
st.set_page_config(page_title="Fajr Tracker", page_icon="🌅", layout="wide")

# small auto-refresh so multiple users see updates quickly (every 5 seconds)
st.markdown('<meta http-equiv="refresh" content="5">', unsafe_allow_html=True)

# Stylish CSS
st.markdown(
    """
    <style>
    :root { --bg1: #f5fbff; --bg2: #fff7ec; }
    .stApp { background: linear-gradient(180deg,var(--bg1),var(--bg2)); }
    .header { font-family: 'Georgia', serif; font-size:32px; font-weight:700; color:#0b3d2b; margin-bottom:6px;}
    .sub { color:#556b63; margin-top: -10px; margin-bottom:20px; }
    .card { background: white; padding: 18px; border-radius:12px; box-shadow: 0 8px 24px rgba(11,61,43,0.06); }
    .member-value { font-size:40px; font-weight:700; color:#102b2a; }
    .small-muted { color:#6b7280; font-size:14px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="header">🌅 Fajr Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Progress and points — auto-updates for the family</div>', unsafe_allow_html=True)

ensure_data()
df = load_data()
scores = compute_scores(df)
cum_df = build_cumulative_df(df)

# Layout: three cards for members
cols = st.columns(3, gap="large")
for i, member in enumerate(MEMBERS):
    with cols[i]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f"### {member}", unsafe_allow_html=True)
        st.markdown(f'<div class="member-value">{scores.get(member,0)} pts</div>', unsafe_allow_html=True)
        today = pd.to_datetime(date.today())
        today_row = df[(df["name"]==member) & (df["date"]==today)]
        if not today_row.empty:
            status = today_row.iloc[-1]["status"]
            st.markdown(f"<div class='small-muted'>Today's entry: {status}</div>", unsafe_allow_html=True)
            if st.button(f"Reset {member}'s Today Entry", key=f"reset_{member}"):
                remove_entry(member)
                st.experimental_rerun()
        else:
            st.markdown("<div class='small-muted'>No entry for today yet</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# Chart area (full width)
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📈 Progress (last 30 days)")
if not cum_df.empty:
    st.line_chart(cum_df)
else:
    st.info("No records yet — members can submit from the entry page.")

st.markdown('</div>', unsafe_allow_html=True)

st.write("")
with st.expander("How members should submit their daily entry (one-time per day)"):
    st.markdown("""
    1. Open the same app link and go to the **Entry** section (below) or use the app's submission form.
    2. Choose your name and pick the correct Fajr type.
    3. Submit — you can only submit once per day. If you made a mistake, use the **Reset Today's Entry** button on the card above.
    """)

with st.expander("Entry (submit once per day):", expanded=False):
    with st.form("entry_form"):
        name = st.selectbox("Your name", MEMBERS)
        choice = st.selectbox("How did you pray Fajr today?", list(OPTIONS.keys()))
        submitted = st.form_submit_button("Save my entry")
        if submitted:
            today = pd.to_datetime(date.today())
            existing = df[(df["name"]==name) & (df["date"]==today)]
            if not existing.empty:
                st.warning("You already recorded your Fajr for today. Use the Reset button on your card if you need to change it.")
            else:
                save_entry(name, choice)
                st.success("Saved! Progress will update for everyone within a few seconds.")
                st.experimental_rerun()

st.markdown('<div style="text-align:center; color:gray; font-size:0.9em;">Made with ❤️ for your family</div>', unsafe_allow_html=True)
