# RFP Schedule Generator
** Town of Howey-in-the-Hills **

This tool automates the generation of a compliant Request for Proposal (RFP) calendar based on the RFP posting date and the selected calendar length (2 weeks or 4 weeks). It accounts for non-working days (Fridays, weekends), skips U.S. federal holidays, and provides a clear downloadable schedule for staff use.


---

## Features

- Choose between **2- week** or **4-week** RFP open periods
- Automatically adjusts for:
 - **Fridays** (Town Hall closed)
 - **Weekends** 
 - **Federal holidays**
- Dynamic calculation of all key RFP events
- Table view of all milestones
- Downloadable schedule as a **CSV file**
- Clean, user-friendly interface

---

## How to Use

### Step 1: Choose calendar length
- Select either **2 weeks** or **4 weeks** for how long the RFP should remain open.

### Step 2: Select RFP posted date
- Choose the date the RFP will be posted.
- Fridays, Saturdays, Sundays, and federal holidays are automatically blocked.

### Step 3: Town Council meeting
- The final approval step ("Town Council Approval of Contract") must be manually verified and added after generating the initial schedule.

### Step 4: Review and download
- View the automatically generated schedule.
- Download the full schedule as a **CSV file** for records or reporting.

---

## File Structure

File Name : Purpose

`rfp_schedule_app.py` : Main application script (Streamlit web app)
`requirements.txt` : Python library dependencies
`howey_logo.png` : Town logo displayed in the app
`README.md` : This documentation

---

## Requirements

- Python 3.8+
- Required Python libraries:
``` text
streamlit
pandas
holidays