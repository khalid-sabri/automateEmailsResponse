from matplotlib import category
import gradio as gr
import pandas as pd
from .email_reader import EmailReader
#from langchain.vectorstores import Chroma
#from langchain_community.vectorstores import Chroma
#  old   from langchain.vectorstores import Chroma
#from langchain_community.embeddings import HuggingFaceEmbeddings
#old    from langchain_huggingface import HuggingFaceEmbeddings
#from langchain_core.output_parsers import StrOutputParser
#from langchain_core.prompts import ChatPromptTemplate
#from langchain_core.runnables import  RunnablePassthrough
import datetime
import os
#from langchain_community.chat_models import ChatOllama
from config import *
#from transformers import pipeline
import logging
import re
from openai import OpenAI
#import openai
import json
import string
import requests



# Initialize zero-shot classification model
Data_path = os.path.join('Email_Data', 'emails.xlsx')

class EmailResponder:
    """Class to handle email responses and sentiment analysis."""

    def __init__(self):
        """Initialize the EmailResponder object."""
        try:
            #self.classifier = pipeline("zero-shot-classification", model=ZERO_SHOT_MODEL)
            self.text_labels = ['Positive', 'Negative', 'Neutral']
            self.template = template
        
            self.DB_PATH = DB_PATH            
            self.ollama_llm = OLLAMA_MODEL
            
            with open('emailCategories.json') as user_file:
                self.jasonFile = json.load(user_file)

            if os.path.exists(Data_path):
                os.remove(Data_path)

        except Exception as e:
            logging.error(f"Error initializing EmailResponder: {e}")
            raise

                   
    def generate_response(self, body, subject):
        """Generate a response based on sentiment analysis and a pre-defined model chain.

        Args:
            body (str): The body of the email.
            subject (str): The subject of the email.

        Returns:
            Tuple[str, float, str]: A tuple containing sentiment label, sentiment score, and the generated reply.
        """
        try:
            # Assuming you want to analyze the body for sentiment
            #body = self.extractLatestMsg(body)
            if  body:
                #result = self.classifier(body, self.text_labels, multi_label=False)
             
                sentiment_label = 0
                sentiment_score = 0
                today = datetime.date.today() 
                orderNum = 0
                orderNum = self.getOrderNumber(body, subject)
                #print (type(orderNum))
                if orderNum != None:
                    sentiment_label = self.getShopifyInfo(orderNum)                                                
                    reply_body  = 0
                    #reply_body = self.get_GPTcompletion(body,orderNum)
                    return sentiment_label, sentiment_score, reply_body
                else:
                    return  sentiment_label, sentiment_score, "Hi\n Thanks for reaching out to us. in order to assist you please provide us with the order number\nkind regards\n Customer support\n"
            
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            raise

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
      
    


    def getOrderNumber(self,body, subject):
        """
        Extracts the order number from the email text.
        Handles various formats like:
        - Order no. 12345
        - Order number: 12345
        - Order#12345
        - Order # 12345
        """
        pattern = r'order\s*(?:no\.?|number|#)?\s*[:\-]?\s*(\d{4,})'
    
        match = re.search(pattern, body, re.IGNORECASE)
        if match:
            return match.group(1)  # Return just the number part
        else:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                return match.group(1)  # Return just the number part

        return None


    def  getShopifyInfo(self,  orderNum):  
        shop = "abitto-ltd"
        api_version = "2024-04"
        access_token = self.shopify_token

        url = f"https://{shop}.myshopify.com/admin/api/{api_version}/graphql.json"

        headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }

        order_number = orderNum

        query = """
        {
          orders(first: 1, query: "name:'%s'") {
            edges {
              node {
                id
                name
                createdAt
                totalPriceSet {
                  shopMoney {
                    amount
                    currencyCode
                  }
                }
                customer {
                  displayName
                  email
                }
              }
            }
          }
        }
        """ % order_number

        response = requests.post(url, headers=headers, data=json.dumps({"query": query}))
        data = response.json()

        # Check the result
        orders = data.get("data", {}).get("orders", {}).get("edges", [])

        if orders:
            order = orders[0]["node"]

            order_Id = order.get('id')
            order_Id = num = order_Id.rpartition('/')[2] 
            BASE_URL_EVENT  = f"https://{shop}.myshopify.com/admin/api/{api_version}/orders/{order_Id}/events.json"
            response = requests.get(BASE_URL_EVENT, headers=headers)
            if response.status_code == 200:
                events = response.json().get("events", [])
                lines = [ f"{event['created_at']}: {event['message']}"  for event in events ]
                timeline_entries = "\n".join(lines)

            else:
                timeline_entries = ["Could'nt get time line \n"]
            return ' '.join(timeline_entries)









            print(f"✅ Found order: {order['name']} created at {order['createdAt']}")
            print(f"Customer: {order['customer']['displayName']} ({order['customer']['email']})")
            print(f"Total: {order['totalPriceSet']['shopMoney']['amount']} {order['totalPriceSet']['shopMoney']['currencyCode']}")
        else:
            print("❌ Order not found.")







         

    def get_GPTcompletion(self, prompt,orderNum ):      
        model="gpt-4-1106-preview"   
        try:
            GptInstruction = f"Read the first 10 lines of the following email message and generate a reply using this order number if needed and the sender should be 'custome support': {orderNum}. This is the email: {prompt}"
                    
            client = OpenAI(api_key="")

            response = client.chat.completions.create(
                model="gpt-4.1",
                max_tokens=150,
                temperature=0.7,                           
                messages=[{"role": "user", "content": GptInstruction}]
            )
            # Extract the reply from the response
            return response.choices[0].message.content

        except Exception as e:
            logging.error(f"Error generating GPT completion: {e}")
            raise
        
    '''
    model="deepseek-chat"
    client = OpenAI(api_key = self.jasonFile["Chat2"], base_url="https://api.deepseek.com")
    messages = [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": GptInstruction}]

    response = client.chat.completions.create(
    model=model,
    messages=messages,
    stream=False
    )
    '''

