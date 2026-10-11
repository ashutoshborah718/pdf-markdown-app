import streamlit as st
import pymupdf
from PIL import Image
import io

st.set_page_config(page_title="PDF & Image Powerhouse", page_icon="⚡", layout="centered")

st.title("⚡ PDF & Image Multi-Tool Hub")
st.write("Your all-in-one free toolkit for advanced document and image operations.")

# Sidebar navigation
tool_category = st.sidebar.selectbox("Choose Category", ["📄 PDF Operations", "🖼️ Image Operations"])

# ==================== PDF OPERATIONS ====================
if tool_category == "📄 PDF Operations":
    st.header("📄 PDF Toolkit")
    pdf_operation = st.selectbox(
        "Select PDF Task", 
        ["Convert PDF to Markdown", "Extract All Text", "Extract Images from PDF"]
    )
    
    uploaded_pdf = st.file_uploader("Upload PDF file", type=["pdf"])
    
    if uploaded_pdf is not None:
        doc = pymupdf.open(stream=uploaded_pdf.read(), filetype="pdf")
        st.success(f"Loaded PDF successfully! Pages: {len(doc)}")
        
        if pdf_operation == "Convert PDF to Markdown":
            if st.button("Run Conversion"):
                markdown_content = []
                for i, page in enumerate(doc):
                    markdown_content.append(f"## Page {i + 1}\n{page.get_text('text')}\n\n---\n")
                final_md = "".join(markdown_content)
                st.text_area("Markdown Output", final_md, height=300)
                st.download_button("Download .md", final_md, file_name="converted.md", mime="text/markdown")
                
        elif pdf_operation == "Extract All Text":
            if st.button("Extract Text"):
                all_text = "".join([page.get_text("text") + "\n" for page in doc])
                st.text_area("Plain Text Output", all_text, height=300)
                st.download_button("Download .txt", all_text, file_name="extracted.txt", mime="text/plain")
                
        elif pdf_operation == "Extract Images from PDF":
            if st.button("Extract Images"):
                image_count = 0
                for i, page in enumerate(doc):
                    image_list = page.get_images(full=True)
                    for img_index, img in enumerate(image_list):
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        image_count += 1
                        st.image(image_bytes, caption=f"Page {i + 1} - Image {img_index + 1}", width=300)
                        st.download_button(
                            label=f"Download Image {image_count} ({image_ext})",
                            data=image_bytes,
                            file_name=f"page_{i+1}_img_{img_index+1}.{image_ext}",
                            mime=f"image/{image_ext}",
                            key=f"dl_img_{i}_{img_index}"
                        )
                if image_count == 0:
                    st.info("No embedded images found in this PDF.")

# ==================== IMAGE OPERATIONS ====================
elif tool_category == "🖼️ Image Operations":
    st.header("🖼️ Image Toolkit")
    img_operation = st.selectbox(
        "Select Image Task", 
        ["Convert Format (PNG/JPG/WEBP)", "Resize Image", "Grayscale Filter"]
    )
    
    uploaded_img = st.file_uploader("Upload Image file", type=["png", "jpg", "jpeg", "webp"])
    
    if uploaded_img is not None:
        image = Image.open(uploaded_img)
        st.image(image, caption="Original Image", use_container_width=True)
        
        if img_operation == "Convert Format (PNG/JPG/WEBP)":
            target_format = st.selectbox("Convert to format", ["PNG", "JPEG", "WEBP"])
            if st.button("Convert Image"):
                buf = io.BytesIO()
                # Handle RGBA to RGB conversion for JPEG
                save_img = image
                if target_format == "JPEG" and image.mode in ("RGBA", "P"):
                    save_img = image.convert("RGB")
                
                save_img.save(buf, format=target_format)
                byte_im = buf.getvalue()
                
                st.success(f"Successfully converted to {target_format}!")
                st.download_button(
                    label=f"Download {target_format} Image",
                    data=byte_im,
                    file_name=f"converted_image.{target_format.lower()}",
                    mime=f"image/{target_format.lower()}"
                )
                
        elif img_operation == "Resize Image":
            width = st.number_input("New Width (pixels)", value=image.width)
            height = st.number_input("New Height (pixels)", value=image.height)
            if st.button("Resize"):
                resized_img = image.resize((int(width), int(height)))
                st.image(resized_img, caption="Resized Image", use_container_width=True)
                
                buf = io.BytesIO()
                resized_img.save(buf, format=image.format if image.format else "PNG")
                st.download_button(
                    label="Download Resized Image",
                    data=buf.getvalue(),
                    file_name=f"resized_image.{image.format.lower() if image.format else 'png'}"
                )
                
        elif img_operation == "Grayscale Filter":
            if st.button("Apply Grayscale"):
                gray_img = image.convert("L")
                st.image(gray_img, caption="Grayscale Image", use_container_width=True)
                
                buf = io.BytesIO()
                gray_img.save(buf, format="PNG")
                st.download_button(
                    label="Download Grayscale Image",
                    data=buf.getvalue(),
                    file_name="grayscale_image.png",
                    mime="image/png"
                )
