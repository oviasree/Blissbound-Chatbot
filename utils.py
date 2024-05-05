import google.generativeai as genai

from langchain_community.utilities import SQLDatabase

from langchain_core.prompts import PromptTemplate

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.sql.base import SQLDatabaseChain
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.utilities import SQLDatabase
from langchain.memory import ConversationBufferMemory

import configparser
import os


def read_properties_file(file_path):
    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    
    # Initialize the configparser
    config = configparser.ConfigParser()
    
    # Read the properties file
    config.read(file_path)
    
    # Access values
    db_path = config['DEFAULT']['db_path']
    gemini_api_key = config['DEFAULT']['gemini_api_key']

    os.environ['GOOGLE_API_KEY'] = "AIzaSyDBNpex-TcGTD0U_pv4Qtjd-H-gNHyQ54U"
    genai.configure(api_key="AIzaSyDBNpex-TcGTD0U_pv4Qtjd-H-gNHyQ54U")
    return db_path, gemini_api_key

def get_property():
    # Path to the properties file
    file_path = 'configProperties.cfg'

    try:
        db_path, gemini_api_key = read_properties_file(file_path)
        print("Database path:", db_path)
        print("Gemini API Key", gemini_api_key)
        return db_path, gemini_api_key
    except FileNotFoundError as e:
        print(e)
        raise e
    
def get_llm(gemini_api_key):
    """
    Creata an instance of og Google Gemini Pro

    returns:
    - llm: An instance of Google Gemini Pro
    """
    # Create llm
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=gemini_api_key, convert_system_message_to_human=True, temperature=0.0)
    print(gemini_api_key)

    return llm

def db_connection(db_path):
    db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
    print(db.dialect)
    print(db.get_usable_table_names())
    resp1 = db.run("SELECT * FROM PROFILE;")
    resp2 = db.run("SELECT * FROM ACTIVITIES;")
    resp3 = db.run("SELECT * FROM EMOTIONS;")
    print("Profile Table")
    print(resp1)
    print()

    print("Activities undertaken")
    print(resp2)
    print()

    print("Emotions mapping")
    print(resp3)
    print()
    return db

def create_conversational_chain():

    try:
        db, gemini_api_key = get_property()

        # Get the instance of LLM
        llm = get_llm(gemini_api_key)
        # Get the DB connection
        db = db_connection(db)

        sql_prompt_template = """
        Only use the following tables:
        {table_info}
        Question: {input}

        Given an input question, first create a syntactically correct
        {dialect} query to run.
        
        Relevant pieces of previous conversation:
        {history}

        (You do not need to use these pieces of information if not relevant)
        Dont include ```, ```sql and \n in the output.
        """
        prompt = PromptTemplate(
                input_variables=["input", "table_info", "dialect", "history"],
                template=sql_prompt_template,
            )
        memory = ConversationBufferMemory(memory_key="history")

        
        db_chain = SQLDatabaseChain.from_llm(
                llm, db, memory=memory, prompt=prompt, return_direct=True,  verbose=True
            )

        output_parser = StrOutputParser()
        chain = llm | output_parser
        

    except Exception as e:
        raise e
    return  db_chain, chain