#-pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

import base64
import csv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def gmail_credentials():
    # Set up OAuth2 credentials
    try:
        creds = Credentials.from_authorized_user_file('token.json')
    except FileNotFoundError:
        #-- token.json does NOT exist --#
        #-- generate token by authorizing via browser (1st time only, I hope so :D) --#
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json',  #credentials JSON file
            ['https://www.googleapis.com/auth/gmail.send']
            )
        creds = flow.run_local_server(port=0)

    #-- token.json exists --#    
    if creds and creds.valid:
        pass
    elif creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    # Save the credentials for future use
    with open('token.json', 'w') as token_file:
        token_file.write(creds.to_json())

    #creds = Credentials.from_authorized_user_file('token.json')
    
    # Build the Gmail service
    
    return creds

def gmail_compose(mail_subject, email_recipient, mail_body):
    message = {
        'raw': base64.urlsafe_b64encode(
            f'MIME-Version: 1.0\n'
            f'Content-Type: text/html; charset="UTF-8"\n'
            f"To: {email_recipient}\n"
            f"Subject: {mail_subject}\n\n"
            f"{mail_body}"
            .encode("utf-8")
        ).decode("utf-8")
    }
    return message


def gmail_send(creds, message):
# Send the email
    service = build('gmail', 'v1', credentials=creds)
    try:
        service.users().messages().send(userId='me', body=message).execute()
        print('Email sent successfully.')
    except Exception as e:
        print('An error occurred while sending the email:', str(e))
        
if __name__ == "__main__":
    
    #-Mail Subject-#
    mail_subject = "[itbaseTV Newsletter] Traditional IPSec vs. SDWAN"

    #-Build HTML content in single line with "space" as separater-#
    mail_body = open('content.html', 'r').read()
    mail_body = mail_body.replace('\n',' ') 

    #--create mail services--#
    creds = gmail_credentials() 

    #--Read line by line in csv, each line includes one user's mail address, and send mail to them.--#
    with open('user_mail_lists.csv', 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for user in reader:
           email_recipient = user['user_email']
           #SEND MAIL#            
           mail_content = gmail_compose(mail_subject, email_recipient, mail_body)
           gmail_send(creds, mail_content)
           

##############
## OPTIONAL ##
##############
#-- You can use below block for multiple threads send mail to optimize the process in case you have--#
#-- the long list of users --#
import time
import concurrent.futures #for multi threads

    with open('user_mail_lists.csv', 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            recipients = [user['user_email'] for user in reader]

        # Create a thread pool executor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for recipient in recipients:
            # Compose the email
            mail_content = gmail_compose(mail_subject, recipient, mail_body)
            # Submit the email sending task to the executor
            future = executor.submit(gmail_send, creds, mail_content)
            futures.append(future)
            time.sleep(1) #some limitation of Google API, could not send a lot of email in short time.

        # Wait for all tasks to complete
        concurrent.futures.wait(futures)