class EmailProcessor(EmailResponder):
    """Class to process emails and manage email-related tasks."""

    def __init__(self):
        """Initialize the EmailProcessor object."""
        super().__init__()
        with open('usersInfo.json') as userInfo_file:                
               self.jasonUsersFile = json.load(userInfo_file)

    def fetch_and_save_emails(self, email_user, email_pass, shopify_token):
        """Fetch unseen emails and save them to an Excel file.

        Args:
            email_user (str): Email username.
            email_pass (str): Email password.

        Returns:
            str: Success message or error message.
        """
        try:
            client = self.get_name(email_user)  # Ensure client gets a value
            if client =="":
                raise Exception("user can not be found!")           

            self.shopify_token = shopify_token
            self.server = self.jasonUsersFile[client]['server']
            if self.server == 'OUTLOOK':
                self.tenant_id = self.jasonUsersFile[client]['TENANT_ID']                
                self.OutlookReader = EmailReader(tenantId=self.tenant_id)
                self.OutlookReader.read_from_outlook()
                self.OutlookReader.save_emails_to_excel(Data_path)
            else:
                self.Imap = gr.State(self.jasonUsersFile[client]["Imap"]).value
                self.Smtp = gr.State(self.jasonUsersFile[client]["Smtp"]).value 
                self.port_in = gr.State(self.jasonUsersFile[client]["PortIn"]).value
                self.port_out = gr.State(self.jasonUsersFile[client]["PortOut"]).value

                reader = EmailReader(imap_url=self.Imap, Smtp_url=self.Smtp, port_num=self.port_in, email_user=email_user, email_pass=email_pass)
                reader.connect()
                reader.login()
                reader.fetch_unseen_emails()
                reader.save_emails_to_excel(Data_path)
        except Exception as e:
            logging.error(f"Error fetching and saving emails: {e}")
            raise
        #reader.save_emails_to_excel(Data_path)
        return "Emails fetched and saved to 'emails.xlsx'"


    def load_emails(self):
        """Load emails from the Excel file.

        Returns:
            Tuple[str, str, str, int]: A tuple containing sender, subject, body, and email index.
        """
        try:
            if os.path.exists(Data_path):
                df = pd.read_excel(Data_path)
                if not df.empty:
                    return self.update_email_content(df, 0)                
            return "N/A", "N/A", "Please load emails first", 0
        
        except Exception as e:
            logging.error(f"Error loading emails: {e}")
            raise
    def send_reply_and_move_next(self, email_user, email_pass, index, reply_body):
        """Send a reply to the current email and move to the next one.

        Args:
            email_user (str): Email username.
            email_pass (str): Email password.
            index (int): Current email index.
            reply_body (str): Reply body.

        Returns:
            Tuple[str, str, str, str, int, str, str, str]: A tuple containing response message, sender, subject, body, index,
            and empty reply and sentiment fields.
        """
        try:
            df = pd.read_excel(Data_path)
            if 0 <= index < len(df):
                # Retrieve the message ID of the current email
                msg_id = df.iloc[index]['Message ID']  # Replace 'Message ID' with the actual column name for message IDs in your DataFrame
                if self.server == 'OUTLOOK':
                     #reader = EmailReader(tenantId=self.tenant_id)
                     #reader.read_from_outlook()
                     response_message = self.OutlookReader.reply_toOutlook_message(msg_id, reply_body)


                else:
                    reader = EmailReader(self.Imap, self.Smtp, self.port_in, email_user, email_pass)
                    reader.connect()
                    reader.login()
                    send_status = reader.reply_to_email(msg_id, reply_body, self.port_out)
                    reader.close_connection()

                    #response_message = send_status if send_status else "Reply sent successfully!"
                    response_message = send_status 
                    From, Subject, Body, index = self.update_email_content(df, index)

                From, Subject, Body, index = self.update_email_content(df, index)
                # Clear reply body and sentiment fields
                return response_message, From, Subject, Body, index, "", "", ""

            else:
                return "Invalid email index.", "", "", "", index, "", "", ""
        except Exception as e:
            logging.error(f"Error sending reply and moving next: {e}")
            raise
    
    def save_in_draft(self, email_user, email_pass, index, reply_body ):
        try:
            df = pd.read_excel(Data_path)
            if 0 <= index < len(df):
                # Retrieve the message ID of the current email
                msg_id = df.iloc[index]['Message ID']  # Replace 'Message ID' with the actual column name for message IDs in your DataFrame
                reader = EmailReader(self.Imap, self.Smtp, self.port_in, email_user, email_pass)
                reader.connect()
                reader.login()
                send_status = reader.move_to_draft(msg_id, reply_body)
                reader.close_connection()

                response_message = send_status if send_status else "Moved to Drafts successfully."
                From, Subject, Body, index = self.update_email_content(df, index)

                # Clear reply body and sentiment fields
                return response_message

            else:
                return "Invalid email index.", "", "", "", index, "", "", ""
        except Exception as e:
            logging.error(f"Error moving to Drafts: {e}")
            raise
        


    def update_email_content(self, df, index):
        """Update email content based on the index.

        Args:
            df (pd.DataFrame): DataFrame containing email data.
            index (int): Email index.

        Returns:
            Tuple[str, str, str, int]: A tuple containing sender, subject, body, and email index.
        """
        try:
            if 0 <= index < len(df):
                email = df.iloc[index]
                return email["From"], email["Subject"], str(email["Body"]), index
            return "N/A", "N/A", "N/A", index
        except Exception as e:
            logging.error(f"Error updating email content: {e}")
            raise


    def navigate_emails(self, direction, index):
        """Navigate through emails based on the given direction.

        Args:
            direction (str): Navigation direction ('next' or 'prev').
            index (int): Current email index.

        Returns:
            Tuple[str, str, str, int]: A tuple containing sender, subject, body, and email index.
        """
        if os.path.exists(Data_path):
            try:
                df = pd.read_excel(Data_path)
                if direction == "next":
                    index = index + 1 if index < len(df) - 1 else index
                elif direction == "prev":
                    index = index - 1 if index > 0 else index
                return self.update_email_content(df, index)
            except Exception as e:
                logging.error(f"Error navigating emails: {e}")
                raise
        else:
            return "N/A", "N/A", "Please load emails first", 0

    def show_popup(self, response_message):
        """Display a popup with the given response message.

        Args:
            response_message (str): Response message.

        Returns:
            gr.Info: Gradio Info object.
        """
        try:
            if response_message:
                gr.update(value=response_message, visible=True)
            return gr.Info(response_message)
        except Exception as e:
            logging.error(f"Error showing popup: {e}")
            raise

    def get_name(self,name):
        # Find the position of the character and slice the string
        index = name.find('@')
        # Check if the character exists in the string
        if index != -1:
            # Strip up to the character (don't include the character itself)
            stripped_text = name[:index].strip()
            return stripped_text
        else:
           return ""






