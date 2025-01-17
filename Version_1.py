import os
import subprocess
import tempfile
from pathlib import Path
import streamlit as st
import openai
from openai import AzureOpenAI
import stat
import shutil  # For cleaning up the temporary directory

# Initialize the Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint="https://aipractices.openai.azure.com/",
    api_version="2024-02-01",
    api_key="e5990e77abe04e74b6de34cdb4d1cce4"
)

model_name = 'gpt-4o-08-06'

# Set up username and password
USERNAME = "admin"
PASSWORD = "password123"

# Function to check authentication
def authenticate(username, password):
    return username == USERNAME and password == PASSWORD

# Function to handle file removal errors
def on_rm_error(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)  # Change the file to writable
    func(path)  # Retry the operation

# Function to clone a repository at a specific commit
def clone_repo_at_commit(github_url, commit_id):
    try:
        temp_dir = tempfile.mkdtemp()
        print(f"Cloning repository for commit {commit_id} into {temp_dir}...")

        # Clone the repository
        result_clone = subprocess.run(
            ["git", "clone", github_url, temp_dir],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"Clone output: {result_clone.stdout}")

        # Checkout the specified commit
        result_checkout = subprocess.run(
            ["git", "checkout", commit_id],
            cwd=temp_dir,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"Checkout output: {result_checkout.stdout}")

        return temp_dir

    except subprocess.CalledProcessError as e:
        print(f"Error during Git operation: {e.stderr}")
        return None
    except Exception as ex:
        print(f"Unexpected error: {ex}")
        return None

# Function to fetch recent commits
def get_recent_commits(github_url):
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Clone the repository
            clone_result = subprocess.run(
                ["git", "clone", "--bare", github_url, temp_dir],
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"Clone output: {clone_result.stdout}")
            print(f"Clone errors: {clone_result.stderr}")
            
            # Fetch commit hashes and messages
            log_result = subprocess.run(
                ["git", "log", "--pretty=%H|||%s"],  # Fetch full SHA and message
                cwd=temp_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"Git log output: {log_result.stdout}")
            
            # Parse the output into (commit_id, message) tuples
            commits = [
                tuple(line.split("|||", 1)) for line in log_result.stdout.splitlines() if "|||" in line
            ]
            print(f"Valid commits: {commits}")
            return commits
        except subprocess.CalledProcessError as e:
            print("Error:", e)
            print("Command output:", e.output)
            return []

# Function to find common files
def find_common_files(dir1, dir2):
    files1 = {file.name for file in Path(dir1).rglob("*") if file.is_file() and file.name.endswith('.py')}
    files2 = {file.name for file in Path(dir2).rglob("*") if file.is_file() and file.name.endswith('.py')}
    return files1.intersection(files2)

# Function to generate release notes and README
def generate_release_notes_and_readme(old_file_path, new_file_path):
    try:
        with open(old_file_path, 'r') as old_file:
            old_code = old_file.read()

        with open(new_file_path, 'r') as new_file:
            new_code = new_file.read()

        prompt = f"""
        You are a software engineer specialized in code analysis. Your job is to:
        
        1. Generate **release notes** that highlight what has been added, removed, or modified between two versions of a code file.
        2. Create a **README-like explanation** describing the overall functionality of the updated code (new code). Include the following sections:
            - Overview
            - Installation and dependencies
              * List all libraries used in the code and their one-line explanation.
              * Provide pip installation instructions for one library as an example.
            - How to use
            - Error Handling
              * Check new_code for errors (logical, syntax, etc.).
        
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
          - How to use
          - Error Handling
        """

        completion = client.chat.completions.create(
            model=model_name,
            temperature=0.1,
            messages=[{'role': 'system', 'content': 'You are an insights generator and can also write Python code.'},
                      {"role": "user", "content": prompt}]
        )

        return {
            "html_output": completion.choices[0].message.content
        }
    except Exception as e:
        return {"html_output": f"Error generating release notes and README: {str(e)}"}

