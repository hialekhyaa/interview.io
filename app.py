from flask import Flask, render_template
import datetime

app = Flask(__name__)

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import datetime

# Retrieve webpage content for interviewers
#small sample
#url_interviewers = "https://www.when2meet.com/?24576433-vNsHV"
#fruit sample
url_interviewers = "https://www.when2meet.com/?24863045-6oyD6"
response_interviewers = requests.get(url_interviewers)
html_content_interviewers = response_interviewers.text

# Retrieve webpage content for interviewees
#small sample
#url_interviewees = "https://www.when2meet.com/?24575881-VeoMM"
#vegetation sample
url_interviewees = "https://www.when2meet.com/?24863077-EewSK"
response_interviewees = requests.get(url_interviewees)
html_content_interviewees = response_interviewees.text

# Parse HTML content for interviewers
soup_interviewers = BeautifulSoup(html_content_interviewers, 'html.parser')

# Parse HTML content for interviewees
soup_interviewees = BeautifulSoup(html_content_interviewees, 'html.parser')

# Define function to extract data using regex
def extract_data(regex, script):
    matches = re.findall(regex, script)
    return matches

# Find script containing relevant data for interviewers
script_tag_interviewers = soup_interviewers.find("script", string=lambda text: text and 'PeopleNames' in text)
if script_tag_interviewers:
    script_interviewers = script_tag_interviewers.string

    # Extract slots data for interviewers
    slots_regex_interviewers = r"TimeOfSlot\[(\d+)\]=(\d+);"
    slots_data_interviewers = extract_data(slots_regex_interviewers, script_interviewers)

    # Extract users data for interviewers
    users_regex_interviewers = r"PeopleNames\[(\d+)\] = '([^']+)';PeopleIDs\[\d+\] = (\d+);"
    users_data_interviewers = extract_data(users_regex_interviewers, script_interviewers)

    # Extract availability data for interviewers
    avails_regex_interviewers = r"AvailableAtSlot\[(\d+)].push\((\d+)\);"
    avails_data_interviewers = extract_data(avails_regex_interviewers, script_interviewers)

    slots_df_interviewers = pd.DataFrame(slots_data_interviewers, columns=['slot_id', 'time_of_slot'])
    #print("slots interviewers:")
    #print(slots_df_interviewers)
    users_df_interviewers = pd.DataFrame(users_data_interviewers, columns=['user_id', 'user_name', 'user_id_num'])
    #print("users interviewers:")
    #print(users_df_interviewers)
    avails_df_interviewers = pd.DataFrame(avails_data_interviewers, columns=['slot_id', 'user_id_num'])
    #print("avails interviewers:")
    #print(avails_df_interviewers)

# Find script containing relevant data for interviewees
script_tag_interviewees = soup_interviewees.find("script", string=lambda text: text and 'PeopleNames' in text)
if script_tag_interviewees:
    script_interviewees = script_tag_interviewees.string

    # Extract slots data for interviewees
    slots_regex_interviewees = r"TimeOfSlot\[(\d+)\]=(\d+);"
    slots_data_interviewees = extract_data(slots_regex_interviewees, script_interviewees)

    # Extract users data for interviewees
    users_regex_interviewees = r"PeopleNames\[(\d+)\] = '([^']+)';PeopleIDs\[\d+\] = (\d+);"
    users_data_interviewees = extract_data(users_regex_interviewees, script_interviewees)

    # Extract availability data for interviewees
    avails_regex_interviewees = r"AvailableAtSlot\[(\d+)].push\((\d+)\);"
    avails_data_interviewees = extract_data(avails_regex_interviewees, script_interviewees)

    slots_df_interviewees = pd.DataFrame(slots_data_interviewees, columns=['slot_id', 'time_of_slot'])
    #print("slots interviewees:")
    #print(slots_df_interviewees)
    users_df_interviewees = pd.DataFrame(users_data_interviewees, columns=['user_id', 'user_name', 'user_id_num'])
    #print("users interviewees:")
    #print(users_df_interviewees)
    avails_df_interviewees = pd.DataFrame(avails_data_interviewees, columns=['slot_id', 'user_id_num'])
    #print("avails interviewees:")
    #print(avails_df_interviewees)

