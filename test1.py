from curses.ascii import isdigit
import sys
from numpy import indices
import gradio as gr
from msal import PublicClientApplication
import re
#import openai
from openai import OpenAI
import os
import pandas as pd
import time
import json
import pdb
from langchain_community.embeddings import HuggingFaceEmbeddings

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
#import ChromeChatGpt
import string

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

email1  ="""

    From: sabri2 <sabri2@doctor.com>
    Sent: 15 March 2025 05:46
    To: saifaldeen@hotmail.com <saifaldeen@hotmail.com>
    Subject: Fw: Order #19596
 




    Sent from my Galaxy



    From: Andy <andy.szkopiak@virginmedia.com>
    Sent: Wednesday, April 5, 2023 1:51 PM
    To: info abitto.com <info@abitto.com>
    Subject: Order #19596
 
    Hi

    Just wondering if you have an update on when the items will be dispatched please?

    Andy Szkopiak
    +44 7479 110200
    """

email2 = '''
From: johnny murtagh <johnnym10@hotmail.co.uk> 
Sent: Wednesday, April 5, 2023 2:32 PM
To: info abitto.com <info@abitto.com
Subject: ORDER #19178
 
Hi, 

14 days has passed and I still haven't received my refund? 

If I don't receive it by Friday I'll be making a complaint with my back to reclaim the money. 

Thanks. 

Sent from Outlook for Android '''


email3='''


k sabri
 
From:
saifaldeen@hotmail.com
To:
moonlight698@myyahoo.com

Tue, 1 Apr at 14:50


From: sabri2 <sabri2@doctor.com>
Sent: 12 March 2025 13:35
To: saifaldeen@hotmail.com <saifaldeen@hotmail.com>
Subject: Toto
 


Hello there
Enquiry 
'''
email4 = '''

    ________________________________
    From: Michael Weir <michael-weir@live.com>
    Sent: Wednesday, April 5, 2023 2:24 PM
    To: info abitto.com <info@abitto.com>
    Subject: Re: Order #19845 confirmed

    Hello,

    Is it possible to track my order that’s below?

    Thanks

    Mike
    ent from my iPhone

    On 1 Apr 2023, at 10:35, Abitto ltd <info@abitto.com> wrote:

    ﻿
    Abitto ltd<https://www.abitto.com>
    Order #19845

    Thank you for your purchase!

    Hi Michael,
    We're getting your order ready to be shipped. We will notify you when it has been sent.



    In the mean time for ideas on how to dress a tweed suit

    Follow our Instagram page<https://www.instagram.com/abitto_style/>

    <https://www.instagram.com/abitto_style/>
    [Example]

    View your order<https://www.abitto.com/4253876294/orders/f53952bad2784c4c6655bbbd7b02349d/authenticate?key=fa4c3a139ff7ee5534c79e58d69256cb>
    or Visit our store<https://www.abitto.com>
    Order summary
    [https://cdn.shopify.com/s/files/1/0042/5387/6294/products/Blueestateedited_cf895024-daf4-451b-a5e3-1859b1ab3c6d_compact_cropped.jpg?v=1614846928]      Blinder Blue Estate Herringbone Tweed 3 Piece Suit × 1

    £199.99

    [https://cdn.shopify.com/s/files/1/0042/5387/6294/products/tie10_compact_cropped.jpg?v=1552923968]      Maroon Knitted Tie × 1

    £9.99

    Subtotal

    £209.98

    Shipping

    £5.99

    Total

    £215.97 GBP
    Customer information
    Shipping address

    Michael Weir
    Orchard View
    Coronation Street
    Fairford GL7 4HX
    United Kingdom

    Billing address

    Michael Weir
    Orchard View
    Coronation Street
    Fairford GL7 4HX
    United Kingdom

    Shipping method

    Within 2-3 Working Days Tracked

    Payment method

    [https://cdn.shopify.com/shopifycloud/shopify/assets/themes_support/notifications/mastercard-c8d6f1c2e7b63ab95f49954c724c675678d205478e3de8d6f3da384fc068589d.png] Payment method

    One last thing.....

    <https://www.abitto.com/collections/accessories/products/automatic-pocket-watch>
    [Example]


    If you have any questions, reply to this email or contact us at info@abitto.com<mailto:info@abitto.com>
    
   
'''

def add():
    return 5

