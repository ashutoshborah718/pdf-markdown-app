import streamlit as st
import pymupdf
from PIL import Image
import numpy as np
import cv2
import io

st.set_page_config(page_title="Advanced Doc & CV Studio", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .main-header { font-size: 2.3rem; font-weight: 700; color: #FF4B4B; }
    .sub-header { font-size: 1.05rem; color: #888; margin-bottom: 25px; }
    .card { background-color: #1e1e1e; padding: 18px; border-radius: 10px; border: 1px solid #333; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.markdown("### 🎛️ Studio Navigation")
tool_category = st.sidebar.radio("Select Module", ["📄 PDF Advanced Hub", "🖼️ Image Compression & Resize", "👁️ Computer Vision & Enhancement"])

# Helper function to convert PIL to OpenCV format
def pil_to_cv2(pil_img):
    numpy_image = np.array(pil_img)
    if len(numpy_image.shape) == 2:
        return numpy_image
    return cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)

# Helper function to convert OpenCV to PIL format
def cv2_to_pil(cv2_img):
    if len(cv2_img.shape) == 2:
        return Image.fromarray(cv2_img)
    return Image.fromarray(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB))

# ==================== 1. PDF ADVANCED HUB ====================
if tool_category == "📄 PDF Advanced Hub":
    st.markdown('<p class="main-header">📄 PDF Advanced Hub</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Convert, extract elements, and compress heavy PDF files.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        uploaded_pdf = st.file_uploader("Upload PDF file", type=["pdf"], key="pdf_hub")
        pdf_op = st.selectbox("Operation", ["Convert to Markdown", "Extract Text", "Extract Images", "Compress PDF File"])
        
    with col2:
        if uploaded_pdf is not None:
            pdf_bytes = uploaded_pdf.read()
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            st.markdown(f'<div class="card"><h4>📊 PDF Info</h4><p><b>Pages:</b> {len(doc)}</p><p><b>Size:</b> {len(pdf_bytes)/1024:.1f} KB</p></div>', unsafe_allow_html=True)
            
            if pdf_op == "Convert to Markdown":
                if st.button("Run Conversion", type="primary"):
                    md = []
                    for i, page in enumerate(doc):
                        md.append(f"## Page {i + 1}\n{page.get_text('text')}\n\n---\n")
                    final_md = "".join(md)
                    st.text_area("Markdown Output", final_md, height=300)
                    st.download_button("Download .md", final_md, file_name="converted.md", mime="text/markdown")
                    
            elif pdf_op == "Extract Text":
                if st.button("Extract Text", type="primary"):
                    text = "".join([page.get_text("text") + "\n" for page in doc])
                    st.text_area("Plain Text", text, height=300)
                    st.download_button("Download .txt", text, file_name="extracted.txt", mime="text/plain")
                    
            elif pdf_op == "Extract Images":
                if st.button("Extract Embedded Images", type="primary"):
                    count = 0
                    for i, page in enumerate(doc):
                        for img_idx, img in enumerate(page.get_images(full=True)):
                            base_img = doc.extract_image(img[0])
                            count += 1
                            st.image(base_img["image"], caption=f"Page {i+1} Image {img_idx+1}", width=250)
                            st.download_button(f"Download Image {count}", base_img["image"], file_name=f"p{i+1}_img{img_idx+1}.{base_img['ext']}", key=f"pdf_img_{i}_{img_idx}")
                    if count == 0: st.info("No embedded raster images found.")
                    
            elif pdf_op == "Compress PDF File":
                quality_mode = st.selectbox("Compression Level", ["Standard (Default)", "High Compression (Smaller Size)"])
                if st.button("Compress PDF", type="primary"):
                    # Save with garbage collection and defragmentation
                    output_stream = io.BytesIO()
                    garbage_val = 4 if quality_mode == "High Compression (Smaller Size)" else 1
                    doc.save(output_stream, garbage=garbage_val, deflate=True)
                    compressed_bytes = output_stream.getvalue()
                    
                    st.success(f"Compressed successfully! New Size: {len(compressed_bytes)/1024:.1f} KB")
                    st.download_button("Download Compressed PDF", compressed_bytes, file_name="compressed_document.pdf", mime="application/pdf")
        else:
            st.info("👈 Upload a PDF file from the left panel.")

# ==================== 2. IMAGE COMPRESSION & RESIZE ====================
elif tool_category == "🖼️ Image Compression & Resize":
    st.markdown('<p class="main-header">🖼️ Image Compression & Resize Studio</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Resize dimensions and reduce file size effortlessly.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        uploaded_img = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg", "webp"], key="img_comp")
        img_task = st.selectbox("Task", ["Resize Image Dimensions", "Compress Image Quality (KB/MB Reduction)"])
    with col2:
        if uploaded_img is not None:
            image = Image.open(uploaded_img)
            st.image(image, caption="Original Preview", use_container_width=True)
            
            if img_task == "Resize Image Dimensions":
                w = st.number_input("Width (px)", value=image.width)
                h = st.number_input("Height (px)", value=image.height)
                if st.button("Resize Image", type="primary"):
                    res = image.resize((int(w), int(h)))
                    st.image(res, caption="Resized Output", use_container_width=True)
                    buf = io.BytesIO()
                    res.save(buf, format="JPEG" if image.format=='JPEG' else 'PNG')
                    st.download_button("Download Resized", buf.getvalue(), file_name="resized_image.jpg")
                    
            elif img_task == "Compress Image Quality (KB/MB Reduction)":
                quality = st.slider("JPEG Quality Factor (Lower = Smaller Size)", 10, 95, 75)
                if st.button("Compress Image", type="primary"):
                    buf = io.BytesIO()
                    rgb_img = image.convert("RGB") if image.mode in ("RGBA", "P") else image
                    rgb_img.save(buf, format="JPEG", quality=quality)
                    comp_bytes = buf.getvalue()
                    st.success(f"Compressed Size: {len(comp_bytes)/1024:.1f} KB")
                    st.image(comp_bytes, caption="Compressed Preview")
                    st.download_button("Download Compressed Image", comp_bytes, file_name="compressed_image.jpg", mime="image/jpeg")
        else:
            st.info("👈 Upload an image file from the left panel.")

# ==================== 3. COMPUTER VISION & ENHANCEMENT ====================
elif tool_category == "👁️ Computer Vision & Enhancement":
    st.markdown('<p class="main-header">👁️ Computer Vision & Enhancement Lab</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Low-light enhancement, color channels, edge detection, and feature analysis.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        cv_file = st.file_uploader("Upload Image for CV", type=["png", "jpg", "jpeg"], key="cv_up")
        cv_op = st.selectbox("CV Operation", [
            "Low-Light Enhancement (Retinex / CLAHE)",
            "Color Space Splitter (RGB / HSV / LAB)",
            "Canny Edge Detection",
            "Contour / Object Boundary Detection"
        ])
    with col2:
        if cv_file is not None:
            pil_img = Image.open(cv_file)
            cv_img = pil_to_cv2(pil_img)
            st.image(pil_img, caption="Input Image", use_container_width=True)
            
            if cv_op == "Low-Light Enhancement (Retinex / CLAHE)":
                enh_method = st.radio("Enhancement Algorithm", ["CLAHE (Adaptive Histogram)", "Gamma Correction (Brightening)"])
                if st.button("Apply Enhancement", type="primary"):
                    if enh_method == "CLAHE (Adaptive Histogram)":
                        lab = cv2.cvtColor(cv_img, cv2.COLOR_BGR2LAB)
                        l, a, b = cv2.split(lab)
                        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
                        cl = clahe.apply(l)
                        merged = cv2.merge((cl, a, b))
                        out_cv = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
                    else:
                        gamma = 1.8
                        invGamma = 1.0 / gamma
                        table = np.array([((i / 255.0) ** invGamma) * 255 for i in range(256)]).astype("uint8")
                        out_cv = cv2.LUT(cv_img, table)
                        
                    out_pil = cv2_to_pil(out_cv)
                    st.image(out_pil, caption="Enhanced Output", use_container_width=True)
                    buf = io.BytesIO()
                    out_pil.save(buf, format="PNG")
                    st.download_button("Download Enhanced Image", buf.getvalue(), file_name="enhanced_image.png")
                    
            elif cv_op == "Color Space Splitter (RGB / HSV / LAB)":
                space = st.selectbox("Color Space", ["RGB", "HSV", "LAB"])
                if st.button("Split Channels", type="primary"):
                    if space == "RGB":
                        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
                        c1, c2, c3 = cv2.split(rgb)
                        names = ["Red Channel", "Green Channel", "Blue Channel"]
                    elif space == "HSV":
                        hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
                        c1, c2, c3 = cv2.split(hsv)
                        names = ["Hue (H)", "Saturation (S)", "Value (V)"]
                    else:
                        lab_space = cv2.cvtColor(cv_img, cv2.COLOR_BGR2LAB)
                        c1, c2, c3 = cv2.split(lab_space)
                        names = ["Lightness (L)", "A-Channel", "B-Channel"]
                        
                    col_a, col_b, col_c = st.columns(3)
                    with col_a: st.image(c1, caption=names[0], use_container_width=True, clamp=True)
                    with col_b: st.image(c2, caption=names[1], use_container_width=True, clamp=True)
                    with col_c: st.image(c3, caption=names[2], use_container_width=True, clamp=True)
                    
            elif cv_op == "Canny Edge Detection":
                t1 = st.slider("Threshold 1", 0, 255, 100)
                t2 = st.slider("Threshold 2", 0, 255, 200)
                if st.button("Detect Edges", type="primary"):
                    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
                    edges = cv2.Canny(gray, t1, t2)
                    st.image(edges, caption="Canny Edges", use_container_width=True, clamp=True)
                    buf = io.BytesIO()
                    Image.fromarray(edges).save(buf, format="PNG")
                    st.download_button("Download Edge Mask", buf.getvalue(), file_name="canny_edges.png")
                    
            elif cv_op == "Contour / Object Boundary Detection":
                thresh_val = st.slider("Binary Threshold", 0, 255, 127)
                if st.button("Find Contours", type="primary"):
                    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
                    _, thresh = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
                    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    cv_contour = cv_img.copy()
                    cv2.drawContours(cv_contour, contours, -1, (0, 255, 0), 2)
                    out_pil = cv2_to_pil(cv_contour)
                    
                    st.success(f"Detected {len(contours)} distinct object boundaries/contours!")
                    st.image(out_pil, caption="Detected Boundaries", use_container_width=True)
        else:
            st.info("👈 Upload an image file for computer vision operations.")
