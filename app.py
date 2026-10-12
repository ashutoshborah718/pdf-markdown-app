import streamlit as st
import pymupdf
from PIL import Image
import numpy as np
import io
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import docx

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="Ashutosh Studio | Enterprise Suite", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== ADVANCED SAAS CSS STYLING ====================
st.markdown("""
    <style>
    /* Global App Theme */
    .stApp {
        background-color: #090d16;
        color: #f3f4f6;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hero Headers */
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        background: linear-gradient(135deg, #60a5fa 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2px;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #9ca3af;
        margin-bottom: 25px;
        font-weight: 400;
    }
    
    /* Glassmorphism Containers */
    .saas-card {
        background: rgba(17, 24, 39, 0.65);
        border: 1px solid rgba(75, 85, 99, 0.3);
        padding: 22px;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
        backdrop-filter: blur(8px);
    }
    
    /* Interactive Module Selection Cards */
    .module-select-box {
        background: rgba(31, 41, 55, 0.5);
        border: 1px solid rgba(75, 85, 99, 0.4);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 12px;
        transition: all 0.2s ease-in-out;
    }
    .module-select-box:hover {
        border-color: #60a5fa;
        background: rgba(31, 41, 55, 0.8);
    }
    
    /* Metric / Status Badges */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        background-color: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
        margin-bottom: 10px;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0e1322;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Button Customization */
    .stButton button {
        border-radius: 10px;
        font-weight: 600;
        letter-spacing: 0.01em;
        transition: all 0.2s ease;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== NAVIGATION & SESSION STATE ====================
if "active_page" not in st.session_state:
    st.session_state.active_page = "🏠 Platform Overview"

st.sidebar.markdown("### ⚡ ASHUTOSH STUDIO")
st.sidebar.markdown("<p style='font-size: 0.8rem; color: #9ca3af; line-height: 1.4;'>Enterprise Computational Hub<br>Principal Architect: <b>Ashutosh Borah</b></p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.markdown("#### 🧭 Workspace Directory")
if st.sidebar.button("🏠 Platform Overview", use_container_width=True):
    st.session_state.active_page = "🏠 Platform Overview"
if st.sidebar.button("📄 Document Intelligence Suite", use_container_width=True):
    st.session_state.active_page = "📄 Document Intelligence Suite"
if st.sidebar.button("🖼️ Media & Image Studio", use_container_width=True):
    st.session_state.active_page = "🖼️ Media & Image Studio"

st.sidebar.markdown("---")
st.sidebar.markdown("""
    <div style='background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); padding: 10px; border-radius: 10px;'>
        <p style='color: #34d399; font-size: 0.75rem; font-weight: 600; margin: 0;'>🟢 SYSTEM STATUS</p>
        <p style='color: #9ca3af; font-size: 0.75rem; margin: 2px 0 0 0;'>All micro-services operating normally.</p>
    </div>
""", unsafe_allow_html=True)

selected_page = st.session_state.active_page


# ==================== PAGE 0: HOME & OVERVIEW ====================
if selected_page == "🏠 Platform Overview":
    st.markdown('<span class="badge">Enterprise Edition v2.5</span>', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">Welcome to Ashutosh Studio</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">A high-performance web platform built for seamless document conversions, formatting pipelines, and professional media optimization.</p>', unsafe_allow_html=True)
    
    st.markdown("### 🚀 Select a Workspace Module")
    
    col1, col2 = st.columns(2, gap="medium")
    
    with col1:
        st.markdown("""
            <div class="saas-card">
                <h3 style="color: #60a5fa; margin-top: 0;">📄 Document Intelligence Suite</h3>
                <p style="color: #9ca3af; font-size: 0.9rem; line-height: 1.5;">Convert between PDF, Word (.docx), and Markdown formats. Merge document queues, compile images into PDFs, optimize file footprints, and generate visual word clouds.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Document Suite ➔", type="primary", use_container_width=True):
            st.session_state.active_page = "📄 Document Intelligence Suite"
            st.rerun()
            
    with col2:
        st.markdown("""
            <div class="saas-card">
                <h3 style="color: #34d399; margin-top: 0;">🖼️ Media & Image Studio</h3>
                <p style="color: #9ca3af; font-size: 0.9rem; line-height: 1.5;">Batch resize image pixel resolutions, adjust quality compression ratios to shrink file payloads, and apply pixel-level color conversions instantly.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Media Studio ➔", type="primary", use_container_width=True):
            st.session_state.active_page = "🖼️ Media & Image Studio"
            st.rerun()


# ==================== PAGE 1: DOCUMENT INTELLIGENCE ====================
elif selected_page == "📄 Document Intelligence Suite":
    st.markdown('<span class="badge">Module: Document Processing</span>', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">Document Intelligence Hub</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">High-speed file conversions, structural parsing, compression, and asset extraction pipelines.</p>', unsafe_allow_html=True)
    
    # Modern Tabbed Selection Process instead of standard dropdowns
    doc_task = st.radio(
        "Select Pipeline Operation", 
        [
            "Convert PDF to Markdown", 
            "Convert PDF to Word (.docx)",
            "Convert Word to PDF (.pdf)",
            "Merge Multiple PDFs",
            "Convert Images to PDF",
            "Compress PDF Footprint",
            "Extract & Generate Word Cloud", 
            "Extract Embedded Assets"
        ],
        horizontal=True
    )
    
    st.markdown("---")
    
    if doc_task == "Merge Multiple PDFs":
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.markdown("#### 🔗 PDF Merger Engine")
        uploaded_files = st.file_uploader("Upload PDF Files to Merge (In Sequence)", type=["pdf"], accept_multiple_files=True, key="merge_files")
        
        if uploaded_files:
            st.info(f"📂 **Files Queued:** {len(uploaded_files)} documents selected.")
            if len(uploaded_files) > 1:
                if st.button("🚀 Execute Document Merge", type="primary", use_container_width=True):
                    with st.spinner("Stitching document streams..."):
                        merged_doc = pymupdf.open()
                        for f in uploaded_files:
                            with pymupdf.open(stream=f.read(), filetype="pdf") as temp_doc:
                                merged_doc.insert_pdf(temp_doc)
                        out_stream = io.BytesIO()
                        merged_doc.save(out_stream)
                        merged_bytes = out_stream.getvalue()
                    st.success("Successfully merged documents!")
                    st.download_button("📥 Download Merged PDF", merged_bytes, file_name="merged_document.pdf", mime="application/pdf", use_container_width=True)
            else:
                st.warning("Please upload at least 2 PDF files to execute merging.")
        else:
            st.info("👈 Upload multiple PDF files using the uploader above.")
        st.markdown('</div>', unsafe_allow_html=True)
            
    elif doc_task == "Convert Images to PDF":
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.markdown("#### 🖼️📄 Image to PDF Compiler")
        img_files = st.file_uploader("Upload Image Assets", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="img_to_pdf_up")
        if img_files:
            if st.button("🚀 Compile Images to PDF", type="primary", use_container_width=True):
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
                st.download_button("📥 Download Compiled PDF", pdf_data, file_name="images_compiled.pdf", mime="application/pdf", use_container_width=True)
        else:
            st.info("👈 Upload image assets to compile.")
        st.markdown('</div>', unsafe_allow_html=True)

    elif doc_task == "Convert Word to PDF (.pdf)":
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.markdown("#### 📝➡️📄 Word to PDF Converter")
        docx_file = st.file_uploader("Upload Word Document (.docx)", type=["docx"], key="docx_up")
        if docx_file is not None:
            if st.button("🚀 Convert Word to PDF", type="primary", use_container_width=True):
                doc_read = docx.Document(docx_file)
                full_text = "\n".join([p.text for p in doc_read.paragraphs])
                
                new_doc = pymupdf.open()
                page = new_doc.new_page()
                rect = pymupdf.Rect(50, 50, 550, 750)
                page.insert_textbox(rect, full_text, fontsize=11, fontname="helv")
                
                pdf_out = io.BytesIO()
                new_doc.save(pdf_out)
                st.success("Converted successfully!")
                st.download_button("📥 Download Converted PDF", pdf_out.getvalue(), file_name="converted_from_word.pdf", mime="application/pdf", use_container_width=True)
        else:
            st.info("👈 Upload a Word document (.docx).")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        uploaded_pdf = st.file_uploader("Upload Target PDF Document", type=["pdf"], key="doc_up")
        if uploaded_pdf is not None:
            pdf_bytes = uploaded_pdf.read()
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            
            st.markdown(f"**File:** {uploaded_pdf.name} &nbsp;|&nbsp; **Pages:** {len(doc)} &nbsp;|&nbsp; **Size:** {len(pdf_bytes)/1024:.1f} KB")
            
            if doc_task == "Convert PDF to Markdown":
                if st.button("🚀 Run Markdown Conversion", type="primary", use_container_width=True):
                    md = [f"## Page {i+1}\n{page.get_text('text')}\n\n---\n" for i, page in enumerate(doc)]
                    final_md = "".join(md)
                    st.success("Conversion successful!")
                    st.text_area("Output Stream", final_md, height=250)
                    st.download_button("📥 Download Markdown", final_md, file_name="document.md", mime="application/pdf", use_container_width=True)
                    
            elif doc_task == "Convert PDF to Word (.docx)":
                if st.button("🚀 Convert to Word (.docx)", type="primary", use_container_width=True):
                    word_doc = docx.Document()
                    word_doc.add_heading(f"Converted from {uploaded_pdf.name}", level=1)
                    for page_num, page in enumerate(doc):
                        word_doc.add_heading(f"Page {page_num + 1}", level=2)
                        word_doc.add_paragraph(page.get_text("text"))
                    
                    doc_io = io.BytesIO()
                    word_doc.save(doc_io)
                    doc_io.seek(0)
                    
                    st.success("Converted to Word document successfully!")
                    st.download_button("📥 Download .docx File", doc_io, file_name="converted_document.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)

            elif doc_task == "Extract & Generate Word Cloud":
                if st.button("🚀 Generate Word Cloud", type="primary", use_container_width=True):
                    full_corpus = " ".join([page.get_text("text") for page in doc])
                    wc = WordCloud(width=900, height=450, background_color="#090d16", colormap="cool").generate(full_corpus)
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wc, interpolation="bilinear")
                    ax.axis("off")
                    fig.patch.set_facecolor('#090d16')
                    st.pyplot(fig)
                        
            elif doc_task == "Compress PDF Footprint":
                if st.button("🚀 Compress PDF File", type="primary", use_container_width=True):
                    out = io.BytesIO()
                    doc.save(out, garbage=4, deflate=True)
                    res_bytes = out.getvalue()
                    st.success(f"Optimized! New Size: {len(res_bytes)/1024:.2f} KB")
                    st.download_button("📥 Download Optimized PDF", res_bytes, file_name="optimized.pdf", mime="application/pdf", use_container_width=True)
                    
            elif doc_task == "Extract Embedded Assets":
                if st.button("🚀 Scan & Extract Media", type="primary", use_container_width=True):
                    counter = 0
                    for i, page in enumerate(doc):
                        for idx, img in enumerate(page.get_images(full=True)):
                            extracted = doc.extract_image(img[0])
                            counter += 1
                            st.image(extracted["image"], caption=f"Page {i+1} Asset {idx+1}", width=200)
                            st.download_button(f"📥 Download Asset {counter}", extracted["image"], file_name=f"p{i+1}_asset{idx+1}.{extracted['ext']}", key=f"asset_{i}_{idx}")
                    if counter == 0: st.info("No raster images found in PDF stream.")
        else:
            st.info("👈 Upload a target PDF document above.")
        st.markdown('</div>', unsafe_allow_html=True)


# ==================== PAGE 2: MEDIA STUDIO ====================
elif selected_page == "🖼️ Media & Image Studio":
    st.markdown('<span class="badge">Module: Image Optimization</span>', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">Media & Image Studio</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Batch resize dimensions, adjust quality compression ratios, and apply filters.</p>', unsafe_allow_html=True)
    
    media_op = st.radio(
        "Select Operation Mode", 
        ["Resize Dimensions", "Quality Compression (KB Reduction)", "Grayscale Conversion"],
        horizontal=True
    )
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.markdown("#### ⚙️ Asset Ingestion")
        media_file = st.file_uploader("Upload Image Asset", type=["png", "jpg", "jpeg", "webp"], key="media_up")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        if media_file is not None:
            img = Image.open(media_file)
            st.markdown(f"**Resolution:** {img.width} x {img.height} px &nbsp;|&nbsp; **Format:** {img.format}")
            st.image(img, caption="Source Preview", use_container_width=True)
            
            if media_op == "Resize Dimensions":
                nw = st.number_input("Target Width (px)", value=img.width)
                nh = st.number_input("Target Height (px)", value=img.height)
                if st.button("🚀 Resize Asset", type="primary", use_container_width=True):
                    res = img.resize((int(nw), int(nh)))
                    st.image(res, caption="Resized Output", use_container_width=True)
                    buf = io.BytesIO()
                    res.save(buf, format="JPEG" if img.format=='JPEG' else 'PNG')
                    st.download_button("📥 Download Resized", buf.getvalue(), file_name="resized.jpg", use_container_width=True)
                    
            elif media_op == "Quality Compression (KB Reduction)":
                q_val = st.slider("Compression Quality Factor", 10, 95, 80)
                if st.button("🚀 Compress Asset", type="primary", use_container_width=True):
                    buf = io.BytesIO()
                    rgb_img = img.convert("RGB") if img.mode in ("RGBA", "P") else img
                    rgb_img.save(buf, format="JPEG", quality=q_val)
                    c_bytes = buf.getvalue()
                    st.success(f"Optimized Size: {len(c_bytes)/1024:.2f} KB")
                    st.image(c_bytes, caption="Compressed Preview")
                    st.download_button("📥 Download Compressed", c_bytes, file_name="compressed.jpg", mime="image/jpeg", use_container_width=True)
                    
            elif media_op == "Grayscale Conversion":
                if st.button("🚀 Apply Grayscale Matrix", type="primary", use_container_width=True):
                    gray = img.convert("L")
                    st.image(gray, caption="Grayscale Output", use_container_width=True)
                    buf = io.BytesIO()
                    gray.save(buf, format="PNG")
                    st.download_button("📥 Download Grayscale", buf.getvalue(), file_name="grayscale.png", mime="image/png", use_container_width=True)
        else:
            st.info("👈 Upload an image asset from the left panel.")
        st.markdown('</div>', unsafe_allow_html=True)

# Footer Watermark
st.markdown("---")
st.markdown("<p style='text-align: center; color: #4b5563; font-size: 0.8rem;'>Engineered with Precision by Ashutosh Borah © 2026</p>", unsafe_allow_html=True)