def doupdate(name):
    #return f"Welcome to Gradio, {name}!"

    with gr.Blocks() as demo:
        gr.Markdown("Start typing below and then click **Run** to see the output.")
        with gr.Row():
            inp = gr.Textbox(placeholder="What is your name?")
            out = gr.Textbox()
        btn = gr.Button("Run")
        btn.click(fn=add, inputs=inp, outputs=out)

    demo.launch()

def mail_authen():
    CLIENT_ID = "a85ef0df-274b-42b2-ae90-2ee4f9c589c6"
    AUTHORITY = "https://login.microsoftonline.com/common"
    SCOPES = ["Mail.Read"]

    app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
    flow = app.initiate_device_flow(scopes=SCOPES)
    print(f"Go to {flow['verification_uri']} and enter the code: {flow['user_code']}")
    token_response = app.acquire_token_by_device_flow(flow)

    if "access_token" in token_response:
        print("Access Token:", token_response["access_token"])
    else:
        print("Failed to authenticate.")



def greet(name):
    return f"Hello, {name}!"

def myui(): # Create Gradio UI
    iface = gr.Interface(fn=greet, inputs="text", outputs="text")

    # Launch the app
    iface.launch()


'''
import win32com.client
def reademail2():
    outlook=win32com.client.Dispatch("Outlook.Application").GetNamespace ("MAPI")
    inbox=outlook.GetDefaultFolder (6)
    messages= inbox. Items
    message= messages.GetLast()
    engine= pyttsx3.init()
'''

def getOrderNumber(body, subject): 
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

def get_GPTcompletion(prompt,gptKey, model="gpt-4-1106-preview"):
    #client = OpenAI(
    #api_key ="sk-proj-Uutf7UfPv_i5oXTFNqWMEh-x1dk1fyVAMemOpFwzI9Visnf-MWNCeyPh7R02H32gZ"\
    #"jhd9P0QJPT3BlbkFJelV2W76z_CXqmFapjBzcMulCe5gHlONcBHsGxInBYi-oZB-TUz7k2HAd5f306Rq35WaBMCx70A"
    #)
    client = OpenAI(api_key = gptKey)

    
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
    )
    return print(response.choices[0].message.content)

def hugging():
    model_name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}
    #pdb.set_trace()
    embed_model = HuggingFaceEmbeddings(
        model_name="WhereIsAI/UAE-Large-V1",
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
          
       )


#def test_revchatgpt():
#    print (ChromeChatGpt.getResponse("how are you "))



#============================================================
def login(name, password):
    return f"Hello {name}! Your password is {password} (stored in cookies)."

def test_cookie():
    with gr.Blocks() as demo:
        gr.Markdown("## Login with Cookies (Demo Only)")

        with gr.Row():
            name = gr.Textbox(label="Name", elem_id="name_input")
            #name.input(checkCocie)
            password = gr.Textbox(label="Password", type="password", elem_id="password_input")

        with gr.Row():
            submit = gr.Button("Submit")
            clear = gr.Button("Clear Credentials")

        output = gr.Textbox(label="Output")

        # Load stored credentials
        demo.load(
            None,
            js="""
            () => {
                const name = localStorage.getItem("name_cookie");
                const pass = localStorage.getItem("pass_cookie");
                if (name) document.getElementById("name_input").value = name;
                if (pass) document.getElementById("password_input").value = pass;
            }
            """
        )

        # Save credentials on submit
        submit.click(
            login,
            inputs=[name, password],
            outputs=output,
            js="""
            (name, pass) => {
                localStorage.setItem("name_cookie", name);
                localStorage.setItem("pass_cookie", pass);
                return [name, pass];
            }
            """
        )

        # Clear credentials button
        clear.click(
            None,
            js="""
            () => {
                localStorage.removeItem("name_cookie");
                localStorage.removeItem("pass_cookie");
                document.getElementById("name_input").value = "";
                document.getElementById("password_input").value = "";
            }
            """
        )

    demo.launch()
#========================================================================

get_local_storage = """
    function() {
      globalThis.setStorage = (key, value)=>{
        localStorage.setItem(key, JSON.stringify(value))
      }
       globalThis.getStorage = (key, value)=>{
        return JSON.parse(localStorage.getItem(key))
      }
       const text_input =  getStorage('text_input')
       const dropdown =  getStorage('dropdown')
       const local_data =  getStorage('local_data')
       return [text_input, dropdown, local_data];
      }
    """


def predict(text_input, dropdown):
    return {
        "text": text_input,
        "dropdown": dropdown,
        "something_else": [text_input] * 3 + [dropdown],
    }

