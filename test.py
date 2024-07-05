print("wassup world?")

# Created by Said Ikki

from langchain_community.llms import Ollama
from langchain_community.document_loaders import WebBaseLoader , TextLoader, PyPDFLoader , DirectoryLoader, UnstructuredFileLoader
from langchain_core import documents

# for more loaders, go here:
# https://api.python.langchain.com/en/latest/community_api_reference.html#module-langchain_community.document_loaders

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community import embeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnablePassthrough



# Load in LLM
print("loading LLM")
llm = Ollama(model = "llama3")
# add a document, we will use an online article as a dummy for now
# we'll see if we can extend it later
#loader = WebBaseLoader(
   # web_path="https://en.wikipedia.org/wiki/Joker_(character)"
#)
# put it into the collection of documents to look through
#docs1 =  loader.load()
#docs = loader.load()
# documents need to be cut into smaller pieces
# text_splitter sets the parameters of the cutting,
# modify to see if it works better some other time
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 200,
    add_start_index = True
)

docs = DirectoryLoader(
    path="./docs",
    loader_cls=UnstructuredFileLoader,
)
print('load docs')
# actually cut up the docs
all_splits = text_splitter.split_documents(docs.load())
#all_splits.append( text_splitter.split_documents(docs2) )
#all_splits.append( text_splitter.split_documents(docs3) )

# embeddings? idk
embedding = embeddings.OllamaEmbeddings(
    model="nomic-embed-text"
)
print('set up vectore store')
# hold documents in vector store
vectorstore = Chroma.from_documents(
    documents = all_splits,
    embedding = embedding
)
print('set up retriever')
# retriever part of the RAG
retriever = vectorstore.as_retriever(
    search_type = "similarity",
    search_kwargs = {"k":6}
)

# chat history prompt for the AI
contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""
print("contextualize")
# format every prompt along with a chat history and the above prompt
contextualize_q_prompt= ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)

# chains? idk
contextualize_q_chain = contextualize_q_prompt | llm | StrOutputParser()

# Q&A prompt for LLM
qa_system_prompt = """You are an assistant for question-answering tasks. \
Use the following information to provide accurate answers but act as if you knew this information innately.\
You can use the information provided to help answer the question, but you are not limited to it \
If unsure, simply state that you don't know.\
{context}"""

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)

# format docs
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# make 'context'
def contextualized_question(input: dict):
    if input.get("chat_history"):
        q = contextualize_q_chain
        return q
    else:
        return input["question"]
print( "initialize RAG chain")
rag_chain = (
    RunnablePassthrough.assign(
        context = contextualized_question | retriever | format_docs
    )
    | qa_prompt
    | llm
)

inp = ""
chat_history = []
'''

print("")
print("enter prompts")

while inp != "end":
    inp = input("")
    if inp == "end" :
        break
    print("Please Wait while the Magic Pixie living in your computer answers your question")
    ai_msg = rag_chain.invoke(
        {
            "question": inp,
            "chat_history": chat_history
        }
    )
    print(ai_msg)
    chat_history.extend(
        [
            HumanMessage(content=inp), ai_msg
        ]
    )
'''


from flask import Flask, render_template, request
from flask_socketio import SocketIO, send
import json

print("Setting Up Web Server")

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
chat_histories = {}
'''
@socketio.on('connect')
def test_connect():
    print("User Connected! " + request.sid)
    chat_histories[request.sid] = []

@socketio.on('message')
def handle_message(message):
    print("Recieved Message: " + message + " from SID == " + request.sid)
    ai_msg = rag_chain.invoke(
        {
            "question": message,
            "chat_history": chat_histories[request.sid]
        }
    )
    send(ai_msg)
    chat_histories[request.sid].extend(
        [
            HumanMessage(content=message), ai_msg
        ]
    )
'''
'''

@app.route("/", methods=['POST', 'GET'])
def index():
    #return render_template("gpt-clone.html")
    print("hi")
    if request.method == 'POST':
        message = (request.data).decode()


        m1 = request.json
        content = m1["inputTranscript"]
        print(content + " : #" + m1["sessionId"])
        print("Recieved Message: " + m1["inputTranscript"])
        session_id = int(m1["sessionId"])
        if chat_histories.get(session_id) == None:
            chat_histories[session_id] = []
        ai_msg = rag_chain.invoke(
        {
            "question": content,
            "chat_history": chat_histories[session_id]
        }
        )
        chat_histories[session_id].extend(
        [
            HumanMessage(content=content), ai_msg
        ]
        )
        print("AI: " + ai_msg)
        print("")
        
        print("=== chat histories ===")
        print( )
        for i in chat_histories:
            print(str((chat_histories[i][0]).content) )
            print(chat_histories[i][1])

        return ai_msg
    return 'hi'
    pass

'''
    
