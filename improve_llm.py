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

class LLM:
    def initialize_standalones(self):


        self.DOCS_PATH = "./dummy_docs"#./docs

        self.contextualize_q_system_prompt = """Given a chat history and the latest user question \
            which might reference context in the chat history, formulate a standalone question \
            which can be understood without the chat history. Do NOT answer the question, \
            just reformulate it if needed and otherwise return it as is."""

        self.qa_system_prompt = """You are an assistant for question-answering tasks. \
            You are not an agent, you simply use data provided by agents to answer basic prompts a user has. \
            Use the following information to provide accurate answers but act as if you knew this information innately.\
            If you do not see any relevant information in the provided documents, simply state that you don't know. \
            You will see transcripts in the information provided. There will be a |User role and an AI bot role. \
            If a user asks a question similarly to what is in the transcript, give them all the information 
            the AI bot role would give without waiting for user confirmation. \
            If unsure, simply state that you don't know.\
            {context}"""
        

        self.llm = Ollama(model = "llama3")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap = 200,
            add_start_index = True  
        )
        self.docs = DirectoryLoader(
            path=self.DOCS_PATH,
            loader_cls=UnstructuredFileLoader,
        )
        self.embedding = embeddings.OllamaEmbeddings(
            model="nomic-embed-text"
        )

        self.all_splits = None
        self.vectorstore = None
        self.retriever = None

        self.contextualize_q_prompt = None
        self.contextualize_q_chain = None
        self.qa_prompt = None
        
        #self.rag_chain = None
        
    # format docs
    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # make 'context'
    def contextualized_question(self, input: dict):
        if input.get("chat_history"):
            q = self.contextualize_q_chain
            return q
        else:
            return input["question"]

    def contextualize_initialize(self):
        self.contextualize_q_prompt= ChatPromptTemplate.from_messages(
            [
                ("system", self.contextualize_q_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{question}"),
            ]
        )
        self.contextualize_q_chain = self.contextualize_q_prompt | self.llm | StrOutputParser()
        self.qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.qa_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{question}"),
            ]
        )
        pass

    def docs_db_initialize(self):
        #self.initialize_standalones()
        print("load and split docs")
        self.all_splits = self.text_splitter.split_documents(self.docs.load())
        print('set up vectore store')
        # hold documents in vector store
        self.vectorstore = Chroma.from_documents(
            documents = self.all_splits,
            embedding = self.embedding
        )
        print('set up retriever')
        # retriever part of the RAG
        self.retriever = self.vectorstore.as_retriever(
            search_type = "similarity",
            search_kwargs = {"k":6}
        )
        pass

    def ask(self, inp, chat_history):
        ai_msg = self.rag_chain.invoke(
            {
                "question": inp,
                "chat_history": chat_history
            }
        )
        return ai_msg
    

    def __init__(self):
        self.initialize_standalones()
        self.docs_db_initialize()
        self.contextualize_initialize()
        self.rag_chain = (
            RunnablePassthrough.assign(
                context = self.contextualized_question | self.retriever | self.format_docs
            )
            | self.qa_prompt
            | self.llm
        )

        pass

    

#ultimate_move = LLM()
'''
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
    #path=./docs",
    path="./dummy_docs",
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
You are not an agent, you simply use data provided by agents to answer basic prompts a user has. \
Use the following information to provide accurate answers but act as if you knew this information innately.\
If you do not see any relevant information in the provided documents, simply state that you don't know. \
You will see transcripts in the information provided. There will be a |User role and an AI bot role. \
If a user asks a question similarly to what is in the transcript, give them all the information the AI bot role would give without waiting for user confirmation. \
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
'''
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