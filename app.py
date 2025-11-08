import streamlit as st
import backend
import auth

def load_message_history():
    for msg in st.session_state['messages']:
        with st.chat_message(msg.get('role', 'assistant')):
            st.markdown(msg.get('content', ''), unsafe_allow_html=False)

# ====================================

st.set_page_config(layout="wide")
st.title("Mini-travel Application")
st.markdown("---")

# ==================== SIDE BAR
st.header("Account")
if "user" not in st.session_state:
    mode = st.segmented_control("Select mode:", ["Login", "Register"])

    if mode == "Login":
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            ok, msg = auth.login(username, password)
            if ok:
                st.rerun()
            else:
                st.error(msg)

    else:  # signup new
        new_user = st.text_input("New Username", key="reg_user")
        new_pass = st.text_input("New Password", type="password", key="reg_pass")
        if st.button("Register"):
            ok, msg = auth.register(new_user, new_pass)
            st.toast(msg)
            if ok:
                st.success("Now log in with your new account.")
    st.stop()
else:
    st.success(f"Logged in as: {st.session_state['user']}")
    if st.button("Logout"):
        del st.session_state["user"]
        st.rerun()
st.markdown("---")

# ==================== MAIN APP
st.subheader("LLM Connecting - Pinggy")
pg_link = st.text_input("Enter the Pinggy link that you got:")
if pg_link.endswith('/'):
    pg_link += "api/generate"
else:
    pg_link += "/api/generate"
st.link_button("Follow This Instruction to get Pinggy link", "https://colab.research.google.com/drive/1eVLijXZyvK5zibql8qJkEuROn3-MDhs5?usp=sharing")
st.markdown("*Note that the application cannot work without a valid Pinggy link.*")

st.markdown("---")

# create chat history in session state
if 'messages' not in st.session_state:
    # messages is a list of {'role': 'user'|'assistant', 'content': str}
    st.session_state['messages'] = []

col1, col2 = st.columns(2, border=True)
generate_button_clicked = False # For later signal sending of button clicking from column 1 to column 2 (i couldn't come up with any better way)

with col1:
    st.subheader("Referrence")

    org_city = st.text_input("Enter Departure:")
    des_city = st.text_input("Enter Destination:")
    start_date = st.date_input(
        "Enter Start Date:",
        min_value="today",
    )
    start_date = f"{start_date.day}-{start_date.month}-{start_date.year}"

    end_date = st.date_input(
        "Enter End Date:",
        min_value="today",
    )
    end_date = f"{end_date.day}-{end_date.month}-{end_date.year}"


    interests_options = [
        "Food",
        "Museums",
        "Nature",
        "Night-life",
    ]
    user_interests = st.pills(
        "Your Interests:", 
        interests_options,
        selection_mode="multi",
    )


    pace_options = [
        "Relaxed",
        "Normal",
        "Tight",
    ]
    pace_captions = [
        "Enjoy your trip without pressure",
        "Balance between speed and comfort",
        "Make the most out of your time",
    ]
    user_pace = st.radio(
        "Choose Your Preferred Pace:",
        pace_options,
        captions = pace_captions,    
    )
    if st.button("Generate Plan"):
        generate_button_clicked = True



with col2:
    st.subheader("Chat")
    # collect input here
    user_input = st.chat_input("Send a message")
    
    with st.container(height=600, border=True):
        load_message_history()

        if generate_button_clicked:
            with st.spinner("Generating plan...", show_time=True):
                LLM_display_text = backend.get_LLM_response(
                    pinggy_link=pg_link,
                    origin=org_city,
                    destination=des_city,
                    start_date=start_date,
                    end_date=end_date,
                    interests=user_interests,
                    pace=user_pace,
                )

            # append plan to chat history and display it
            st.session_state['messages'].append({
                'role': 'assistant',
                'content': LLM_display_text or "",
            })
            auth.save_history()
            with st.chat_message('assistant'):
                st.markdown(LLM_display_text, unsafe_allow_html=False)
        
        if user_input:
            # append user's message to history
            st.session_state['messages'].append({'role': 'user', 'content': user_input})
            auth.save_history()
            load_message_history()
            
            with st.spinner("Generating Answer...", show_time=True):
                # call backend with user_message and conversation history (backend will accept these optional params)
                LLM_reply = backend.get_LLM_response(
                    pinggy_link=pg_link,
                    origin=org_city,
                    destination=des_city,
                    start_date=start_date,
                    end_date=end_date,
                    interests=user_interests,
                    pace=user_pace,
                    user_message=user_input,
                    history=st.session_state['messages'],
                )

            st.session_state['messages'].append({'role': 'assistant', 'content': LLM_reply or ""})
            with st.chat_message('assistant'):
                st.markdown(LLM_reply, unsafe_allow_html=False)