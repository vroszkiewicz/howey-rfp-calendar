import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from calendar import monthcalendar, MONDAY
import holidays

# ---- PAGE SETUP ----
st.set_page_config(page_title="RFP Calendar Generator", layout="centered")

# ---- BRANDING ----
st.markdown("<h1 style='text-align: center;'>Town of Howey-in-the-Hills</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #004d7a;'>Public Works – RFP Schedule Generator</h2>", unsafe_allow_html=True)
st.write("This tool generates an RFP schedule, skipping holidays and weekends, and includes the next Town Council meeting based on the 2nd or 4th Monday rule.")

# ---- STEP 1: USER SELECTS RFP POSTED DATE ----
st.markdown("### Step 1: Enter the RFP Posted Date")
rfp_posted_date = st.date_input("RFP Posted Date")

# ---- SET HOLIDAYS ----
if rfp_posted_date:
    us_holidays = holidays.US(years=rfp_posted_date.year)
else:
    us_holidays = set()

# ---- FUNCTION: SKIP TO NEXT VALID BUSINESS DAY ----
def next_valid_business_day(date, holiday_list):
    adjusted = False
    while date.weekday() >= 4 or date in holiday_list:
        date += timedelta(days=1)
        adjusted = True
    return date, adjusted

# ---- FUNCTION: FIND NEXT 2ND OR 4TH MONDAY ----
def get_next_2nd_or_4th_monday(after_date):
    if isinstance(after_date, datetime.date) and not isinstance(after_date, datetime):
        after_date = datetime.combine(after_date, datetime.min.time())

    year = after_date.year
    month = after_date.month

    while True:
        cal = monthcalendar(year, month)
        mondays = [week[MONDAY] for week in cal if week[MONDAY] != 0]

        possible_meetings = []
        if len(mondays) >= 2:
            possible_meetings.append(datetime(year, month, mondays[1]))
        if len(mondays) >= 4:
            possible_meetings.append(datetime(year, month, mondays[3]))

        for meeting in sorted(possible_meetings):
            if meeting > after_date:
                return meeting

        month += 1
        if month > 12:
            month = 1
            year += 1

# ---- MAIN LOGIC ----
if rfp_posted_date:
    # RFP timeline events and day offsets
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

    # ---- STEP 2: DETERMINE NEXT COUNCIL MEETING ----
    from datetime import datetime
    from calendar import monthcalendar, MONDAY

    def get_closest_2nd_or_4th_monday(rfp_posted_date):
        # Determines the closest valid council meeting date (2nd or 4th Monday) after the given RFP posted date.
        # Returns (1) a label of "Second Monday" or "Fourth Monday"; (2) datetime object of the selected Monday

        year = rfp_posted_date.year
        month = rfp_posted_date.month
        cal = monthcalendar(year, month)

    # Get all Mondays in the month
    mondays = [week[MONDAY] for week in cal if week[MONDAY] != 0]

    # Grad 2nd and 4th Monday if they exist
    second_monday = datetime(year, month, mondays[1]) if len(mondays) >= 2 else None
    fourth_monday = datetime(year, month, mondays[3]) if len(mondays) >= 4 else None

     # Store options that are after RFP date
    valid_options = []
    if second_monday and second_monday > rfp_posted_date:
        valid_options.append(("Second Monday", second_monday))
    if fourth_monday and fourth_monday > rfp_posted_date:
        valid_options.append(("Fourth Monday", fourth_monday))

    def choose_closest_valid_option(valid_options, rfp_posted_date):
    # Return the closest valid option
    if valid_options:
        return min(valid_options, key=lambda x: (x[1] - rfp_posted_date).days)
    else:
        return None, None

    # ---- STEP 3: SHOW FINAL SCHEDULE ----
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

    csv = df.to_csv(index=False)
    st.download_button(
        label="Download Schedule as CSV",
        data=csv,
        file_name="rfp_schedule.csv",
        mime="text/csv"
    )

else:
    st.info("Please select the RFP Posted Date above to begin.")
