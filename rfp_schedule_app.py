import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from datetime import date
import holidays

# ---- PAGE CONFIG ----
st.set_page_config(page_title="RFP Schedule Generator", layout="centered")

# ---- BRANDING ----
col1, col2, col3 = st.columns(3)
with col2:
    st.image("howey_logo.png", width=150)

st.markdown("<h1 style='text-align: center;'>Town of Howey-in-the-Hills</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #004d7a;'>RFP Schedule Generator</h2>", unsafe_allow_html=True)
st.write("Enter your RFP timeline below. We’ll calculate all key dates and skip holidays and weekends.")

# ---- STEP 1: SELECT CALENDAR LENGTH ----
st.markdown("### 1. Select Calendar Length")

calendar_length = st.radio(
    "How long will this RFP be open?",
    options=["2 weeks", "4 weeks"],
    index=0,
    horizontal=True
)

# ---- STEP 2: SELECT RFP POSTED DATE ----
st.markdown("### 2. Select the RFP Posted Date")

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
def next_valid_business_day(date, holiday_list):
    adjusted = False
    while date.weekday() >= 4 or date in holiday_list:
        date += timedelta(days=1)
        adjusted = True
    return date, adjusted

def add_working_days(start_date, working_days_needed, holiday_list):
    date = start_date
    days_added = 0
    while days_added < working_days_needed:
        date += timedelta(days=1)
        if date.weekday() < 4 and date not in holiday_list:
            days_added += 1
    return date

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
    days_remaining = {}

    today = datetime.today().date()

    for event, raw_date in events.items():
        final_date, adjusted = next_valid_business_day(raw_date, us_holidays)
        schedule[event] = final_date
        if isinstance(final_date, datetime):
            days_remaining[event] = (final_date.date() - today).days
        else:
            days_remaining[event] = ""

    from datetime import datetime, date

    today = date.today()

    df = pd.DataFrame([
        {
            "Event": event,
            "Date": (
                event_date.strftime('%B %d, %Y')
                if isinstance(event_date, (datetime, date))
                else event_date
            ),
            "Days Left": (
                "Due Today" if event_date == today else
                f"Overdue by {(today - event_date).days} days" if event_date < today else
                f"{(event_date - today).days} days left"
            ) if isinstance(event_date, (datetime, date)) else ""
        }
        for event, event_date in schedule.items()
    ])
    
    # ---- MANUAL TOWN COUNCIL APPROVAL ----
    st.markdown("### 3. Town Council Approval")
    st.write("Add the next Town Council meeting manually when finalizing the schedule.")

    schedule["Town Council Approval of Contract"] = "Next Town Council Meeting (please verify manually)"
    adjustments["Town Council Approval of Contract"] = False
    days_remaining["Town Council Approval of Contract"] = ""

    # ---- FINAL SCHEDULE TABLE ----
    st.markdown("### 4. View and Download the Schedule")

    
            

    # ---- DISPLAY TABLE ----
    st.dataframe(df.set_index("Event"), use_container_width=True)
    
    # ---- CSV DOWNLOAD ----
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download Schedule as CSV",
        data=csv,
        file_name="rfp_schedule.csv",
        mime="text/csv"
    )

else:
    st.info("Please select the RFP Posted Date to begin.")
