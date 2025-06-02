import streamlit as st
import pandas as pd
import joblib
from fpdf import FPDF
import os
import hashlib
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="DocAnApp", layout="centered")

model_data = joblib.load("therapy_recommendation_model_with_age_groups.pkl")
model = model_data['model']
encoders = model_data['encoders']

USER_DB = "users.csv"
if not os.path.exists(USER_DB):
    pd.DataFrame(columns=["username", "password_hash"]).to_csv(USER_DB, index=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def signup(username, password):
    df = pd.read_csv(USER_DB)
    if username in df["username"].values:
        return False, "Username already exists."
    new_row = pd.DataFrame([{"username": username, "password_hash": hash_password(password)}])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(USER_DB, index=False)
    return True, "User registered successfully."

def login(username, password):
    df = pd.read_csv(USER_DB)
    hashed = hash_password(password)
    user_row = df[(df.username == username) & (df.password_hash == hashed)]
    return not user_row.empty

def generate_pdf(patient_name, patient_id, inputs, recommendation, confidence):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="DocAnApp Cancer Therapy Report", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Patient Name: {patient_name}", ln=True)
    pdf.cell(200, 10, txt=f"Patient ID: {patient_id}", ln=True)
    for label, value in inputs.items():
        pdf.cell(200, 10, txt=f"{label}: {value}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Recommended Therapy: {recommendation}", ln=True)
    pdf.cell(200, 10, txt=f"Confidence: {confidence*100:.2f}%", ln=True)
    file_path = "therapy_report.pdf"
    pdf.output(file_path)
    return file_path

def therapy_advice(therapy):
    if "PARP" in therapy:
        return "Monitor for hematological toxicity and discuss fertility if applicable."
    elif "Osimertinib" in therapy:
        return "Monitor for lung or cardiac side effects."
    elif "+" in therapy:
        return "Combination therapy: monitor closely for cumulative side effects."
    else:
        return "Standard clinical follow-up advised."

def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""

    if not st.session_state.logged_in:
        auth_choice = st.sidebar.selectbox("Choose Action", ["Login", "Sign Up"])
        st.title("🔐 Welcome to DocAnApp")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if auth_choice == "Login":
            if st.button("Login"):
                if login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        else:
            if st.button("Sign Up"):
                success, message = signup(username, password)
                if success:
                    st.success(message)
                else:
                    st.error(message)
    else:
        st.sidebar.success(f"Logged in as: {st.session_state.username}")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

        st.title("🧬 DocAnApp – Cancer Therapy Recommendation")
        st.markdown("---")

        st.header("Enter Patient Information")
        patient_name = st.text_input("Patient Name")
        patient_id = st.text_input("Patient ID")

        st.header("Clinical Inputs")
        cancer_type = st.selectbox("Cancer Type", encoders['cancer_type'].classes_)
        age_group = st.selectbox("Age Group", encoders['age_group'].classes_)
        tumor_stage = st.selectbox("Tumor Stage", encoders['tumor_stage'].classes_)
        previous_therapy = st.selectbox("Previous Therapy", encoders['previous_therapy'].classes_)
        all_mutations = sorted(set(encoders['mutation_1'].classes_) | set(encoders['mutation_2'].classes_))
        mutation_1 = st.selectbox("Mutation 1", all_mutations)
        mutation_2 = st.selectbox("Mutation 2", ["None"] + all_mutations)

        if st.button("Get Recommendation"):
            inputs = {
                'cancer_type': cancer_type,
                'age_group': age_group,
                'tumor_stage': tumor_stage,
                'previous_therapy': previous_therapy,
                'mutation_1': mutation_1,
                'mutation_2': mutation_2
            }
            df_input = pd.DataFrame([inputs])
            for col in df_input.columns:
                df_input[col] = encoders[col].transform(df_input[col])

            prediction = model.predict(df_input)[0]
            probabilities = model.predict_proba(df_input)[0]
            confidence = max(probabilities)
            recommendation = encoders['recommended_therapy'].inverse_transform([prediction])[0]
            advice = therapy_advice(recommendation)

            st.success(f"Recommended Therapy: **{recommendation}**")
            st.info(f"Confidence in this recommendation: **{confidence*100:.2f}%**")
            st.warning(f"Advice: {advice}")

            if patient_name and patient_id:
                report_file = generate_pdf(patient_name, patient_id, inputs, recommendation, confidence)
                with open(report_file, "rb") as f:
                    st.download_button("📄 Download PDF Report", f, file_name=report_file)
            else:
                st.warning("Please enter patient name and ID to generate report.")

if __name__ == "__main__":
    main()
