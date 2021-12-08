import datetime
import os

import pytz
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/tasks']

creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('/root/cron_jobs/token.json'):
    creds = Credentials.from_authorized_user_file('/root/cron_jobs/token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            '/root/cron_jobs/credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('/root/cron_jobs/token.json', 'w') as token:
        token.write(creds.to_json())

service = build('tasks', 'v1', credentials=creds)

# Call the Tasks API
results = service.tasklists().list(maxResults=10).execute()
lists = results.get('items', [])

# Jeff's list is the first entry
jlist_id = lists[0]['id']

#now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
now_pacific = datetime.datetime.now(pytz.timezone(zone='US/Pacific')).isoformat()
# Annoying... it ignores the timezone apparently, in the sense that it just
# converts it to UTC? So, need to trick it by manually replacing '-07:00' or '-08:00'
# with 'Z'
#print(now_pacific)
now_pacific = now_pacific[:-6] + 'Z'
#print(now_pacific)

tasks_service = service.tasks()
request = tasks_service.insert(tasklist=jlist_id,
                              body={
                                  'title':'Take Buspirone',
                                  'due': now_pacific,
                              })
result = request.execute()
print(result)