# Merge data for interviewers
availability_df_interviewers = pd.merge(avails_df_interviewers, users_df_interviewers, on='user_id_num')
availability_df_interviewers = pd.merge(availability_df_interviewers, slots_df_interviewers, on='slot_id')

# Merge data for interviewees
availability_df_interviewees = pd.merge(avails_df_interviewees, users_df_interviewees, on='user_id_num')
availability_df_interviewees = pd.merge(availability_df_interviewees, slots_df_interviewees, on='slot_id')

#print("Availability DataFrame for Interviewers:")
#print(availability_df_interviewers)

#print("\nAvailability DataFrame for Interviewees:")
#print(availability_df_interviewees)

# Find common available time slots between interviewers and interviewees
common_available_slots = pd.merge(availability_df_interviewers, availability_df_interviewees, on='time_of_slot')

# Display common available time slots
#print("Common Available Time Slots:")
#print(common_available_slots[['user_name_x', 'user_name_y', 'time_of_slot']])

common_available_slots_sorted = common_available_slots.sort_values(by='time_of_slot')
#print("Common Available Time Slots (Sorted):")
#print(common_available_slots_sorted[['user_name_x', 'user_name_y', 'time_of_slot']])

# ASSIGNMENT #

# Create dictionaries to store assignments and time slots
assignments = {}
time_slots = {}

# Track the number of interviewees each interviewer has been assigned
interviewer_counts = {}

# Track the interviewees already assigned to each interviewer
assigned_interviewees = {}

# Track the interviewers already assigned to each interviewee
assigned_interviewers = {}

assigned_slots = {}

# Iterate over each row in the sorted common available slots dataframe
for index, row in common_available_slots_sorted.iterrows():
    interviewer = row['user_name_x']
    interviewee = row['user_name_y']
    time_slot = row['time_of_slot']

    # Check if the interviewer can still be assigned more interviewees
    if interviewer not in interviewer_counts or interviewer_counts[interviewer] < 2:
        # Check if the interviewer is available at this time slot
        if time_slot not in assigned_slots.get(interviewer, []):
            # Check if the interviewee has not been assigned to another interviewer already
            if interviewee not in assigned_interviewers:
                # Assign interviewee to the interviewer
                assignments.setdefault(interviewer, []).append((interviewee, time_slot))
                # Increment the count of interviewees assigned to this interviewer
                interviewer_counts[interviewer] = interviewer_counts.get(interviewer, 0) + 1
                # Track the assigned interviewee for this interviewer
                assigned_interviewees[interviewee] = interviewer
                # Track the assigned interviewer for this interviewee
                assigned_interviewers[interviewee] = interviewer
                # Mark this time slot as assigned to the interviewer
                assigned_slots.setdefault(interviewer, []).append(time_slot)

def convert_epoch_to_datetime(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time)

# Print the assignments with time slots
print("Interview Assignments:")
for interviewer, interviewee_slots in assignments.items():
    for interviewee, time_slot in interviewee_slots:
        # Convert epoch time to readable format
        time_slot_readable = convert_epoch_to_datetime(int(time_slot))
        print(f"{interviewer} will interview {interviewee} at time {time_slot_readable}.")


@app.route('/')
def index():
    # Prepare data to pass to the template
    interview_assignments = []
    for interviewer, interviewee_slots in assignments.items():
        for interviewee, time_slot in interviewee_slots:
            time_slot_readable = convert_epoch_to_datetime(int(time_slot))
            interview_assignments.append({
                'interviewer': interviewer,
                'interviewee': interviewee,
                'time_slot': time_slot_readable
            })
    return render_template('index.html', interview_assignments=interview_assignments)

if __name__ == '__main__':
    app.run(debug=True)