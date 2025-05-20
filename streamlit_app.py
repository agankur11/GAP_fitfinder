import streamlit as st

from openai import OpenAI

import re


client = OpenAI(api_key = st.secrets["OpenAI_key"])

mock_inventory = [
    {"brand": "GAP", "name": "GAP Logo Hoodie", "category": "Hoodie", "fit": "Regular", "price": "$49.99"},
    {"brand": "Old Navy", "name": "Vintage Denim Jacket", "category": "Jacket", "fit": "Relaxed", "price": "$59.99"},
    {"brand": "Athleta", "name": "Ultimate Yoga Leggings", "category": "Leggings", "fit": "Tight", "price": "$79.00"},
    {"brand": "Banana Republic", "name": "Heritage Oxford Shirt", "category": "Shirt", "fit": "Tailored", "price": "$89.50"},
    {"brand": "GAP", "name": "Essential Crewneck Tee", "category": "T-Shirt", "fit": "Slim", "price": "$24.99"},
    {"brand": "Old Navy", "name": "Everyday Joggers", "category": "Pants", "fit": "Relaxed", "price": "$39.99"},
]

customer_profiles = {
    "Emily": {
        "height": "5'5\\\"",
        "weight": "135 lbs",
        "style": "casual + athleisure",
        "preferred_fit": "slim",
        "usual_brand": "Athleta",
        "usual_size": "M",
        "purchase_history": [
            {"brand": "Athleta", "product": "Salutation Jogger", "size": "M", "fit_feedback": "Perfect"},
            {"brand": "GAP", "product": "Relaxed Crewneck", "size": "M", "fit_feedback": "A bit loose"}
        ]
    },
    "Jason": {
        "height": "6'0\\\"",
        "weight": "180 lbs",
        "style": "classic + smart casual",
        "preferred_fit": "regular",
        "usual_brand": "GAP",
        "usual_size": "L",
        "purchase_history": [
            {"brand": "Banana Republic", "product": "Heritage Oxford Shirt", "size": "L", "fit_feedback": "Too tight"},
            {"brand": "Old Navy", "product": "Everyday Joggers", "size": "L", "fit_feedback": "Good fit"}
        ]
    }
}

def get_size(height, weight, brand, usual_brand, usual_size):
    brand_adjust = {
        "Old Navy": "large",
        "GAP": "slightly large",
        "Athleta": "true to size",
        "Banana Republic": "fitted",
    }

    if brand_adjust[brand] == "large":
        size_map = {"S": "XS", "M": "S", "L": "M", "XL": "L"}
    elif brand_adjust[brand] == "slightly large":
        size_map = {"S": "S", "M": "M", "L": "M", "XL": "L"}
    elif brand_adjust[brand] == "fitted":
        size_map = {"S": "M", "M": "L", "L": "XL", "XL": "XXL"}
    else:
        size_map = {"S": "S", "M": "M", "L": "L", "XL": "XL"}

    return size_map.get(usual_size.upper(), "M")

st.title("👕 FitFinder – Get Your Perfect Size")
st.markdown("Simulate logging in as a returning customer.")
selected_profile_name = st.selectbox("Select a customer profile:", list(customer_profiles.keys()))
profile = customer_profiles[selected_profile_name]

st.markdown("Fill in your details and let our AI stylist recommend the right size for you across GAP Inc. brands.")

brand = st.selectbox("Which brand are you shopping?", ["GAP", "Old Navy", "Athleta", "Banana Republic"])
product = st.selectbox(
    "Select a product:",
    [item["name"] for item in mock_inventory if item["brand"] == brand]
)

height = st.text_input("Your height (in feet/inches or cm):", profile["height"])
weight = st.text_input("Your weight (lbs or kg):", profile["weight"])
usual_brand = st.selectbox("A brand you usually shop:", ["H&M", "Uniqlo", "Nike", "Athleta", "GAP"], index=["H&M", "Uniqlo", "Nike", "Athleta", "GAP"].index(profile["usual_brand"]))
usual_size = st.selectbox("What size do you usually wear in that brand?", ["S", "M", "L", "XL"], index=["S", "M", "L", "XL"].index(profile["usual_size"]))

if st.button("Find My Size"):
    recommended_size = get_size(height, weight, brand, usual_brand, usual_size)
    selected_product = next(item for item in mock_inventory if item["name"] == product and item["brand"] == brand)
    history_summary = ", ".join([
        f"{h['brand']} {h['product']} (Size {h['size']}, Feedback: {h['fit_feedback']})"
        for h in profile["purchase_history"]
    ])

    explanation_prompt = f"""
    You are a friendly virtual stylist for GAP Inc. Based on the customer's information:
    - Name: {selected_profile_name}
    - Style: {profile['style']}
    - Preferred fit: {profile['preferred_fit']}
    - Brand: {brand}
    - Product: {selected_product['name']}
    - Height: {height}
    - Weight: {weight}
    - Usual brand: {usual_brand}
    - Usual size: {usual_size}
    - Purchase history: {history_summary}

    Suggest the best fit in {brand} for this product and explain why. Picking up a value for <SIZE> from XS,S,M,L,XL,XXL, Please begin your response with: 'Recommended size is <SIZE>' followed by a short explanation.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful AI stylist."},
                {"role": "user", "content": explanation_prompt}
            ],
            temperature=0.7
        )
        explanation = response.choices[0].message.content
    except Exception as e:
        explanation = f"AI explanation unavailable. Error: {e}"

    match = re.search(r"recommended size is (?:a )?(\b(?:XS|S|M|L|XL|XXL)\b)", explanation, re.IGNORECASE)
    if match:
        recommended_size = match.group(1).upper()
    else:
        recommended_size = "Not specified"

    st.success(f"🎯 Recommended Size in {brand}: **{recommended_size}**")
    st.markdown(f"**Why?** {explanation}")
    st.markdown("---")
    st.subheader("🛍️ Product Details")
    st.markdown(f"**{selected_product['name']}**  ")
    st.markdown(f"Category: {selected_product['category']}  ")
    st.markdown(f"Fit: {selected_product['fit']}  ")
    st.markdown(f"Price: {selected_product['price']}")

st.markdown("---")
st.caption("This is a simple AI demo to enhance customer experience for GAP Inc. brands using agentic behavior.")