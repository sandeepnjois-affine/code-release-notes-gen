import streamlit as st
import importlib

# Set page configuration
st.set_page_config(page_title="Streamlit Multi-Tab App", layout="wide")

# Header Section
st.markdown("""
<div style='text-align: center; margin-top:-40px; margin-bottom: 5px; margin-left: -50px;'>
<h2 style='font-size: 40px; font-family: Courier New, monospace;
                letter-spacing: 2px; text-decoration: none;'>
<span style='background: linear-gradient(45deg, #ed4965, #c05aaf);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        text-shadow: none;'>
                CodeZen: AI-powered code companion
</span>
</h2>
</div>
""", unsafe_allow_html=True)

# Custom CSS for Background Highlighting
st.markdown(
    """
    <style>
    /* Default Button Styling */
    div.stButton > button {
        border-radius: 10px;
        padding: 8px;
        width: 100%;
        background-color: #0072B2;  /* Default color */
        color: white;
        font-weight: bold;
        border: none;
    }
    
    /* Button Hover Effect */
    div.stButton > button:hover {
        background-color: #005a8d;
    }

    /* Highlighted Background for Active Tab */
    .active-tab {
        background-color: #d6e6f2;  /* Light Blue Background for Active Tab */
        padding: 10px;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Define tab names
tabs = ["Code generation", "Code comparison", "Code Unit test", "Code quality", "Code conversion", "Code security"]

# Initialize session state for tab selection
if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = tabs[0]  # Default tab

# Create tab navigation using columns
cols = st.columns(len(tabs))

# Render tabs with background highlighting for active tab
for i, tab in enumerate(tabs):
    if tab == st.session_state.selected_tab:
        with cols[i]:
            st.markdown(f"<div class='active-tab' style='text-align: center;'><b>{tab}</b></div>", unsafe_allow_html=True)
    else:
        if cols[i].button(tab, key=tab):
            st.session_state.selected_tab = tab  # Update session state
            st.rerun()  # Force rerun to update UI

st.divider()

# Dictionary to map tab names to module files
tab_modules = {
    "Code generation": "code_generation",
    "Code comparison": "code_comparison",
    "Code Unit test": "code_unit_test",
    "Code quality": "code_quality",
    "Code conversion": "code_conversion",
    "Code security": "code_security",
}

# Dynamically import and run the selected tab module
module_name = tab_modules[st.session_state.selected_tab]
module = importlib.import_module(module_name)

# Use the full width to display tab content
with st.container():
    if hasattr(module, "main"):
        module.main()
    else:
        st.error(f"Module {module_name} is missing a main() function.")
