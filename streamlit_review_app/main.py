import os
import streamlit as st
from app.utils import list_files, load_file, save_file
from app.pdf_utils import get_pdf_region
from datetime import datetime

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
            st.experimental_rerun()
    with col2:
        if st.button("Next", disabled=st.session_state.current_file_index == len(files) - 1):
            st.session_state.current_file_index += 1
            st.session_state.current_data = None  # Reset data for the new file
            st.experimental_rerun()

    # Display file name
    st.write(f"### Currently Reviewing: **{current_file}**")

    # Display fields for editing
    data = st.session_state.current_data

    # PDF display
    pdf_name = os.path.splitext(current_file)[0] + ".pdf"
    pdf_path = os.path.join(PDF_FOLDER, pdf_name)
    # Debugging: Print PDF path to verify
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

        cleaned_dos1 = cols[1].date_input(
            "Date of Service 1",
            value=datetime.strptime(data.get("cleaned_dos1", "2025-01-01"), "%Y-%m-%d") if data.get("cleaned_dos1") else None,
            key="cleaned_dos1"
        )
        data["cleaned_dos1"] = cleaned_dos1.strftime("%Y-%m-%d") if cleaned_dos1 else ""

        cleaned_dos2 = cols[2].date_input(
            "Date of Service 2",
            value=datetime.strptime(data.get("cleaned_dos2", "2025-01-01"), "%Y-%m-%d") if data.get("cleaned_dos2") else None,
            key="cleaned_dos2"
        )
        data["cleaned_dos2"] = cleaned_dos2.strftime("%Y-%m-%d") if cleaned_dos2 else ""

        # Show cropped line items image
        line_items_image = get_pdf_region(pdf_path, "line_items")
        if line_items_image:
            st.image(line_items_image, caption="Line Items Region", use_container_width=True)

        # Line items fields
        st.write("### Line Items")
        for idx, item in enumerate(data.get("line_items", [])):
            st.write(f"#### Line Item {idx + 1}")
            cols = st.columns(6)
            item["date_of_service"] = cols[0].text_input(f"DOS (Item {idx + 1})", value=item.get("date_of_service", ""))
            item["plos"] = cols[1].text_input(f"PLOS (Item {idx + 1})", value=item.get("plos", ""))
            item["cpt"] = cols[2].text_input(f"CPT Code (Item {idx + 1})", value=item.get("cpt", ""))
            item["modifier"] = cols[3].text_input(f"Modifier (Item {idx + 1})", value=item.get("modifier", ""))
            item["cleaned_charge"] = cols[4].text_input(f"Charge (Item {idx + 1})", value=item.get("cleaned_charge", ""))
            item["units"] = cols[5].text_input(f"Units (Item {idx + 1})", value=item.get("units", ""))

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

        # Open full PDF button
        if st.button("Open Full PDF"):
            st.write(f"[Open {pdf_name}](./data/pdfs/{pdf_name})", unsafe_allow_html=True)
    else:
        st.warning(f"PDF file not found: {pdf_name}")

    # Reset button
    if st.button("Reset Changes"):
        st.session_state.current_data = load_file(file_path)  # Reload original data
        st.experimental_rerun()

    # Save button
    if st.button("Save Changes"):
        save_file(data, current_file, FAILS_FOLDER, OUTPUT_FOLDER, ORIGINALS_FOLDER)
        st.success(f"Changes saved for {current_file}")
        st.session_state.current_file_index += 1  # Move to the next file
        if st.session_state.current_file_index < len(files):
            st.session_state.current_data = None  # Reset data for the new file
            st.experimental_rerun()
        else:
            st.write("### No more files to review!")
            st.session_state.current_file_index = 0  # Reset to the first file
else:
    st.write("No files to review.")
