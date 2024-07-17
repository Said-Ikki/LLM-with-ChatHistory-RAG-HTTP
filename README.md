# LLM-with-ChatHistory-RAG-HTTP

Note: whats missing is you need to create a test.db database with the correct columns
- the code to set that up is commnted out in ping.py
- you may need to insert some dummy records in there
  
you'll also need to download a lot of dependencies:
- langchain
- langchain-community
- bs4
- chromadb
- unstructured[all-docs]
- flask
- sqlite3
- googletrans==4.0.0-rc1

you also need the Ollama client ( I was working on Linux so I just curled it curl -fsSL https://ollama.com/install.sh | sh )

and pull llama3 and nomic-embed-text

don't forget gpu drivers if you can; its not necessary but it will speed up response time significantly

chromadb may have some build dependencies that you might need

hopefully this page helps you out there https://gist.github.com/ashmalvayani/ab3f4a8469fe3a2e9904c3a2674ea947

I'll need to revisit this to make sure I didn't miss any dependencies but those were the ones I remember off the top of my head
