
Fajr Tracker v2 - Elegant Streamlit App
=======================================

Files:
- fajr_tracker_v2.py    : The Streamlit web app
- requirements.txt      : Python packages needed
- README.md             : This file
- data.csv              : (created automatically) stores entries

How to run locally:
1. Install dependencies:
   pip install -r requirements.txt
2. Run the app:
   streamlit run fajr_tracker_v2.py
3. The app opens in your browser at http://localhost:8501

Deploy to Streamlit Community Cloud (recommended for sharing):
1. Create a new public GitHub repository and upload all files.
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click 'New app' and select your repo & branch. Set Main file to fajr_tracker_v2.py.
4. Click Deploy. Share the URL with your family.

Notes:
- The app uses a simple CSV backend (data.csv) that Streamlit Cloud will persist between runs.
- The page auto-refreshes every 5 seconds so family members see updates quickly.
- Each member can submit once per day; they can reset their own day entry using the card button.
