
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain.tools import tool

import psycopg2
from dotenv import load_dotenv
import os



load_dotenv()

def get_connection():
    try:
        
        conn = psycopg2.connect("postgresql://postgres:hello@localhost:5432/langchain-agent")
        return conn
    except Exception as e:
        print(f"Encountered an error while connecting to the database\n ERROR: {e}")


@tool
def query_database(query: str, anything_to_return: bool) -> list[tuple] | None:
    """Execute a PostgreSQL query on the database"""
    conn = get_connection()
    print("Query is",query)
    curr = conn.cursor()
    try:
        curr.execute(query)
    except Exception as e:
        print(f"There is some problem with the prompt.\n EEROR: {e}")
        return [("NO DATA BECAUSE OF A TOOL ERROR")]
    if anything_to_return:
        data = curr.fetchall()
        conn.close()
        return data


model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.1,
    max_tokens = 1000,
    max_retries=2,
)
#The schema of its columns are as given below:
    #(video_id VARCHAR, user_id INT, channel_id INT, uploaded_duration TIME, uploaded_at TIMESTAMP)
system_prompt = """
You are a helpful assistant who queries a database.

Try to answer the questions of the user based on the database and only that.
"""

agent = create_agent(model = model, tools = [query_database], system_prompt = system_prompt)
messages = {"messages": []}

while True:
    prompt = str(input("USER:\n"))
    if not prompt:
        continue

    messages["messages"].append({"role" : "user", "content" : prompt})
    response = agent.invoke(messages)
    print("\nAGENT:\n")
    print(response["messages"][-1].content)
    messages["messages"] = response["messages"]
