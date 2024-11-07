import streamlit as st
from huggingface_hub import InferenceClient
from hf_utils import *
from streamlit_extras.grid import grid

# ---------set up page config -------------#
st.set_page_config(page_title="Cosmo the Chatdog",
                   layout="centered", page_icon="🐶", initial_sidebar_state="collapsed")

# ---------set button css-------------#
st.markdown(custom_css, unsafe_allow_html=True)

# --- Initialize the Inference Client with the API key ----#
client = InferenceClient(token=st.secrets["huggingfacehub_api_token"])

# ---------set model ------------#
model = {"qwen2.5-72b": "Qwen/Qwen2.5-72B-Instruct",
         "llama3.1-70b": "meta-llama/Meta-Llama-3.1-70B-Instruct",
         }

model_select = model["qwen2.5-72b"]

# ------- Store conversations with session state --------#
if 'msg_history' not in st.session_state:

    st.session_state.msg_history = []

    system_message = """You are Cosmo the friendly chatdog that provides helpful information.
    Look back at the chat history to find information if needed"""

    st.session_state.msg_history.append(
        {"role": "system", "content": f"{system_message}"})

# -------Write chat history to UI --------#
for msg in st.session_state.msg_history:
    if msg['role'] != "system":
        st.chat_message(msg["role"]).write(msg["content"])

# ------- Set up header --------#
with st.sidebar:
    st.subheader("Meet Sonic Cosmo")
    st.image("cosmo.jpg")
    st.write(intro)
# ------- Set up buttons --------#
button_pressed = ""

btn_grid = grid(2, gap='small', vertical_align="top")

if btn_grid.button(example_prompts[0]):
    button_pressed = example_prompts[0]

elif btn_grid.button(example_prompts[1]):
    button_pressed = example_prompts[1]

elif btn_grid.button(example_prompts[2]):
    button_pressed = example_prompts[2]

elif btn_grid.button(example_prompts[3]):
    button_pressed = example_prompts[3]

# ---- Input field for users to continue the conversation -----#
if user_input := (st.chat_input("Type your message or click a button...") or button_pressed):

    # Append the user's input to the msg_history
    st.session_state.msg_history.append(
        {"role": "user", "content": user_input})

    # write current chat on UI
    st.chat_message("user").write(user_input)

    # ---- find keys words to activate function and append to chat history ----#
    if contains_any_keyword(user_input, ["video"]):

        video_var = video_search(user_input)
        st.session_state.msg_history.append({"role": "system",
                                             "content": f"Here is the youtube video for {user_input} : {video_var}"})

    if contains_any_keyword(user_input, ["weather", "rain"]):

        st.session_state.msg_history.append(
            {"role": "system", "content": f"Here is the weather forecast for today - {datetime_var}: {weather_var}"})

    if contains_any_keyword(user_input, ["time", "date"]):

        st.session_state.msg_history.append(
            {"role": "system", "content": f"Here are the date and time for today: {datetime_var}"})

    if contains_any_keyword(user_input, ["news", "headlines", "headline"]):

        st.session_state.msg_history.append(
            {"role": "system", "content": f"These are the news headlines for today - {datetime_var} : {news_var}"})

    # ----- Create a placeholder for the streaming response ------- #
    with st.empty():
        # Stream the response
        stream = client.chat.completions.create(
            model=model_select,
            messages=st.session_state.msg_history,
            temperature=0.5,
            max_tokens=1524,
            top_p=0.7,
            stream=True,)

        # Initialize an empty string to collect the streamed content
        collected_response = ""

        # Stream the response and update the placeholder in real-time
        for chunk in stream:
            if 'delta' in chunk.choices[0] and 'content' in chunk.choices[0].delta:
                collected_response += chunk.choices[0].delta.content
                st.chat_message("assistant").write(collected_response)

    # Add the assistant's response to the conversation history
    st.session_state.msg_history.append(
        {"role": "assistant", "content": collected_response})

    # Keep history to 10, pop 2 item from the list
    if len(st.session_state.msg_history) >= 10:
        st.session_state.msg_history.pop(1)

    # play video if response contain youtube link but don't re-run script
    if "https://www.youtube.com/watch?" in collected_response and button_pressed != "Translate in Chinese":
        st.video(video_var)

    # rerun scripts for the other responses.
    else:
        st.rerun()
