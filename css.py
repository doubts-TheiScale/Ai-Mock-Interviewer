import streamlit as st
def form():
    st.markdown("""
    <style>
        /* Page background */
        .main {
            background-color: #121212;
        }

        /* Stylish form container */
        
        /* Header styles */
        h1, h2, h3 {
            color: #00c3ff;
            text-align: center;
        }

        /* Input fields */
        .stTextInput>div>div>input,
        .stSelectbox>div>div,
        .stDateInput>div>div>input {
            background-color: #2c2c2c;
            color: #ffffff;
            border-radius: 8px;
            padding: 10px;
            border: 1px solid #444;
        }

        /* Submit button styling */
        .center-button {
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }

        .stButton>button {
            background-color: #00c3ff;
            color: white;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 10px;
            cursor: pointer;
        }

        .stButton>button:hover {
            background-color: #00a0cc;
        }
    </style>
""", unsafe_allow_html=True)
def cicle_button():
    st.markdown("""
        <style>
        /* Target the button using Streamlit's internal structure */
        div[class^="stButton"] > button {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background-color: #008080;
            color: white;
            font-weight: bold;
            font-size: 16px;
            padding: 0;
            border: none;
            margin-left: 37%;
            margin-top: 70px;
        }
        
        @media (max-width: 640px) {
        div[class^="stButton"] > button {
            margin-top: 0px;
            margin-left:43%;
            
        }
        div[class^="stButton"] > button:hover {
            background-color: #009999;
            margin-left: 90px;
        }
        @media (max-width: 767px) {
        div[class^="stButton"] > button:hover{
            margin-top: 0px;
            margin-left:60px;   
        }
        @media (max-width: 640px) {
        div[class^="stButton"] > button:hover{
            margin-top: 0px;
            margin-left:43%;   
        }
        </style>
        """, unsafe_allow_html=True)