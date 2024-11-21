import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, Listbox, END
from translate import (
    read_word_csv, write_word_csv, read_error_csv, write_error_csv, 
    search_word, get_categories, search_error, add_word, add_error, 
    update_correction_counter, suggest_similar_words, read_rules_csv, write_rules_csv, search_rules, sort_words
)

def centrar_ventana(ventana, ancho, alto):
    """Centra la ventana en la pantalla."""
    ventana.update_idletasks()
    width = ventana.winfo_screenwidth()
    height = ventana.winfo_screenheight()
    x = (width // 2) - (ancho // 2)
    y = (height // 2) - (alto // 2)
    ventana.geometry(f'{ancho}x{alto}+{x}+{y}')

def mostrar_opciones(titulo, mensaje, opciones):
    ventana = tk.Toplevel()
    ventana.title(titulo)
    ventana.configure(bg='#f0f0f0')

    # Tamaño de la ventana
    ancho = 400
    alto = 300
    centrar_ventana(ventana, ancho, alto)

    seleccion = tk.IntVar(value=-1)

    # Etiqueta de mensaje
    tk.Label(ventana, text=mensaje, bg='#f0f0f0', font=("Arial", 12)).pack(pady=20)

    # Crear botones de opción
    for idx, opcion in enumerate(opciones):
        tk.Radiobutton(ventana, text=opcion, variable=seleccion, value=idx,
                        bg='#f0f0f0', font=("Arial", 10)).pack(anchor="w", padx=20)

    # Botón de confirmación
    confirmar = tk.Button(ventana, text="Aceptar", command=ventana.quit,
                            bg='#4CAF50', fg='white', font=("Arial", 12), width=10)
    confirmar.pack(pady=20)

    ventana.mainloop()

    seleccion_idx = seleccion.get()
    ventana.destroy()
    return seleccion_idx

def corregir_palabra(word):
    # Buscar correcciones y sugerencias
    corrections = search_error(word, error_list)
    suggestions = suggest_similar_words(word, word_list)

    # Combinar correcciones y sugerencias en un diccionario
    combined_corrections = {corr[0]: corr[1] for corr in corrections} if corrections else {}

    # Agregar sugerencias a las correcciones combinadas
    for suggestion in suggestions:
        if suggestion not in combined_corrections:
            combined_corrections[suggestion] = 0  

    # Ordenar correcciones
    sorted_corrections = sorted(combined_corrections.items(), key=lambda x: x[1], reverse=True)

    # Manejo de correcciones
    if corrections:  # Asegurarse de que hay correcciones o sugerencias
        correction_options = [c[0] for c in sorted_corrections]
        correction_options.append("Agregar corrección")
        selection_idx = mostrar_opciones("Correcciones", f"Posibles correcciones para {word}: ", correction_options)

        if selection_idx is not None: 
            try:
                selection_idx = int(selection_idx)  # Convertir a entero
                if 0 <= selection_idx < len(sorted_corrections):  # Validar el rango del índice
                    selected_correction = sorted_corrections[selection_idx][0]
                    val = list(sorted_corrections[selection_idx])
                    if val in corrections:
                        update_correction_counter(word, selected_correction, error_list)
                    else:
                        add_error(word, selected_correction, error_list)

                    write_error_csv(error_list)
                    return selected_correction
                else:
                    correction = simpledialog.askstring("Corrección", "Ingrese la corrección:")
                    if correction:
                        add_error(word, correction, error_list)
                        write_error_csv(error_list)
                        trad = search_word(correction, word_list)
                        if trad:
                            return correction
                        else:
                            trad = simpledialog.askstring("Nueva Traducción", f"Ingrese la traducción para '{correction}':")
                            if trad:
                                sel_cate = mostrar_opciones("Categoría", "Seleccione su categoría:", ["Sustantivo", "Adjetivo"])
                                cate = "s" if sel_cate == 0 else "ad"
                                add_word(correction, trad, cate, word_list)
                                write_word_csv(word_list)
                                return correction
            except ValueError:
                print("Error: El índice seleccionado no es un número válido.")

    else:
        # Si no hay correcciones, preguntar al usuario si quiere registrar el error
        choice = messagebox.askquestion("Registrar Error", f"'{word}' no está registrada. ¿Desea registrarla como error?")
        if choice == "yes":
            correction = simpledialog.askstring("Corrección", "Ingrese la corrección:")
            if correction:
                add_error(word, correction, error_list)
                write_error_csv(error_list)
        else:
            # Manejo de sugerencias
            if suggestions:
                suggestion_options = suggestions + ["Agregar nueva palabra"]
                select = mostrar_opciones("Sugerencias", "Sugerencias de palabras similares:", suggestion_options)

                if select is not None and 0 <= int(select) < len(suggestions):
                    selected_word = suggestions[int(select)]
                    return selected_word
                elif select == len(suggestions):  # Agregar nueva palabra
                    trad = simpledialog.askstring("Nueva Traducción", f"Ingrese la traducción para '{word}':")
                    if trad:
                        sel_cate = mostrar_opciones("Categoría", "Seleccione su categoría:", ["Sustantivo", "Adjetivo"])
                        cate = "s" if sel_cate == 0 else "ad"
                        add_word(word, trad, cate, word_list)
                        write_word_csv(word_list)
            else:
                # Si no hay sugerencias, preguntar por la nueva traducción
                trad = simpledialog.askstring("Nueva Traducción", f"Ingrese la traducción para '{word}':")
                if trad:
                    sel_cate = mostrar_opciones("Categoría", "Seleccione su categoría:", ["Sustantivo", "Adjetivo"])
                    print(sel_cate)
                    cate = "s" if sel_cate == 0 else "ad"
                    add_word(word, trad, cate, word_list)
                    write_word_csv(word_list)
                    return (word, cate)


def traducir():
    phrase = simpledialog.askstring("Traducir", "Ingrese una frase para traducir:") 
    if not phrase:
        return
    words = phrase.split()

    if len(words) > 1:  
        all_registered = all(search_word(word, word_list) for word in words)

        if not all_registered:
            messagebox.showinfo("Información", "Algunas palabras no están registradas.")

            for i in range(len(words)):
                word = words[i]
                if not search_word(word, word_list):
                    result = corregir_palabra(word)
                    if result:
                        words[i] = result
                    else:
                        print("No se encontró una corrección para la palabra.")

            categories = tuple(get_categories(words, word_list))

            rule = search_rules(categories, rules_list)
            # Verificar si las categorías están en la lista de reglas
            if rule:
                # Reemplazar cada palabra por su traducción usando search_word
                for i in range(len(words)):
                    words[i] = search_word(words[i], word_list)

                words = sort_words(words, rule)
                list_trad = [word[0] for word in words]
                trad_string = " ".join(list_trad)
                messagebox.showinfo("Traducción", f"Traducción: {trad_string}")
            else:
                messagebox.showinfo("Error", f"No se encontró regla para las categorías: {categories}")
        else:
            # Obtener las categorías para las palabras ingresadas
            categories = tuple(get_categories(words, word_list))
            rule = search_rules(categories, rules_list)

            # Verificar si las categorías están en la lista de reglas
            if rule:
                # Reemplazar cada palabra por su traducción usando search_word
                for i in range(len(words)):
                    words[i] = search_word(words[i], word_list)
                words = sort_words(words, rule)
                if rule[0] == 'a':
                    a = tuple(['el', 'a'])
                    words.insert(0,a)

                list_trad = [word[0] for word in words]
                trad_string = " ".join(list_trad)
                messagebox.showinfo("Traducción", f"Traducción: {trad_string}")
            else:
                messagebox.showinfo("Error", f"No se encontró regla para las categorías: {categories}")


    elif len(words) == 1:  
        word = words[0]
        result = search_word(word, word_list)
        
        if result:
            messagebox.showinfo("Traducción", f"Traducción: {result[0]}")
        else:
            corrections = search_error(word, error_list)
            suggestions = suggest_similar_words(word, word_list)
            combined_corrections = {corr[0]: corr[1] for corr in corrections} if corrections else {}
            
            for suggestion in suggestions:
                if suggestion not in combined_corrections:
                    combined_corrections[suggestion] = 0  

            sorted_corrections = sorted(combined_corrections.items(), key=lambda x: x[1], reverse=True)

            if corrections:
                correction_options = [c[0] for c in sorted_corrections]
                correction_options.append("Agregar corrección")

                selection_idx = mostrar_opciones("Correcciones", "Posibles correcciones:", correction_options)

                if selection_idx is not None:  # Verificar que selection_idx no sea None
                    try:
                        selection_idx = int(selection_idx)  # Convertir a entero
                        if 0 <= selection_idx < len(sorted_corrections):  # Validar el rango del índice
                            selected_correction = sorted_corrections[selection_idx][0]
                            val = list(sorted_corrections[selection_idx])

                            if val in corrections:
                                update_correction_counter(word, selected_correction, error_list)
                            else:
                                add_error(word, selected_correction, error_list)

                            trad = search_word(selected_correction, word_list)
                            write_error_csv(error_list)
                            messagebox.showinfo("Traducción", f"Traducción: {trad[0]}")
                        else:
                            correction = simpledialog.askstring("Corrección", "Ingrese la corrección:")
                            if correction:
                                add_error(word, correction, error_list)
                                write_error_csv(error_list)
                                trad = search_word(correction, word_list)
                                if trad:
                                    messagebox.showinfo("Traducción", f"Traducción: {trad[0]}")
                                else:
                                    trad = simpledialog.askstring("Nueva Traducción", f"Ingrese la traducción para '{word}':")
                                    if trad:
                                        sel_cate = mostrar_opciones("Categoría", "Seleccione su categoría:", ["Sustantivo", "Adjetivo"])
                                        cate = "s" if sel_cate == 0 else "ad"
                                        add_word(correction, trad, cate, word_list)
                                        write_word_csv(word_list)
                                        
                    except ValueError:
                        print("Error: El índice seleccionado no es un número válido.")
                
                    
            else:
                choice = messagebox.askquestion("Registrar Error", f"'{word}' no está registrada. ¿Desea registrarla como error?")
                if choice == "yes":
                    correction = simpledialog.askstring("Corrección", "Ingrese la corrección:")
                    if correction:
                        add_error(word, correction, error_list)
                        write_error_csv(error_list)
                else:
                    if suggestions:
                        suggestion_options = [s for s in suggestions] + ["Agregar nueva palabra"]
                        select = mostrar_opciones("Sugerencias", "Sugerencias de palabras similares:", suggestion_options)
                        
                        if select is not None and 0 <= int(select) < len(suggestions):
                            selected_word = suggestions[int(select)]
                            result = search_word(selected_word, word_list)
                            messagebox.showinfo("Traducción", f"Traducción: {result[0]}")
                        elif select == len(suggestions):
                            trad = simpledialog.askstring("Nueva Traducción", f"Ingrese la traducción para '{word}':")
                            if trad:
                                sel_cate = mostrar_opciones("Categoría", "Seleccione su categoría:", ["Sustantivo", "Adjetivo"])
                                cate = "s" if sel_cate == 0 else "ad"
                                add_word(word, trad, cate, word_list)
                                write_word_csv(word_list)
                    else:
                        trad = simpledialog.askstring("Nueva Traducción", f"Ingrese la traducción para '{word}':")
                        if trad:
                            sel_cate = mostrar_opciones("Categoría", "Seleccione su categoría:", ["Sustantivo", "Adjetivo"])
                            cate = "s" if sel_cate == 0 else "ad"
                            add_word(word, trad, cate, word_list)
                            write_word_csv(word_list)


def agregar():
    global rules_list
    # Solicitar la frase a agregar
    phrase = simpledialog.askstring("Agregar Frase", "Ingrese una frase para agregar:")
    if not phrase:
        return
    
    # Dividir la frase en palabras
    words = phrase.split()
    
    # Solicitar la traducción de la frase
    translations = simpledialog.askstring("Traducción", "Ingrese la traducción para la frase:")
    if not translations:
        return

    # Verificar si todas las palabras están registradas
    all_registered = all(search_word(word, word_list) for word in words)
    if not all_registered:
        messagebox.showinfo("Información", "Algunas palabras no están registradas.")

        for i in range(len(words)):
            word = words[i]
            if not search_word(word, word_list):
                result = corregir_palabra(word)
                if result:
                    words[i] = result
                else:
                    print("No se encontró una corrección para la palabra.")
        
        # Todas las palabras están registradas, se construye la regla
        categories_Phrase = get_categories(words, word_list)  # Obtener categorías de la frase original
        categories_Translations = get_categories(translations.split(), word_list)  # Categorías de la traducción

        # Añadir la nueva regla a la lista global 'rules_list'
        rules_list.append([categories_Phrase, categories_Translations])
        
        # Guardar la lista actualizada de reglas en el archivo CSV
        write_rules_csv(rules_list)
        rules_list = read_rules_csv()  # Actualizar la lista de reglas global

        # Mostrar mensaje de confirmación
        messagebox.showinfo("Regla Aprendida", f"{categories_Phrase} = {categories_Translations}")
        
    else:
        # Todas las palabras están registradas, se construye la regla
        categories_Phrase = get_categories(words, word_list)  # Obtener categorías de la frase original
        categories_Translations = get_categories(translations.split(), word_list)  # Categorías de la traducción

        # Añadir la nueva regla a la lista global 'rules_list'
        rules_list.append([categories_Phrase, categories_Translations])
        
        # Guardar la lista actualizada de reglas en el archivo CSV
        write_rules_csv(rules_list)
        rules_list = read_rules_csv()  # Actualizar la lista de reglas global

        # Mostrar mensaje de confirmación
        messagebox.showinfo("Regla Aprendida", f"{categories_Phrase} = {categories_Translations}")

def show_word_list():
    # Create a new window
    list_window = Toplevel(root)
    list_window.title("Lista de Palabras")
    
    # Add a listbox to display words
    listbox = Listbox(list_window, font=("Arial", 12), width=50, height=15)
    listbox.pack(padx=10, pady=10)
    
    # Insert words into the listbox
    for word in word_list:
        listbox.insert(END, f"{word[0]} -> {word[1]} ({word[2]})")  # Assuming word_list contains tuples (word, translation, category)

def main():
    global word_list, error_list, rules_list
    word_list = read_word_csv()
    error_list = read_error_csv()
    rules_list = read_rules_csv()

    global root
    root = tk.Tk()
    root.title("Traductor Minimalista")
    root.configure(bg='#e0e0e0')

    # Tamaño de la ventana
    ancho = 400
    alto = 250
    centrar_ventana(root, ancho, alto)

    tk.Label(root, text="Seleccione una acción:", bg='#e0e0e0', font=("Arial", 14)).pack(pady=15)

    btn_traducir = tk.Button(root, text="Traducir", command=traducir,
                                bg='#008CBA', fg='white', font=("Arial", 12), width=15)
    btn_traducir.pack(pady=10)

    btn_agregar = tk.Button(root, text="Agregar una Regla", command=agregar,
                            bg='#f44336', fg='white', font=("Arial", 12), width=15)
    btn_agregar.pack(pady=10)

    btn_listar = tk.Button(root, text="Listar Palabras", command=show_word_list,
                            bg='#4CAF50', fg='white', font=("Arial", 12), width=15)
    btn_listar.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()