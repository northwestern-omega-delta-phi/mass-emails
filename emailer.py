from __future__ import print_function
import pickle
import os.path
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
import time

sender_email = 'odphistep@gmail.com'

chapter_html = open('./chapter.html', 'r')
council_html = open('./council.html', 'r')

# change test to contacts once we want to actually send the emails out
with open('test.json') as json_file:  
    contacts = json.load(json_file)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://mail.google.com/']

def create_message(sender, to, subject, message_text):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText(message_text, 'html')
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject

  print("Sent to ", to)

  return {'raw': base64.urlsafe_b64encode(message.as_string())}


def send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    print ('Message Id: %s' % message['id'])
    return message
  except HttpError as error:
    print ('An error occurred: %s' % error)

def main():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.pickle stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
      creds = pickle.load(token)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
      creds = flow.run_local_server()
      # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
      pickle.dump(creds, token)

  service = build('gmail', 'v1', credentials=creds)

  
  # FOR INDIVIDUAL CHAPTERS
  chapter_email = chapter_html.read()
  for chapter in contacts['orgs']:
    intro = '<html lang=\"en\"> <body> <p>Dear '
    if chapter['type'] == 'f':
      intro += 'Brothers of '
    elif chapter['type'] == 's':
      intro += 'Sisters of '
    else:
      intro += 'Members of '
    intro += chapter['org'] + ',</p>'

    contents = intro + chapter_email + "</body> </html>"

    email = create_message(sender_email, chapter['address1'], 'Stroll the Yard Competition', contents)
    # send_message(service, "me", email)
    if chapter['address2'] != "N/A":
      time.sleep(2)
      email = create_message(sender_email, chapter['address2'], 'Stroll the Yard Competition', contents)
      # send_message(service, "me", email)
    time.sleep(2)

  # FOR COUNCILS
  council_email = council_html.read()
  for council in contacts['councils']:
    intro = '<html lang=\"en\"> <body> <p>Dear Members of ' + council['org'] + ",</p>"

    contents = intro + council_email + "</body> </html>"

    email = create_message(sender_email, council['address1'], 'Stroll the Yard Competition', contents)
    send_message(service, "me", email)

    if council['address2'] != "N/A":
      time.sleep(2)
      email = create_message(sender_email, council['address2'], 'Stroll the Yard Competition', contents)
      send_message(service, "me", email)
    time.sleep(2)
    
  # intro = "<html lang=\"en\"> <body> <p> Hello Gabe, </p> "
  # contents = council_html.read() + "</body> </html>"
  # contents = intro + contents

  # email = create_message('odphistep@gmail.com', 'rojaswestall@gmail.com', 'Stroll the Yard Competition', contents)
  # send_message(service, "me", email)

if __name__ == '__main__':
  main()