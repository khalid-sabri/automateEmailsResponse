from revChatGPT.Unofficial import Chatbot
import json

import pdb


def getResponse(prompt):
	f = open ("gptconfig.json")
	token = json.load(f)
	pdb.set_trace()
	api = Chatbot(token)
	resp = api.ask(prompt)
	return (resp['message'])