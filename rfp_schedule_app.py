# --- LIBRARIES ---
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import holidays
import requests
from bs4 import BeautifulSoup
from dateutil import parser

# --- PAGE CONFIG ---
st.set_page_config(page_title="Howey RFP Calendar Generator", layout="centered")

# --- BRANDING AND HEADING ---
st.markdown("<h1 style='text-align: center;'>Town of Howey-in-the-Hills</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #004d7a;'>RFP Schedule Generator</h2>", unsafe_allow_html=True)
st.write("This tool will generate an RFP schedule, excluding non-working days and holidays.")

# --- STEP 1 USER INPUT ---
st.markdown("### Step 1: Enter the date the RFP was posted.")
rfp_posted_date = st.date_input("RFP Posted Date")

if rfp_posted_date:
    us_holidays = holidays.US(years=rfp_posted_date.year)
else:
    us_holidays = set()

# --- BUSINESS DAY FUNCTION ---
def next_valid_business_day(date, holiday_list):
    adjusted = False
    while date.weekday() >= 4 or date in holiday_list:  # Skip Friday (4), Saturday (5), Sunday (6), and holidays
        date += timedelta(days=1)
        adjusted = True
    return date, adjusted

# --- FUNCTION TO SCRAPE TC MEETINGS ---
def fetch_town_council_meetings():
    try:
        url = "https://www.howey.org/meetings?field_microsite_tid_1=31"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            st.error("Unable to connect to the Town's meeting calendar.")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all("tr", class_=["even", "odd"])

        meetings = []
        for row in rows:
            if "Town Council" in row.get_text():
                link = row.find("a")
                if link and "title" in link.attrs:
                    try:
                        dt = parser.parse(link["title"])
                        if dt > datetime.now():
                            meetings.append(dt)
                    except:
                        continue

        return sorted(meetings)

    except Exception as e:
        st.error(f"Error retrieving council meetings: {e}")
        return []

# --- MAIN SCHEDULE LOGIC ---
if rfp_posted_date:
    events = {
        "RFP Posted on Town Website": 0,
        "Questions Due to the Town": 7,
        "Responses to Questions Posted": 9,
        "Proposal Packages Due to the Town": 16,
        "Proposal Packages Opened and Evaluated": 16,
        "Notice to Award Contract Posted on Town Website": 20,
        "Contract Negotiated with the Town": 23,
    }

    schedule = {}
    adjustments = {}

    for event, offset in events.items():
        raw_date = rfp_posted_date + timedelta(days=offset)
        final_date, adjusted = next_valid_business_day(raw_date, us_holidays)
        schedule[event] = final_date
        adjustments[event] = adjusted

    # --- STEP 2 COUNCIL MEETING AFTER NEGOTIATION ---
    st.markdown("### Step 2: Locate the Next Town Council meeting")
    meetings = fetch_town_council_meetings()
    negotiation_date = schedule["Contract Negotiated with the Town"]

    if meetings:
        next_meeting = next((m for m in meetings if m > negotiation_date), None)
        if next_meeting:
            council_final, council_adjusted = next_valid_business_day(next_meeting, us_holidays)
            schedule["Town Council Approval of Contract"] = council_final
            adjustments["Town Council Approval of Contract"] = council_adjusted
        else:
            st.warning("No upcoming Town Council meetings found after the negotiation date.")
            schedule["Town Council Approval of Contract"] = "Unavailable"
            adjustments["Town Council Approval of Contract"] = False
    else:
        st.warning("Unable to retrieve upcoming Town Council meetings.")
        schedule["Town Council Approval of Contract"] = "Unavailable"
        adjustments["Town Council Approval of Contract"] = False

    # --- STEP 3 OUTPUT FINAL SCHEDULE ---
    st.markdown("### Step 3: Review and Export the Schedule")

    df = pd.DataFrame([
        {
            "Event": event,
            "Date": date.strftime('%B %d, %Y') if isinstance(date, datetime) else date,
            "Note": "Adjusted for holidays and weekends" if adjustments[event] else ""
        }
        for event, date in schedule.items()
    ])

    st.success("RFP schedule generated successfully.")
    st.table(df)

    csv = df.to_csv(index=False)
    st.download_button(
        label="Download Schedule as CSV",
        data=csv,
        file_name="rfp_schedule.csv",
        mime="text/csv"
    )
