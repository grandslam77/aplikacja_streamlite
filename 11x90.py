import streamlit as st
import pandas as pd
#import sqlite3
#import os


#new_directory = 'E:/PROJEKTY/PROJEKTY/NewWycenaNieruchomosci/egzamin/'
#os.chdir(new_directory)

# df = pd.read_excel("zestaw1.xlsx")
# df = pd.read_excel("zestaw2.xlsx")
# df = pd.read_excel("zestaw3.xlsx")
df = pd.read_excel("zestaw_19.xlsx")
# df = pd.read_excel("zestaw10.xlsx")
# df = pd.read_excel("pytania_i_odpowiedzi_X.xlsx")


# Load data from uploaded Excel file
# uploaded_file = '/mnt/data/zestaw5.xlsx'
# df = pd.read_excel(uploaded_file)
liczba_pytan=90
# Set up unique test codes for selection
test_codes = df['Kod_Testu'].unique()
selected_test_code = st.selectbox("Wybierz zestaw pytań według Kod_Testu:", test_codes)

# Function to get random questions for the selected test code
def get_random_questions(df, kod_testu, n=liczba_pytan):
    filtered_df = df[df['Kod_Testu'] == kod_testu]
    unique_questions = filtered_df[['Kod_Testu', 'Numer_Pytania', 'Tresc_Pytania']].drop_duplicates(subset=['Numer_Pytania']).sample(n)
    return unique_questions

# Initialize random questions in session state if not already done
def initialize_questions(df, kod_testu, n=liczba_pytan):
    if "random_questions" not in st.session_state:
        st.session_state["random_questions"] = get_random_questions(df, kod_testu, n)

# Generate the test form
def generate_test():
    random_questions = st.session_state["random_questions"]
    all_checkbox_keys = []

    for _, question_row in random_questions.iterrows():
        kod_testu = question_row['Kod_Testu']
        question_number = question_row['Numer_Pytania']
        question_text = question_row['Tresc_Pytania']

        st.markdown(f"<span style='color:lightblue'><b>Pytanie {question_number} (Test {kod_testu}):</b> {question_text}</span>", unsafe_allow_html=True)

        answers = df[(df['Kod_Testu'] == kod_testu) & (df['Numer_Pytania'] == question_number)][['Numer_Odpowiedzi', 'Tresc_Odpowiedzi']]
        for idx, row in answers.iterrows():
            checkbox_key = f"checkbox_{kod_testu}_{question_number}_{row['Numer_Odpowiedzi']}"
            st.checkbox(row['Tresc_Odpowiedzi'], key=checkbox_key)
            all_checkbox_keys.append(checkbox_key)

    return all_checkbox_keys

# Check answers and summarize results
def check_answers(df, all_checkbox_keys):
    correct = 0
    user_answers = {}
    results = []

    for checkbox_key in all_checkbox_keys:
        _, kod_testu, question_number, answer_id = checkbox_key.split('_')
        kod_testu = int(kod_testu)
        question_number = int(question_number)

        if st.session_state[checkbox_key]:
            if (kod_testu, question_number) not in user_answers:
                user_answers[(kod_testu, question_number)] = []
            user_answers[(kod_testu, question_number)].append(answer_id)

    for (kod_testu, question_number), user_selections in user_answers.items():
        correct_answers_df = df[(df['Kod_Testu'] == kod_testu) & (df['Numer_Pytania'] == question_number) & (df['prawidlowosc'] == 'x')]
        correct_answers = correct_answers_df['Numer_Odpowiedzi'].tolist()
        
        correct_answers_text = correct_answers_df['Tresc_Odpowiedzi'].tolist()
        user_answers_text = df[(df['Kod_Testu'] == kod_testu) & (df['Numer_Pytania'] == question_number) & (df['Numer_Odpowiedzi'].isin(user_selections))]['Tresc_Odpowiedzi'].tolist()

        is_correct = set(user_selections) == set(correct_answers)
        if is_correct:
            correct += 1

        question_text = df[(df['Kod_Testu'] == kod_testu) & (df['Numer_Pytania'] == question_number)]['Tresc_Pytania'].values[0]

        results.append({
            'kod_testu': kod_testu,
            'question_number': question_number,
            'question': question_text,
            'user_answers': user_answers_text,
            'correct_answers': correct_answers_text,
            'is_correct': is_correct
        })

    return correct, results

# Display results after test completion
def display_results(results):
    for result in results:
        if result['is_correct']:
            st.markdown(f"<span style='color:green'><b>Pytanie {result['question_number']} (Test {result['kod_testu']}):</b> {result['question']}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='color:red'><b>Pytanie {result['question_number']} (Test {result['kod_testu']}):</b> {result['question']}</span>", unsafe_allow_html=True)

        st.write("Twoje odpowiedzi:")
        for answer in result['user_answers']:
            st.write(f"- {answer}")

        st.write("Poprawne odpowiedzi:")
        for correct_answer in result['correct_answers']:
            st.write(f"- {correct_answer}")

        if result['is_correct']:
            st.markdown("<span style='color:green'>Odpowiedź poprawna!</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='color:red'>Odpowiedź błędna.</span>", unsafe_allow_html=True)

# Application interface
st.title("Test wielokrotnego wyboru")

if "test_started" not in st.session_state:
    st.session_state["test_started"] = False

if "test_completed" not in st.session_state:
    st.session_state["test_completed"] = False

# Start the test with selected test code
if not st.session_state["test_started"] and not st.session_state["test_completed"]:
    if st.button("Rozpocznij test"):
        st.session_state["test_started"] = True
        initialize_questions(df, selected_test_code, n=liczba_pytan)

# Generate the test if it has started
if st.session_state["test_started"]:
    all_checkbox_keys = generate_test()

    if st.button("Zakończ test"):
        correct_answers, results = check_answers(df, all_checkbox_keys)
        st.write(f"Poprawnych odpowiedzi: {correct_answers}.")
        st.session_state["test_completed"] = True
        st.session_state["test_started"] = False

        display_results(results)

# After test completion, allow a new test or repeating the previous one
if st.session_state["test_completed"]:
    if st.button("Powtórz test"):
        st.session_state["test_completed"] = False
        st.session_state["test_started"] = True
        st.session_state["random_questions"] = st.session_state["random_questions"]  # Use the same set of questions
        all_checkbox_keys = generate_test()  # Generate the test again
    if st.button("Rozpocznij nowy test"):
        st.session_state["test_completed"] = False
        st.session_state["test_started"] = False
        del st.session_state["random_questions"]
        st.experimental_rerun()
