# Queue Mood Tracker

A simple internal tool for tracking and visualizing the emotional state of your support queue throughout the day.

[Demo video](https://www.loom.com/share/060078bcc882420c896b161c97af359a?sid=8a3a9307-d662-4485-9652-8ad62d926c10)

## Features

- Log moods with emoji selection
- Add optional notes to each mood entry
- Real-time visualization of mood distribution
- Data stored in Google Sheets
- Auto-refreshing dashboard

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Google Sheets API:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the Google Sheets API
   - Create a service account and download the credentials JSON file
   - Rename the downloaded file to `credentials.json` and place it in the project root
   - Create a new Google Sheet named "Queue_Mood_Tracker"
   - Share the sheet with the service account email (found in the credentials.json file)

3. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Select a mood from the emoji options
2. (Optional) Add a note about the current queue state
3. Click "Submit Mood" to log the entry
4. View the mood distribution chart on the right side of the dashboard

The chart automatically updates to show today's mood distribution.

## Requirements

- Python 3.7+
- Google Sheets API credentials
- Internet connection for Google Sheets integration 
