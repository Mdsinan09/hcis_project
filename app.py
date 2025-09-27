import streamlit as st

st.title("HCIS Project Dashboard")
st.write("Welcome to your HCIS project Streamlit app!")

# Example input
name = st.text_input("Enter your name:")
if st.button("Submit"):
    st.success(f"Hello, {name}!")
    st.write("Testing dev branch!")