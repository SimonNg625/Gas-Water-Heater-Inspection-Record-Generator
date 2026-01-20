import streamlit as st
import os
import zipfile
import shutil
import re
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import tempfile
from io import BytesIO

# --- 1. Helper Functions (Logic remains mostly the same) ---

def create_embedded_template(save_path):
    doc = Document()
    heading = doc.add_heading('Gas Water Heater Inspection Record', level=0)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    table = doc.add_table(rows=4, cols=2)
    table.style = 'Table Grid'
    
    labels = ["Project Name/Location", "Flat", "Name of Inspector", "Inspection Date"]
    
    for i, label in enumerate(labels):
        cell = table.cell(i, 0)
        cell.text = label
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.bold = True

    doc.save(save_path)

def parse_filename(filename):
    # Expected: Project-Tower-Flat-Inspector-Date
    base_name = os.path.splitext(filename)[0]
    clean_name = re.sub(r'\s\(\d+\)$', '', base_name) # Remove (1), (2) duplicates
    parts = clean_name.split('-')
    
    if len(parts) >= 5:
        project = parts[0]
        tower = parts[1]
        flat = parts[2]
        inspector = parts[3]
        date = '-'.join(parts[4:])
        group_key = f"{project}-{tower}-{flat}"
        return project, tower, flat, inspector, date, group_key
    else:
        return None, None, None, None, None, None

# --- 2. Main Streamlit App ---

def main():
    st.set_page_config(page_title="Inspection Report Generator", page_icon="📝")
    
    st.title("📝 Gas Water Heater Inspection Record Generator")
    st.markdown("""
    **Instructions:**
    1. Rename your images to this format: `Project-Tower-Flat-Inspector-Date.jpg`  
       *(e.g., `太湖花園大埔道18號-5座-1A-譚大文-5-10-2021.jpg`)*
    2. Zip all images into a single `.zip` file.
    3. Upload below and click **Generate**.
    """)

    # File Uploader
    uploaded_file = st.file_uploader("Upload Images ZIP", type="zip")

    if uploaded_file is not None:
        if st.button("Generate Reports", type="primary"):
            
            # Create a temporary directory to work in
            with tempfile.TemporaryDirectory() as temp_dir:
                extract_path = os.path.join(temp_dir, "input_images")
                output_path = os.path.join(temp_dir, "output_docs")
                os.makedirs(extract_path)
                os.makedirs(output_path)
                
                # Extract ZIP
                with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                
                # Generate Template
                template_path = os.path.join(temp_dir, "template.docx")
                create_embedded_template(template_path)

                # Group Images
                grouped_data = {}
                valid_count = 0
                
                # Walk through extracted files
                for root_dir, dirs, files in os.walk(extract_path):
                    for file in files:
                        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                            project, tower, flat, inspector, date, key = parse_filename(file)
                            if project:
                                if key not in grouped_data:
                                    grouped_data[key] = {
                                        'project': project, 'tower': tower, 'flat': flat, 
                                        'inspector': inspector, 'date': date, 'images': []
                                    }
                                full_path = os.path.join(root_dir, file)
                                grouped_data[key]['images'].append(full_path)
                                valid_count += 1

                if valid_count == 0:
                    st.error("No valid images found! Please check your filenames.")
                else:
                    st.success(f"Found {len(grouped_data)} unique locations. Generating reports...")
                    
                    # Progress Bar
                    progress_bar = st.progress(0)
                    
                    # Generate Docs
                    for i, (key, data) in enumerate(grouped_data.items()):
                        try:
                            doc = Document(template_path)
                            table = doc.tables[0]
                            table.cell(0, 1).text = data['project']
                            table.cell(1, 1).text = f"{data['tower']} {data['flat']}"
                            table.cell(2, 1).text = data['inspector']
                            table.cell(3, 1).text = data['date']
                            
                            data['images'].sort()
                            p = doc.add_paragraph()
                            p.paragraph_format.line_spacing = 1.2
                            p.paragraph_format.space_before = Pt(12)
                            p.paragraph_format.space_after = Pt(12)
                            
                            for img_path in data['images']:
                                try:
                                    run = p.add_run()
                                    run.add_picture(img_path, width=Inches(2.5))
                                    run.add_text(" " * 8)
                                except Exception as e:
                                    st.warning(f"Could not add image: {os.path.basename(img_path)}")

                            safe_filename = f"{key}.docx".replace('/', '_')
                            doc.save(os.path.join(output_path, safe_filename))
                        
                        except Exception as e:
                            st.error(f"Error generating {key}: {e}")
                        
                        # Update progress
                        progress_bar.progress((i + 1) / len(grouped_data))

                    # Zip the results into memory
                    st.info("Zipping files...")
                    
                    zip_buffer = BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                        for root, _, files in os.walk(output_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                zf.write(file_path, arcname=file)
                    
                    zip_buffer.seek(0)
                    
                    st.success("✅ Done! Download your reports below.")
                    
                    # Download Button
                    st.download_button(
                        label="⬇️ Download All Reports (ZIP)",
                        data=zip_buffer,
                        file_name="Inspection_Reports.zip",
                        mime="application/zip"
                    )

if __name__ == "__main__":
    main()