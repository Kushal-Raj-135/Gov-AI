import streamlit as st
import requests
import json

# Function to get detailed explanations from GOV-AI
def query_gov_ai(input_text, schemes_summary=None):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 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"  # Replace with your token
    }

    # Prepare the prompt
    if schemes_summary:
        prompt = (
            f"Here are some government schemes:\n{schemes_summary}\n"
            f"The user has this query:\n{input_text}\n"
            f"Provide a detailed and relevant answer."
        )
    else:
        prompt = (
            f"The user has the following question:\n{input_text}\n"
            f"Answer the query with detailed and accurate information."
        )

    # Prepare payload for GOV-AI
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are GOV-AI, an assistant knowledgeable about government schemes and everything else."},
            {"role": "user", "content": prompt}
        ]
    }

    # Make API call
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code}, {response.text}"

# Load government schemes from the JSON file
def load_schemes():
    try:
        with open('government_schemes_updated.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("The schemes file is missing.")
        return []

# Filter schemes based on user inputs
def filter_schemes(age, income, education_level, schemes):
    recommendations = []
    for scheme in schemes:
        age_min, age_max = scheme.get("age_range", (0, 100))
        income_range = scheme.get("income_max", [0, None])  # Use range format
        if income_range[0] <= income <= income_range[1]:
            if age_min <= age <= age_max:
                # Check if the education level matches
                scheme_education_levels = scheme.get("education_level", [])
                if isinstance(scheme_education_levels, list):
                    if education_level.lower() in [level.lower() for level in scheme_education_levels]:
                        recommendations.append(scheme)
                elif education_level.lower() in scheme_education_levels.lower():
                    recommendations.append(scheme)
    return recommendations

# Streamlit App
def main():
    st.title("GOV-AI: Smart Government Services")
    st.subheader("Discover government schemes tailored to your profile!")

    # Images in a single row
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image("image1.jpg", width=150)  # Replace with your image path
    with col2:
        st.image("image2.jpg", width=150)  # Replace with your image path

    # Input Section
    age = st.number_input("Enter your age:", min_value=0, max_value=100, step=1)

    # Ask for income only if the age is above 25
    if age > 25:
        income = st.number_input("Enter your annual income (in INR):", min_value=0, step=1000)
    else:
        income = 0  # Default to 0 for users aged 25 or below

    # Education Level options
    education_level = st.selectbox(
        "Select your education level:",
        ["Undergraduate", "Postgraduate", "Student", "Secondary", "Primary", "Others"]
    )

    # Load schemes
    schemes = load_schemes()

    # Recommendation Button
    if st.button("Get Recommendations"):
        st.write("### Recommendations:")

        # Filter schemes
        filtered_schemes = filter_schemes(age, income, education_level, schemes)

        if filtered_schemes:
            for scheme in filtered_schemes:
                st.markdown(f"**{scheme['scheme_name']}**")
                st.write(f"Education Level: {scheme['education_level']}")
                st.write(f"Description: {scheme['description']}")
                st.write(f"Eligibility: {scheme['eligibility']}")
                st.markdown(f"[Apply Here]({scheme['website']})")
                st.write("---")

            # Call GOV-AI for detailed scheme explanations
            with st.spinner("Fetching detailed explanations from GOV-AI..."):
                schemes_summary = "\n".join(
                    [f"- {scheme['scheme_name']}: {scheme['description']}" for scheme in filtered_schemes]
                )
                detailed_explanations = query_gov_ai("Explain the above schemes in detail.", schemes_summary=schemes_summary)
                st.write("### GOV-AI-Generated Explanations:")
                st.write(detailed_explanations)

        else:
            st.warning("No schemes found matching your details.")

    # Prompt for general or scheme-related queries
    user_input = st.text_area("Have any specific questions (about these schemes or anything else)? Type them here:", height=100)

    if st.button("Ask GOV-AI"):
        if user_input.strip():
            with st.spinner("Fetching answers from GOV-AI..."):
                # Send query to GOV-AI without schemes context if unrelated
                response = query_gov_ai(user_input, schemes_summary=None)
                st.write("### GOV-AI Response to Your Query:")
                st.write(response)
        else:
            st.warning("Please type a question before clicking 'Ask GOV-AI'.")

if __name__ == "__main__":
    main()
