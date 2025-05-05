import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import holidays

# ---- PAGE CONFIG ----
st.set_page_config(page_title="RFP Schedule Generator", layout="centered")

# ---- BRANDING ----
col1, col2, col3, co4, col5 = st.columns(5)
with col3:
    st.image("howey_logo.png", width=150)

st.markdown("<h1 style='text-align: center;'>Town of Howey-in-the-Hills</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #004d7a;'>RFP Schedule Generator</h2>", unsafe_allow_html=True)

# ---- STEP 1: SELECT CALENDAR LENGTH ----
st.markdown("### Select Calendar Length")

calendar_length = st.radio(
    "How long will this RFP be open?",
    options=["2 weeks", "4 weeks"],
    index=0,
    horizontal=True
)

st.markdown("### Add Project Details")

project_title = st.text_input("Enter Project Title")

department = st.selectbox(
    "Select Department",
    ["Public Works", "Administration", "Library", "Parks and Recreation", "Police Department"]
)

# ---- STEP 2: SELECT RFP POSTED DATE ----
st.markdown("### Select the RFP Posted Date")

rfp_posted_date = st.date_input("Select a date")

us_holidays = holidays.US(years=rfp_posted_date.year) if rfp_posted_date else set()

# Block invalid days
if rfp_posted_date:
    if rfp_posted_date.weekday() in [4, 5, 6]:
        st.error("RFPs cannot be posted on Fridays, Saturdays, or Sundays.")
        st.stop()
    elif rfp_posted_date in us_holidays:
        st.error("RFPs cannot be posted on federal holidays.")
        st.stop()

# ---- BUSINESS DAY HELPERS ----
def next_valid_business_day(date_value, holiday_list):
    adjusted = False
    while date_value.weekday() >= 4 or date_value in holiday_list:
        date_value += timedelta(days=1)
        adjusted = True
    return date_value, adjusted

def add_working_days(start_date, working_days_needed, holiday_list):
    date_value = start_date
    days_added = 0
    while days_added < working_days_needed:
        date_value += timedelta(days=1)
        if date_value.weekday() < 4 and date_value not in holiday_list:
            days_added += 1
    return date_value

# ---- MAIN LOGIC ----
if rfp_posted_date:
    proposal_days = 8 if calendar_length == "2 weeks" else 16
    proposal_due_date = add_working_days(rfp_posted_date, proposal_days, us_holidays)

    events = {
        "RFP Posted on Town Website": rfp_posted_date,
        "Questions Due to the Town": add_working_days(rfp_posted_date, 4, us_holidays),
        "Responses to Questions Posted": add_working_days(rfp_posted_date, 6, us_holidays),
        "Proposal Packages Due to the Town": proposal_due_date,
        "Proposal Packages Opened and Evaluated": proposal_due_date,
        "Notice to Award Contract Posted on Town Website": add_working_days(proposal_due_date, 2, us_holidays),
        "Contract Negotiated with Town": add_working_days(proposal_due_date, 5, us_holidays),
    }

    schedule = {}
    adjustments = {}
    today = date.today()

    for event, raw_date in events.items():
        final_date, adjusted = next_valid_business_day(raw_date, us_holidays)
        schedule[event] = final_date
        adjustments[event] = adjusted

    # ---- SELECT AND AUTO-ASSIGN TOWN COUNCIL MEETING ----

    st.markdown("### Select Upcoming Town Council Meeting Dates ")

    st.write("Select up to four upcoming Town Council meetings. The earliest valid meeting date will be used automatically.")

    tc_meeting_1 = st.date_input("Meeting 1", key="tc1")
    tc_meeting_2 = st.date_input("Meeting 2", key="tc2")
    tc_meeting_3 = st.date_input("Meeting 3", key="tc3")
    tc_meeting_4 = st.date_input("Meeting 4", key="tc4")

    tc_dates = [d for d in [tc_meeting_1, tc_meeting_2, tc_meeting_3, tc_meeting_4] if isinstance(d, date)]
    tc_dates = sorted(tc_dates)

    contract_date = schedule["Contract Negotiated with Town"]
    chosen_tc_date = next((d for d in tc_dates if d > contract_date), None)

    if chosen_tc_date:
        schedule["Town Council Approval of Contract"] = chosen_tc_date
        adjustments["Town Council Approval of Contract"] = False
    else:
        schedule["Town Council Approval of Contract"] = "No valid Town Council meeting date available."
        adjustments["Town Council Approval of Contract"] = False

    # ---- BUILD FINAL TABLE ----
    st.markdown("### View and Download the Schedule")

    df = pd.DataFrame([
        {
            "Project": project_title,
            "Department": department,
            "Event": event,
            "Date": (
                event_date.strftime('%B %d, %Y')
                if isinstance(event_date, (datetime, date)) else event_date
            ),
            "Days Left": (
                "Due Today" if event_date == today else
                f"Overdue by {(today - event_date).days} day" if (event_date < today and (today - event_date).days == 1) else
                f"Overdue by {(today - event_date).days} days" if event_date < today else
                f"{(event_date - today).days} days left"
            ) if isinstance (event_date, (datetime, date)) else ""
        }
        for event, event_date in schedule.items()
    ])

    st.table(df)  # No index, all rows shown

    csv = df.to_csv(index=False)
    st.download_button(
        label="Download Schedule as CSV",
        data=csv,
        file_name="rfp_schedule.csv",
        mime="text/csv"
    )

