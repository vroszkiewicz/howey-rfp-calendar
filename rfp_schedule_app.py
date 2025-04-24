# ---- LIBRARIES ----
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from calendar import monthcalendar, MONDAY
import holidays

# ---- PAGE SETUP ----
st.set_page_config(page_title="RFP Calendar Generator", layout="centered")

# ---- HEADER AND BRANDING ----
st.markdown("<h1 style='text-align: center;'>Town of Howey-in-the-Hills</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #004d7a;'>RFP Schedule Generator</h2>", unsafe_allow_html=True)
st.write("This tool generates an RFP schedule, skipping holidays and weekends, and includes the next Town Council meeting.")

# ---- STEP 1: RFP DATE INPUT ----
st.markdown("### Step 1: Enter the RFP Posted Date")
rfp_posted_date = st.date_input("RFP Posted Date")

# ---- HOLIDAY SETUP ----
if rfp_posted_date:
    us_holidays = holidays.US(years=rfp_posted_date.year)
else:
    us_holidays = set()

# ---- FUNCTION: NEXT VALID BUSINESS DAY ----
def next_valid_business_day(date, holiday_list):
    adjusted = False
    while date.weekday() >= 4 or date in holiday_list:
        date += timedelta(days=1)
        adjusted = True
    return date, adjusted

# ---- FUNCTION: GET 2ND AND 4TH MONDAYS ----
def get_recurring_mondays(start_date, months=12):
    """
    Returns a list of 2nd and 4th Mondays starting after the given date.
    """
    results = []
    year = start_date.year
    month = start_date.month

    for _ in range(months):
        cal = monthcalendar(year, month)
        mondays = [week[MONDAY] for week in cal if week[MONDAY] != 0]

        if len(mondays) >= 2:
            second_monday = datetime(year, month, mondays[1])
            if second_monday > start_date:
                results.append(second_monday)
        if len(mondays) >= 4:
            fourth_monday = datetime(year, month, mondays[3])
            if fourth_monday > start_date:
                results.append(fourth_monday)

        # Move to next month
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1

    return results

# ---- MAIN LOGIC ----
if rfp_posted_date:
    # Define RFP event schedule
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

    # Calculate each event's date
    for event, offset in events.items():
        raw_date = rfp_posted_date + timedelta(days=offset)
        final_date, adjusted = next_valid_business_day(raw_date, us_holidays)
        schedule[event] = final_date
        adjustments[event] = adjusted

    # ---- COUNCIL MEETING SELECTION ----
    st.markdown("### Step 2: Locate the Next Town Council Meeting")

    negotiation_date = schedule["Contract Negotiated with Town"]
    meetings = get_recurring_mondays(start_date=negotiation_date)

    if meetings:
        next_meeting = next((m for m in meetings if m > negotiation_date), None)
        if next_meeting:
            council_final, council_adjusted = next_valid_business_day(next_meeting, us_holidays)
            schedule["Town Council Approval of Contract"] = council_final
            adjustments["Town Council Approval of Contract"] = council_adjusted
        else:
            st.warning("No Town Council meeting found after contract negotiation.")
            schedule["Town Council Approval of Contract"] = "Not found"
            adjustments["Town Council Approval of Contract"] = False
    else:
        st.warning("Could not generate Town Council meeting dates.")
        schedule["Town Council Approval of Contract"] = "Unavailable"
        adjustments["Town Council Approval of Contract"] = False

    # ---- DISPLAY FINAL SCHEDULE ----
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
