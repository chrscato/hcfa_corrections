import os
import streamlit as st
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
            st.image(header_image, caption="Header Region", use_column_width=True)

        # Header fields
        st.write("### Header Information")
        data["patient_name"] = st.text_input("Patient Name", value=data.get("patient_name", ""))
        data["cleaned_dos1"] = st.text_input("Date of Service 1", value=data.get("cleaned_dos1", ""))
        data["cleaned_dos2"] = st.text_input("Date of Service 2", value=data.get("cleaned_dos2", ""))

        # Show cropped line items image
        line_items_image = get_pdf_region(pdf_path, "line_items")
        if line_items_image:
            st.image(line_items_image, caption="Line Items Region", use_column_width=True)

        # Line items fields
        st.write("### Line Items")
        for idx, item in enumerate(data.get("line_items", [])):
            st.write(f"#### Line Item {idx + 1}")
            item["date_of_service"] = st.text_input(f"DOS (Item {idx + 1})", value=item.get("date_of_service", ""))
            item["cpt"] = st.text_input(f"CPT Code (Item {idx + 1})", value=item.get("cpt", ""))
            item["cleaned_charge"] = st.text_input(f"Charge (Item {idx + 1})", value=item.get("cleaned_charge", ""))

        # Show cropped footer image
        footer_image = get_pdf_region(pdf_path, "footer")
        if footer_image:
            st.image(footer_image, caption="Footer Region", use_column_width=True)

        # Footer fields
        st.write("### Footer Information")
        data["cleaned_total_charge"] = st.text_input("Total Charge", value=data.get("cleaned_total_charge", ""))
        data["patient_acct_no"] = st.text_input("Patient Account No", value=data.get("patient_acct_no", ""))

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
