### Release Notes:
- Added:
  - No new features or functions were added.
- Removed:
  - No features or functions were removed.
- Modified:
  - No modifications were made to the code.

### README:

#### Overview
The `DocumentGeneration` class is designed to automate the process of generating HR documents by replacing placeholders in a document template with data from a CSV file. The class uses the Azure OpenAI service to generate text and fill in the placeholders. The generated documents can be downloaded individually or as a ZIP archive if multiple documents are generated.

#### Installation and dependencies
The code relies on several libraries to function correctly. Below is a list of the libraries used and their purpose:

- `openai`: Provides access to OpenAI's GPT models.
- `pandas`: Used for data manipulation and analysis.
- `docx`: Used to create and update Microsoft Word (.docx) files.
- `io`: Provides the `BytesIO` class for handling binary data.
- `urllib.parse`: Used for parsing URLs.
- `mimetypes`: Used to guess the MIME type of files.
- `base64`: Used for encoding and decoding base64 data.
- `re`: Provides regular expression matching operations.
- `os`: Provides a way of using operating system-dependent functionality.
- `time`: Provides various time-related functions.
- `streamlit`: Used for creating web apps.
- `zipfile`: Used for creating and extracting ZIP archives.

Example pip installation for one library:
```bash
pip install openai
```

#### How to use
1. **Initialization**: Create an instance of the `DocumentGeneration` class by providing the path to the document template, the data (as a pandas DataFrame), and the template name.
   ```python
   template = 'templates/Offshore_Appointment letter_with Relocation.docx'
   data = pd.read_excel('/path/to/data.xlsx')
   obj = DocumentGeneration(template_path=template, data=data, template='TemplateName')
   ```

2. **Generate Documents**: Call the `doc_gen_main` method to generate the documents. This method will return a buffer and a filename.
   ```python
   file_buffer, filename = obj.doc_gen_main()
   ```

3. **Download Documents**: The generated documents can be downloaded directly or as a ZIP archive if multiple documents are generated.

#### Error Handling
The code includes basic error handling, particularly when calling the GPT API. If an error occurs during the API call, the error message is printed, and the method returns the error and a `False` flag.

**Logical and Syntax Errors Check**:
- The code does not contain any syntax errors.
- Logical errors are handled by checking the success flag (`gpt_flag`) after calling the GPT API.
- The code ensures that placeholders are correctly identified and replaced in the document.
- The code handles both single and multiple document generation scenarios effectively.

Overall, the code is robust and should function as expected, provided the necessary dependencies are installed and the Azure OpenAI service is correctly configured.