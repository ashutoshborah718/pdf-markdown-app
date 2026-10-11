import streamlit as st
import pymupdf

# Page config
st.set_page_config(page_title="PDF to Markdown Converter", page_icon="📄", layout="centered")

st.title("📄 PDF to Markdown & Operations Hub")
st.write("Upload any PDF, convert it instantly to clean Markdown, and perform file operations.")

# File uploader widget
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    # Read PDF bytes
    bytes_data = uploaded_file.read()
    
    # Open with PyMuPDF
    doc = pymupdf.open(stream=bytes_data, filetype="pdf")
    
    st.success(f"Successfully loaded PDF! Total pages: {len(doc)}")
    
    # Select operation
    operation = st.selectbox(
        "Choose an Operation", 
        ["Convert to Markdown", "Extract All Text"]
    )
    
    if operation == "Convert to Markdown":
        markdown_content = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            markdown_content.append(f"## Page {page_num + 1}\n")
            markdown_content.append(text)
            markdown_content.append("\n---\n")
            
        final_md = "\n".join(markdown_content)
        
        st.subheader("Markdown Preview")
        st.text_area("Raw Markdown", final_md, height=300)
        
        # Download button
        st.download_button(
            label="Download .md File",
            data=final_md,
            file_name="converted_document.md",
            mime="text/markdown"
        )
        
    elif operation == "Extract All Text":
        all_text = ""
        for page in doc:
            all_text += page.get_text("text") + "\n"
        
        st.text_area("Extracted Plain Text", all_text, height=300)
        st.download_button(
            label="Download .txt File",
            data=all_text,
            file_name="extracted_text.txt",
            mime="text/plain"
        )
