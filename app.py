import streamlit as st
import pymupdf
from PIL import Image
import io

# 1. Page Configuration & Custom CSS Styling
st.set_page_config(
    page_title="Doc & Image Hub", 
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FF4B4B;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6c757d;
        margin-bottom: 30px;
    }
    .card {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Sidebar Navigation with Styling
st.sidebar.markdown("### 🎛️ Navigation Hub")
tool_category = st.sidebar.radio("Select Toolset", ["📄 PDF Studio", "🖼️ Image Studio"])

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Upload your file first, choose an operation, and click run to process instantly!")

# ==================== PDF STUDIO ====================
if tool_category == "📄 PDF Studio":
    st.markdown('<p class="main-header">📄 Advanced PDF Studio</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Convert, extract text, and pull assets out of your documents instantly.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📤 Upload PDF")
        uploaded_pdf = st.file_uploader("Choose a PDF file", type=["pdf"], key="pdf_up")
        
        pdf_operation = st.selectbox(
            "🛠️ Choose Operation", 
            ["Convert to Markdown", "Extract All Text", "Extract Embedded Images"]
        )

    with col2:
        if uploaded_pdf is not None:
            doc = pymupdf.open(stream=uploaded_pdf.read(), filetype="pdf")
            
            st.markdown(f"""
                <div class="card">
                    <h4>📊 File Summary</h4>
                    <p><b>Filename:</b> {uploaded_pdf.name}</p>
                    <p><b>Total Pages:</b> {len(doc)}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if pdf_operation == "Convert to Markdown":
                if st.button("🚀 Run Markdown Conversion", type="primary"):
                    with st.spinner("Converting document structure..."):
                        markdown_content = []
                        for i, page in enumerate(doc):
                            markdown_content.append(f"## Page {i + 1}\n{page.get_text('text')}\n\n---\n")
                        final_md = "".join(markdown_content)
                    
                    st.success("Conversion completed successfully!")
                    st.text_area("📝 Markdown Output Preview", final_md, height=250)
                    st.download_button("📥 Download .md File", final_md, file_name="converted_document.md", mime="text/markdown")
                    
            elif pdf_operation == "Extract All Text":
                if st.button("🚀 Extract Plain Text", type="primary"):
                    with st.spinner("Extracting text layers..."):
                        all_text = "".join([page.get_text("text") + "\n" for page in doc])
                    
                    st.success("Extraction completed!")
                    st.text_area("📝 Text Output Preview", all_text, height=250)
                    st.download_button("📥 Download .txt File", all_text, file_name="extracted_text.txt", mime="text/plain")
                    
            elif pdf_operation == "Extract Embedded Images":
                if st.button("🚀 Scan & Extract Images", type="primary"):
                    image_count = 0
                    with st.spinner("Scanning pages for embedded media..."):
                        for i, page in enumerate(doc):
                            image_list = page.get_images(full=True)
                            for img_index, img in enumerate(image_list):
                                xref = img[0]
                                base_image = doc.extract_image(xref)
                                image_bytes = base_image["image"]
                                image_ext = base_image["ext"]
                                image_count += 1
                                
                                st.image(image_bytes, caption=f"Page {i + 1} - Image {img_index + 1}", width=250)
                                st.download_button(
                                    label=f"📥 Download Image {image_count} ({image_ext})",
                                    data=image_bytes,
                                    file_name=f"p{i+1}_img_{img_index+1}.{image_ext}",
                                    mime=f"image/{image_ext}",
                                    key=f"dl_img_{i}_{img_index}"
                                )
                    if image_count == 0:
                        st.info("No embedded raster images found in this PDF.")
        else:
            st.info("👈 Please upload a PDF file using the left panel to get started.")

# ==================== IMAGE STUDIO ====================
elif tool_category == "🖼️ Image Studio":
    st.markdown('<p class="main-header">🖼️ Advanced Image Studio</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Resize, apply grayscale filters, and change image formats seamlessly.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📤 Upload Image")
        uploaded_img = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg", "webp"], key="img_up")
        
        img_operation = st.selectbox(
            "🛠️ Choose Operation", 
            ["Convert Format (PNG/JPG/WEBP)", "Resize Dimensions", "Apply Grayscale Filter"]
        )

    with col2:
        if uploaded_img is not None:
            image = Image.open(uploaded_img)
            
            st.markdown(f"""
                <div class="card">
                    <h4>📊 Image Properties</h4>
                    <p><b>Dimensions:</b> {image.width} x {image.height} px</p>
                    <p><b>Format:</b> {image.format}</p>
                    <p><b>Color Mode:</b> {image.mode}</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.image(image, caption="Original Image Preview", use_container_width=True)
            
            if img_operation == "Convert Format (PNG/JPG/WEBP)":
                target_format = st.selectbox("Select Target Format", ["PNG", "JPEG", "WEBP"])
                if st.button("🚀 Convert Format", type="primary"):
                    buf = io.BytesIO()
                    save_img = image
                    if target_format == "JPEG" and image.mode in ("RGBA", "P"):
                        save_img = image.convert("RGB")
                    
                    save_img.save(buf, format=target_format)
                    byte_im = buf.getvalue()
                    
                    st.success(f"Successfully converted to {target_format}!")
                    st.download_button(
                        label=f"📥 Download {target_format} Image",
                        data=byte_im,
                        file_name=f"converted_image.{target_format.lower()}",
                        mime=f"image/{target_format.lower()}"
                    )
                    
            elif img_operation == "Resize Dimensions":
                new_w = st.number_input("New Width (px)", value=image.width)
                new_h = st.number_input("New Height (px)", value=image.height)
                if st.button("🚀 Resize Image", type="primary"):
                    resized_img = image.resize((int(new_w), int(new_h)))
                    st.image(resized_img, caption="Resized Result", use_container_width=True)
                    
                    buf = io.BytesIO()
                    resized_img.save(buf, format=image.format if image.format else "PNG")
                    st.download_button(
                        label="📥 Download Resized Image",
                        data=buf.getvalue(),
                        file_name=f"resized_image.{image.format.lower() if image.format else 'png'}"
                    )
                    
            elif img_operation == "Apply Grayscale Filter":
                if st.button("🚀 Apply Filter", type="primary"):
                    gray_img = image.convert("L")
                    st.image(gray_img, caption="Grayscale Result", use_container_width=True)
                    
                    buf = io.BytesIO()
                    gray_img.save(buf, format="PNG")
                    st.download_button(
                        label="📥 Download Grayscale Image",
                        data=buf.getvalue(),
                        file_name="grayscale_image.png",
                        mime="image/png"
                    )
        else:
            st.info("👈 Please upload an image file using the left panel to get started.")
