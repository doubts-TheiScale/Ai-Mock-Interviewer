from langchain.agents import initialize_agent, AgentType
from langchain_groq import ChatGroq
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
import re
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st
from langchain.prompts import PromptTemplate
from voice import text_to_speech,transcribe
import css
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import requests
from langchain.schema.messages import SystemMessage
import re

load_dotenv()
groq_key = st.secrets["openai"]["api_key"]
users = os.getenv("User_names").split(",")
passwords = os.getenv("Passwords").split(",")
user=""
st.session_state.n_ques=0

user_input=0
llm = ChatGroq(model="llama-3.3-70b-versatile",groq_api_key=groq_key)
tools = []


import gspread
from oauth2client.service_account import ServiceAccountCredentials

import json

def connect_to_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    return client.open("Interview Results").sheet1

 

sheet = connect_to_sheet()


def log_to_sheet(student_name, interview_type, q_no, question, answer, feedback):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [student_name, interview_type, q_no, question, answer, feedback, timestamp ]
    sheet.append_row(row)













st.set_page_config(page_title="Ai Mock Interview",layout="centered")
st.session_state.user_input=0


st.markdown(
    """
    <style>
    /* Target the logo image in the sidebar */
    [alt="Logo"] {
        height: 600px; /* Adjust this to your desired height */
        width: auto;  /* Maintain aspect ratio */
        
    }
    .block-container {
            padding-top: 0rem;
        }
    header { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True
)
col1, col2 = st.columns([1, 6])
with col1:
    st.markdown("""
    <style>
    @media only screen and (max-width: 959px) {
        img {
            max-width: 600px;
            height: auto;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    st.logo("logo2.png")
# --- NAVIGATION BAR ---
def login():
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    css.form()
    st.subheader("Login Page")
    st.markdown('<div class="form-style">', unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.session_state.user_name=st.text_input("Enter Username:")
        st.session_state.user_age=22
        st.session_state.user_exp=st.text_input("Enter User's Exprence with detail NaN if none :")
        st.session_state.difficulty_level = st.selectbox(
                            "How would you like to be contacted?",
                            ("Beginner", "Intermediate", "Advanced"),
                        )

        phone_number=st.text_input("Enter Phone number:")
        st.session_state.email=st.text_input("Enter Email:")

        submitted = st.form_submit_button("Log in")
        
        if submitted:
            if st.session_state.user_name and st.session_state.difficulty_level and phone_number and st.session_state.email:
                st.success("Login successful")
                st.session_state.logged_in = True
                st.session_state.alredy_asked=["none"]
                st.session_state.next_question=0

                st.rerun()

            else:
                st.error("Enter Every Details")
            
    st.markdown('</div>', unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()






if st.session_state.logged_in:
    with col2:
        st.markdown("""
        <style>
        @media only screen and (max-width: 768px) {
            .custom-navbar {
                margin-top: 50px !important;
            }
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="custom-navbar">', unsafe_allow_html=True)
        selected = option_menu(
            menu_title=None,
            options=["Tech.", "HR","Settings"],
            icons=["chat-left-text", "envelope","gear"],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "background-color": "#0E1117"},
                "icon": {"color": "white", "font-size": "20px"},
                "nav-link": {"font-size": "18px", "text-align": "center", "margin": "0px", "--hover-color": "#204044"},
                "nav-link-selected": {"background-color": "#1f6f78"},
            }
        )
        st.markdown('</div>', unsafe_allow_html=True)

    if selected == "Settings":
        st.title("⚙️ Settings")
        
    elif selected == "Tech.":
        
      
        if "agent" not in st.session_state:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            system_prompt = f"""
You are an AI mock interview agent for data analyst students. You will conduct a 20-question technical interview strictly from the approved syllabus.

The interview should be customized based on the following user information:

- Name: {st.session_state.user_name}
- Experience Level: {st.session_state.user_exp}  (e.g., "Fresher", "0-1 years", "1-3 years", etc.)
- Difficulty Level Selected by User: {st.session_state.difficulty_level} (e.g., "Beginner", "Intermediate", "Advanced")

Use this information to:
- Adjust the complexity of questions based on the difficulty level selected.
- Choose appropriate topics considering the user’s experience.
- Greet the user by name during the first question (e.g., “Hi {st.session_state.user_name}, let's begin with...”)

---

You must follow this structure:

1. Ask questions one by one, numbered clearly.
Format each question exactly like this:
Q<number>: <question text>

2. Only ask questions from the following domains:
- Python (from the approved syllabus below) and advanced questions 
- SQL
- Power BI
- Excel

Python Topics (LIMIT STRICTLY to these):
- Python Basics (introduction, variables, operators)
- Built-in Functions
- Conditional Statements
- Loops
- User-Defined Functions
- Strings, Lists, Tuples, Sets, Dictionaries
- NumPy, Pandas, Matplotlib
- Projects (Covid-19 Dashboard, Image Scraping, WhatsApp Chat Analysis)

**Important Instruction:** Do NOT ask any Python questions outside the above topics. No OOP, decorators, threading, classes, etc., unless explicitly listed.

SQL Topics:
- SELECT, WHERE, GROUP BY, ORDER BY
- JOINs
- Aggregations
- Window Functions
- Subqueries, CTEs

Power BI Topics:
- Power Query Editor
- Creating and formatting visuals
- Slicers and filters
- Dashboards
- DAX basics

Excel Topics:
- VLOOKUP, IF statements
- Pivot Tables
- Conditional Formatting
- Data Validation
- Excel charts and formulas

---

3. For each answer:
- Carefully evaluate the user's explanation and assess both correctness and clarity.
- Only then respond with a brief, specific feedback AND a score out of 10 using this strict format:

- Feedback: <short sentence>
- Score: <x>/10

Be objective and critical. Avoid lenient scoring. Give low scores when important concepts are missing or incorrectly explained.

Example:
Feedback: That’s mostly correct but you missed the explanation of joins.
Score: 7/10

4. After 19 technical questions, ask this as the 20th question:
Q20: Briefly explain your most recent project in data analytics or Python.

5. After Q20, summarize the interview with:
- Overall rating (Ready / Needs More Practice / Below Average)
- One-sentence final feedback

-----------------------------------------------------

Other rules:
- Do not simulate answers.
- Ask follow-up questions only if relevant.
- SQL, Excel, and Power BI topics must be entry-level or beginner-friendly unless difficulty is set to "Advanced".
- Always keep track of the questions already asked, and do not repeat any question.
- The first question must be randomly chosen from the eligible domains and should vary each time. Ensure variety across interviews.

Be brief, professional, and stick strictly to the format.
"""

            memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
            memory.chat_memory.messages.append(SystemMessage(content=system_prompt))
            st.session_state.agent = initialize_agent(
                tools=tools,
                llm=llm,
                agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
                memory=memory,
                verbose=True,
                handle_parsing_errors=True, 
                )
            st.session_state.chat_history = []


            
        path = "Animation.json"
        with open(path, "r") as file:
            url = json.load(file)

        st_lottie(url, reverse=True,  speed=1, loop=True, quality='high')

            

        c1,c2=st.columns([6, 1])
        # uploaded_file = c1.audio_input("Record a Asnwer here")
        # c2.write(" ")
        # c2.write(" ")
        # if c2.button('Confirm Audio'):
        #     if uploaded_file:
        #         user_input = transcribe(uploaded_file)
        user_input = st.chat_input("Ask something to the agent...")
        if not st.session_state.next_question:
            if st.button("Start"):
                user_input = "Start The interview"
                
        
        
        if user_input:

            
            st.session_state.chat_history.append({"role": "user", "content": user_input })
            
            # Run agent
            
            with st.spinner("Thinking..."):
                response = st.session_state.agent.run({"input": f"you asked{st.session_state.next_question}, users answer : {user_input},list of questions already asked:{st.session_state.alredy_asked}"})
                pattern = r"Q(\d+):\s*(.+)"
                st.session_state.next_question = re.findall(pattern, response)
                st.session_state.alredy_asked.append(st.session_state.next_question)
                st.subheader(f"Next question is :blue[{st.session_state.next_question[0][1]}] ")

                score_match = re.search(r"Score:\s*(\d+)/10", response)
                feedback_match = re.search(r"Feedback:\s*(.+?)\n", response)

                score = int(score_match.group(1)) if score_match else None
                feedback = feedback_match.group(1).strip() if feedback_match else "No feedback"
                print(st.session_state.alredy_asked[-2])
                if st.session_state.next_question:
                    q_no, question_text = st.session_state.next_question[0]
                    log_to_sheet(
                        student_name=st.session_state.user_name,
                        interview_type="Technical",
                        q_no=q_no,
                        question=st.session_state.alredy_asked[-2][0],
                        answer=user_input,
                        feedback=score
                    )
                # Show feedback on UI
                
                st.sidebar.markdown(f"**Feedback:** {feedback}")
                st.sidebar.markdown(f"**Score:** :blue[{score}/10]")
                
                if response.strip():
                    audio_file = text_to_speech(response)
                    st.sidebar.audio(audio_file, format='audio/mp3', autoplay=True)
                # st.sidebar.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})

    else:
        if "agent1" not in st.session_state:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            system_prompt = f"""
You are an AI mock interview agent conducting an **HR interview** for data analyst students. You will conduct a 10-question HR interview based strictly on behavioral, situational, and career-oriented topics.

The interview should be customized based on the following user information:

- Name: {st.session_state.user_name}
- Experience Level: {st.session_state.user_exp}  (e.g., "Fresher", "0-1 years", "1-3 years", etc.)
- Difficulty Level Selected by User: {st.session_state.difficulty_level} (e.g., "Beginner", "Intermediate", "Advanced")

Use this information to:
- Adjust the depth and tone of questions based on the difficulty level and experience.
- Choose relevant scenarios (college, internship, previous job, etc.).
- Greet the user by name in the first message and ask for a brief self-introduction before starting the formal HR questions.
  (e.g., "Hi {st.session_state.user_name}, before we begin, please give a brief introduction about yourself.")

---

You must follow this structure:

1. Begin by asking the candidate for a brief introduction. Format it like this:
Intro: Hi {st.session_state.user_name}, before we begin the HR interview, could you please introduce yourself briefly?

2. After the introduction is given, start the interview with:
Q1: <question text>
Q2: <question text>
... up to ...
Q10: <question text>

3. Question Domains (rotate between these):
- Self-introduction and background
- Motivation & career goals
- Strengths, weaknesses, personality
- Situational and behavioral judgment
- Teamwork and conflict resolution
- Communication & work ethic
- Resume and project-related discussion
- Company fit, values, adaptability

4. For each answer from the student, respond with:
- A very short 1-line feedback
- Then a score in this format:
  Score: <x>/10

  Example:
  “That was a thoughtful answer, but could use a clearer example. Score: 7/10”

5. Question 20 must always be:
Q20: Why should we hire you for this role as a data analyst?

6. After Q10, summarize the interview with:
- Overall Rating: Excellent / Good / Needs More Practice / Below Average
- Final Feedback: One sentence based on the overall performance

-----------------------------------------------------

Other Instructions:
- Do NOT simulate candidate responses.
- Ensure no repetition of questions.
- Rotate topics with diversity.
- Always begin with the introduction request.
- Maintain a brief and professional tone throughout.
"""

            memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
            memory.chat_memory.messages.append(SystemMessage(content=system_prompt))
            st.session_state.agent1 = initialize_agent(
                tools=tools,
                llm=llm,
                agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
                memory=memory,
                verbose=True,
                handle_parsing_errors=True, 
                )
            st.session_state.chat_history = []


            
        path = "Animation.json"
        with open(path, "r") as file:
            url = json.load(file)

        st_lottie(url, reverse=True,  speed=1, loop=True, quality='high')

            

        c1,c2=st.columns([6, 1])
        uploaded_file = c1.audio_input("Record a Asnwer here")
        c2.write(" ")
        c2.write(" ")
        if c2.button('Confirm Audio'):
            if uploaded_file:
                user_input = transcribe(uploaded_file)

        if not st.session_state.next_question:
            if st.button("Start"):
                user_input = "Start The interview"
                
        
        
        if user_input:

            
            st.session_state.chat_history.append({"role": "user", "content": user_input })
            
            # Run agent
            
            with st.spinner("Thinking..."):
                response = st.session_state.agent1.run({"input": f"you asked{st.session_state.next_question}, users answer : {user_input},list of questions already asked:{st.session_state.alredy_asked}"})
                pattern = r"Q(\d+):\s*(.+)"
                st.session_state.next_question = re.findall(pattern, response)
                st.session_state.alredy_asked.append(st.session_state.next_question)
                st.subheader(f"Next question is :blue[{st.session_state.next_question[0][1]}] ")
                match = re.search(r"Score:\s*(\d{1,2})/10", response)
                score=0
                if match:
                    score = int(match.group(1))if match else None
                if st.session_state.next_question:
                    q_no, question_text = st.session_state.next_question[0]
                    log_to_sheet(
                        student_name=st.session_state.user_name,
                        interview_type="HR",
                        q_no=q_no,
                        question=st.session_state.alredy_asked[-2][0][1],
                        answer=user_input,
                        feedback=score
                    )
                # Show feedback on UI
                
                
                st.sidebar.subheader(f"**Score:** :blue[{score}/10]")
                if response.strip():
                    audio_file = text_to_speech(response)
                    st.sidebar.audio(audio_file, format='audio/mp3', autoplay=True)
                st.sidebar.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})

