import os
import streamlit as st
import zipfile
import io
from datetime import datetime
from app.utils import list_files, load_file, save_file
from app.pdf_utils import get_pdf_region

# Base directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Configurations for folders
FAILS_FOLDER = os.path.join(DATA_DIR, "fails")
OUTPUT_FOLDER = os.path.join(DATA_DIR, "output")
ORIGINALS_FOLDER = os.path.join(DATA_DIR, "originals")
PDF_FOLDER = os.path.join(DATA_DIR, "pdfs")

# Initialize session state
if "current_file_index" not in st.session_state:
    st.session_state.current_file_index = 0  # Start with the first file
if "current_data" not in st.session_state:
    st.session_state.current_data = None  # Store the data of the current file

# Function to create a zip file of processed files and clear the folder
def zip_and_clear_folder(folder_path):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zf.write(file_path, os.path.relpath(file_path, folder_path))
                os.remove(file_path)  # Clear files after adding to zip
    zip_buffer.seek(0)
    return zip_buffer

# Fetch list of JSON files
files = list_files(FAILS_FOLDER)

if files:
    # Ensure the index is within bounds
    st.session_state.current_file_index = min(st.session_state.current_file_index, len(files) - 1)

    # Get the currently selected file
    current_file = files[st.session_state.current_file_index]
    file_path = os.path.join(FAILS_FOLDER, current_file)

    # Load data for the current file if not already loaded
    if st.session_state.current_data is None:
        st.session_state.current_data = load_file(file_path)

    # Display navigation progress
    st.write(f"**File {st.session_state.current_file_index + 1} of {len(files)}**")

    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Previous", disabled=st.session_state.current_file_index == 0):
            st.session_state.current_file_index -= 1
            st.session_state.current_data = None  # Reset data for the new file
            st.rerun()
    with col2:
        if st.button("Next", disabled=st.session_state.current_file_index == len(files) - 1):
            st.session_state.current_file_index += 1
            st.session_state.current_data = None  # Reset data for the new file
            st.rerun()

    # Display file name
    st.write(f"### Currently Reviewing: **{current_file}**")

    # Display fields for editing
    data = st.session_state.current_data

    # PDF display
    pdf_name = os.path.splitext(current_file)[0] + ".pdf"
    pdf_path = os.path.join(PDF_FOLDER, pdf_name)
    print(f"Processing PDF path: {pdf_path}")
    if os.path.exists(pdf_path):
        st.write("### PDF Preview")
        # Show cropped header image
        header_image = get_pdf_region(pdf_path, "header")
        if header_image:
            st.image(header_image, caption="Header Region", use_container_width=True)

        # Header fields
        st.write("### Header Information")
        cols = st.columns(3)
        data["patient_name"] = cols[0].text_input("Patient Name", value=data.get("patient_name", ""))

        # Use st.date_input for DOS fields with existing values or leave blank if not available
        cleaned_dos1 = st.date_input(
            "Date of Service 1",
            value=datetime.strptime(data["cleaned_dos1"], "%Y-%m-%d") if data.get("cleaned_dos1") else None,
            key="cleaned_dos1"
        )
        data["cleaned_dos1"] = cleaned_dos1.strftime("%Y-%m-%d") if cleaned_dos1 else ""
        
        cleaned_dos2 = st.date_input(
            "Date of Service 2",
            value=datetime.strptime(data["cleaned_dos2"], "%Y-%m-%d") if data.get("cleaned_dos2") else None,
            key="cleaned_dos2"
        )
        data["cleaned_dos2"] = cleaned_dos2.strftime("%Y-%m-%d") if cleaned_dos2 else ""

        # Show cropped line items image
        line_items_image = get_pdf_region(pdf_path, "line_items")
        if line_items_image:
            st.image(line_items_image, caption="Line Items Region", use_container_width=True)

        # Line items fields
        st.write("### Line Items")
        if "line_items" not in data:
            data["line_items"] = []

        if st.button("Add Line Item"):
            data["line_items"].append({
                "date_of_service": "",
                "plos": "",
                "cpt": "",
                "modifier": "",
                "cleaned_charge": "",
                "units": ""
            })

        for idx, item in enumerate(data.get("line_items", [])):
            st.write(f"#### Line Item {idx + 1}")
            cols = st.columns(6)
            item["date_of_service"] = cols[0].text_input(f"DOS (Item {idx + 1})", value=item.get("date_of_service", ""))
            item["plos"] = cols[1].text_input(f"PLOS (Item {idx + 1})", value=item.get("plos", ""))
            item["cpt"] = cols[2].text_input(f"CPT Code (Item {idx + 1})", value=item.get("cpt", ""))
            item["modifier"] = cols[3].text_input(f"Modifier (Item {idx + 1})", value=item.get("modifier", ""))
            item["cleaned_charge"] = cols[4].text_input(f"Charge (Item {idx + 1})", value=item.get("cleaned_charge", ""))
            item["units"] = cols[5].text_input(f"Units (Item {idx + 1})", value=item.get("units", ""))

            if st.button(f"Remove Line Item {idx + 1}"):
                data["line_items"].pop(idx)
                st.rerun()

        # Show cropped footer image
        footer_image = get_pdf_region(pdf_path, "footer")
        if footer_image:
            st.image(footer_image, caption="Footer Region", use_container_width=True)

        # Footer fields
        st.write("### Footer Information")
        cols = st.columns(3)
        data["cleaned_total_charge"] = cols[0].text_input("Total Charge", value=data.get("cleaned_total_charge", ""))
        data["patient_acct_no"] = cols[1].text_input("Patient Account No", value=data.get("patient_acct_no", ""))
        data["tin"] = cols[2].text_input("TIN", value=data.get("tin", ""))

        if st.button("Open Full PDF"):
            st.write(f"[Open {pdf_name}](./data/pdfs/{pdf_name})", unsafe_allow_html=True)
    else:
        st.warning(f"PDF file not found: {pdf_name}")

    # Reset button
    if st.button("Reset Changes"):
        st.session_state.current_data = load_file(file_path)
        st.rerun()

    # Save button
    if st.button("Save Changes"):
        save_file(data, current_file, FAILS_FOLDER, OUTPUT_FOLDER, ORIGINALS_FOLDER)
        st.success(f"Changes saved for {current_file}")
        st.session_state.current_file_index += 1
        if st.session_state.current_file_index < len(files):
            st.session_state.current_data = None
            st.rerun()
        else:
            st.write("### No more files to review!")
            st.session_state.current_file_index = 0
else:
    st.write("No files to review.")

# Divider for download section
st.divider()
st.header("Download Processed Files")

# Button to download and clear processed files
if st.button("Download and Clear Processed Files"):
    processed_files = list_files(OUTPUT_FOLDER)
    if processed_files:
        zip_buffer = zip_and_clear_folder(OUTPUT_FOLDER)
        st.download_button(
            label="Download Processed JSONs",
            data=zip_buffer,
            file_name="processed_files.zip",
            mime="application/zip"
        )
        st.success("Processed files downloaded and cleared.")
    else:
        st.warning("No processed files to download.")
