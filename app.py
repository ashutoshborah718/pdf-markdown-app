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
    page_title="Shohail | Enterprise Studio", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS Styling & Modern UI Framework
st.markdown("""
    <style>
    /* Main Background & Theme */
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    
    /* Custom Headers */
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #60a5fa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #9ca3af;
        margin-bottom: 25px;
    }
    
    /* Glassmorphism Cards */
    .metric-card {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(75, 85, 99, 0.4);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation Header
st.sidebar.markdown("### ⚡ ASHUTOSH STUDIO")
st.sidebar.markdown("<p style='font-size: 0.85rem; color: #9ca3af;'>Created & Managed by <b>Ashutosh Borah</b></p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

tool_category = st.sidebar.radio(
    "Select Enterprise Module", 
    ["📄 Document Intelligence", "👁️ Computer Vision & CV", "📊 Signal & Data Analytics", "🖼️ Media Studio"]
)

# Helper conversion utilities
def pil_to_cv2(pil_img):
    arr = np.array(pil_img)
    if len(arr.shape) == 2: return arr
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

def cv2_to_pil(cv2_img):
    if len(cv2_img.shape) == 2: return Image.fromarray(cv2_img)
    return Image.fromarray(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB))

# ==================== 1. DOCUMENT INTELLIGENCE ====================
if tool_category == "📄 Document Intelligence":
    st.markdown('<p class="hero-title">📄 Document Intelligence Suite</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Developed by Ashutosh Borah — High-performance parsing, markdown conversion, and visual word analytics.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        st.markdown("### 📥 Source Ingestion")
        uploaded_pdf = st.file_uploader("Upload PDF Document", type=["pdf"], key="doc_up")
        doc_task = st.selectbox("Pipeline Operation", [
            "Convert to Clean Markdown", 
            "Extract & Generate Word Cloud", 
            "Compress PDF Footprint",
            "Extract Embedded Assets"
        ])
        
    with col2:
        if uploaded_pdf is not None:
            pdf_bytes = uploaded_pdf.read()
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            
            st.markdown(f"""
                <div class="metric-card">
                    <h4>📊 Metadata Inspection</h4>
                    <p><b>Filename:</b> {uploaded_pdf.name}</p>
                    <p><b>Page Count:</b> {len(doc)}</p>
                    <p><b>Payload Size:</b> {len(pdf_bytes)/1024:.2f} KB</p>
                </div>
            """, unsafe_allow_html=True)
            
            if doc_task == "Convert to Clean Markdown":
                if st.button("🚀 Initialize Conversion Pipeline", type="primary"):
                    with st.spinner("Processing document layout..."):
                        md = [f"## Page {i+1}\n{page.get_text('text')}\n\n---\n" for i, page in enumerate(doc)]
                        final_md = "".join(md)
                    st.success("Conversion successful!")
                    st.text_area("Markdown Stream Output", final_md, height=280)
                    st.download_button("📥 Download Markdown File", final_md, file_name="document.md", mime="text/markdown")
                    
            elif doc_task == "Extract & Generate Word Cloud":
                if st.button("🚀 Generate Corpus Word Cloud", type="primary"):
                    with st.spinner("Aggregating text and rendering word cloud..."):
                        full_corpus = " ".join([page.get_text("text") for page in doc])
                        wc = WordCloud(width=900, height=450, background_color="#0b0f19", colormap="cool").generate(full_corpus)
                        
                        fig, ax = plt.subplots(figsize=(10, 5))
                        ax.imshow(wc, interpolation="bilinear")
                        ax.axis("off")
                        fig.patch.set_facecolor('#0b0f19')
                        st.pyplot(fig)
                        
            elif doc_task == "Compress PDF Footprint":
                comp_level = st.selectbox("Compression Strategy", ["Standard Deflate", "Aggressive Garbage Collection"])
                if st.button("🚀 Execute Compression", type="primary"):
                    out = io.BytesIO()
                    g_val = 4 if "Aggressive" in comp_level else 1
                    doc.save(out, garbage=g_val, deflate=True)
                    res_bytes = out.getvalue()
                    
                    st.success(f"Optimized! New Size: {len(res_bytes)/1024:.2f} KB (Saved {(1 - len(res_bytes)/len(pdf_bytes))*100:.1f}%)")
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
                    if counter == 0: st.info("No raster image assets embedded in document stream.")
        else:
            st.info("👈 Upload a PDF document via the control panel to initialize workflow.")

# ==================== 2. COMPUTER VISION & CV ====================
elif tool_category == "👁️ Computer Vision & CV":
    st.markdown('<p class="hero-title">👁️ Computer Vision Studio</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Advanced low-light enhancement, structural edge mapping, and Otsu thresholding.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        st.markdown("### 📥 Frame Ingestion")
        cv_upload = st.file_uploader("Upload Image Target", type=["png", "jpg", "jpeg"], key="cv_file")
        cv_pipeline = st.selectbox("Vision Algorithm", [
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
                if st.button("🚀 Run Enhancement Algorithm", type="primary"):
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
                    
                    st.success(f"Otsu Segmentation Complete: Identified {len(contours)} distinct structures.")
                    st.image(final_pl, caption="Segmented Boundaries", use_container_width=True)
        else:
            st.info("👈 Upload an image file for computer vision processing.")

# ==================== 3. SIGNAL & DATA ANALYTICS ====================
elif tool_category == "📊 Signal & Data Analytics":
    st.markdown('<p class="hero-title">📊 Signal & Data Spectrum Analyzer</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Generate synthetic signal waveforms or run Fast Fourier Transform (FFT) frequency analysis.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        st.markdown("### ⚙️ Signal Parameters")
        freq = st.slider("Signal Frequency (Hz)", 1, 50, 5)
        noise_level = st.slider("Additive Noise Factor", 0.0, 1.0, 0.2)
        analysis_type = st.selectbox("Analysis Mode", ["Time-Domain Waveform", "Frequency Spectrum (FFT Power Density)"])
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <h4>📈 Simulation Status</h4>
                <p><b>Sampling Rate:</b> 1000 Hz</p>
                <p><b>Configuration:</b> Sine Wave + Gaussian Noise</p>
            </div>
        """, unsafe_allow_html=True)
        
        np.random.seed(42)
        t = np.linspace(0, 1, 1000)
        signal = np.sin(2 * np.pi * freq * t) + noise_level * np.random.normal(size=1000)
        
        fig, ax = plt.subplots(figsize=(9, 4))
        fig.patch.set_facecolor('#0b0f19')
        ax.set_facecolor('#111827')
        
        if analysis_type == "Time-Domain Waveform":
            ax.plot(t[:200], signal[:200], color="#60a5fa", linewidth=2)
            ax.set_title("Time-Domain Signal Capture", color="white")
            ax.set_xlabel("Time (s)", color="#9ca3af")
            ax.set_ylabel("Amplitude", color="#9ca3af")
        else:
            yf = np.fft.fft(signal)
            xf = np.fft.fftfreq(1000, 1/1000)[:500]
            ax.plot(xf, 2.0/1000 * np.abs(yf[0:500]), color="#c084fc", linewidth=2)
            ax.set_title("FFT Frequency Power Spectrum", color="white")
            ax.set_xlabel("Frequency (Hz)", color="#9ca3af")
            ax.set_ylabel("Power Spectral Density", color="#9ca3af")
            
        ax.tick_params(colors="#9ca3af")
        for spine in ax.spines.values(): spine.set_edgecolor("#374151")
        st.pyplot(fig)

