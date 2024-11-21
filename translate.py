import csv
from difflib import SequenceMatcher

def normalize(word):
    return word.strip().lower()

def levenshtein_sim(a, b):
    return SequenceMatcher(None, a, b).ratio()

def read_word_csv():
    with open('words.csv', newline='') as file:
        reader_csv = csv.reader(file)
        word_list = [(normalize(row[0]), normalize(row[1]), normalize(row[2])) for row in reader_csv]
    return word_list

def write_word_csv(word_list):
    with open('words.csv', mode='w', newline='') as file:
        writer_csv = csv.writer(file)
        for word, trad, cate in word_list:
            writer_csv.writerow([word, trad, cate])

def read_error_csv():
    with open('errors.csv', newline='') as file:
        reader_csv = csv.reader(file)
        error_list = []
        for row in reader_csv:
            error = normalize(row[0])
            corrections = [[normalize(row[i]), int(row[i+1])] for i in range(1, len(row), 2)]
            error_list.append((error, corrections))
    return error_list

def write_error_csv(error_list):
    with open('errors.csv', mode='w', newline='') as file:
        writer_csv = csv.writer(file)
        for error, corrections in error_list:
            flat_list = [error] + [item for sublist in corrections for item in sublist]
            writer_csv.writerow(flat_list)

def read_rules_csv():
    rules = []
    
    with open('rules.csv', newline='') as file:
        reader_csv = csv.reader(file)
        
        for row in reader_csv:
            if '=' in row:
                # Find the index of the '=' symbol
                equal_index = row.index('=')
                
                # Extract all elements before and after the '=' symbol
                left_tuple = tuple(normalize(item) for item in row[:equal_index])
                right_tuple = tuple(normalize(item.strip(';')) for item in row[equal_index+1:])
                
                # Append tuples as a list
                rules.append([left_tuple, right_tuple])
    return rules

def write_rules_csv(rules):
    with open('rules.csv', mode='w', newline='') as file:
        writer_csv = csv.writer(file)
        
        for rule_pair in rules:
            left_tuple = rule_pair[0]
            right_tuple = rule_pair[1]
            
            # Format and write as: elements before '=' + '=' + elements after '=' + ';'
            row = list(left_tuple) + ['='] + list(right_tuple) + [';']
            writer_csv.writerow(row)

def search_word(word, word_list):
    word = normalize(word)
    for w, trad, cate in word_list:
        if word == w or word == trad:
            return trad if word == w else w, cate
    return None

def search_rules(rule, rules_list):
    # Función auxiliar para comparar reglas ignorando los valores vacíos
    def compare_rules(r1, r2):
        return all(a == b or b == '' for a, b in zip(r1, r2))
    
    # Iterar sobre cada par de reglas en rules_list
    for left, right in rules_list:
        # Si la regla coincide con la parte izquierda, retornar la parte derecha
        if compare_rules(rule, left):
            return right
        # Si la regla coincide con la parte derecha, retornar la parte izquierda
        elif compare_rules(rule, right):
            return left
    # Si no se encontró una coincidencia, retornar None
    return None

def sort_words(words, rule):
    # Crear una lista vacía para almacenar las palabras en el orden correcto
    ordered_words = [None] * len(rule)

    # Iterar sobre la tupla `rule` para encontrar el orden correspondiente en `words`
    for idx, rule_category in enumerate(rule):
        for word_tuple in words:
            word, category = word_tuple  # Desempaquetar la palabra y su categoría
            if category == rule_category:
                # Asignar la palabra en el índice correspondiente
                ordered_words[idx] = word_tuple
                break

    # Filtrar cualquier valor None que no se haya llenado (si alguna palabra no coincide)
    ordered_words = [word for word in ordered_words if word is not None]
    
    return ordered_words

def get_categories(words, word_list):
    categories = []
    for word in words:
        result = search_word(word, word_list)
        if result:
            categories.append(result[1])
    return categories

def search_error(word, error_list):
    word = normalize(word)
    for error, corrections in error_list:
        if word == error:
            return corrections
    return None

def add_word(word, trad, cate, word_list):
    word_list.append((normalize(word), normalize(trad), normalize(cate)))
    return word_list

def add_error(error, correction, error_list):
    normalized_correction = normalize(correction)
    correction = (normalized_correction, 1)  # correction como tupla
        
    for i, (err, corrections) in enumerate(error_list):
        if error == err:
            corrections.append(correction)
            error_list[i] = (err, corrections)
            return error_list
    
    error_list.append((normalize(error), [correction]))
    return error_list

def update_correction_counter(error, selected_correction, error_list):
    for i, (err, corrections) in enumerate(error_list):
        if normalize(error) == err:
            for j, (corr, count) in enumerate(corrections):
                if corr == normalize(selected_correction):
                    corrections[j] = (corr, count + 1)
                    error_list[i] = (err, corrections)
                    return error_list
    return error_list

def suggest_similar_words(word, word_list, threshold=0.7):
    suggestions = []
    for w, trad, _ in word_list:
        if levenshtein_sim(word, w) >= threshold or levenshtein_sim(word, trad) >= threshold:
            suggestions.append(w)
    return suggestions