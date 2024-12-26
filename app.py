import openai
from openai import AzureOpenAI
import streamlit as st
import os

# Initialize the Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=st.secrets["AZURE_ENDPOINT"],
    api_version=st.secrets["AZURE_VERSION"],
    api_key=st.secrets["AZURE_KEY"]
)

model_name = st.secrets["AZURE_MODEL"]

# Set up username and password
USERNAME = st.secrets["USERNAME"]
PASSWORD = st.secrets["PASSWORD"]

# Function to check authentication
def authenticate(username, password):
    return username == USERNAME and password == PASSWORD

# Function to generate release notes and README using Azure OpenAI
def generate_release_notes_and_readme_from_files(old_file_path, new_file_path):
    try:
        # Read the content of the old and new files
        with open(old_file_path, 'r') as old_file:
            old_code = old_file.read()

        with open(new_file_path, 'r') as new_file:
            new_code = new_file.read()

        # Prepare the prompt
        prompt = f"""
        You are a software engineer specialized in code analysis. Your job is to:
        
        1. Generate **release notes** that highlight what has been added, removed, or modified between two versions of a code file.
        2. Create a **README-like explanation** describing the overall functionality of the updated code (new code). Include what it does and how it should be used by adding three sections:
            - Overview
            - Installation and dependencies
              * List all libraries used in the code and their one line explanation.
              * Provide pip installation instructions only for one library as an example.
            - How to use
            - Error Handling
              * Check new_code file if it has any error (logical error, syntax error, etc.)
        
        Here are the two code versions:
        
        ### Old Code:
        {old_code}
        
        ### New Code:
        {new_code}
        
        Output format:
        - Release Notes:
          - Added:
          - Removed:
          - Modified:
        - README:
          - Overview
           - Installation and dependencies
            * Dependencies and its one line definition:
            * Installation:
           - How to use
            * Provide the complete "how to use" explantion with proper code and hightlight important words.
            * Provde the complete explanation with proper code and hightlight important words in "How to Use"
           - Error Handling:
            * Evaluate the uploaded new_code file to identify any syntax errors, logical issues, or deviations from the expected code flow by directly analyzing its content. If errors or mismatches are found:
            * Provide detailed feedback on the identified issues.
            * Suggest precise corrections and include a corrected code block.
        """

        # Call Azure OpenAI's GPT model
        completion = client.chat.completions.create(
            model=model_name,
            temperature=0.1,
            messages=[
                {'role': 'system', 'content': 'You are an insights generator and can also write Python code'},
                {"role": "user", "content": prompt}
            ]
        )

        content = completion.choices[0].message.content
        return {"html_output": content}

    except Exception as e:
        return {"error": f"Error generating release notes and README: {str(e)}"}

# Streamlit UI
def main():
    #st.title("Welcome")
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🌟 Welcome to Our Website! 🌟</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #555;'>We're delighted to have you here. Explore and enjoy!</h3>", unsafe_allow_html=True)
    st.divider()
    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "result" not in st.session_state:
        st.session_state.result = None

    if not st.session_state.authenticated:
        # Authentication form
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.success("Welcome, you are authenticated!")
            else:
                st.error("Invalid username or password.")
    else:
        # App Content after authentication
        st.markdown("""
        <div style='text-align: center; margin-top:-40px; margin-bottom: 5px;margin-left: -50px;'>
        <h2 style='font-size: 40px; font-family: Courier New, monospace;
                        letter-spacing: 2px; text-decoration: none;'>
        <img src="https://acis.affineanalytics.co.in/assets/images/logo_small.png" alt="logo" width="70" height="60">
        <span style='background: linear-gradient(45deg, #ed4965, #c05aaf);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                            text-shadow: none;'>
                    CodeGlance: AI-powered code insights
        </span>
        </h2>
        </div>
        """, unsafe_allow_html=True)

        st.write("Upload two code files to generate release notes and a README-like explanation:")

        old_file = st.file_uploader("Upload Old Code File", type=["py", "txt"], key="old_file")
        new_file = st.file_uploader("Upload New Code File", type=["py", "txt"], key="new_file")

        if st.button("Generate"):
            with st.spinner('Wait for it...Generating the release notes and a README-like explanation'):
                if old_file and new_file:
                    old_file_path = f"temp_old_{old_file.name}"
                    new_file_path = f"temp_new_{new_file.name}"

                    # Save uploaded files temporarily
                    with open(old_file_path, "wb") as f:
                        f.write(old_file.getbuffer())

                    with open(new_file_path, "wb") as f:
                        f.write(new_file.getbuffer())

                    # Generate release notes and README
                    result = generate_release_notes_and_readme_from_files(old_file_path, new_file_path)

                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.session_state.result = result

                    # Clean up temporary files
                    os.remove(old_file_path)
                    os.remove(new_file_path)
                else:
                    st.warning("Please upload both files before clicking Generate.")

        # Display the generated result if available
        if st.session_state.result:
            st.markdown(st.session_state.result["html_output"], unsafe_allow_html=True)

            # Provide download link for README
            readme_file_path = "generated_readme.md"
            with open(readme_file_path, "w") as readme_file:
                readme_file.write(st.session_state.result["html_output"])

            with open(readme_file_path, "rb") as readme_file:
                st.download_button(
                    label="Download README.md",
                    data=readme_file,
                    file_name="README.md",
                    mime="text/markdown"
                )

if __name__ == "__main__":
    main()