# ==================== 4. MEDIA STUDIO ====================
elif tool_category == "🖼️ Media Studio":
    st.markdown('<p class="hero-title">🖼️ Media Compression & Format Studio</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Batch resize dimensions, adjust quality compression ratios, and apply filters.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        st.markdown("### 📥 Media Ingestion")
        media_file = st.file_uploader("Upload Image Asset", type=["png", "jpg", "jpeg", "webp"], key="media_up")
        media_op = st.selectbox("Operation Mode", ["Resize Dimensions", "Quality Compression (KB Reduction)", "Grayscale Conversion"])
    with col2:
        if media_file is not None:
            img = Image.open(media_file)
            st.markdown(f"""
                <div class="metric-card">
                    <h4>📊 Asset Specifications</h4>
                    <p><b>Resolution:</b> {img.width} x {img.height} px</p>
                    <p><b>Format:</b> {img.format}</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.image(img, caption="Source Preview", use_container_width=True)
            
            if media_op == "Resize Dimensions":
                nw = st.number_input("Target Width (px)", value=img.width)
                nh = st.number_input("Target Height (px)", value=img.height)
                if st.button("🚀 Resize Asset", type="primary"):
                    res = img.resize((int(nw), int(nh)))
                    st.image(res, caption="Resized Output", use_container_width=True)
                    buf = io.BytesIO()
                    res.save(buf, format="JPEG" if img.format=='JPEG' else 'PNG')
                    st.download_button("📥 Download Resized Image", buf.getvalue(), file_name="resized.jpg")
                    
            elif media_op == "Quality Compression (KB Reduction)":
                q_val = st.slider("Compression Quality Factor", 10, 95, 80)
                if st.button("🚀 Compress Asset", type="primary"):
                    buf = io.BytesIO()
                    rgb_img = img.convert("RGB") if img.mode in ("RGBA", "P") else img
                    rgb_img.save(buf, format="JPEG", quality=q_val)
                    c_bytes = buf.getvalue()
                    st.success(f"Optimized File Size: {len(c_bytes)/1024:.2f} KB")
                    st.image(c_bytes, caption="Compressed Preview")
                    st.download_button("📥 Download Compressed Image", c_bytes, file_name="compressed.jpg", mime="image/jpeg")
                    
            elif media_op == "Grayscale Conversion":
                if st.button("🚀 Apply Grayscale Matrix", type="primary"):
                    gray = img.convert("L")
                    st.image(gray, caption="Grayscale Output", use_container_width=True)
                    buf = io.BytesIO()
                    gray.save(buf, format="PNG")
                    st.download_button("📥 Download Grayscale Image", buf.getvalue(), file_name="grayscale.png", mime="image/png")
        else:
            st.info("👈 Upload an image asset from the left panel.")

# Footer Watermark
st.markdown("---")
st.markdown("<p style='text-align: center; color: #4b5563; font-size: 0.85rem;'>Engineered with Precision by Ashutosh Borah © 2026</p>", unsafe_allow_html=True)
