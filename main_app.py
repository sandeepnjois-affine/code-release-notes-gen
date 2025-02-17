import streamlit as st


# Set up username and password
USERNAME = "admin"
PASSWORD = "password123"

# st.set_page_config(page_title="Streamlit Multi-Tab App", layout="wide")


# Function to check authentication
def authenticate(username, password):
    return username == USERNAME and password == PASSWORD


def main():
    # st.markdown("<h1 style='text-align: center; color: #4CAF50;'> CodeZen - AI coding companion </h1>", unsafe_allow_html=True)
    # st.markdown("<h3 style='text-align: center; color: #555;'>We're delighted to have you here. Explore and enjoy!</h3>", unsafe_allow_html=True)
    # st.divider()
    st.markdown("""
    <div style='text-align: center; margin-top:-40px; margin-bottom: 5px;margin-left: -50px;'>
    <h2 style='font-size: 40px; font-family: Courier New, monospace;
                    letter-spacing: 2px; text-decoration: none;'>
    <img src="https://acis.affineanalytics.co.in/assets/images/logo_small.png" alt="logo" width="70" height="60">
    <span style='background: linear-gradient(45deg, #ed4965, #c05aaf);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                            text-shadow: none;'>
                    CodeZen: AI-powered code companion
    </span>
    <span style='font-size: 40%;'>
    </span>
    </h2>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        # Authentication form
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid username or password.")
    else:
        st.write('Welcome!')





if __name__ == "__main__":
    main()