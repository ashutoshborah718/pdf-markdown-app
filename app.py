import streamlit as st
import pymupdf
from PIL import Image
import numpy as np
import cv2
import io
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Page Configuration
st.set_page_config(
    page_title="Ashutosh Studio | Multi-Page Enterprise Suite", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS Styling & App-Like Theme
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #60a5fa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: #9ca3af;
        margin-bottom: 25px;
    }
    .app-card {
        background: rgba(17, 24, 39, 0.75);
        border: 1px solid rgba(75, 85, 99, 0.4);
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 8px 16px -4px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
    }
    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== MULTI-PAGE ROUTER ====================
st.sidebar.markdown("### ⚡ ASHUTOSH STUDIO")
st.sidebar.markdown("<p style='font-size: 0.85rem; color: #9ca3af;'>Multi-Page Enterprise Hub<br>Architect: <b>Ashutosh Borah</b></p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

selected_page = st.sidebar.radio(
    "🧭 Navigation Directory", 
    [
        "🏠 Home & Overview", 
        "📄 Document Intelligence Hub", 
        "👁️ Computer Vision & Lab", 
        "🖼️ Media & Image Studio"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **System Status:** All micro-services online & operational.")

# Helper utilities
def pil_to_cv2(pil_img):
    arr = np.array(pil_img)
    if len(arr.shape) == 2: return arr
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

def cv2_to_pil(cv2_img):
    if len(cv2_img.shape) == 2: return Image.fromarray(cv2_img)
    return Image.fromarray(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB))


# ==================== PAGE 0: HOME & OVERVIEW ====================
if selected_page == "🏠 Home & Overview":
    st.markdown('<p class="hero-title">Welcome to Ashutosh Studio 🚀</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">An enterprise-grade platform built for seamless document conversion, advanced document formatting, and computer vision operations.</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="app-card">
                <h3>📄 Document Suite</h3>
                <p style="color: #9ca3af; font-size: 0.9rem;">Convert PDF to Markdown, PDF to Word (DOCX), Word to PDF, merge queues, compile images to PDF, and generate word clouds.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
            <div class="app-card">
                <h3>👁️ Computer Vision</h3>
                <p style="color: #9ca3af; font-size: 0.9rem;">Apply low-light Retinex/CLAHE enhancement, multi-channel color splitting, Canny edge detection, and Otsu contour segmentation.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
            <div class="app-card">
                <h3>🖼️ Media Studio</h3>
                <p style="color: #9ca3af; font-size: 0.9rem;">Batch resize image dimensions, optimize quality compression ratios, and apply pixel-level filters effortlessly.</p>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("### 🌐 Quick Launch Directory")
    st.info("👈 Use the **Navigation Directory** in the sidebar to switch between suites.")


# ==================== PAGE 1: DOCUMENT INTELLIGENCE ====================
elif selected_page == "📄 Document Intelligence Hub":
    st.markdown('<p class="hero-title">📄 Document Intelligence Suite</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Convert between PDF, Word, and Markdown, merge files, compress documents, and run visual analytics.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        st.markdown("### ⚙️ Pipeline Controls")
        doc_task = st.selectbox("Select Tool Mode", [
            "Convert PDF to Markdown", 
            "Convert PDF to Word (.docx)",
            "Convert Word to PDF (.pdf)",
            "Merge Multiple PDFs",
            "Convert Images to PDF",
            "Compress PDF Footprint",
            "Extract & Generate Word Cloud", 
            "Extract Embedded Assets"
        ])
        
    with col2:
        if doc_task == "Merge Multiple PDFs":
            st.markdown("### 🔗 PDF Merger Module")
            uploaded_files = st.file_uploader("Upload PDF Files to Merge (In Sequence)", type=["pdf"], accept_multiple_files=True, key="merge_files")
            
            if uploaded_files:
                st.markdown(f'<div class="app-card"><h4>📊 Status</h4><p><b>Files Loaded:</b> {len(uploaded_files)}</p></div>', unsafe_allow_html=True)
                if len(uploaded_files) > 1:
                    if st.button("🚀 Execute Document Merge", type="primary"):
                        with st.spinner("Merging document streams..."):
                            merged_doc = pymupdf.open()
                            for f in uploaded_files:
                                with pymupdf.open(stream=f.read(), filetype="pdf") as temp_doc:
                                    merged_doc.insert_pdf(temp_doc)
                            out_stream = io.BytesIO()
                            merged_doc.save(out_stream)
                            merged_bytes = out_stream.getvalue()
                        st.success(f"Successfully merged {len(uploaded_files)} documents!")
                        st.download_button("📥 Download Merged PDF", merged_bytes, file_name="merged_document.pdf", mime="application/pdf")
                else:
                    st.info("Please upload at least 2 PDF files.")
            else:
                st.info("👈 Upload multiple PDF files using the uploader above.")
                
        elif doc_task == "Convert Images to PDF":
            st.markdown("### 🖼️📄 Image to PDF Compiler")
            img_files = st.file_uploader("Upload Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="img_to_pdf_up")
            if img_files:
                if st.button("🚀 Compile Images to PDF", type="primary"):
                    with st.spinner("Compiling images..."):
                        image_list = []
                        for im_file in img_files:
                            pil_img = Image.open(im_file)
                            if pil_img.mode in ("RGBA", "P"):
                                pil_img = pil_img.convert("RGB")
                            image_list.append(pil_img)
                        pdf_buffer = io.BytesIO()
                        image_list[0].save(pdf_buffer, format="PDF", save_all=True, append_images=image_list[1:])
                        pdf_data = pdf_buffer.getvalue()
                    st.success("Successfully compiled images into PDF!")
                    st.download_button("📥 Download Compiled PDF", pdf_data, file_name="images_compiled.pdf", mime="application/pdf")
            else:
                st.info("👈 Upload images to compile.")

        elif doc_task == "Convert Word to PDF (.pdf)":
            st.markdown("### 📝➡️📄 Word to PDF Converter")
            docx_file = st.file_uploader("Upload Word Document (.docx)", type=["docx"], key="docx_up")
            if docx_file is not None:
                st.info("ℹ️ To convert .docx files to PDF cleanly in web cloud environments, text streams are parsed and restructured.")
                if st.button("🚀 Convert Word to PDF", type="primary"):
                    # Basic text fallback extraction to render a clean PDF
                    import docx
                    doc_read = docx.Document(docx_file)
                    full_text = "\n".join([p.text for p in doc_read.paragraphs])
                    
                    new_doc = pymupdf.open()
                    page = new_doc.new_page()
                    rect = pymupdf.Rect(50, 50, 550, 750)
                    page.insert_textbox(rect, full_text, fontsize=11, fontname="helv")
                    
                    pdf_out = io.BytesIO()
                    new_doc.save(pdf_out)
                    st.success("Converted successfully!")
                    st.download_button("📥 Download Converted PDF", pdf_out.getvalue(), file_name="converted_from_word.pdf", mime="application/pdf")
            else:
                st.info("👈 Upload a Word document (.docx).")

        else:
            uploaded_pdf = st.file_uploader("Upload Target PDF", type=["pdf"], key="doc_up")
            if uploaded_pdf is not None:
                pdf_bytes = uploaded_pdf.read()
                doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
                
                st.markdown(f"""
                    <div class="app-card">
                        <h4>📊 Metadata Inspection</h4>
                        <p><b>Filename:</b> {uploaded_pdf.name}</p>
                        <p><b>Page Count:</b> {len(doc)}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if doc_task == "Convert PDF to Markdown":
                    if st.button("🚀 Run Markdown Conversion", type="primary"):
                        md = [f"## Page {i+1}\n{page.get_text('text')}\n\n---\n" for i, page in enumerate(doc)]
                        final_md = "".join(md)
                        st.success("Conversion successful!")
                        st.text_area("Output Stream", final_md, height=280)
                        st.download_button("📥 Download Markdown", final_md, file_name="document.md", mime="text/markdown")
                        
                elif doc_task == "Convert PDF to Word (.docx)":
                    if st.button("🚀 Convert to Word", type="primary"):
                        import docx
                        word_doc = docx.Document()
                        word_doc.add_heading(f"Converted from {uploaded_pdf.name}", level=1)
                        for page_num, page in enumerate(doc):
                            word_doc.add_heading(f"Page {page_num + 1}", level=2)
                            word_doc.add_paragraph(page.get_text("text"))
                        
                        doc_io = io.BytesIO()
                        word_doc.save(doc_io)
                        doc_io.seek(0)
                        
                        st.success("Converted to Word document successfully!")
                        st.download_button("📥 Download .docx File", doc_io, file_name="converted_document.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

                elif doc_task == "Extract & Generate Word Cloud":
                    if st.button("🚀 Generate Word Cloud", type="primary"):
                        full_corpus = " ".join([page.get_text("text") for page in doc])
                        wc = WordCloud(width=900, height=450, background_color="#0b0f19", colormap="cool").generate(full_corpus)
                        fig, ax = plt.subplots(figsize=(10, 5))
                        ax.imshow(wc, interpolation="bilinear")
                        ax.axis("off")
                        fig.patch.set_facecolor('#0b0f19')
                        st.pyplot(fig)
                            
                elif doc_task == "Compress PDF Footprint":
                    if st.button("🚀 Compress PDF", type="primary"):
                        out = io.BytesIO()
                        doc.save(out, garbage=4, deflate=True)
                        res_bytes = out.getvalue()
                        st.success(f"Optimized! New Size: {len(res_bytes)/1024:.2f} KB")
                        st.download_button("📥 Download Optimized PDF", res_bytes, file_name="optimized.pdf", mime="application/pdf")
                        
                elif doc_task == "Extract Embedded Assets":
                    if st.button("🚀 Scan & Extract Media", type="primary"):
                        counter = 0
                        for i, page in enumerate(doc):
                            for idx, img in enumerate(page.get_images(full=True)):
                                extracted = doc.extract_image(img[0])
                                counter += 1
                                st.image(extracted["image"], caption=f"Page {i+1} Asset {idx+1}", width=220)
                                st.download_button(f"📥 Download Asset {counter}", extracted["image"], file_name=f"p{i+1}_asset{idx+1}.{extracted['ext']}", key=f"asset_{i}_{idx}")
                        if counter == 0: st.info("No raster images found.")
            else:
                st.info("👈 Upload a PDF document from the control panel.")


# ==================== PAGE 2: COMPUTER VISION ====================
elif selected_page == "👁️ Computer Vision & Lab":
    st.markdown('<p class="hero-title">👁️ Computer Vision Laboratory</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Advanced low-light enhancement, color channel splitting, edge detection, and Otsu segmentation.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        st.markdown("### ⚙️ Vision Controls")
        cv_upload = st.file_uploader("Upload Image Target", type=["png", "jpg", "jpeg"], key="cv_file")
        cv_pipeline = st.selectbox("Algorithm Pipeline", [
            "Low-Light Retinex/CLAHE Enhancement",
            "Multi-Channel Space Splitter (RGB/HSV/LAB)",
            "Canny Structural Edge Detector",
            "Otsu Binarization & Contour Extraction"
        ])
    with col2:
        if cv_upload is not None:
            pil_i = Image.open(cv_upload)
            cv_i = pil_to_cv2(pil_i)
            st.image(pil_i, caption="Raw Input Feed", use_container_width=True)
            
            if cv_pipeline == "Low-Light Retinex/CLAHE Enhancement":
                if st.button("🚀 Run Enhancement Pipeline", type="primary"):
                    lab = cv2.cvtColor(cv_i, cv2.COLOR_BGR2LAB)
                    l, a, b = cv2.split(lab)
                    clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(8,8))
                    cl = clahe.apply(l)
                    merged = cv2.merge((cl, a, b))
                    out_cv = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
                    out_pl = cv2_to_pil(out_cv)
                    st.image(out_pl, caption="Enhanced Output Matrix", use_container_width=True)
                    buf = io.BytesIO()
                    out_pl.save(buf, format="PNG")
                    st.download_button("📥 Download Enhanced Image", buf.getvalue(), file_name="enhanced_vision.png")
                    
            elif cv_pipeline == "Multi-Channel Space Splitter (RGB/HSV/LAB)":
                space_target = st.selectbox("Target Color Space", ["RGB", "HSV", "LAB"])
                if st.button("🚀 Split Spectral Layers", type="primary"):
                    if space_target == "RGB":
                        conv = cv2.cvtColor(cv_i, cv2.COLOR_BGR2RGB)
                        n1, n2, n3 = "Red Channel", "Green Channel", "Blue Channel"
                    elif space_target == "HSV":
                        conv = cv2.cvtColor(cv_i, cv2.COLOR_BGR2HSV)
                        n1, n2, n3 = "Hue (H)", "Saturation (S)", "Value (V)"
                    else:
                        conv = cv2.cvtColor(cv_i, cv2.COLOR_BGR2LAB)
                        n1, n2, n3 = "Lightness (L)", "A-Component", "B-Component"
                        
                    ch1, ch2, ch3 = cv2.split(conv)
                    c_a, c_b, c_c = st.columns(3)
                    with c_a: st.image(ch1, caption=n1, use_container_width=True, clamp=True)
                    with c_b: st.image(ch2, caption=n2, use_container_width=True, clamp=True)
                    with c_c: st.image(ch3, caption=n3, use_container_width=True, clamp=True)
                    
            elif cv_pipeline == "Canny Structural Edge Detector":
                t_low = st.slider("Lower Threshold", 0, 255, 50)
                t_high = st.slider("Upper Threshold", 0, 255, 150)
                if st.button("🚀 Execute Edge Detection", type="primary"):
                    gray = cv2.cvtColor(cv_i, cv2.COLOR_BGR2GRAY)
                    edges = cv2.Canny(gray, t_low, t_high)
                    st.image(edges, caption="Edge Boundary Mask", use_container_width=True, clamp=True)
                    buf = io.BytesIO()
                    Image.fromarray(edges).save(buf, format="PNG")
                    st.download_button("📥 Download Mask", buf.getvalue(), file_name="edges.png")
                    
            elif cv_pipeline == "Otsu Binarization & Contour Extraction":
                if st.button("🚀 Compute Otsu Thresholding", type="primary"):
                    gray = cv2.cvtColor(cv_i, cv2.COLOR_BGR2GRAY)
                    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    annotated = cv_i.copy()
                    cv2.drawContours(annotated, contours, -1, (0, 255, 0), 2)
                    final_pl = cv2_to_pil(annotated)
                    st.success(f"Otsu Segmentation Complete: Identified {len(contours)} structures.")
                    st.image(final_pl, caption="Segmented Boundaries", use_container_width=True)
        else:
            st.info("👈 Upload an image file for computer vision processing.")


# ==================== PAGE 3: MEDIA STUDIO ====================
elif selected_page == "🖼️ Media & Image Studio":
    st.markdown('<p class="hero-title">🖼️ Media & Image Compression Studio</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Batch resize dimensions, adjust quality compression ratios, and apply filters.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        st.markdown("### ⚙️ Asset Controls")
        media_file = st.file_uploader("Upload Image Asset", type=["png", "jpg", "jpeg", "webp"], key="media_up")
        media_op = st.selectbox("Operation Mode", ["Resize Dimensions", "Quality Compression (KB Reduction)", "Grayscale Conversion"])
    with col2:
        if media_file is not None:
            img = Image.open(media_file)
            st.markdown(f'<div class="app-card"><h4>📊 Asset Specs</h4><p><b>Resolution:</b> {img.width} x {img.height} px</p></div>', unsafe_allow_html=True)
            st.image(img, caption="Source Preview", use_container_width=True)
            
            if media_op == "Resize Dimensions":
                nw = st.number_input("Target Width (px)", value=img.width)
                nh = st.number_input("Target Height (px)", value=img.height)
                if st.button("🚀 Resize Asset", type="primary"):
                    res = img.resize((int(nw), int(nh)))
                    st.image(res, caption="Resized Output", use_container_width=True)
                    buf = io.BytesIO()
                    res.save(buf, format="JPEG" if img.format=='JPEG' else 'PNG')
                    st.download_button("📥 Download Resized", buf.getvalue(), file_name="resized.jpg")
                    
            elif media_op == "Quality Compression (KB Reduction)":
                q_val = st.slider("Compression Quality Factor", 10, 95, 80)
                if st.button("🚀 Compress Asset", type="primary"):
                    buf = io.BytesIO()
                    rgb_img = img.convert("RGB") if img.mode in ("RGBA", "P") else img
                    rgb_img.save(buf, format="JPEG", quality=q_val)
                    c_bytes = buf.getvalue()
                    st.success(f"Optimized Size: {len(c_bytes)/1024:.2f} KB")
                    st.image(c_bytes, caption="Compressed Preview")
                    st.download_button("📥 Download Compressed", c_bytes, file_name="compressed.jpg", mime="image/jpeg")
                    
            elif media_op == "Grayscale Conversion":
                if st.button("🚀 Apply Grayscale Matrix", type="primary"):
                    gray = img.convert("L")
                    st.image(gray, caption="Grayscale Output", use_container_width=True)
                    buf = io.BytesIO()
                    gray.save(buf, format="PNG")
                    st.download_button("📥 Download Grayscale", buf.getvalue(), file_name="grayscale.png", mime="image/png")
        else:
            st.info("👈 Upload an image asset from the left panel.")

# Footer Watermark
st.markdown("---")
st.markdown("<p style='text-align: center; color: #4b5563; font-size: 0.85rem;'>Engineered with Precision by Ashutosh Borah © 2026</p>", unsafe_allow_html=True)
