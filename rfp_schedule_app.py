import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import holidays

# ---- PAGE CONFIG ----
st.set_page_config(page_title="RFP Schedule Generator", layout="centered")

# ---- BRANDING ----
st.markdown("<h1 style='text-align: center;'>Town of Howey-in-the-Hills</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #004d7a;'>RFP Schedule Generator</h2>", unsafe_allow_html=True)
st.write("Enter the date your RFP was posted. We’ll calculate all key dates into one downloadable file.")

# ---- STEP 1: SELECT CALENDAR LENGTH ----
st.markdown("### Step 1: Select the length of the calendar")

calendar_length = st.radio(
    "How long will this RFP be open?",
    options=["2 weeks", "4 weeks"],
    index=0,
    horizontal=True
)

# ---- STEP 2: SELECT RFP POSTED DATE ----
st.markdown("### Step 2: Select the date the RFP was posted")

rfp_posted_date = st.date_input("Select a date")

# Load U.S. holidays for the correct year
us_holidays = holidays.US(years=rfp_posted_date.year) if rfp_posted_date else set()

# Block invalid RFP dates
if rfp_posted_date:
    if rfp_posted_date.weekday() in [4, 5, 6]:
        st.error("RFPs cannot be posted on Fridays, Saturdays, or Sundays.")
        st.stop()
    elif rfp_posted_date in us_holidays:
        st.error("RFPs cannot be posted on holidays.")
        st.stop()

# ---- BUSINESS DAY FUNCTIONS ----

def next_valid_business_day(date, holiday_list):
    """
    Adjusts forward to the next Monday–Thursday that is not a holiday.
    """
    adjusted = False
    while date.weekday() >= 4 or date in holiday_list:
        date += timedelta(days=1)
        adjusted = True
    return date, adjusted

def add_working_days(start_date, working_days_needed, holiday_list):
    """
    Adds a specific number of working days (Mon–Thurs, skips holidays).
    """
    date = start_date
    days_added = 0

    while days_added < working_days_needed:
        date += timedelta(days=1)
        if date.weekday() < 4 and date not in holiday_list:
            days_added += 1

    return date

# ---- MAIN LOGIC ----
if rfp_posted_date:
    # Determine working days needed based on calendar choice
    if calendar_length == "2 weeks":
        proposal_due_days = 8  # 8 working days
    else:
        proposal_due_days = 16  # 16 working days

    # Calculate Proposal Due Date
    proposal_due_date = add_working_days(rfp_posted_date, proposal_due_days, us_holidays)

    # Build the full schedule
    events = {
        "RFP Posted on Town Website": rfp_posted_date,
        "Questions Due to the Town": add_working_days(rfp_posted_date, 4, us_holidays),  # Midpoint for questions
        "Responses to Questions Posted": add_working_days(rfp_posted_date, 6, us_holidays),
        "Proposal Packages Due to the Town": proposal_due_date,
        "Proposal Packages Opened and Evaluated": proposal_due_date,
        "Notice to Award Contract Posted on Town Website": add_working_days(proposal_due_date, 2, us_holidays),
        "Contract Negotiated with Town": add_working_days(proposal_due_date, 5, us_holidays),
    }

    schedule = {}
    adjustments = {}

    for event, event_date in events.items():
        final_date, adjusted = next_valid_business_day(event_date, us_holidays)
        schedule[event] = final_date
        adjustments[event] = adjusted

    # ---- MANUAL TOWN COUNCIL APPROVAL ----
    st.markdown("### Step 3: Approval by Town Council")
    st.write("Add the next Town Council meeting manually when finalizing the schedule.")

    schedule["Town Council Approval of Contract"] = "Next Town Council Meeting (please verify manually)"
    adjustments["Town Council Approval of Contract"] = False

    # ---- STEP 4: OUTPUT THE TABLE ----
    st.markdown("### Step 4: View and download your schedule")

    df = pd.DataFrame([
        {
            "Event": event,
            "Date": date.strftime('%B %d, %Y') if isinstance(date, datetime) else date,
            "Flag": "Adjusted for holiday/weekend" if adjustments[event] else ""
        }
        for event, date in schedule.items()
    ])

    st.success("RFP schedule generated successfully!")
    st.table(df)

    csv = df.to_csv(index=False)
    st.download_button(
        label="Download Schedule as CSV",
        data=csv,
        file_name="rfp_schedule.csv",
        mime="text/csv"
    )

else:
    st.info("Please select the RFP Posted Date to begin.")
