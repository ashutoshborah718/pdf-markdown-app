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

# ==================== HIGH-CONTRAST DARK MODE CSS ====================
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        background: linear-gradient(135deg, #60a5fa 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #9ca3af;
        margin-bottom: 25px;
    }
    .overview-card {
        background: #111827;
        border: 1px solid #374151;
        padding: 24px;
        border-radius: 14px;
        margin-bottom: 20px;
    }
    section[data-testid="stSidebar"] {
        background-color: #0e1322;
        border-right: 1px solid #1f2937;
    }
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
    }
    /* Fix tab text visibility in dark mode */
    .stTabs [data-baseweb="tab"] {
        color: #9ca3af;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #60a5fa;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== NAVIGATION STATE ====================
if "active_page" not in st.session_state:
    st.session_state.active_page = "🏠 Platform Overview"

st.sidebar.markdown("### ⚡ ASHUTOSH STUDIO")
st.sidebar.markdown("<p style='font-size: 0.8rem; color: #9ca3af; line-height: 1.4;'>Enterprise Computational Hub<br>Architect: <b>Ashutosh Borah</b></p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.markdown("#### 🧭 Workspace Directory")
if st.sidebar.button("🏠 Platform Overview", use_container_width=True):
    st.session_state.active_page = "🏠 Platform Overview"
if st.sidebar.button("📄 Document Intelligence", use_container_width=True):
    st.session_state.active_page = "📄 Document Intelligence"
if st.sidebar.button("🖼️ Media Studio", use_container_width=True):
    st.session_state.active_page = "🖼️ Media Studio"

st.sidebar.markdown("---")
st.sidebar.markdown("<p style='color: #34d399; font-size: 0.75rem; font-weight: 600;'>🟢 SYSTEM ONLINE</p>", unsafe_allow_html=True)

selected_page = st.session_state.active_page

# ==================== 0. OVERVIEW PAGE ====================
if selected_page == "🏠 Platform Overview":
    st.markdown('<p class="hero-title">Welcome to Ashutosh Studio</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">An enterprise-grade computational platform for advanced document operations and media optimization.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("""
            <div class="overview-card">
                <h3 style="color: #60a5fa; margin-top: 0;">📄 Document Intelligence Suite</h3>
                <p style="color: #9ca3af; font-size: 0.9rem;">Convert PDF files to Markdown, Word (.docx), or compile images into PDFs. Merge multi-file queues, compress documents, generate word frequency clouds, and extract embedded raster assets.</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="overview-card">
                <h3 style="color: #34d399; margin-top: 0;">🖼️ Media & Image Studio</h3>
                <p style="color: #9ca3af; font-size: 0.9rem;">Batch resize image resolutions, optimize quality compression ratios to reduce file sizes (KB/MB), and apply grayscale pixel conversions effortlessly.</p>
            </div>
        """, unsafe_allow_html=True)
        
    st.info("👈 Use the **Workspace Directory** in the sidebar to navigate to your desired module.")

# ==================== 1. DOCUMENT INTELLIGENCE PAGE ====================
elif selected_page == "📄 Document Intelligence":
    st.markdown('<p class="hero-title">📄 Document Intelligence Hub</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">High-speed file conversions, parsing, and pipeline operations.</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "PDF to Markdown", 
        "PDF to Word", 
        "Word to PDF", 
        "Merge PDFs", 
        "Images to PDF", 
        "Compress PDF", 
        "Word Cloud", 
        "Extract Assets"
    ])
    
    with tab1:
        st.markdown("### Convert PDF to Markdown")
        pdf_file = st.file_uploader("Upload PDF File", type=["pdf"], key="md_up")
        if pdf_file and st.button("Run Conversion", type="primary"):
            doc = pymupdf.open(stream=pdf_file.read(), filetype="pdf")
            md = "".join([f"## Page {i+1}\n{p.get_text('text')}\n\n---\n" for i, p in enumerate(doc)])
            st.text_area("Output Preview", md, height=250)
            st.download_button("Download Markdown", md, file_name="converted.md", mime="text/markdown")

    with tab2:
        st.markdown("### Convert PDF to Word (.docx)")
        pdf_file = st.file_uploader("Upload PDF File", type=["pdf"], key="word_up")
        if pdf_file and st.button("Convert to Word", type="primary"):
            doc = pymupdf.open(stream=pdf_file.read(), filetype="pdf")
            word_doc = docx.Document()
            for i, p in enumerate(doc):
                word_doc.add_heading(f"Page {i+1}", level=2)
                word_doc.add_paragraph(p.get_text("text"))
            bio = io.BytesIO()
            word_doc.save(bio)
            st.download_button("Download .docx", bio.getvalue(), file_name="converted.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    with tab3:
        st.markdown("### Convert Word to PDF (.pdf)")
        docx_file = st.file_uploader("Upload Word Document", type=["docx"], key="docx_up")
        if docx_file and st.button("Convert to PDF", type="primary"):
            word_read = docx.Document(docx_file)
            text = "\n".join([p.text for p in word_read.paragraphs])
            new_doc = pymupdf.open()
            new_doc.new_page().insert_textbox(pymupdf.Rect(50, 50, 550, 750), text, fontsize=11)
            bio = io.BytesIO()
            new_doc.save(bio)
            st.download_button("Download PDF", bio.getvalue(), file_name="converted.pdf", mime="application/pdf")

    with tab4:
        st.markdown("### Merge Multiple PDFs")
        files = st.file_uploader("Upload PDFs in Sequence", type=["pdf"], accept_multiple_files=True, key="merge_up")
        if files and len(files) > 1 and st.button("Merge PDFs", type="primary"):
            merged = pymupdf.open()
            for f in files:
                merged.insert_pdf(pymupdf.open(stream=f.read(), filetype="pdf"))
            bio = io.BytesIO()
            merged.save(bio)
            st.download_button("Download Merged PDF", bio.getvalue(), file_name="merged.pdf", mime="application/pdf")

    with tab5:
        st.markdown("### Compile Images to PDF")
        imgs = st.file_uploader("Upload Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="img_pdf_up")
        if imgs and st.button("Compile to PDF", type="primary"):
            pil_list = [Image.open(im).convert("RGB") for im in imgs]
            bio = io.BytesIO()
            pil_list[0].save(bio, format="PDF", save_all=True, append_images=pil_list[1:])
            st.download_button("Download Compiled PDF", bio.getvalue(), file_name="compiled.pdf", mime="application/pdf")

    with tab6:
        st.markdown("### Compress PDF Footprint")
        pdf_file = st.file_uploader("Upload PDF to Compress", type=["pdf"], key="comp_up")
        if pdf_file and st.button("Compress PDF", type="primary"):
            doc = pymupdf.open(stream=pdf_file.read(), filetype="pdf")
            bio = io.BytesIO()
            doc.save(bio, garbage=4, deflate=True)
            st.download_button("Download Compressed PDF", bio.getvalue(), file_name="compressed.pdf", mime="application/pdf")

    with tab7:
        st.markdown("### Generate Word Cloud")
        pdf_file = st.file_uploader("Upload PDF for Corpus Analysis", type=["pdf"], key="wc_up")
        if pdf_file and st.button("Generate Word Cloud", type="primary"):
            doc = pymupdf.open(stream=pdf_file.read(), filetype="pdf")
            corpus = " ".join([p.get_text("text") for p in doc])
            wc = WordCloud(width=800, height=400, background_color="#0b0f19", colormap="cool").generate(corpus)
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            fig.patch.set_facecolor('#0b0f19')
            st.pyplot(fig)

    with tab8:
        st.markdown("### Extract Embedded Assets")
        pdf_file = st.file_uploader("Upload PDF to Scan Images", type=["pdf"], key="ext_up")
        if pdf_file:
            doc = pymupdf.open(stream=pdf_file.read(), filetype="pdf")
            count = 0
            for i, page in enumerate(doc):
                for img_idx, img in enumerate(page.get_images(full=True)):
                    extracted = doc.extract_image(img[0])
                    count += 1
                    st.image(extracted["image"], width=180, caption=f"Page {i+1}")
                    st.download_button(f"Download Asset {count}", extracted["image"], file_name=f"p{i+1}_img.{extracted['ext']}", key=f"dl_{i}_{img_idx}")
            if count == 0:
                st.info("No embedded raster images found.")

# ==================== 2. MEDIA STUDIO PAGE ====================
elif selected_page == "🖼️ Media Studio":
    st.markdown('<p class="hero-title">🖼️ Media Studio</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Resize, compress, and process image assets.</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Resize Dimensions", "Quality Compression", "Grayscale Filter"])
    
    with tab1:
        st.markdown("### Resize Image Dimensions")
        img_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg", "webp"], key="resize_up")
        if img_file:
            img = Image.open(img_file)
            w = st.number_input("Width (px)", value=img.width)
            h = st.number_input("Height (px)", value=img.height)
            if st.button("Resize Image", type="primary"):
                res = img.resize((int(w), int(h)))
                st.image(res, width=400)
                bio = io.BytesIO()
                res.save(bio, format="PNG")
                st.download_button("Download Resized", bio.getvalue(), file_name="resized.png")

    with tab2:
        st.markdown("### Quality Compression (KB Reduction)")
        img_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg", "webp"], key="comp_img_up")
        if img_file:
            img = Image.open(img_file)
            q = st.slider("JPEG Quality", 10, 95, 80)
            if st.button("Compress Image", type="primary"):
                bio = io.BytesIO()
                img.convert("RGB").save(bio, format="JPEG", quality=q)
                st.image(bio.getvalue(), width=400)
                st.download_button("Download Compressed", bio.getvalue(), file_name="compressed.jpg", mime="image/jpeg")

    with tab3:
        st.markdown("### Grayscale Conversion")
        img_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg", "webp"], key="gray_up")
        if img_file:
            img = Image.open(img_file)
            if st.button("Apply Grayscale", type="primary"):
                gray = img.convert("L")
                st.image(gray, width=400)
                bio = io.BytesIO()
                gray.save(bio, format="PNG")
                st.download_button("Download Grayscale", bio.getvalue(), file_name="grayscale.png")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #4b5563; font-size: 0.75rem;'>Engineered with Precision by Ashutosh Borah © 2026</p>", unsafe_allow_html=True)