'''
    def getOrderNumber(self,body, subject): 
    Inbody =  (body
            .replace("#"," ")
            .replace("number"," ")
            .replace(".", " ")
            .replace('\n',' ')
            .lower()   )
    Inbody= (' '.join(Inbody.split()) ) +' '
    Inbody =Inbody.split(" ")
    Inbody.append(" ")


    Insubject =  (subject
            .replace("#"," ")
            .replace("number"," ")
            .lower()
            .split() )

    ordNum =0xFFFF
    for  r in range (len(Inbody)-1):
        #if Inbody[r]=="order":
        #    indices = [i for i, item in enumerate(Inbody[r:]) if item.isnumeric()]
        #    if len (indices) !=0:                
        #        ordNum = Inbody[r+ indices[0]]
        if Inbody[r] == "order" and Inbody[r+1].isnumeric():
            ordNum = Inbody[r+1]
            print (ordNum)
            break
    if ordNum == 0xFFFF:
        for  r in range (len(Insubject)-1):
            if Insubject[r]== "order":
                indices = [i for i, item in enumerate(Insubject[r:]) if item.isnumeric()]
                if len (indices) !=0:                
                    ordNum = Insubject[r+ indices[0]]
                    print (ordNum)
                    break
    return ordNum

    def  getShopifyInfo_old(self,  orderNum):

        # Shopify API credentials
        shop_name = "abitto-ltd"
        access_token = self.shopify_token

        # REST API endpoint for orders
        url = f"https://{shop_name}.myshopify.com/admin/api/2024-04/orders.json"

        # Auth headers
        headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }

        # Optional: params to control what you fetch (like only paid orders)
        params = {
            "status": "any",         # open, closed, cancelled, any
            #"name":f'#{orderNum}'
            "limit": 250               # adjust to fetch more orders
        }


        #url = f"https://{shop_name}.myshopify.com/admin/api/2024-04/orders/{int(orderNum)}.json"
       
        # Make GET request
        response = requests.get(url, headers=headers, params=params)

        # Check result
        order_info = {}
        if response.status_code == 200:
            orders = response.json().get("orders", [])
            print(f"Found {len(orders)} orders.")
            
            for order in orders:
                if order['order_number'] == int(orderNum):
                    print(f"found Order: {order['order_number']}")
                    #order_info = order['line_items'][0]
                    #order_info = "\n".join(f"{key}: {value}" for key, value in order.items())
                    order_info = "\n".join(f"{key}: {value}" for key, value in order['line_items'][0].items())
        else:
            print(f"Failed to fetch orders: {response.status_code}\n{response.text}")

        return order_info


    def  getShopifyInfo_old2(self,  orderNum):

        # Your Shopify store info
        SHOP_NAME = "abitto-ltd"
        ACCESS_TOKEN = self.shopify_token
        API_VERSION = "2024-04"

        # Base URL
        BASE_URL_ORDER = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/orders.json"

        # Request headers
        HEADERS = {
            "X-Shopify-Access-Token": ACCESS_TOKEN,
            "Content-Type": "application/json"
        }

        # Parameters for the first request
        params = {
            "limit": 250,
            "status": "any"
        }

        # Target order number you want to find

        found_order = None  # to store the found order

        order_info = {}        
        while True:
            response = requests.get(BASE_URL_ORDER, headers=HEADERS, params=params)
            if response.status_code != 200:
                return "couldnt get order number \n"
            data = response.json()
    
            orders = data.get("orders", [])
            print(f"Fetched {len(orders)} orders.")

            # Search for the target order number in this batch
            for order in orders:
                if order.get("order_number") == int(orderNum):
                   order_info = "\n".join(f"{key}: {value}" for key, value in order['line_items'][0].items())
                   order_Id = order.get('id')
                   BASE_URL_EVENT  = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/orders/{order_Id}/events.json"
                   response = requests.get(BASE_URL_EVENT, headers=HEADERS)
                   if response.status_code == 200:
                        events = response.json().get("events", [])
                        lines = [ f"{event['created_at']}: {event['message']}"  for event in events ]
                        timeline_entries = "\n".join(lines)

                   else:
                       timeline_entries = ["Could'nt get time line \n"]
                   return ' '.join(timeline_entries)

            # Check for pagination (rel="next")
            link_header = response.headers.get("Link")
            if link_header and 'rel="next"' in link_header:
                match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
                if match:
                    next_url = match.group(1)
                    BASE_URL = next_url.split("?")[0]
                    page_info = next_url.split("page_info=")[-1].split("&")[0]
                    params = {
                        "limit": 250,
                        "page_info": page_info
                    }
                else:
                    break
            else:
                break



'''