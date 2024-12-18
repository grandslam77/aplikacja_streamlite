import streamlit as st
import pandas as pd
import sqlite3
import random
import os

# Sprawdzenie aktualnego katalogu roboczego
# current_directory = os.getcwd()
# print("Aktualny katalog roboczy:", current_directory)

# 
# # Połączenie z bazą danych SQLite
# 
# new_directory = 'E:/PROJEKTY/PROJEKTY/NewWycenaNieruchomosci'
# os.chdir(new_directory)
# 
# conn = sqlite3.connect('baza/PovertyVerse.db')
# df = pd.read_sql_query("SELECT * FROM testy_pytania_odpowiedzi_klucze", conn)
# conn.close()

# Wczytanie danych z pliku Excel z pytaniami i odpowiedziami



# df = pd.read_excel("zestaw1.xlsx")
# df = pd.read_excel("zestaw2.xlsx")
# df = pd.read_excel("zestaw3.xlsx")
df = pd.read_excel("zestaw21.xlsx")
# df = pd.read_excel("zestaw10.xlsx")
# df = pd.read_excel("pytania_i_odpowiedzi_X.xlsx")


# df['Kod_Testu'] = df['Kod_Testu'].astype(str)
# df['Numer_Pytania'] = df['Numer_Pytania'].astype(str)

# Losowanie pytań na podstawie "Kod_Testu" i "Numer_Pytania"
liczba_pytan=90
def get_random_questions(df, n=liczba_pytan):
    unique_questions = df[['Kod_Testu', 'Numer_Pytania', 'Tresc_Pytania']].drop_duplicates(subset=['Kod_Testu', 'Numer_Pytania']).sample(n)
    return unique_questions

# Funkcja generująca pytania, która zapisuje je w st.session_state
def initialize_questions(df, n=liczba_pytan):
    if "random_questions" not in st.session_state:
        st.session_state["random_questions"] = get_random_questions(df, n)

# Generowanie formularza testowego
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

# Funkcja do sprawdzania odpowiedzi po naciśnięciu przycisku "Zakończ test"
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

# Funkcja wyświetlająca wyniki po zakończeniu testu
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

# Interfejs aplikacji
st.title("Test wielokrotnego wyboru")

if "test_started" not in st.session_state:
    st.session_state["test_started"] = False

if "test_completed" not in st.session_state:
    st.session_state["test_completed"] = False

# Start testu
if not st.session_state["test_started"] and not st.session_state["test_completed"]:
    if st.button("Rozpocznij test"):
        st.session_state["test_started"] = True
        initialize_questions(df, n=liczba_pytan)

# Generowanie testu, jeśli test się rozpoczął
if st.session_state["test_started"]:
    all_checkbox_keys = generate_test()

    if st.button("Zakończ test"):
        correct_answers, results = check_answers(df, all_checkbox_keys)
        st.write(f"Poprawnych odpowiedzi: {correct_answers}.")
        st.session_state["test_completed"] = True
        st.session_state["test_started"] = False

        display_results(results)

# Po zakończeniu testu - wyświetlenie wyniku i możliwość rozpoczęcia nowego testu
if st.session_state["test_completed"]:
    if st.button("Powtórz test"):
        # Resetowanie stanu testu po zakończeniu
        st.session_state["test_completed"] = False
        st.session_state["test_started"] = True
        # Użyj zapisanych pytań w sesji
        st.session_state["random_questions"] = st.session_state["random_questions"]  # Przywróć ten sam zestaw pytań
        all_checkbox_keys = generate_test()  # Generuj test ponownie
    if st.button("Rozpocznij nowy test"):
        # Resetowanie stanu testu po zakończeniu
        st.session_state["test_completed"] = False
        st.session_state["test_started"] = False
        del st.session_state["random_questions"]
        st.experimental_rerun()
