import imaplib
import email
import pandas as pd
from email.header import decode_header
import smtplib
import logging
import string
from config import *
import time

from msal import PublicClientApplication
from msal import ConfidentialClientApplication
import httpx
from bs4 import BeautifulSoup



class EmailReader:
    """
    Class to read and process emails using IMAP.
    """

    def __init__(self, imap_url=0, Smtp_url=0, port_num=0, email_user=0, email_pass=0, tenantId=0):
        """
        Initialize the EmailReader object.

        Args:
            imap_url (str): IMAP server URL.
            email_user (str): Email username.
            email_pass (str): Email password.
        """
        self.imap_url = imap_url
        self.Smtp_url = Smtp_url
        self.port = port_num
        self.email_user = email_user
        self.email_pass = email_pass
        self.mail = None
        self.tenantId = tenantId
        self.access_token = 0
        self.df = pd.DataFrame(columns=['Email ID', 'Message ID', 'From', 'Subject', 'Body'])

    def connect(self):
        """
        Connect to the IMAP server.
        """
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_url,port=self.port)
            self.mail.debug = 4
            #self.mail=imaplib.IMAP4(self.imap_url,port=self.port)
            #self.mail.starttls()
        except imaplib.IMAP4.error as e:
            logging.error(f"Failed to connect to IMAP server: {e}")
            raise ConnectionError(f"Failed to connect to IMAP server: {e}")

    def login(self):
        """
        Login to the email account.
        """
        try:
            self.mail.login(self.email_user, self.email_pass)
        except imaplib.IMAP4.error as e:
            logging.error(f"Login failed: {e}")
            raise ConnectionError(f"Login failed: {e}")

    def fetch_unseen_emails(self):
        """
        Fetch unseen emails and process them.
        """
        try:
            self.mail.select('inbox')
            status, messages = self.mail.search(None, 'ALL')
            if status == 'OK':
                for num in messages[0].split():
                    status, data = self.mail.fetch(num, '(RFC822)')
                    if status == 'OK':
                        msg = email.message_from_bytes(data[0][1])
                        self.process_email(msg, num)
        except Exception as e:
            logging.error(f"Error fetching emails: {e}")
            raise Exception(f"Error fetching emails: {e}")

    def process_email(self, msg, email_id):
        """
        Process the email and add it to the DataFrame.

        Args:
            msg (email.message.Message): Email message.
            email_id (bytes): Email ID.
        """
        try:
            message_id = msg.get('Message-ID')
            subject = decode_header(msg['subject'])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
            from_ = msg.get('from')
            body = self.get_email_body(msg)
            body = self.extractLatestMsg(body)
            #body = ReadLastEmail.extract_last_reply(msg)
            self.df = self.df._append({'Email ID': email_id.decode(), 'Message ID': message_id, 'From': from_, 'Subject': subject, 'Body': body}, ignore_index=True)
        except Exception as e:
            logging.error(f"Error processing email: {e}")
            raise Exception(f"Error processing email: {e}")

    def extractLatestMsg(self,body):
        Inbody =  (
        body
        .lower()
        .translate(str.maketrans('', '', string.punctuation)).split() 
        )
        foundStr = body;
        for  r in range (len(Inbody)-1):
            if Inbody[r]=="hi" or Inbody[r]=="hello":
                indices = [i for i, item in enumerate(Inbody[r:]) if item == "regards" or item == "thanks"]
                if len (indices) !=0:
                    foundStr = ' '.join(Inbody[r:r+indices[0]])
                    break
        return foundStr       


    def get_email_body(self, msg):
        """
        Get the body of the email.

        Args:
            msg (email.message.Message): Email message.

        Returns:
            str: Email body.
        """
        body = ""
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_maintype() == 'text':
                        body = part.get_payload(decode=True)
                        if body is not None:
                            body = body.decode()
                        break
            else:
                body = msg.get_payload(decode=True)
                if body is not None:
                    body = body.decode()
        except Exception as e:
            logging.error(f"Error getting email body: {e}")
        return body


    def save_emails_to_excel(self, filename):
        """
        Save emails to an Excel file.

        Args:
            filename (str): Name of the Excel file.
        """
        try:
            self.df.to_excel(filename, index=False)
        except Exception as e:
            logging.error(f"Error saving emails to Excel: {e}")
            raise Exception(f"Error saving emails to Excel: {e}")

    def close_connection(self):
        """
        Close the IMAP connection.
        """
        try:
            self.mail.close()
            self.mail.logout()
        except Exception as e:
            logging.error(f"Error closing connection: {e}")
            print(f"Error closing connection: {e}")

    def reply_to_email(self, msg_id, reply_body, port):
        """
        Reply to an email.

        Args:
            msg_id (str): Message ID of the email to reply to.
            reply_body (str): Body of the reply.

        Returns:
            str: Status message.
        """
        try:
            self.mail.select('inbox')
            
            msg_id = msg_id.strip('"').strip()
            result, data = self.mail.search(None, f'(HEADER Message-ID "{msg_id}")')
            if result == 'OK':
                email_ids = data[0].split()
                latest_email_id = email_ids[-1]
                result, data = self.mail.fetch(latest_email_id, '(RFC822)')

                if result == 'OK':
                    raw_email = data[0][1]
                    email_message = email.message_from_bytes(raw_email)
                    result = self.mail.append('Drafts', '', imaplib.Time2Internaldate(time.time()), email_message.as_bytes())
                    reply = email.message.EmailMessage()
                    reply['Subject'] = 'Re: ' + email_message['Subject']
                    reply['To'] = email_message['Reply-To'] or email_message['From']
                    reply['From'] = self.email_user
                    reply.set_content(reply_body)

                    with smtplib.SMTP(self.Smtp_url, port) as smtp:
                        smtp.ehlo()
                        smtp.starttls()
                        smtp.ehlo()
                        smtp.login(self.email_user, self.email_pass)
                        smtp.send_message(reply)
                    return "Reply sent successfully."
                else:
                    return "Failed to fetch the email."
            else:
                return "Email not found."
        except Exception as e:
            logging.error(f"Error in sending email: {e}")
            raise Exception(f"Error in sending email: {e}")

    def move_to_draft(self, msg_id, reply_body):
        try:
            self.mail.select('inbox')
            
            msg_id = msg_id.strip('"').strip()
            result, data = self.mail.search(None, f'(HEADER Message-ID "{msg_id}")')
            if result == 'OK':
                email_ids = data[0].split()
                if len(email_ids) !=0:    #avoid error from moving same email again
                    latest_email_id = email_ids[-1]

                    result = self.mail.copy(latest_email_id, 'Drafts')  # Adjust folder name if needed
                    if result[0] == 'OK':
                    # Mark the original message for deletion
                        self.mail.store(latest_email_id, '+FLAGS', '\\Deleted')


                '''
                result, data = self.mail.fetch(latest_email_id, '(RFC822)')

            status, folders = self.mail.list()
            if status == 'OK':
                for folder in folders:
                    print(folder.decode())

                if result == 'OK':
                    raw_email = data[0][1]
                    email_message = email.message_from_bytes(raw_email)
                    result = self.mail.append('\Spam', '', imaplib.Time2Internaldate(time.time()), email_message.as_bytes())
                    if result =='OK':
                        return "Moved to Drafts successfully."
                    else: 
                        return "Failed to move to Drafts."
                else:
                    return "Failed to Moved to Drafts "
            else:
                return "Email not found."
            '''
        except Exception as e:
            logging.error(f"Error in sending email: {e}")
            raise Exception(f"Error in sending email: {e}")




    def get_access_token2(self):
        AUTHORITY = f"https://login.microsoftonline.com/{self.tenantId}"
        SCO = ["https://graph.microsoft.com/.default"]

        app = PublicClientApplication(client_id="74885322-da4b-4a93-8c88-cc15a0080a7c", authority=AUTHORITY)
        result = app.acquire_token_interactive(scopes=SCO)
        self.access_token = result["access_token"]
 
        return self.access_token



    def read_from_outlook(self):
        MS_GRAPH_BASE_URL = 'https://graph.microsoft.com/v1.0'
        scopes= ['User.Read', 'Mail.ReadWrite', 'Mail.Send']

        endpoint = f'{MS_GRAPH_BASE_URL}/me/mailFolders/Inbox/messages'
        access_token = self.get_access_token2()
        headers = {
        'Authorization': 'Bearer ' + access_token
        }

        try:
            for i in range(0, 4, 2):
                params = {
                    '$top': 2,
                    '$select': '*',
                    '$skip': i,
                    '$orderby': 'receivedDateTime desc'
            }

                response = httpx.get(endpoint, headers=headers, params=params)
                if response.status_code != 200:
                    raise Exception(f'Failed to retrieve emails: {response.text}')

                json_response = response.json()           

                for mail_message in json_response.get('value', []):        
                    message_id = mail_message.get('id')
                    subject    =  mail_message.get('subject')
                    from_ =  mail_message.get('from')                   
                    body = mail_message.get('bodyPreview')
                    body = self.extractLatestMsg(body)
                    self.df = self.df._append({'Email ID': 0, 'Message ID': message_id, 'From': from_, 'Subject': subject, 'Body': body}, ignore_index=True)

        except httpx.HTTPStatusError as e:
            print(f'HTTP Error: {e}')
        except Exception as e:
            print(f'Error: {e}')

    def reply_toOutlook_message(self, messageId, reply_body):
        """
        read unique message ID from outlook emails.
        """
        try:
            if self.access_token: 
                headers = { "Authorization": f"Bearer {self.access_token}"  }
                response = httpx.get(f"https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages/{messageId}",  headers=headers)
                if response.status_code == 200:
                    message = response.json()

                    from_field = message.get("from", {})
                    email_address = from_field.get("emailAddress", {}).get("address")

                    html_content = message.get("body", {}).get("content", "")
                    soup = BeautifulSoup(html_content, "html.parser")
                    body_content = reply_body + "\n" + soup.get_text()
                    
                    email_payload = {
                        "message": {
                            "subject":message['subject'],
                            "body": {
                                "contentType": "Text",
                                "content": f'{ body_content }'
                            },
                            "toRecipients": [
                                {
                                    "emailAddress": {
                                        "address": email_address
                                    }
                                }
                            ]
                        },
                        "saveToSentItems": "true"
                     }

                    response = httpx.post(
                        "https://graph.microsoft.com/v1.0/me/sendMail",
                        headers=headers,
                        json=email_payload
                     )
                    if response == 202:
                        return "Email sent successfully."
                    else:
                        return "Failed to send email"

            else:
                raise  Exception(f'No access token found')


        except httpx.HTTPStatusError as e:
            print(f'HTTP Error: {e}')
        except Exception as e:
            print(f'Error: {e}')
       

