import sqlite3
from langchain_core.messages import AIMessage, HumanMessage

class Database:

    def new_user(username, password, session, id_to_session, self=None):


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
        print("similar users: " + str(similarUser) )
        if similarUser > 0:
                
                return "ERROR: USER ALREADY IN DATABASE"

        insertStmt =    """
                            INSERT INTO User(username, password, id)
                            VALUES ('{username}', '{password}', {id})
                            """.format(username=username, password=password, id=newId)
            
        c_thread.execute(insertStmt)
        con_thread.commit()
        x = 0
        isFound = False
        for i in id_to_session: # keep this one, its expected to fail so the return isn't so easy
                print("id to sesh: " + id_to_session[x][0])
                print("x : " + str(x))
                if id_to_session[x][0] == session:
                    isFound = True
                    id_to_session[x][1] = newId
                    id_to_session[x][2] = username
                    break
                else:
                    x = x + 1
        if isFound == False:
                id_to_session.extend(  [[session , newId, username, "None"]] ) 

        print(c_thread.execute("SELECT * FROM User").fetchall())
        return "USER CREATED"
    

    def check_username(usernameMaybe, session, id_to_session, self=None):
            print(usernameMaybe)
            query = """
                        SELECT COUNT(*) 
                        FROM User 
                        WHERE username = '{x}'
                    """.format(x=usernameMaybe) # find a user with this username, just the number of them to not leak data
            con_thread = sqlite3.connect("test.db")
            c_thread = con_thread.cursor()
            isUsernameIn = c_thread.execute(query).fetchall()[0][0]
            print(isUsernameIn)
            if int(isUsernameIn) > 0: # if there are usernames, lets get their passwords
                msg = "YES, ASK FOR PASSWORD"
                print(msg)
                x = find_id(session, id_to_session)

                id_to_session[x][2] = usernameMaybe# and pair the username to the session
            elif isUsernameIn == 0:
                msg = "NO, ASK FOR USERNAME"
            
            #print_id_to_session(id_to_session)
            return msg
    

    def check_username_password_pair(passcode, session, id_to_session, self=None):
            x = find_id(session, id_to_session)
            #print("""/n/n/n/n/n/n/n\n\n/n/n/n/n/n/n/n/n\n\n\n/n/n/n/n/n\nn\n\n\n""")
            #print("length: " + str(len(id_to_session)) )
            #print("x : " + str(x) )
            #print("username : " + id_to_session[x][2])
            username = id_to_session[x][2]
            password = passcode
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
            #print_id_to_session(id_to_session)
            return msg
    
    def clean_chat(chat, self=None):
        chat = chat.replace("\"", "")
        chat = chat.replace("\'", "")
        return chat

    def insert_chat(userId, ai_msg, human_msg, self=None):
            con_thread = sqlite3.connect("test.db")
            c_thread = con_thread.cursor()
            numberOfUserMsgs = c_thread.execute("""
                                                SELECT COUNT(*) 
                                                FROM Chat 
                                                WHERE user_id = '{x}'
                                                """.format(x=userId)).fetchall()[0][0]
            #print_id_to_session(id_to_session)
            print("number of msgs from this user: " + str(numberOfUserMsgs))
            human = Database.clean_chat(human_msg)
            #human = human_msg
            #human = human.replace("\"", "")
            #human = human.replace("\'", "")
            ai = Database.clean_chat(ai_msg)
            #ai = si_msg
            #ai = ai.replace("\"", "")
            #ai = ai.replace("\'", "")
            insertStmt =    """
                            INSERT INTO Chat(user_id, human, ai, msgOrder) 
                            VALUES ({user_id}, "{human}", "{ai}", {msgOrder})
                            """.format(user_id=userId, human=human, ai=ai, msgOrder=(numberOfUserMsgs+1))
            c_thread.execute(insertStmt) # will crash if ai creates a msg with double quotes in it (")
            con_thread.commit() # this has to be uncommented or else it wont be saved to the DB
            # the msg will be lost the moment this thread terminate, which is at 'return ai_msg'

    def load_chats(self=None):
        con = sqlite3.connect("test.db")
        cursor = con.cursor()

        user_id_list = cursor.execute("select distinct U.id from User U, Chat C where C.user_id = U.id").fetchall()
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
            
            x= 0 
            chats = cursor.execute(query).fetchall()
            #print(chats)
            for k in chats:
                human = chats[x][0]
                ai_msg = chats[x][1]
                print(human)
                print(ai_msg)
                print("")
                x = x + 1
                chat_histories[i].extend(
                    [
                        HumanMessage(content=human), AIMessage(ai_msg)
                    ]
                    )
            
        return chat_histories
    
def find_id(session, id_to_session):
        x = 0
        isFound = False
        print(id_to_session)
        print(session)
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





