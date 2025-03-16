import streamlit as st
import openai
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Legal Document Generator",
    page_icon=":scroll:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize OpenAI client for OpenRouter
# Ensure your OpenRouter API key is stored in your secrets or replace st.secrets[...] with your key for testing.
openai.api_key = st.secrets["OPENROUTER_API_KEY"]
openai.api_base = "https://openrouter.ai/api/v1"

st.title("Legal Document Generator")
st.write("Generate customized legal documents with ease.")

# Sidebar: Select the document language
# List includes English plus several popular Indian languages.
languages = ["English", "Hindi", "Bengali", "Tamil", "Telugu", "Marathi", "Gujarati", "Kannada", "Malayalam"]
selected_language = st.sidebar.selectbox("Select Document Language:", languages)

# Sidebar for document configuration
st.sidebar.header("Document Configuration")
document_templates = {
    "Non-Disclosure Agreement": ["Party One Name", "Party Two Name", "Effective Date", "Confidential Information"],
    "Employment Contract": ["Employee Name", "Employer Name", "Job Title", "Start Date", "Salary"],
    "Lease Agreement": ["Lessor Name", "Lessee Name", "Property Address", "Lease Start Date", "Lease Term", "Monthly Rent"],
    "Sales Contract": ["Seller Name", "Buyer Name", "Item Description", "Sale Date", "Sale Price"],
    "Service Agreement": ["Service Provider Name", "Client Name", "Service Description", "Start Date", "Service Fee"]
}
selected_document = st.sidebar.selectbox("Select Document Type:", list(document_templates.keys()))

# Collect user inputs for the selected document type
user_inputs = {}
if selected_document:
    st.sidebar.subheader(f"{selected_document} Details")
    for field in document_templates[selected_document]:
        if "Date" in field:
            user_inputs[field] = st.sidebar.date_input(field)
        elif any(term in field for term in ["Salary", "Fee", "Rent", "Price"]):
            user_inputs[field] = st.sidebar.number_input(field, min_value=0.0, step=0.01)
        else:
            user_inputs[field] = st.sidebar.text_input(field)

# Function to generate content using DeepSeek via OpenRouter
def generate_with_deepseek(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="deepseek/deepseek-chat:free",
            messages=[
                {"role": "system", "content": "You are a legal document assistant."},
                {"role": "user", "content": prompt}
            ],
            extra_headers={
                "X-Title": "Legal Document Generator",  # Optional: Replace with your site's title
            },
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        st.error(f"Error generating content with DeepSeek: {e}")
        return ""

# Main content area: Display generated document
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("Generated Document")
    if st.button("Generate Document"):
        # Format dates as strings
        for key, value in user_inputs.items():
            if isinstance(value, datetime):
                user_inputs[key] = value.strftime("%B %d, %Y")
        # Construct the prompt to include the selected language.
        prompt = f"Generate a {selected_document} in {selected_language} with the following details:\n"
        for key, value in user_inputs.items():
            prompt += f"{key}: {value}\n"
        # Generate the document using DeepSeek via OpenRouter.
        generated_document = generate_with_deepseek(prompt)
        if generated_document:
            st.success("Document generated successfully!")
            st.text_area("Your Legal Document", value=generated_document, height=400)
        else:
            st.error("Failed to generate the document. Please try again.")
