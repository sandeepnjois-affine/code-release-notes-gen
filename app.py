import openai
from openai import AzureOpenAI
import streamlit as st
import os

# Initialize the Azure OpenAI client

client = AzureOpenAI(
    azure_endpoint=st.secrets["AZURE_ENDPOINT"],
    api_version=st.secrets["AZURE_VERSION"],
    api_key=st.secrets["AZURE_KEY"])

model_name = st.secrets["AZURE_MODEL"]


# print(client)

def generate_release_notes_and_readme_from_files(old_file_path, new_file_path):
    """
    Compare old and new code files, generate release notes, and a README-like explanation.

    Parameters:
    old_file_path (str): Path to the file containing the old code.
    new_file_path (str): Path to the file containing the new code.

    Returns:
    dict: A dictionary containing the release notes and the README-like explanation in HTML.
    """
    try:
        # Read the content of the old and new files
        with open(old_file_path, 'r') as old_file:
            old_code = old_file.read()

        with open(new_file_path, 'r') as new_file:
            new_code = new_file.read()

        # Combine both pieces of code into a prompt for GPT
        prompt = f"""
        You are a software engineer specialized in code analysis. Your job is to:
        
        1. Generate **release notes** that highlight what has been added, removed, or modified between two versions of a code file.
        2. Create a **README-like explanation** describing the overall functionality of the updated code (new code). Include what it does and how it should be used by adding three sections:
            - Overview
            - Installation and dependencies
              * List all libraries used in the code and their one line explanation.
              * Provide pip installation instructions only for one library as an example.
            - How to use
            
        
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
         
        """

        # Call Azure OpenAI's GPT model
        completion = client.chat.completions.create(
            model=model_name,
            temperature=0.1,
            messages=[{'role': 'system', 'content': 'You are an insights generator and can also write Python code'},
                      {"role": "user", "content": prompt}])

        print(completion)
        content = completion.choices[0].message.content
        print(content)

        return {"html_output": content}
        

    except Exception as e:
        return {"error": f"Error generating release notes and README: {str(e)}"}

def main():
    # Initialize session state for the result if it doesn't exist
    if "result" not in st.session_state:
        st.session_state.result = None

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
    <span style='font-size: 40%;'>
    </span>
    </h2>
    </div>
    """, unsafe_allow_html=True)

    st.write("Upload two code files to generate release notes and a README-like explanation:")

    old_file = st.file_uploader("Upload Old Code File", type=["py", "txt"])
    new_file = st.file_uploader("Upload New Code File", type=["py", "txt"])

    if st.button("Generate"):
        with st.spinner('Wait for it...release notes and a README-like explanation:'):
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

                # Store result in session state
                st.session_state.result = result

                # Clean up temporary files
                os.remove(old_file_path)
                os.remove(new_file_path)
            else:
                st.warning("Please upload both files before clicking Generate.")

    # Display result if available in session state
    if st.session_state.result:
        result = st.session_state.result
        st.markdown(result["html_output"], unsafe_allow_html=True)

        # Provide download link for README
        readme_file_path = "generated_readme.md"
        with open(readme_file_path, "w") as readme_file:
            readme_file.write(result["html_output"])

        with open(readme_file_path, "rb") as readme_file:
            st.download_button(
                label="Download README.md",
                data=readme_file,
                file_name="README.md",
                mime="text/markdown"
            )

if __name__ == "__main__":
    main()