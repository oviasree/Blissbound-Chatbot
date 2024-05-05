import streamlit as st
from streamlit_chat import message
import google.generativeai as genai
import utils as utils
from PIL import Image

def initialize_session_state():
    """
    Initialize session state variables.
    """
    st.session_state.setdefault('history', [])
    st.session_state.setdefault('generated', ["Hello! I am here to provide answers to questions fetched from Database."])
    st.session_state.setdefault('past', ["Hello Buddy!"])

def display_chat(conversation_chain, chain):
    """
    Display chat interface and process user input.
    """
    reply_container = st.container()
    container = st.container()
    with container:
        with st.form(key='chat_form', clear_on_submit=True):
            user_input = st.text_input("Question:", placeholder="Discuss with me to find clarity")
            submit_button = st.form_submit_button(label='Enter⬆️')
        
        if submit_button and user_input:
            output = generate_response(user_input, conversation_chain, chain)
            
    display_generated_responses(reply_container)


def generate_response(user_input, conversation_chain, chain):
    """
    Generate LLM response based on the user input.
    """
    with st.spinner('Generating response...'):
        response = conversation_chat(user_input, conversation_chain, chain, st.session_state['history'])
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(response)
        output = response
        

    return output

def conversation_chat(user_input, conversation_chain, chain, history):
    """
    Generate a response using conversational chain.
    """
    response = conversation_chain.invoke(user_input)
    final_response = chain.invoke(f"Based on the following information generate a human-readable response: {response['query']},  {response['result']}")
    history.append((user_input, final_response))
    return final_response

def display_generated_responses(reply_container):
    """
    Display generated responses to the UI.
    """
    with reply_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=f"{i}_user", avatar_style="big-smile")
            message(st.session_state["generated"][i], key=str(i), avatar_style="bottts")


def main():
    """
    Main function to run the Streamlit app.
    """
    initialize_session_state()
    
    image = Image.open('logo.jpg')
    st.image(image, width=150)

    st.title("Chat with bot")

    
    
    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

    conversation_chain, chain = utils.create_conversational_chain()

    display_chat(conversation_chain, chain)

if __name__ == "__main__":
    main()
