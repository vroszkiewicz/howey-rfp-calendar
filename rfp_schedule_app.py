import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import holidays
from calendar import monthcalendar, MONDAY

# ---- PAGE CONFIG ----
st.set_page_config(page_title="RFP Calendar Generator", layout="centered")

# ---- HEADER / BRANDING ----
st.markdown("<h1 style='text-align: center;'>Town of Howey-in-the-Hills</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #004d7a;'>RFP Schedule Generator</h2>", unsafe_allow_html=True)
st.write("This tool generates an RFP schedule, skipping holidays and weekends. The Town Council meeting date must be verified manually.")

# ---- LOGO ----
st.image("howey_logo.png", width=150) 
st.markdown(
    "<div style='text-align: center'><img src='howey_logo.png" width='150'><div>",
    unsafe_allow_html=True
)

# ---- STEP 1: INPUT DATE ----
st.markdown("### Step 1: Enter the RFP Posted Date")
rfp_posted_date = st.date_input("RFP Posted Date")

# ---- HOLIDAYS ----
if rfp_posted_date:
    us_holidays = holidays.US(years=rfp_posted_date.year)
else:
    us_holidays = set()

# ---- BUSINESS DAY ADJUSTER ----
def next_valid_business_day(date, holiday_list):
    adjusted = False
    while date.weekday() >= 4 or date in holiday_list:  # Skip Friday–Sunday and holidays
        date += timedelta(days=1)
        adjusted = True
    return date, adjusted

# ---- MAIN LOGIC ----
if rfp_posted_date:
    # Event schedule and day offsets
    events = {
        "RFP Posted on Town Website": 0,
        "Questions Due to the Town": 7,
        "Responses to Questions Posted": 9,
        "Proposal Packages Due to the Town": 16,
        "Proposal Packages Opened and Evaluated": 16,
        "Notice to Award Contract Posted on Town Website": 20,
        "Contract Negotiated with Town": 23,
    }

    schedule = {}
    adjustments = {}

    for event, offset in events.items():
        raw_date = rfp_posted_date + timedelta(days=offset)
        final_date, adjusted = next_valid_business_day(raw_date, us_holidays)
        schedule[event] = final_date
        adjustments[event] = adjusted

    # ---- STEP 2: TOWN COUNCIL MANUAL PLACEHOLDER ----
    st.markdown("### Step 2: Confirm Town Council Meeting Manually")

    schedule["Town Council Approval of Contract"] = "Next Town Council Meeting (please verify manually)"
    adjustments["Town Council Approval of Contract"] = False

    # ---- STEP 3: OUTPUT TABLE ----
    st.markdown("### Step 3: Review and Export the Schedule")

    df = pd.DataFrame([
        {
            "Event": event,
            "Date": date.strftime('%B %d, %Y') if isinstance(date, datetime) else date,
            "Note": "Adjusted for holiday/weekend" if adjustments[event] else ""
        }
        for event, date in schedule.items()
    ])

    st.success("RFP schedule generated successfully.")
    st.table(df)

    # ---- DOWNLOAD BUTTON ----
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download Schedule as CSV",
        data=csv,
        file_name="rfp_schedule.csv",
        mime="text/csv"
    )

else:
    st.info("Please select the RFP Posted Date above to begin.")
