import streamlit as st
import requests

st.title("📑 PDF Difference Checker with Database Storage")

pdf1 = st.file_uploader("Upload first PDF", type="pdf")
pdf2 = st.file_uploader("Upload second PDF", type="pdf")

if st.button("Compare and Save") and pdf1 and pdf2:
    with st.spinner("Comparing PDFs..."):
        files = {
            "pdf1": (pdf1.name, pdf1, "application/pdf"),
            "pdf2": (pdf2.name, pdf2, "application/pdf"),
        }
        response = requests.post("http://127.0.0.1:8000/compare-pdfs/", files=files)

        if response.status_code == 200:
            data = response.json()
            st.success(f"Stored in DB with ID: {data['id']}")
            st.subheader("Differences:")
            
            # Display differences with highlighting
            for line in data["differences"].split("\n"):
                if line.startswith("❌"):
                    st.markdown(f"<span style='color:red'>{line}</span>", unsafe_allow_html=True)
                elif line.startswith("✅"):
                    st.markdown(f"<span style='color:green'>{line}</span>", unsafe_allow_html=True)
                else:
                    st.write(line)
        else:
            st.error("Error: Could not compare PDFs.")
