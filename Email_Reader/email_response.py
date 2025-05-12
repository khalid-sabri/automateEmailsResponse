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
import json
import string

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
            #self.embed_model = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)            
            
            #model_name = "sentence-transformers/all-mpnet-base-v2"
            #model_kwargs = {'device': 'cpu'}
            #encode_kwargs = {'normalize_embeddings': False}
            
            #self.embed_model = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs )
    


            self.DB_PATH = DB_PATH
            #self.vectorstore = Chroma(persist_directory=self.DB_PATH, embedding_function=self.embed_model)
            #self.retriever = self.vectorstore.as_retriever()
            #self.prompt = ChatPromptTemplate.from_template(self.template)
            self.ollama_llm = OLLAMA_MODEL
            #self.model_local = ChatOllama(model=self.ollama_llm)
            #self.chain = (
            #    {"context": self.retriever, "question": RunnablePassthrough()}
            #    | self.prompt
            #    | self.model_local
             #   | StrOutputParser()
            #)
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
            body = self.extractLatestMsg(body)
            if  body:
                #result = self.classifier(body, self.text_labels, multi_label=False)
                result = {'labels': 0}
                result = {'scores': 0}
                sentiment_label = result['labels'][0]
                sentiment_score = result['scores'][0]
                today = datetime.date.today() 
                orderNum = 0xFFFF
                orderNum = self.getOrderNumber(body, subject)
                if orderNum != 0xFFFF:
                    self.getShopifyInfo(orderNum)
                query = f" Todays date -{today}\n  sentiment - {sentiment_label}\n Subject -{subject}\n Body-{body} "
        

                #query = f"""categorize this text ' {body} ' as follows:
                #if it belongs to: {self.jasonFile["categories"][0]["cat1"]} then just say {self.jasonFile["categories"][0]["reply"]} or 
                #if it belongs to: {self.jasonFile["categories"][1]["cat2"] } then generate a reponse using this order number {orderNum}
                #otherwise just say not found """
        

                reply_body = self.chain.invoke(query)
            
                #reply_body  = 0
                #reply_body = self.get_GPTcompletion(query,orderNum)
                return sentiment_label, sentiment_score, reply_body
            
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
        #x = re.search( (body.replace("#"," ") ).lower(),"\b(?:Order\s*[:\-]?\s*)\d+\b" )
        Inbody =  (body
              .replace("#"," ")
              .replace("number"," ")
              .lower()
              .split() )
        Insubject =  (subject
              .replace("#"," ")
              .replace("number"," ")
              .lower()
              .split() )

        ordNum =0xFFFF
        for  r in range (len(Inbody)-1):
            if Inbody[r]=="order":
                indices = [i for i, item in enumerate(Inbody[r:]) if item.isnumeric()]
                if len (indices) !=0:                
                    ordNum = Inbody[r+ indices[0]]
                    print (ordNum)
                    break
        if ordNum == 0xFFFF:
            for  r in range (len(Insubject)-1):
                if Insubject[r]=="order":
                    indices = [i for i, item in enumerate(Insubject[r:]) if item.isnumeric()]
                    if len (indices) !=0:                
                        ordNum = Insubject[r+ indices[0]]
                        print (ordNum)
                        break
        return ordNum

    def  getShopifyInfo(self,  orderNum):
        pass

     

    def get_GPTcompletion(self, prompt,orderNum ):

        #GptInstruction = f"""categorize this text ' {prompt} ' as follows:
        #if it belongs to: {self.jasonFile["categories"][0]["cat1"]} then just say {self.jasonFile["categories"][0]["reply"]} or 
        #if it belongs to: {self.jasonFile["categories"][1]["cat2"] } then generate a reponse using this order number {orderNum}
        #otherwise just say not found """
        
        #GptInstruction = f"""provide a reponse to this email {prompt}using this {orderNum} if needed"""
        
        model="gpt-4-1106-preview"
        client = OpenAI(api_key = self.jasonFile["ChatGpt_apikey"])
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
        )
        '''
        model="deepseek-chat"
        client = OpenAI(api_key = self.jasonFile["DeepSeek"], base_url="https://api.deepseek.com")
        messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": GptInstruction}]

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=False
        )
        '''

        return response.choices[0].message.content


class EmailProcessor(EmailResponder):
    """Class to process emails and manage email-related tasks."""

    def __init__(self):
        """Initialize the EmailProcessor object."""
        super().__init__()
        with open('usersInfo.json') as userInfo_file:                
               self.jasonUsersFile = json.load(userInfo_file)

    def fetch_and_save_emails(self, email_user, email_pass):
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
            self.Imap = gr.State(self.jasonUsersFile[client]["Imap"]).value
            self.Smtp = gr.State(self.jasonUsersFile[client]["Smtp"]).value 
            self.port_in = gr.State(self.jasonUsersFile[client]["PortIn"]).value
            self.port_out = gr.State(self.jasonUsersFile[client]["PortOut"]).value

            reader = EmailReader(self.Imap, self.Smtp, self.port_in, email_user, email_pass)
            reader.connect()
            reader.login()
            reader.fetch_unseen_emails()
            reader.save_emails_to_excel(Data_path)
            return "Emails fetched and saved to 'emails.xlsx'"
        except Exception as e:
            logging.error(f"Error fetching and saving emails: {e}")
            raise

    def load_emails(self):
        """Load emails from the Excel file.

        Returns:
            Tuple[str, str, str, int]: A tuple containing sender, subject, body, and email index.
        """
        try:
            df = pd.read_excel(Data_path)
            if not df.empty:
                return self.update_email_content(df, 0)
            return "N/A", "N/A", "N/A", 0
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
                reader = EmailReader(self.Imap, self.Smtp, self.port_in, email_user, email_pass)
                reader.connect()
                reader.login()
                send_status = reader.reply_to_email(msg_id, reply_body, self.port_out)
                reader.close_connection()

                response_message = send_status if send_status else "Reply sent successfully!"
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