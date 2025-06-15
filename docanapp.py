import streamlit as st
import pandas as pd
import joblib
from fpdf import FPDF
import base64
import json
import os

from io import BytesIO

from fpdf import FPDF
from io import BytesIO

from fpdf import FPDF

def clean_text(text):
    if not isinstance(text, str):
        text = str(text)
    return text.encode('latin-1', errors='ignore').decode('latin-1')

def generate_pdf_report(name, pid, cancer, stage, age_grp, prev, mut1, mut2, recommended, price, coverage, advice_list, age_comment, prev_comment):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, clean_text("🧬 Cancer Therapy Recommendation Report"), ln=True, align="C")

    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Patient Name: {clean_text(name)}", ln=True)
    pdf.cell(0, 10, f"Patient ID: {clean_text(pid)}", ln=True)

    pdf.ln(5)
    pdf.cell(0, 10, f"Cancer Type: {clean_text(cancer)}", ln=True)
    pdf.cell(0, 10, f"Tumor Stage: {clean_text(stage)}", ln=True)
    pdf.cell(0, 10, f"Age Group: {clean_text(age_grp)}", ln=True)
    pdf.cell(0, 10, f"Previous Therapy: {clean_text(prev)}", ln=True)
    pdf.cell(0, 10, f"Mutation 1: {clean_text(mut1)}", ln=True)
    pdf.cell(0, 10, f"Mutation 2: {clean_text(mut2)}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, clean_text("Recommended Therapy:"), ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, clean_text(recommended), ln=True)
    pdf.cell(0, 10, f"Price: {clean_text(price)}", ln=True)
    pdf.cell(0, 10, f"Insurance Coverage: {clean_text(coverage)}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, clean_text("Clinical Advice:"), ln=True)
    pdf.set_font("Arial", size=12)
    for advice in advice_list:
        pdf.multi_cell(0, 10, clean_text(f"- {advice}"))

    pdf.ln(10)
    pdf.cell(0, 10, f"Age Group Comment: {clean_text(age_comment)}", ln=True)
    pdf.cell(0, 10, f"Previous Therapy Comment: {clean_text(prev_comment)}", ln=True)

    # Export PDF to bytes
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    return pdf_bytes





# ========== Load Model and Encoders ==========
model_data = joblib.load("cancer_model_bundle.pkl")
model = model_data['model']
encoders = model_data['encoders']

# ========== Data from your generation code ==========
cancer_types = ['Lung', 'Breast', 'Colorectal', 'Prostate', 'Ovarian']
age_groups = ['Young', 'Middle-aged', 'Elderly']
tumor_stages = ['I', 'II', 'III', 'IV']
previous_therapies = ['NoPreviousTherapy', 'Chemotherapy', 'Immunotherapy', 'Hormone Therapy', 'HER2 Therapy', 'PARP Inhibitors']

mutation_map = {
    'Lung': ['EGFR', 'ALK', 'KRAS G12C', 'ROS1', 'BRAF V600E'],
    'Breast': ['BRCA1', 'BRCA2', 'HER2', 'TP53', 'PIK3CA'],
    'Colorectal': ['KRAS G12C', 'BRAF V600E', 'MSI-H', 'NRAS', 'HER2 amplification'],
    'Prostate': ['BRCA2', 'ATM', 'CHEK2', 'TMPRSS2-ERG'],
    'Ovarian': ['BRCA1', 'BRCA2', 'TP53', 'PIK3CA']
}

def get_valid_mutation_2(cancer, mut1):
    muts = mutation_map[cancer]
    return [m for m in muts if m != mut1] + ['NoMutation']

mutation_info_links = {
    'EGFR': 'https://www.lung.org/lung-health-diseases/lung-disease-lookup/lung-cancer/symptoms-diagnosis/biomarker-testing/egfr',
    'ALK': 'cfamerica.org/about-lung-cancer/diagnosis/biomarkers/alk/',
    'KRAS G12C': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC10543081/',
    'ROS1': 'https://lcfamerica.org/about-lung-cancer/diagnosis/biomarkers/ros1/',
    'BRAF V600E': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC9934973/',
    'BRCA1': 'https://www.cancer.gov/about-cancer/causes-prevention/genetics/brca-fact-sheet#what-are-brca1-and-brca2',
    'BRCA2': 'https://www.cancer.gov/about-cancer/causes-prevention/genetics/brca-fact-sheet#what-are-brca1-and-brca2',
    'HER2': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC6571037/',
    'TP53': 'https://www.cancer.gov/espanol/publicaciones/diccionarios/diccionario-cancer/def/gen-tp53',
    'PIK3CA': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC3781181/',
    'MSI-H': 'https://pubmed.ncbi.nlm.nih.gov/15528785/',
    'NRAS': 'https://medlineplus.gov/genetics/gene/nras/',
    'HER2 amplification': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4698879/',
    'ATM': 'https://www.mskcc.org/es/cancer-care/patient-education/about-mutations-atm-gene',
    'CHEK2': 'https://www.mskcc.org/cancer-care/patient-education/about-mutations-chek2-gene',
    'TMPRSS2-ERG': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC3527835/',
}

therapy_price_info = {
    'Osimertinib': ('Covered by EU healthcare', 'Approx. 5000 EUR/month'),
    'Alectinib': ('Covered by EU healthcare', 'Approx. 4500 EUR/month'),
    'Sotorasib': ('Out-of-pocket', 'Approx. 12000 EUR/month'),
    'Crizotinib': ('Covered by EU healthcare', 'Approx. 4000 EUR/month'),
    'Dabrafenib + Trametinib': ('Covered by EU healthcare', 'Approx. 8000 EUR/month combined'),
    'Olaparib': ('Covered by EU healthcare', 'Approx. 6000 EUR/month'),
    'Trastuzumab': ('Covered by EU healthcare', 'Approx. 3000 EUR/month'),
    'Alpelisib': ('Out-of-pocket', 'Approx. 9000 EUR/month'),
    'Standard chemotherapy': ('Covered by EU healthcare', 'Varies'),
    'Olaparib (investigational)': ('Clinical trial / out-of-pocket', 'N/A'),
    'PARP inhibitors (trials)': ('Clinical trial', 'N/A'),
    'Pembrolizumab': ('Covered by EU healthcare', 'Approx. 7000 EUR/month'),
    'Exclude EGFR inhibitors': ('N/A', 'N/A'),
    'Androgen receptor therapy': ('Covered by EU healthcare', 'Varies'),
    'Less aggressive option advised': ('Consult physician', 'N/A'),
    'Switch to alt. PARP inhibitor or monitor': ('Consult physician', 'N/A'),
    'Standard of care': ('Covered by EU healthcare', 'Varies'),
}

patient_advices = {
    'Lung': "Smoking cessation and regular follow‑ups are crucial.",
    'Breast': "Consider genetic counseling and family screening.",
    'Colorectal': "Maintain a high‑fiber diet and regular colonoscopy checks.",
    'Prostate': "Discuss hormone therapy side effects with your doctor.",
    'Ovarian': "Regular CA‑125 testing and symptom monitoring recommended.",
    'Less aggressive option advised': "Due to age, less intensive treatment is safer.",
    'Switch to alt. PARP inhibitor or monitor': "Monitor closely or switch PARP therapy as needed.",
    'Standard of care': "Follow standard therapy protocols with your oncologist.",
}
age_group_comments = {
    'Young': "🧬 Younger patients may respond better to aggressive therapy but need long-term side-effect planning.",
    'Middle-aged': "⚖️ Middle-aged patients often benefit from a balanced approach between therapy intensity and quality of life.",
    'Elderly': "🧓 Elderly patients may require less toxic options and supportive care integration."
}

previous_therapy_comments = {
   'NoPreviousTherapy': "No prior therapy; standard first-line recommendations apply.",
    'Chemotherapy': "Previous chemotherapy may influence resistance patterns and requires careful selection of next therapy.",
    'Immunotherapy': "Prior immunotherapy exposure may affect response rates and immune-related adverse events.",
    'Hormone Therapy': "Prior hormone therapy can impact hormone receptor status and subsequent treatment choices.",
    'HER2 Therapy': "Previous HER2-targeted therapy may affect resistance and necessitate alternative HER2 agents or combinations.",
    'PARP Inhibitors': "Prior PARP inhibitor use may influence efficacy of subsequent DNA damage response-targeted treatments."
}


# ========== JSON-based Authentication ==========
USERS_FILE = "users.json"

def load_users_json():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    else:
        return {}

def save_users_json(u):
    with open(USERS_FILE, "w") as f:
        json.dump(u, f)

def signup(username, password):
    users = load_users_json()
    if username in users:
        return False
    users[username] = password
    save_users_json(users)
    return True

def login(username, password):
    users = load_users_json()
    return users.get(username) == password

def logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]

# ========== Streamlit App ==========
def main():
    st.title("🧬 DocAnApp - Cancer Therapy Recommender")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "page" not in st.session_state:
        st.session_state.page = "login"

    if st.session_state.logged_in:
        st.sidebar.write(f"Logged in as: Dr. {st.session_state.username}")
        if st.sidebar.button("Logout"):
            logout()
            st.session_state.page = "login"
            st.rerun()

    if not st.session_state.logged_in:
        option = st.sidebar.radio("Choose", ["Login", "Sign Up"])
        st.session_state.page = option.lower()
        if st.session_state.page == "login":
            st.header("🔐 Login")
            user = st.text_input("Username", key="login_user")
            pwd = st.text_input("Password", type="password", key="login_pwd")
            if st.button("Login"):
                if login(user, pwd):
                    st.session_state.logged_in = True
                    st.session_state.username = user
                    st.success("Login successful")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        else:
            st.header("👤 Sign Up")
            user = st.text_input("Choose username", key="signup_user")
            pwd = st.text_input("Choose password", type="password", key="signup_pwd")
            if st.button("Sign Up"):
                if signup(user, pwd):
                    st.success("Account created! Please log in.")
                    st.session_state.page = "login"
                else:
                    st.error("Username already exists")
        return

    # --- Authenticated user sees this ---
    st.success(f"✅ Logged in as Dr. {st.session_state.username}")

    st.subheader("📝 Patient Information")
    name = st.text_input("Patient Name")
    pid = st.text_input("Patient ID")

    st.subheader("🧪 Medical Inputs")
    cancer = st.selectbox("Cancer Type", cancer_types)
    stage = st.selectbox("Tumor Stage", tumor_stages)
    age_grp = st.selectbox("Age Group", age_groups)
    prev = st.selectbox("Previous Therapy", previous_therapies)

    mut1 = st.selectbox("Mutation 1", mutation_map[cancer])
    mut2 = st.selectbox("Mutation 2", get_valid_mutation_2(cancer, mut1))

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"[ℹ️ Info on {mut1}]({mutation_info_links.get(mut1,'#')})")
    with col2:
        if mut2 != 'None':
            st.markdown(f"[ℹ️ Info on {mut2}]({mutation_info_links.get(mut2,'#')})")
        else:
            st.write("No Mutation 2")

    if st.button("📊 Get Recommendation"):
        enc = [
            encoders['cancer_type'].transform([cancer])[0],
            encoders['age_group'].transform([age_grp])[0],
            encoders['tumor_stage'].transform([stage])[0],
            encoders['previous_therapy'].transform([prev])[0],
            encoders['mutation_1'].transform([mut1])[0],
            encoders['mutation_2'].transform([mut2])[0]
        ]
        pred = model.predict([enc])[0]
        recommended = encoders['recommended_therapy'].inverse_transform([pred])[0]

        price, coverage = therapy_price_info.get(recommended, ('N/A','N/A'))
        advice_list = []
        advice_list.append(patient_advices.get(cancer,""))
        if "PARP" in recommended:
            advice_list.append("Monitor for fatigue, nausea, blood count changes.")
        if "Trastuzumab" in recommended:
            advice_list.append("Regular cardiac monitoring recommended.")

        st.markdown(f"<h3 style='color:green;'>✅ {recommended}</h3>", unsafe_allow_html=True)
        st.markdown(f"*Price:* {price}")
        st.markdown(f"*Insurance coverage:* {coverage}")
        st.subheader("🩺 Advice")
        for a in advice_list:
            st.info(a)
            # Clinical context-based comments
        age_comment = age_group_comments.get(age_grp, "ℹ️ No comment available for this age group.")
        prev_comment = previous_therapy_comments.get(prev, "ℹ️ No comment available for previous therapy.")

        st.markdown("### 🧠 Clinical Considerations")
        st.info(f"**Age Group ({age_grp}):** {age_comment}")
        st.info(f"**Previous Therapy ({prev}):** {prev_comment}")
        # Generate PDF bytes
        pdf_bytes = generate_pdf_report(
            name, pid, cancer, stage, age_grp, prev, mut1, mut2,
            recommended, price, coverage, advice_list, age_comment, prev_comment
    )

    # Download button for PDF
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_bytes,
            file_name=f"therapy_report_{pid}.pdf",
            mime="application/pdf"
    )


if __name__ == "__main__":
    main()


