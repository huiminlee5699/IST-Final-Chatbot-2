import streamlit as st
from openai import OpenAI
import time

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "Welcome to Chatbot, a new OpenAI-powered chatbot! "
    "Feel free to ask me anything!"
)

# Use the API key from Streamlit secrets
openai_api_key = st.secrets["openai_api_key"]

# Create an OpenAI client.
client = OpenAI(api_key=openai_api_key)

# Create a session state variable to store the chat messages. This ensures that the
# messages persist across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"],unsafe_allow_html=True)
        
# Create a chat input field to allow the user to enter a message. 
if prompt := st.chat_input("What would you like to know today?"):
    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Generate a response using the OpenAI API.
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ],
        stream=True,
    )
    
    time.sleep(1)
    
    # Stream the assistant response while building it up
    with st.chat_message("assistant"):
        response_container = st.empty()  # placeholder for streaming text
        full_response = ""
        
        # Count previous assistant messages
        assistant_messages = [
            msg for msg in st.session_state.messages if msg["role"] == "assistant"
        ]
        
        # If this is after the second assistant message (2nd, 4th, etc.), prepend the message
        prepend_message = ""
        if len(assistant_messages) == 1:  # Changed condition to display after 2nd response
            prepend_message = (
                "💡🧠🤓 <strong>Want to learn how I come up with responses?</strong>\n"
                "<a href=\"https://www.figma.com/proto/haXTVr4wZaeSC344BqDBpR/Text-Transparency-Card?page-id=0%3A1&node-id=1-33&p=f&viewport=144%2C207%2C0.47&t=Hp8ZCw5Fg7ahsiq1-8&scaling=min-zoom&content-scaling=fixed&hide-ui=1\" target=\"_blank\" style=\"color: #007BFF; text-decoration: none;\">\n"
                "Read more here →\n"
                "</a>\n\n ---------------- \n"
            )
              
            full_response += prepend_message
            response_container.markdown(full_response, unsafe_allow_html=True)
        
        # Continue streaming the assistant's response
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                response_container.markdown(full_response, unsafe_allow_html=True)
    
        # Store the final response in session state
        st.session_state.messages.append({"role": "assistant", "content": full_response})
