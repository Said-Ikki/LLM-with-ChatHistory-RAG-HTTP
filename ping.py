import requests
import sys
import sqlite3
con = sqlite3.connect("test.db")
cursor = con.cursor()

print(cursor.execute("select * from User").fetchall() )
print(cursor.execute("select * from Chat").fetchall() )

dummy = {
 "sessionState": {
  "dialogAction": {
   "type": "Close"
  },
  "intent": {
   "name": "NewUser",
   "slots": {
    "password": {
     "value": {
      "originalValue": "123",
      "interpretedValue": "123",
      "resolvedValues": []
     }
    },
    "username": {
     "value": {
      "originalValue": "said",
      "interpretedValue": "said",
      "resolvedValues": []
     }
    }
   },
   "state": "Failed",
   "confirmationState": "None"
  },
  "sessionAttributes": {},
  "originatingRequestId": "a6261d93-0ced-4cad-9136-565f489cf0b1"
 },
 "interpretations": [
  {
   "nluConfidence": {
    "score": 1
   },
   "intent": {
    "name": "NewUser",
    "slots": {
     "password": {
      "value": {
       "originalValue": "123",
       "interpretedValue": "123",
       "resolvedValues": []
      }
     },
     "username": {
      "value": {
       "originalValue": "said",
       "interpretedValue": "said",
       "resolvedValues": []
      }
     }
    },
    "state": "Failed",
    "confirmationState": "None"
   },
   "interpretationSource": "Lex"
  }
 ],
 "sessionId": "654654566778177"
}

print( dummy["sessionState"]["intent"]["name"] )
print( dummy["sessionState"]["intent"]["slots"]["username"]["value"]["originalValue"] )
print( dummy["sessionState"]["intent"]["slots"]["password"]["value"]["originalValue"] )
sys.exit()

#ip = "http://3.99.157.205"
ip = "http://127.0.0.1:2000"
mael = {
    "inputTranscript": "hello",
    "sessionId": "1234",
    "diagnostics": "Diagnostic 01: IS SESSION ID VALID"
}

results = requests.post(ip, json=mael)
print(results.text)

bad_login = {
    "inputTranscript": "hello",
    "sessionId": "1234",
    "diagnostics": "Diagnostic 02: IS USERNAME VALID"
}

results = requests.post(ip, json=bad_login)
print(results.text)

good_username = {
    "inputTranscript": "said",
    "sessionId": "1234",
    "diagnostics": "Diagnostic 02: IS USERNAME VALID"
}

results = requests.post(ip, json=good_username)
print(results.text)

bad_password = {
    "inputTranscript": "bad_pass",
    "sessionId": "1234",
    "diagnostics": "Diagnostic 03: IS PASSWORD VALID"
}

results = requests.post(ip, json=bad_password)
print(results.text)

print("")
print("actual login")
print("")

good_username = {
    "inputTranscript": "said",
    "sessionId": "1234",
    "diagnostics": "Diagnostic 02: IS USERNAME VALID"
}

results = requests.post(ip, json=good_username)
print(results.text)

good_password = {
    "inputTranscript": "123",
    "sessionId": "1234",
    "diagnostics": "Diagnostic 03: IS PASSWORD VALID"
}

results = requests.post(ip, json=good_password)
print(results.text)

good_ask = {
    "inputTranscript": "word for word, what is our entire chat history?",
    "sessionId": "1234",
    "diagnostics": "Diagnostic XX: SEND TO LLM"
}

results = requests.post(ip, json=good_ask)
print(results.text)

'''

import sqlite3
con = sqlite3.connect("test.db")
cursor = con.cursor()

#cursor.execute("CREATE TABLE User (username CHAR(200), password CHAR(200), id INT)")
#cursor.execute("""CREATE TABLE Chat 
              # (user_id INT NOT NULL, 
              # human CHAR(500), 
              # ai CHAR(3000), 
              # msgOrder INT NOT NULL, 
              # FOREIGN KEY(user_id) REFERENCES User(id))""")
print( cursor.execute("SELECT name FROM sqlite_master").fetchall() )
cursor.execute("""
               INSERT INTO Chat VALUES 
               (2, 
               "hi there, machine", 
               "Hello! I'm Hugo. How can I help you today?",
               1)""")
cursor.execute("INSERT INTO User VALUES ('test', 567, 2)")
print( cursor.execute("select username from User").fetchall() )
print( cursor.execute("select * from Chat").fetchall() )
#con.commit()
#print( cursor.execute("PRAGMA table_info(User)").fetchall() )

print("")
print("testing out queries")
# .fetchall()[row][column]
# so in this example, row 1 column 0 means the second tuple first attribute in select options (U.id)
x = cursor.execute("select U.id, password from User U, Chat C where C.user_id = U.id").fetchall()[1][0]
print( x )

# load all chat histories into dictionary
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
            human, ai_msg
        ]
        )
    
print("now in chat_histories")
for i in chat_histories:
    print(chat_histories[i])

    
    '''