def gradiolocalset():
    with gr.Blocks() as block:
        text_input = gr.Text(label="Input")
        dropdown = gr.Dropdown(["first", "second", "third"], type="index")
        local_data = gr.JSON({}, label="Local Storage")

        dropdown.change(None, dropdown, None, js="(v)=>{ setStorage('dropdown',v) }")
        text_input.change(None, text_input, None, js="(v)=>{ setStorage('text_input',v) }")
        local_data.change(None, local_data, None, js="(v)=>{ setStorage('local_data',v) }")
        btn = gr.Button("Set New Data")
        btn.click(fn=predict, inputs=[text_input, dropdown], outputs=[local_data])
        block.load(
            None,
            inputs=None,
            outputs=[text_input, dropdown, local_data],
            js=get_local_storage,
        )
    block.launch(debug=True)

def extractLatestMsg_t(body):
    Inbody =  (
    body
    .lower()
    .translate(str.maketrans('', '', string.punctuation)).split() 
    )
    foundStr =str();
    for  r in range (len(Inbody)-1):
        if Inbody[r]=="hi" or Inbody[r]=="hello":

            indices = [i for i, item in enumerate(Inbody[r:]) if item == "regards" or item == "thanks"]
            if len (indices) !=0:
                foundStr = ' '.join(Inbody[r:r+indices[0]])
                break
    return foundStr       




def use_selenium():
    # Set up WebDriver
    driver = webdriver.Chrome()  # Replace with your preferred browser

    # Navigate to ChatGPT
    driver.get("https://chat.openai.com/")

    # Wait for the input field
    input_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//textarea"))
    )

    # Send a message
    input_field.send_keys("Hello, how are you?\n")
    input_field = WebDriverWait(driver, 20).until(    EC.element_to_be_clickable((By.XPATH, "//textarea"))  )
    input_field.send_keys(u'\ue007')  # Send Enter key

    # Wait for the response
    response = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'response')]"))
    )

    # Print the response
    print(response.text)

    # Close the browser
    driver.quit()

def get_name(name):
    # Find the position of the character and slice the string
    index = name.find('@')

    # Check if the character exists in the string
    if index != -1:
        # Strip up to the character (don't include the character itself)
        stripped_text = name[:index].strip()
        return stripped_text
    else:
       return ""



import requests
import json

def read_list_of_lists_from_url(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    data = json.loads(response.text)
    tmp= [] 

    for inner_list in len(data):
        x = inner_list[0]
        y = inner_list[2]
       tmp[x,y] =inner_list[1]

    for i in tmp:
        for j in i:
            print (j)
       
        
        print(inner_list)

    return data








if __name__ == "__main__":
    '''
    #myui()
    #doupdate("hello")
    #mail_authen()M
    #openai.api_key ="sk-proj-Uutf7UfPv_i5oXTFNqWMEh-x1dk1fyVAMemOpFwzI9Visnf-MWNCeyPh7R02H32gZ"\
    #"jhd9P0QJPT3BlbkFJelV2W76z_CXqmFapjBzcMulCe5gHlONcBHsGxInBYi-oZB-TUz7k2HAd5f306Rq35WaBMCx70A"


    with open('emailCategories.json') as user_file:
        jasonFile = json.load(user_file)

   
    txt ="hello i am tracing my order number "
    sub ="nothing here order 63542"

    #GptInstruction = fcategorize this email {txt} into category {   jasonFile[["categories"][1]["cat1"]] or jasonFile[["categories"][2]["cat2"]]   }'
    GptInstruction = f"""categorize this text ' {txt} ' as follows:
        if it belongs to: {jasonFile["categories"][0]["cat1"]} then just say cat1 or 
        if it belongs to: {jasonFile["categories"][1]["cat2"] } then just say cat2
        otherwise just say not found """
    print (GptInstruction)
    '''

    #hugging()
    #test_revchatgpt()
    #test_cookie()
    #gradiolocalset()
    
#print( extractLatestMsg_t(body = email1))
#print ( extractLatestMsg_t(body = email2))
#print ( extractLatestMsg_t(body = email3))
#print ( extractLatestMsg_t(body = email4))

#getOrderNumber(txt,sub)
with open('emailCategories.json') as user_file:
        jasonFile = json.load(user_file)
#print( get_GPTcompletion("how are you ", jasonFile["ChatGpt_apikey"] ) )
#use_selenium()
print(get_name("sgdfbgrtmyyahoo.com"))

   
        