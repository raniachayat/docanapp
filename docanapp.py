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

def generate_pdf_report(name, pid, cancer, stage, age_grp, prev, mut1, mut2, recommended, advice_list, age_comment, prev_comment):
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
    pdf.multi_cell(0, 10, clean_text(recommended))


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
model_data = joblib.load("cancer_model_bundle_compressed.pkl")
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
    'ALK': 'https://www.lung.org/lung-health-diseases/lung-disease-lookup/lung-cancer/symptoms-diagnosis/biomarker-testing/alk-lung-cancer',
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



patient_advices = {
    'Lung': (
        "Smoking cessation significantly improves survival and reduces recurrence risk. "
        "Scheduled imaging (e.g., low-dose CT) and biomarker monitoring post-treatment are essential for early detection of relapse."
    ),
    'Breast': (
        "Genetic counseling is advised for patients with early-onset or familial breast cancer. "
        "Screen first-degree relatives if BRCA1/2 or other pathogenic variants are detected."
    ),
    'Colorectal': (
        "Advise a diet rich in fiber and low in processed meats. "
        "Surveillance colonoscopy intervals should follow post-resection risk stratification (e.g., 1 year, then every 3–5 years)."
    ),
    'Prostate': (
        "Hormonal therapy (ADT) may cause fatigue, hot flashes, and bone density loss. "
        "Baseline DEXA scan and cardiovascular risk assessment are recommended before initiating treatment."
    ),
    'Ovarian': (
        "Monitor CA-125 and HE4 levels post-treatment. "
        "Educate on subtle symptoms of recurrence (e.g., bloating, pelvic pain). "
        "Consider periodic imaging for high-risk histologies or residual disease."
    ),
    'Less aggressive option advised': (
        "In frail or elderly patients, de-escalated regimens or active surveillance may optimize quality of life with minimal compromise on outcomes."
    ),
    'Switch to alt. PARP inhibitor or monitor': (
        "In cases of emerging resistance, consider PARP switching (e.g., to niraparib or talazoparib) or transition to platinum-based regimens with molecular re-evaluation."
    ),
    'Standard of care': (
        "Standard protocols (e.g., NCCN, ESMO) should be followed. Consider molecular profiling to refine first-line or maintenance options."
    ),
}


age_group_comments = {
    'Young': (
        "🧬 Younger patients (≤40 years) typically tolerate aggressive regimens better. "
        "However, long-term toxicities (e.g., cardiotoxicity, infertility, neurocognitive effects) must be addressed. "
        "Fertility preservation and survivorship planning are essential."
    ),
    'Middle-aged': (
        "⚖️ For patients aged 40–65, balance efficacy with risk of comorbidities. "
        "Offer full standard regimens but assess cardiovascular, renal, and psychosocial status before escalation."
    ),
    'Elderly': (
        "🧓 In patients ≥65, especially with ECOG ≥2, consider geriatric assessment. "
        "Opt for less intensive regimens or supportive care with attention to polypharmacy, frailty, and cognition."
    )
}




previous_therapy_comments = {
    'NoPreviousTherapy': (
        "No prior systemic treatment. First-line standard-of-care recommendations apply based on molecular subtype and stage."
    ),
    'Chemotherapy': (
        "Prior chemotherapy may select for resistant clones or cause cumulative toxicities (e.g., neuropathy, myelosuppression). "
        "Reassess eligibility for platinum or taxane re-exposure and consider non-cross-resistant agents."
    ),
    'Immunotherapy': (
        "Previous immune checkpoint inhibitor use may lead to immune-related adverse events (irAEs). "
        "Monitor for delayed toxicities and assess response durability before retreatment."
    ),
    'Hormone Therapy': (
        "Prior endocrine therapy may downregulate hormone receptor expression. "
        "Check receptor status via re-biopsy and consider CDK4/6 inhibitors or SERDs for endocrine resistance."
    ),
    'HER2 Therapy': (
        "Progression on trastuzumab or pertuzumab may necessitate switch to T-DXd or tucatinib combinations. "
        "Assess HER2 expression heterogeneity in metastatic lesions."
    ),
    'PARP Inhibitors': (
        "PARPi resistance may involve reversion mutations or restored homologous recombination. "
        "Re-challenge may not be effective; consider platinum rechallenge, ATR inhibitors, or enrollment in clinical trials."
    )
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
        advice_list = []
        advice_list.append(patient_advices.get(cancer,""))
        if "PARP" in recommended:
            advice_list.append("Monitor for fatigue, nausea, blood count changes.")
        if "Trastuzumab" in recommended:
            advice_list.append("Regular cardiac monitoring recommended.")

        st.markdown(f"<h3 style='color:green;'>✅ {recommended}</h3>", unsafe_allow_html=True)
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
            recommended,advice_list,age_comment,prev_comment
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


