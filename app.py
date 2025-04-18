import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Google Sheets credentials
def get_google_sheets_client():
    try:
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        if not os.path.exists('credentials.json'):
            st.error("❌ credentials.json file not found. Please follow the setup instructions in the README.")
            return None
        
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"❌ Error setting up Google Sheets client: {str(e)}")
        return None

def ensure_headers(sheet):
    """Ensure the sheet has the required headers"""
    try:
        # Get the first row
        first_row = sheet.row_values(1)
        required_headers = ['timestamp', 'mood', 'note']
        
        # If the sheet is empty or headers don't match
        if not first_row or first_row != required_headers:
            # Clear the sheet if it has data
            if first_row:
                sheet.clear()
            # Add headers
            sheet.append_row(required_headers)
            st.info("ℹ️ Created required headers in the sheet")
    except Exception as e:
        st.error(f"❌ Error setting up sheet headers: {str(e)}")

def load_mood_data():
    """Load mood data from Google Sheets"""
    try:
        client = get_google_sheets_client()
        if client is None:
            st.error("Cannot load data - Google Sheets client not available")
            return None
        
        sheet = client.open("Mochi Health Takehome").sheet1
        ensure_headers(sheet)
        
        records = sheet.get_all_records()
        return pd.DataFrame(records)
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return None

def update_graph(df, start_date, end_date, mood_emojis):
    """Update the graph with filtered data"""
    if df is not None and not df.empty:
        # Convert timestamp to datetime and filter by date range
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        
        if not filtered_df.empty:
            # Get mood counts and ensure all moods are represented
            mood_counts = filtered_df['mood'].value_counts().reindex(mood_emojis).fillna(0).reset_index()
            mood_counts.columns = ['mood', 'count']
            
            # Create bar chart with fixed mood order
            fig = px.bar(mood_counts,
                       x='mood',
                       y='count',
                       title=f"Mood Distribution ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})",
                       labels={'mood': 'Mood', 'count': 'Count'},
                       category_orders={"mood": mood_emojis})
            st.plotly_chart(fig)
        else:
            st.info(f"ℹ️ No mood data available for the selected date range ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})")
    else:
        st.info("ℹ️ No mood data available yet.")

# Initialize session state
if 'moods' not in st.session_state:
    st.session_state.moods = []
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'df' not in st.session_state:
    st.session_state.df = None

# Page config
st.set_page_config(page_title="Queue Mood Tracker", page_icon="😊")

# Title and description
st.title("Queue Mood Tracker")
st.markdown("Track the emotional state of your support queue throughout the day.")

# Load initial data
if st.session_state.df is None:
    st.session_state.df = load_mood_data()

# Date range filter
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input(
        "Start Date",
        value=datetime.now().date() - timedelta(days=7),
        max_value=datetime.now().date()
    )
with col2:
    end_date = st.date_input(
        "End Date",
        value=datetime.now().date(),
        max_value=datetime.now().date()
    )

# Ensure end date is not before start date
if end_date < start_date:
    st.error("End date must be after start date")
    st.stop()

# Mood lists in order
moods = ["Happy", "Neutral", "Confused", "Frustrated", "Sad"]
mood_emojis = ["😊", "😐", "😕", "😤", "😢"]

# Create two columns for layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Log a Mood")
    selected_mood = st.radio("Select Mood", mood_emojis)
    note = st.text_input("Add a note (optional)")
    
    if st.button("Submit Mood"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mood_data = {
            "timestamp": timestamp,
            "mood": selected_mood,
            "note": note
        }
        
        try:
            # Get Google Sheets client
            client = get_google_sheets_client()
            if client is None:
                st.error("Cannot submit mood - Google Sheets client not available")
                st.stop()
            
            # Try to open the sheet
            try:
                sheet = client.open("Mochi Health Takehome").sheet1
                ensure_headers(sheet)
            except gspread.exceptions.SpreadsheetNotFound:
                st.error("❌ 'Mochi Health Takehome' sheet not found. Please create it and share it with the service account email.")
                st.stop()
            
            # Append new row
            sheet.append_row([timestamp, selected_mood, note])
            
            # Reload data after submission
            st.session_state.df = load_mood_data()
            st.success("✅ Mood logged successfully!")
        except Exception as e:
            st.error(f"❌ Error logging mood: {str(e)}")

with col2:
    st.subheader("Mood Distribution")
    # Update graph with current filters
    update_graph(st.session_state.df, start_date, end_date, mood_emojis)
    
    # Show last update time if available
    if st.session_state.last_update:
        st.caption(f"Last updated: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}") 
