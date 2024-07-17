from improve_llm import LLM
from database_manipulator import Database

from flask import Flask, render_template, request
from flask_socketio import SocketIO, send
import json

from langchain_core.messages import AIMessage, HumanMessage

import sqlite3
from googletrans import Translator

def find_id(session, id_to_session, self=None):
        x = 0
        isFound = False
        print(id_to_session)
        for i in id_to_session:
                print("id to sesh: ")
                print(id_to_session[x])
                print("x : " + str(x))
                if id_to_session[x][0] == session:
                    isFound = True
                    break
                else:
                    x = x + 1
        return x

def print_id_to_session(id_to_session):
    for i in id_to_session:
        print("Session ID: " + str(i[0]) )
        print("User ID   : " + str(i[1]) )
        print("Username  : " + str(i[2]) )
        print("Password  : " + str(i[3]) )

ultimate_move = LLM()

app = Flask(__name__)
#socketio = SocketIO(app, cors_allowed_origins="*")

translator = Translator()

chat_histories = Database.load_chats()
print("now in chat_histories")
for i in chat_histories:
    print(chat_histories[i])

# 0 = session, 1 = user_id, 2 = username, 3 = password
# | sessionId | user_id    | username    | password    | 
# 2D array with 4 columns and variable rows

id_to_session = [[]]
id_to_session[0] = ["None", "None", "None", "None"]

@app.route("/", methods=['POST', 'GET'])
def index():
    print("hi")
    if request.method == 'POST':

        m1 = request.json
        print(m1["sessionId"])
        session = m1["sessionId"]
        msg = ""
        isSessionFound = False

        if m1["sessionState"]["intent"]["name"] == "NewUser":
            username = m1["sessionState"]["intent"]["slots"]["username"]["value"]["originalValue"]
            password = m1["sessionState"]["intent"]["slots"]["password"]["value"]["originalValue"]
            session = m1["sessionId"]

            msg = Database.new_user(username, 
                              password, 
                              session, 
                              id_to_session)
            
            return msg
        pass

        print(id_to_session)
        print_id_to_session(id_to_session)

        if m1["diagnostics"] == "Diagnostic 01: IS SESSION ID VALID":
            for i in id_to_session:
                if m1["sessionId"] == i[0] and i[1] != "None": # user id is paired with session
                    msg = "YES, ALLOW ACCESS"
                    print(msg)
                    isSessionFound = True
                elif m1["sessionId"] == i[0] and i[1] == "None": # user id not found: either no username entered or no password provided yet
                    isSessionFound = True
                    if i[2] == "None": # no username
                        msg = "NO, NEED USERNAME"
                        print(msg + " : found")
                    elif i[2] != "None" and i[3] == "None": # username viable, no password given yet
                        msg = "NO, NEED PASSWORD"
                        print(msg)
            
            if isSessionFound == False: # if sessionId not found
                id_to_session.extend(  [[m1["sessionId"] , "None", "None", "None"]] ) # add the Id to the list
                msg = "NO, NEED USERNAME"
                print("var: " + msg)
            print(id_to_session)
            print_id_to_session(id_to_session)
            return msg
        elif m1["diagnostics"] == "Diagnostic 02: IS USERNAME VALID":
            username = m1["inputTranscript"]
            msg = Database.check_username(username, 
                                    session, 
                                    id_to_session)
            return msg
        elif m1["diagnostics"] == "Diagnostic 03: IS PASSWORD VALID":
            passcode = m1["inputTranscript"]
            print("=== data recieved ===")
            print("passcode " + passcode )
            print("session " + str(session))
            print("id to sesh ")
            print(id_to_session)
            msg = Database.check_username_password_pair(passcode, 
                                                        session, 
                                                        id_to_session)
            return msg
        
        elif m1["diagnostics"] == "Diagnostic XX: SEND TO LLM":
            print("")
            print("Sending to LLM")
            print("")
            x = find_id(session, 
                                 id_to_session)

            userId = id_to_session[x][1]
            print("Recieved: " + m1["inputTranscript"])
            print("From: " + str(userId) )
            print("Session #: " + m1["sessionId"])
            if chat_histories.get(userId) == None:
                chat_histories[userId] = []
            
           # '''
            data = translator.detect(m1["inputTranscript"])
            ai_msg = ''
            transVal = m1["inputTranscript"]
            print("language detected: " + data.lang)
            if data.lang != 'en':
                transVal = translator.translate(m1["inputTranscript"], dest='en')
                transVal = transVal.text
                ai_msg = ultimate_move.ask(inp=transVal, 
                              chat_history=chat_histories[userId])
            else:
                ai_msg = ultimate_move.ask(inp=m1["inputTranscript"], 
                              chat_history=chat_histories[userId])
           # '''
            #ai_msg = ultimate_move.ask(inp=m1["inputTranscript"], 
            #                  chat_history=chat_histories[userId])
            
            chat_histories[userId].extend(
                [
                    HumanMessage(content=transVal), AIMessage(content=ai_msg)
                ]
                )
            
            print("AI: " + ai_msg)
            print("")

            Database.insert_chat(userId=userId, 
                                 ai_msg=ai_msg, 
                                 human_msg=transVal)

            print("====== chat history ======")
            print("python dictionary")
            print(chat_histories[userId])
            print("")
            print("sql finds")
            con_thread = sqlite3.connect("test.db")
            c_thread = con_thread.cursor()
            print(c_thread.execute("select * from Chat where user_id = {uid}".format(uid=userId)).fetchall())
            
            msg = ai_msg
            if data.lang != 'en':
                msg = translator.translate(msg, dest=data.lang).text
            return msg
'''

inp = ""
chat_history = []

print("")
print("enter prompts")

while inp != "end":
    inp = input("")
    if inp == "end" :
        break
    print("Please Wait while the Magic Pixie living in your computer answers your question")
    ai_msg = ultimate_move.ask(inp, chat_history)
    print(ai_msg)
    print("")
    print("====")
    print("enter prompts")
    chat_history.extend(
        [
            HumanMessage(content=inp), ai_msg
        ]
    )

'''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2000)#, allow_unsafe_werkzeug=True)
    #socketio.run(app, host="0.0.0.0", port=2000, allow_unsafe_werkzeug=True)