# IN DEVELOPMENT: REMEMBER TO TEST WITH ping.py
# YOU HAVE TO SET UP ping.py TO ACTUALLY TEST
#'''
def print_id_to_session(id_to_session):
    for i in id_to_session:
        print("Session ID: " + str(i[0]) )
        print("User ID   : " + str(i[1]) )
        print("Username  : " + str(i[2]) )
        print("Password  : " + str(i[3]) )


import sqlite3
con = sqlite3.connect("test.db")
cursor = con.cursor()

user_id_list = cursor.execute("select U.id from User U, Chat C where C.user_id = U.id").fetchall()
uid_formatted = []
for i in user_id_list:
    print(i[0])
    uid_formatted.append(i[0])

for i in uid_formatted:
    print(i)

chat_histories = {}

for i in uid_formatted:
    chat_histories[i] = []
    print("ID#" + str(i) + " initialized")

for i in uid_formatted:
    query = """
            SELECT human, ai 
            FROM Chat c
            WHERE c.user_id = {i}
            ORDER BY c.msgOrder
    """.format(i=i)
    human = cursor.execute(query).fetchall()[0][0]
    ai_msg = cursor.execute(query).fetchall()[0][1]
    print(human)
    print(ai_msg)
    print("")
    
    chat_histories[i].extend(
        [
            HumanMessage(content=human), ai_msg
        ]
        )
    
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
        message = (request.data).decode()


        m1 = request.json
        print(m1["sessionId"])
        msg = ""
        isSessionFound = False
        
        if m1["sessionState"]["intent"]["name"] == "NewUser":
            username = m1["sessionState"]["intent"]["slots"]["username"]["value"]["originalValue"]
            password = m1["sessionState"]["intent"]["slots"]["password"]["value"]["originalValue"]
            idQuery =       """
                            SELECT COUNT(*)
                            FROM User 
                            """
            con_thread = sqlite3.connect("test.db")
            c_thread = con_thread.cursor()

            newId = c_thread.execute(idQuery).fetchall()[0][0] + 1
            similarUser = c_thread.execute("""
                                           select count(*) 
                                           from User 
                                           where username = '{x}' 
                                           and password = '{y}'""".format(x=username, y=password) ).fetchall()[0][0]
            
            if similarUser >= 0:
                return "ERROR: USER ALREADY IN DATABASE"

            insertStmt =    """
                            INSERT INTO User(username, password, id)
                            VALUES ('{username}', '{password}', {id})
                            """.format(username=username, password=password, id=newId)
            
            c_thread.execute(insertStmt)
            con_thread.commit()
            x = 0
            isFound = False
            for i in id_to_session:
                print("id to sesh: " + id_to_session[x][0])
                print("x : " + str(x))
                if id_to_session[x][0] == m1["sessionId"]:
                    isFound = True
                    id_to_session[x][1] = newId
                    id_to_session[x][2] = username
                    break
                else:
                    x = x + 1
            if isFound == False:
                id_to_session.extend(  [[m1["sessionId"] , newId, username, "None"]] ) 

            print(c_thread.execute("SELECT * FROM User").fetchall())
            return "USER CREATED"
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
            usernameMaybe = m1["inputTranscript"]
            print(usernameMaybe)
            query = """
                        SELECT COUNT(*) 
                        FROM User 
                        WHERE username = '{x}'
                    """.format(x=m1["inputTranscript"]) # find a user with this username, just the number of them to not leak data
            con_thread = sqlite3.connect("test.db")
            c_thread = con_thread.cursor()
            isUsernameIn = c_thread.execute(query).fetchall()[0][0]
            print(isUsernameIn)
            if int(isUsernameIn) > 0: # if there are usernames, lets get their passwords
                msg = "YES, ASK FOR PASSWORD"
                print(msg)
                x = 0
                isFound = False
                for i in id_to_session:
                    print("id to sesh: " + id_to_session[x][0])
                    print("x : " + str(x))
                    if id_to_session[x][0] == m1["sessionId"]:
                        isFound = True
                        break
                    else:
                        x = x + 1
                #while x < len(id_to_session) and isFound == False:
                #    if id_to_session[x][0] == m1["sessionId"]:
                #            isFound == True
                #    else:
                #        x = x + 1

                id_to_session[x][2] = m1["inputTranscript"] # and pair the username to the session
            elif isUsernameIn == 0:
                msg = "NO, ASK FOR USERNAME"
            
            print_id_to_session(id_to_session)
            return msg
            pass
        elif m1["diagnostics"] == "Diagnostic 03: IS PASSWORD VALID":
            x = 0
            isFound = False
            for i in id_to_session:
                print("id to sesh: " + id_to_session[x][0])
                print("x : " + str(x))
                if id_to_session[x][0] == m1["sessionId"]:
                    isFound = True
                    break
                else:
                    x = x + 1
            
            username = id_to_session[x][2]
            password = m1["inputTranscript"]
            isFoundQuery =  """
                                SELECT COUNT(*)
                                FROM User 
                                WHERE username = '{x}' AND password = '{y}'
                            """.format(x=username, y=password)
            query = """
                        SELECT id 
                        FROM User 
                        WHERE username = '{x}' AND password = '{y}'
                    """.format(x=username, y=password) # find a user id matching the username and password
            con_thread = sqlite3.connect("test.db")
            c_thread = con_thread.cursor()
            userId = "None"
            if c_thread.execute(isFoundQuery).fetchall()[0][0] > 0 :
                userId = c_thread.execute(query).fetchall()[0][0]

            if userId == "None":
                msg = "NO, RESTART AUTH"
                id_to_session[x][2] = "None"
            elif userId != "None":
                msg = "YES, USER LOGGED IN"
                id_to_session[x][1] = userId
            print_id_to_session(id_to_session)
            return msg

            pass
        elif m1["diagnostics"] == "Diagnostic XX: SEND TO LLM":
            
            print("")
            print("Sending to LLM")
            print("")
            x = 0
            isFound = False
            for i in id_to_session:
                print("id to sesh: " + id_to_session[x][0])
                print("x : " + str(x))
                if id_to_session[x][0] == m1["sessionId"]:
                    isFound = True
                    break
                else:
                    x = x + 1

            userId = id_to_session[x][1]
            print("Recieved: " + m1["inputTranscript"])
            print("From: " + str(userId) )
            print("Session #: " + m1["sessionId"])
            if chat_histories.get(userId) == None:
                chat_histories[userId] = []
            ai_msg = rag_chain.invoke(
                {
                    "question": m1["inputTranscript"],
                    "chat_history": chat_histories[userId]
                }
                )
            chat_histories[userId].extend(
                [
                    HumanMessage(content=m1["inputTranscript"]), ai_msg
                ]
                )
            print("AI: " + ai_msg)
            print("")
            con_thread = sqlite3.connect("test.db")
            c_thread = con_thread.cursor()
            numberOfUserMsgs = c_thread.execute("""
                                                SELECT COUNT(*) 
                                                FROM Chat 
                                                WHERE user_id = '{x}'
                                                """.format(x=userId)).fetchall()[0][0]
            #print_id_to_session(id_to_session)
            print("number of msgs from this user: " + str(numberOfUserMsgs))
            insertStmt =    """
                            INSERT INTO Chat(user_id, human, ai, msgOrder) 
                            VALUES ({user_id}, "{human}", "{ai}", {msgOrder})
                            """.format(user_id=userId, human=m1["inputTranscript"], ai=ai_msg, msgOrder=(numberOfUserMsgs+1))
            c_thread.execute(insertStmt) # will crash if ai creates a msg with double quotes in it (")
            con_thread.commit() # this has to be uncommented or else it wont be saved to the DB
            # the msg will be lost the moment this thread terminate, which is at 'return ai_msg'
            print("====== chat history ======")
            print("python dictionary")
            print(chat_histories[userId])
            print("")
            print("sql finds")
            print(c_thread.execute("select * from Chat where user_id = {uid}".format(uid=userId)).fetchall())

            return ai_msg

            pass
    
    
#'''
            

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=2000, allow_unsafe_werkzeug=True)