# Main function
def main():
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
        st.markdown("""<div style='text-align: center; margin-top:-40px; margin-bottom: 5px;margin-left: -50px;'>
                        <h2 style='font-size: 40px; font-family: Courier New, monospace; letter-spacing: 2px; text-decoration: none;'>
                        <img src="https://acis.affineanalytics.co.in/assets/images/logo_small.png" alt="logo" width="70" height="60">
                        <span style='background: linear-gradient(45deg, #ed4965, #c05aaf); -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent; text-shadow: none;'> CodeGlance: AI-powered code insights </span> </h2> </div>""", unsafe_allow_html=True)

        # File Upload or GitHub URL
        upload_option = st.radio("Select upload option:", ("Upload Files from Device", "GitHub Link"))

        if upload_option == "Upload Files from Device":
            st.write("Upload two code files to generate release notes and a README-like explanation:")
            old_file = st.file_uploader("Upload Old Code File", type=["py", "txt"], key="old_file")
            new_file = st.file_uploader("Upload New Code File", type=["py", "txt"], key="new_file")

            if st.button("Generate"):
                if old_file and new_file:
                    old_file_path = f"temp_old_{old_file.name}"
                    new_file_path = f"temp_new_{new_file.name}"

                    # Save uploaded files temporarily
                    with open(old_file_path, "wb") as f:
                        f.write(old_file.read())

                    with open(new_file_path, "wb") as f:
                        f.write(new_file.read())

                    # Generate release notes and README
                    result = generate_release_notes_and_readme(old_file_path, new_file_path)

                    if result:
                        st.session_state.result = result
                        st.markdown(result["html_output"], unsafe_allow_html=True)

                    # Clean up temporary files
                    os.remove(old_file_path)
                    os.remove(new_file_path)
                else:
                    st.warning("Please upload both files before clicking Generate.")

        elif upload_option == "GitHub Link":
            github_url = st.text_input("Enter the GitHub repository URL:")

            if github_url:
                # Add the "Generate" button for the user to trigger the action
                if st.button("Generate"):
                    st.write("Fetching recent commits...")
                    commits = get_recent_commits(github_url)

                    if len(commits) < 2:
                        st.error("The repository has fewer than two commits. Comparison cannot proceed.")
                        return

                    st.write(f"Recent commits:\n1. {commits[0][0]} - {commits[0][1]}\n2. {commits[1][0]} - {commits[1][1]}")  


                    # Correct the error: Extract only the commit hash (the first item in the tuple)
                    dir1 = clone_repo_at_commit(github_url, commits[0][0])  # Use commit hash, not the full tuple
                    dir2 = clone_repo_at_commit(github_url, commits[1][0])  # Use commit hash, not the full tuple
                    

                    if dir1 is None or dir2 is None:
                        st.error("Failed to clone one or both commits.")
                        return

                    # Find common files and process them
                    common_files = find_common_files(dir1, dir2)


                    if not common_files:
                        st.warning("No common files found between the two commits.")
                    else:
                        st.write("Common files found:")
                        selected_file = st.selectbox("Select a file to compare:", list(common_files))

                        file1_path = Path(dir1) / selected_file
                        file2_path = Path(dir2) / selected_file

                        if file1_path.exists() and file2_path.exists():
                            release_notes = generate_release_notes_and_readme(file1_path, file2_path)
                            st.markdown(release_notes["html_output"], unsafe_allow_html=True)


                            # Provide download link for README  
                            readme_file_path = "generated_readme.md"  
                            with open(readme_file_path, "w") as readme_file:  
                                readme_file.write(release_notes["html_output"])  
  
                            with open(readme_file_path, "rb") as readme_file:  
                                st.download_button(  
                                    label="Download README.md",  
                                    data=readme_file,  
                                    file_name="README.md",  
                                    mime="text/markdown"  
                                )  
  
                            # Clean up the temporary directories  
                            shutil.rmtree(dir1, onerror=on_rm_error)  
                            shutil.rmtree(dir2, onerror=on_rm_error) 


                        else:
                            st.error("The selected file does not exist in one or both commits.")

                            

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
