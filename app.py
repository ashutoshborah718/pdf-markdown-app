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

# ==================== HIGH-CONTRAST & POLISHED CSS ====================
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
    .workflow-card {
        background: #111827;
        border: 1px solid #374151;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    section[data-testid="stSidebar"] {
        background-color: #0e1322;
        border-right: 1px solid #1f2937;
    }
    /* Bright Sidebar Text & Navigation Links */
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] label {
        color: #e5e7eb !important;
    }
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* High-Contrast Tab Text & Hover States */
    .stTabs [data-baseweb="tab"] {
        background-color: #111827 !important;
        border: 1px solid #374151 !important;
        padding: 10px 16px !important;
        border-radius: 8px 8px 0px 0px !important;
        margin-right: 4px !important;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #1f2937 !important;
        border-color: #60a5fa !important;
    }
    .stTabs [data-baseweb="tab"] p {
        color: #f3f4f6 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #1f2937 !important;
        border-bottom: 3px solid #ef4444 !important; /* Distinct visual red accent cue */
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] p {
        color: #ef4444 !important;
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
            <div class="workflow-card">
                <h3 style="color: #60a5fa; margin-top: 0;">📄 Document Intelligence Suite</h3>
                <p style="color: #9ca3af; font-size: 0.9rem;">Convert PDF files to Markdown, Word (.docx), or compile images into PDFs. Merge multi-file queues, compress documents, generate word frequency clouds, and extract embedded raster assets.</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="workflow-card">
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
        st.markdown("<p style='color: #9ca3af; font-size: 0.85rem;'>Extract text layout page-by-page and export clean Markdown (.md) documents.</p>", unsafe_allow_html=True)
        pdf_file = st.file_uploader("Upload PDF File", type=["pdf"], key="md_up")
        if pdf_file:
            st.markdown(f"<div class='workflow-card'><p><b>File:</b> {pdf_file.name} | <b>Size:</b> {len(pdf_file.getvalue())/1024:.1f} KB</p></div>", unsafe_allow_html=True)
            if st.button("🚀 Run Markdown Conversion", type="primary"):
                doc = pymupdf.open(stream=pdf_file.read(), filetype="pdf")
                md = "".join([f"## Page {i+1}\n{p.get_text('text')}\n\n---\n" for i, p in enumerate(doc)])
                st.text_area("Output Preview", md, height=250)
                st.download_button("📥 Download Markdown", md, file_name="converted.md", mime="text/markdown")
        else:
            st.info("💡 **Workflow Example:** Upload a PDF → Inspect Metadata → Convert → Download `.md` file.")

    with tab2:
        st.markdown("### Convert PDF to Word (.docx)")
        st.markdown("<p style='color: #9ca3af; font-size: 0.85rem;'>Parse PDF text streams and restructure them into editable Microsoft Word documents.</p>", unsafe_allow_html=True)
        pdf_file = st.file_uploader("Upload PDF File", type=["pdf"], key="word_up")
        if pdf_file:
            st.markdown(f"<div class='workflow-card'><p><b>File:</b> {pdf_file.name} | <b>Size:</b> {len(pdf_file.getvalue())/1024:.1f} KB</p></div>", unsafe_allow_html=True)
            if st.button("🚀 Convert to Word", type="primary"):
                doc = pymupdf.open(stream=pdf_file.read(), filetype="pdf")
                word_doc = docx.Document()
                for i, p in enumerate(doc):
                    word_doc.add_heading(f"Page {i+1}", level=2)
                    word_doc.add_paragraph(p.get_text("text"))
                bio = io.BytesIO()
                word_doc.save(bio)
                st.success("Conversion successful!")
                st.download_button("📥 Download .docx", bio.getvalue(), file_name="converted.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        else:
            st.info("💡 **Workflow Example:** Upload PDF → Parse Layout → Generate `.docx` → Download.")

    with tab3:
        st.markdown("### Convert Word to PDF (.pdf)")
        st.markdown("<p style='color: #9ca3af; font-size: 0.85rem;'>Upload Word documents (.docx), inspect specs, and compile into standardized PDF files.</p>", unsafe_allow_html=True)
        docx_file = st.file_uploader("Upload Word Document", type=["docx"], key="docx_up")
        if docx_file:
            st.markdown(f"<div class='workflow-card'><p><b>File:</b> {docx_file.name} | <b>Size:</b> {len(docx_file.getvalue())/1024:.1f} KB</p></div>", unsafe_allow_html=True)
            if st.button("🚀 Convert to PDF", type="primary"):
                word_read = docx.Document(docx_file)
                text = "\n".join([p.text for p in word_read.paragraphs])
                new_doc = pymupdf.open()
                new_doc.new_page().insert_textbox(pymupdf.Rect(50, 50, 550, 750), text, fontsize=11)
                bio = io.BytesIO()
                new_doc.save(bio)
                st.success("Converted successfully!")
                st.download_button("📥 Download Converted PDF", bio.getvalue(), file_name="converted.pdf", mime="application/pdf")
        else:
            st.info("💡 **Workflow Example:** Upload `.docx` → View File Details → Convert → Download PDF.")

    with tab4:
        st.markdown("### Merge Multiple PDFs")
        st.markdown("<p style='color: #9ca3af; font-size: 0.85rem;'>Combine multiple separate PDF files in sequence into a single master document.</p>", unsafe_allow_html=True)
        files = st.file_uploader("Upload PDFs in Sequence", type=["pdf"], accept_multiple_files=True, key="merge_up")
        if files:
            st.markdown(f"<div class='workflow-card'><p><b>Files Queued:</b> {len(files)} documents selected.</p></div>", unsafe_allow_html=True)
            if len(files) > 1 and st.button("🚀 Merge PDFs", type="primary"):
                merged = pymupdf.open()
                for f in files:
                    merged.insert_pdf(pymupdf.open(stream=f.read(), filetype="pdf"))
                bio = io.BytesIO()
                merged.save(bio)
                st.success("Successfully merged documents!")
                st.download_button("📥 Download Merged PDF", bio.getvalue(), file_name="merged.pdf", mime="application/pdf")
        else:
            st.info("💡 **Workflow Example:** Upload multiple PDFs → Review Queue Count → Merge → Download.")

    with tab5:
        st.markdown("### Compile Images to PDF")
        st.markdown("<p style='color: #9ca3af; font-size: 0.85rem;&apos;>Upload multiple image assets (PNG, JPG) and compile them into a unified PDF document.</p>", unsafe_allow_html=True)
        imgs = st.file_uploader("Upload Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="img_pdf_up")
        if imgs:
            st.markdown(f"<div class='workflow-card'><p><b>Images Loaded:</b> {len(imgs)} assets ready for compilation.</p></div>", unsafe_allow_html=True)
            if st.button("🚀 Compile to PDF", type="primary"):
                pil_list = [Image.open(im).convert("RGB") for im in imgs]
                bio = io.BytesIO()
                pil_list[0].save(bio, format="PDF", save_all=True, append_images=pil_list[1:])
                st.success("Successfully compiled images!")
                st.download_button("📥 Download Compiled PDF", bio.getvalue(), file_name="compiled.pdf", mime="application/pdf")
        else:
            st.info("💡 **Workflow Example:** Upload Images → Preview Count → Compile → Download PDF.")

    with tab6:
        st.markdown("### Compress PDF Footprint")
        st.markdown("<p style='color: #9ca3af; font-size: 0.85rem;'>Reduce heavy PDF file sizes using advanced garbage collection and compression.</p>", unsafe_allow_html=True)
        pdf_file = st.file_uploader("Upload PDF to Compress", type=["pdf"], key="comp_up")
        if pdf_file:
            orig_size = len(pdf_file.getvalue())
            st.markdown(f"<div class='workflow-card'><p><b>Original Size:</b> {orig_size/1024:.1f} KB</p></div>", unsafe_allow_html=True)
            if st.button("🚀 Compress PDF", type="primary"):
                doc = pymupdf.open(stream=pdf_file.read(), filetype="pdf")
                bio = io.BytesIO()
                doc.save(bio, garbage=4, deflate=True)
                new_size = bio.getbuffer().nbytes
                st.success(f"Optimized! New Size: {new_size/1024:.1f} KB (Saved {(1 - new_size/orig_size)*100:.1f}%)")
                st.download_button("📥 Download Compressed PDF", bio.getvalue(), file_name="compressed.pdf", mime="application/pdf")
        else:
            st.info("💡 **Workflow Example:** Upload PDF → Check Original Size → Compress → Download Optimized File.")

    with tab7:
        st.markdown("### Generate Word Cloud")
        st.markdown("<p style='color: #9ca3af; font-size: 0.85rem;'>Aggregate text across the entire PDF corpus and render a visual word frequency map.</p>", unsafe_allow_html=True)
        pdf_file = st.file_uploader("Upload PDF for Corpus Analysis", type=["pdf"], key="wc_up")
        if pdf_file:
            st.markdown(f"<div class='workflow-card'><p><b>File:</b> {pdf_file.name}</p></div>", unsafe_allow_html=True)
            if st.button("🚀 Generate Word Cloud", type="primary"):
                doc = pymupdf.open(stream=pdf_file.read(), filetype="pdf")
                corpus = " ".join([p.get_text("text") for p in doc])
                wc = WordCloud(width=800, height=400, background_color="#0b0f19", colormap="cool").generate(corpus)
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.imshow(wc, interpolation="bilinear")
                ax.axis("off")
                fig.patch.set_facecolor('#0b0f19')
                st.pyplot(fig)
        else:
            st.info("💡 **Workflow Example:** Upload PDF → Extract Corpus → Render Word Cloud Plot.")

    with tab8:
        st.markdown("### Extract Embedded Assets")
        st.markdown("<p style='color: #9ca3af; font-size: 0.85rem;'>Scan document streams and download all embedded raster images or graphics.</p>", unsafe_allow_html=True)
        pdf_file = st.file_uploader("Upload PDF to Scan Images", type=["pdf"], key="ext_up")
        if pdf_file:
            doc = pymupdf.open(stream=pdf_file.read(), filetype="pdf")
            count = 0
            for i, page in enumerate(doc):
                for img_idx, img in enumerate(page.get_images(full=True)):
                    extracted = doc.extract_image(img[0])
                    count += 1
                    st.image(extracted["image"], width=180, caption=f"Page {i+1} Asset")
                    st.download_button(f"📥 Download Asset {count}", extracted["image"], file_name=f"p{i+1}_img.{extracted['ext']}", key=f"dl_{i}_{img_idx}")
            if count == 0:
                st.info("No embedded raster images found.")
        else:
            st.info("💡 **Workflow Example:** Upload PDF → Scan Streams → Preview Assets → Download Individually.")

# ==================== 2. MEDIA STUDIO PAGE ====================
elif selected_page == "🖼️ Media Studio":
    st.markdown('<p class="hero-title">🖼️ Media Studio</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Resize dimensions, reduce payloads with quality compression, and apply image filters.</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Resize Dimensions", "Quality Compression", "Grayscale Filter"])
    
    with tab1:
        st.markdown("### Resize Image Dimensions")
        st.markdown("<p style='color: #9ca3af; font-size: 0.85rem;'>Compare original image dimensions with custom target pixel parameters.</p>", unsafe_allow_html=True)
        img_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg", "webp"], key="resize_up")
        if img_file:
            img = Image.open(img_file)
            st.markdown(f"<div class='workflow-card'><p><b>Original Dimensions:</b> {img.width} x {img.height} px | <b>Format:</b> {img.format}</p></div>", unsafe_allow_html=True)
            w = st.number_input("Target Width (px)", value=img.width)
            h = st.number_input("Target Height (px)", value=img.height)
            if st.button("🚀 Resize Image", type="primary"):
                res = img.resize((int(w), int(h)))
                st.markdown(f"<p style='color: #34d399;'>✅ Output Dimensions: {res.width} x {res.height} px</p>", unsafe_allow_html=True)
                st.image(res, width=400)
                bio = io.BytesIO()
                res.save(bio, format="PNG")
                st.download_button("📥 Download Resized Image", bio.getvalue(), file_name="resized.png")
        else:
            st.info("💡 **Workflow Example:** Upload Image → View Original Specs → Set Dimensions → Download.")

    with tab2:
        st.markdown("### Quality Compression (KB Reduction)")
        st.markdown("<p style='color: #9ca3af; font-size: 0.85rem;'>Adjust JPEG quality factors to optimize image payload sizes.</p>", unsafe_allow_html=True)
        img_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg", "webp"], key="comp_img_up")
        if img_file:
            img = Image.open(img_file)
            orig_size = len(img_file.getvalue())
            st.markdown(f"<div class='workflow-card'><p><b>Original Size:</b> {orig_size/1024:.1f} KB | <b>Resolution:</b> {img.width} x {img.height} px</p></div>", unsafe_allow_html=True)
            q = st.slider("JPEG Quality Factor", 10, 95, 80)
            if st.button("🚀 Compress Image", type="primary"):
                bio = io.BytesIO()
                img.convert("RGB").save(bio, format="JPEG", quality=q)
                c_bytes = bio.getvalue()
                st.success(f"Optimized Size: {len(c_bytes)/1024:.1f} KB (Saved {(1 - len(c_bytes)/orig_size)*100:.1f}%)")
                st.image(c_bytes, width=400)
                st.download_button("📥 Download Compressed Image", c_bytes, file_name="compressed.jpg", mime="image/jpeg")
        else:
            st.info("💡 **Workflow Example:** Upload Image → Check Original Size → Adjust Slider → Download.")

    with tab3:
        st.markdown("### Grayscale Conversion")
        st.markdown("<p style='color: #9ca3af; font-size: 0.85rem;'>Instantly transform color images into single-channel grayscale matrices.</p>", unsafe_allow_html=True)
        img_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg", "webp"], key="gray_up")
        if img_file:
            img = Image.open(img_file)
            st.markdown(f"<div class='workflow-card'><p><b>File Format:</b> {img.format} | <b>Color Mode:</b> {img.mode}</p></div>", unsafe_allow_html=True)
            if st.button("🚀 Apply Grayscale Filter", type="primary"):
                gray = img.convert("L")
                st.image(gray, width=400)
                bio = io.BytesIO()
                gray.save(bio, format="PNG")
                st.download_button("📥 Download Grayscale Image", bio.getvalue(), file_name="grayscale.png")
        else:
            st.info("💡 **Workflow Example:** Upload Image → Apply Filter → Preview Output → Download.")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #4b5563; font-size: 0.75rem;'>Engineered with Precision by Ashutosh Borah © 2026</p>", unsafe_allow_html=True)
