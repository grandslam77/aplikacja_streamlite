# Normalizacja danych
def remove_prefix(value):
    if isinstance(value, str) and "_" in value:
        return value.split("_", 1)[-1]
    return value

df['Kod_Testu'] = df['Kod_Testu'].apply(remove_prefix)
df['Klucz_Wiersza'] = df['Klucz_Wiersza'].apply(remove_prefix)

# Funkcje dostosowane do nowych danych
def get_random_questions(df, n=11):
    unique_questions = df[['Kod_Testu', 'Numer_Pytania', 'Tresc_Pytania']].copy()
    unique_questions['Kod_Testu'] = unique_questions['Kod_Testu'].apply(remove_prefix)
    unique_questions = unique_questions.drop_duplicates(subset=['Kod_Testu', 'Numer_Pytania']).sample(n)
    return unique_questions

# Wykorzystanie funkcji `remove_prefix` w pozostałych częściach kodu
def check_answers(df, all_checkbox_keys):
    correct = 0
    user_answers = {}
    results = []

    for checkbox_key in all_checkbox_keys:
        _, kod_testu, question_number, answer_id = checkbox_key.split('_')
        kod_testu = remove_prefix(kod_testu)
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
