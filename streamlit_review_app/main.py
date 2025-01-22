import streamlit as st
from app.utils import list_files, load_file, save_file
from app.pdf_utils import get_pdf_region
import os

# Configurations
FAILS_FOLDER = "streamlit_review_app/data/fails"
OUTPUT_FOLDER = "streamlit_review_app/data/output"
PDF_FOLDER = "streamlit_review_app/data/pdfs"
ORIGINALS_FOLDER = "streamlit_review_app/data/originals"

# Streamlit App
st.title("JSON Review Interface")

# File List
files = list_files(FAILS_FOLDER)
if not files:
    st.write("No files to review.")
else:
    selected_file = st.selectbox("Select a file to review:", files)
    if selected_file:
        st.subheader(f"Reviewing: {selected_file}")
        data = load_file(os.path.join(FAILS_FOLDER, selected_file))
        
        # Full PDF Button
        pdf_path = os.path.join(PDF_FOLDER, os.path.splitext(selected_file)[0] + '.pdf')
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
                st.download_button(
                    label="Open Full PDF",
                    data=pdf_bytes,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf"
                )
        else:
            st.error("Corresponding PDF not found.")

        # Header Section
        st.write("### Header Section")
        st.image(get_pdf_region(PDF_FOLDER, selected_file, 'header'), caption="Header Region", use_column_width=True)
        st.write("#### Header Fields")
        data["patient_name"] = st.text_input("Patient Name", value=data.get("patient_name", ""))
        data["cleaned_dos1"] = st.text_input("Date of Service 1", value=data.get("cleaned_dos1", ""))
        data["cleaned_dos2"] = st.text_input("Date of Service 2", value=data.get("cleaned_dos2", ""))
        
        # Line Items Section
        st.write("### Line Items Section")
        st.image(get_pdf_region(PDF_FOLDER, selected_file, 'line_items'), caption="Line Items Region", use_column_width=True)
        st.write("#### Line Items Fields")
        for idx, item in enumerate(data.get("line_items", [])):
            st.write(f"##### Line Item {idx + 1}")
            item["date_of_service"] = st.text_input(f"DOS (Item {idx + 1})", value=item.get("date_of_service", ""))
            item["cpt"] = st.text_input(f"CPT Code (Item {idx + 1})", value=item.get("cpt", ""))
            item["cleaned_charge"] = st.text_input(f"Charge (Item {idx + 1})", value=item.get("cleaned_charge", ""))
            item["modifier"] = st.text_input(f"Modifier (Item {idx + 1})", value=item.get("modifier", ""))
            item["units"] = st.text_input(f"Units (Item {idx + 1})", value=item.get("units", ""))

        # Footer Section
        st.write("### Footer Section")
        st.image(get_pdf_region(PDF_FOLDER, selected_file, 'footer'), caption="Footer Region", use_column_width=True)
        st.write("#### Footer Fields")
        data["cleaned_total_charge"] = st.text_input("Total Charge", value=data.get("cleaned_total_charge", ""))
        data["patient_acct_no"] = st.text_input("Patient Account No", value=data.get("patient_acct_no", ""))
        
        # Save Changes
        if st.button("Save Changes"):
            save_file(data, selected_file, FAILS_FOLDER, OUTPUT_FOLDER, ORIGINALS_FOLDER)
            st.success(f"Saved changes to {selected_file}")
