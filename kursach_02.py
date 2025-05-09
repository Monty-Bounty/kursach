import csv
import tkinter as tk
from tkinter import messagebox

# --- Константы и глобальные переменные ---
FILENAME = "users.data" # Файл будет в папке запуска скрипта
XOR_KEY = "SimpleKey"
user_list = []
current_logged_in_user = None # Для хранения данных вошедшего пользователя

# --- Функции для работы с данными ---

def xor_cipher(text, key):
  """
  Кодирует/декодирует текст с помощью XOR.
  Принимает строку, возвращает строку.
  Результат может содержать непечатные символы.
  """
  repeated_key = (key * (len(text) // len(key) + 1))[:len(text)]
  # Применяем XOR к каждому символу
  result = ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(text, repeated_key))
  return result

def load_users(filename):
  """Загружает список пользователей из файла."""
  users = []
  # Если файла нет, он будет создан при первой регистрации (режим 'a+')
  with open(filename, 'a+', newline='', encoding='utf-8') as file:
      file.seek(0) # Перемещаем курсор в начало для чтения
      reader = csv.reader(file, delimiter=';')
      for row in reader:
          if row and len(row) == 9: # Ожидаем 9 полей
              user_data = {
                  "last_name": row[0],
                  "first_name": row[1],
                  "middle_name": row[2],
                  "birth_date": row[3],
                  "gender": row[4],
                  "city": row[5],
                  "email": row[6],
                  "login": row[7],
                  "password_xor_encoded": row[8] # Пароль "зашифрован" XOR
              }
              users.append(user_data)
  return users


def save_users(users, filename):
  """Сохраняет список пользователей в файл."""
  with open(filename, 'w', newline='', encoding='utf-8') as file:
      writer = csv.writer(file, delimiter=';')
      for user in users:
          writer.writerow([
              user["last_name"],
              user["first_name"],
              user["middle_name"],
              user["birth_date"],
              user["gender"],
              user["city"],
              user["email"],
              user["login"],
              user["password_xor_encoded"] # Сохраняем XOR "зашифрованный" пароль
          ])


def find_user_by_login(users, login):
  """Ищет пользователя по логину."""
  for user_data_item in users: # Изменено имя переменной для ясности
    if user_data_item["login"] == login:
      return user_data_item
  return None

# --- Функции для GUI ---

def clear_entries(entries_list):
    """Очищает поля ввода из списка."""
    for entry in entries_list:
        if isinstance(entry, tk.Entry):
            entry.delete(0, tk.END)
    if 'gender_var' in globals() and isinstance(gender_var, tk.StringVar):
        gender_var.set("")

def show_frame(frame_to_show):
    """Показывает выбранный фрейм и скрывает остальные."""
    login_frame.pack_forget()
    register_frame.pack_forget()
    user_info_frame.pack_forget() # Также скрываем фрейм информации о пользователе
    frame_to_show.pack(fill="both", expand=True, padx=20, pady=20)

def display_user_info(user_data):
    """Заполняет метки на фрейме user_info_frame данными пользователя."""
    global current_logged_in_user
    current_logged_in_user = user_data

    # Очищаем предыдущие значения, если они были
    for widget in user_info_display_frame.winfo_children():
        if isinstance(widget, tk.Label) and hasattr(widget, 'is_data_label'):
            widget.destroy() # Удаляем только метки с данными

    # Создаем и размещаем метки с информацией о пользователе
    info_labels_config = [
        ("Фамилия:", user_data.get("last_name", "N/A")),
        ("Имя:", user_data.get("first_name", "N/A")),
        ("Отчество:", user_data.get("middle_name", "N/A") or "Отсутствует"), # Показываем "Отсутствует", если пусто
        ("Дата рождения:", user_data.get("birth_date", "N/A")),
        ("Пол:", user_data.get("gender", "N/A")),
        ("Город:", user_data.get("city", "N/A")),
        ("Email:", user_data.get("email", "N/A")),
        ("Логин:", user_data.get("login", "N/A")),
    ]

    for i, (text, value) in enumerate(info_labels_config):
        '''Пользовательский атрибут для идентификации'''
        label_text = tk.Label(user_info_display_frame, text=text, font=("Arial", 11), anchor="w")
        label_text.grid(row=i, column=0, padx=5, pady=2, sticky="w")
        label_text.is_data_label = True 

        label_value = tk.Label(user_info_display_frame, text=value, font=("Arial", 11, "bold"), anchor="w")
        label_value.grid(row=i, column=1, padx=5, pady=2, sticky="w")
        label_value.is_data_label = True

    show_frame(user_info_frame)


def handle_login():
    """Обрабатывает попытку входа."""
    login = login_entry_login.get()
    password_attempt = password_entry_login.get()

    if not login or not password_attempt:
        messagebox.showerror("Ошибка входа", "Пожалуйста, введите логин и пароль.")
        return

    user = find_user_by_login(user_list, login)

    if user:
        # "Дешифруем" сохраненный пароль (применяем XOR еще раз)
        stored_password_decoded = xor_cipher(user["password_xor_encoded"], XOR_KEY)

        if password_attempt == stored_password_decoded:
            # Формируем имя для приветствия
            user_name_for_greeting = user.get('first_name', 'Пользователь')
            if user.get('last_name'):
                user_name_for_greeting = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()

            messagebox.showinfo("Успешный вход", f"Добро пожаловать, {user_name_for_greeting}!")
            
            clear_entries([login_entry_login, password_entry_login])
            display_user_info(user) # Показываем информацию о пользователе
        else:
            messagebox.showerror("Ошибка входа", "Неверный пароль.")
    else:
        messagebox.showerror("Ошибка входа", "Пользователь с таким логином не найден.")

def handle_register():
    """Обрабатывает попытку регистрации."""
    last_name = last_name_entry_reg.get()
    first_name = first_name_entry_reg.get()
    middle_name = middle_name_entry_reg.get()
    birth_date = birth_date_entry_reg.get()
    gender = gender_var.get()
    city = city_entry_reg.get()
    email = email_entry_reg.get()
    login = login_entry_reg.get()
    password = password_entry_reg.get()
    password_confirm = password_confirm_entry_reg.get()

    if not all([last_name, first_name, birth_date, gender, city, email, login, password, password_confirm]):
        messagebox.showerror("Ошибка регистрации", "Пожалуйста, заполните все обязательные поля (кроме Отчества).")
        return

    if password != password_confirm:
        messagebox.showerror("Ошибка регистрации", "Пароли не совпадают.")
        return

    if find_user_by_login(user_list, login):
        messagebox.showerror("Ошибка регистрации", f"Пользователь с логином '{login}' уже существует.")
        return

    # "Шифрование" пароля с помощью XOR
    password_xor_encoded = xor_cipher(password, XOR_KEY)

    new_user = {
        "last_name": last_name,
        "first_name": first_name,
        "middle_name": middle_name,
        "birth_date": birth_date,
        "gender": gender,
        "city": city,
        "email": email,
        "login": login,
        "password_xor_encoded": password_xor_encoded
    }

    user_list.append(new_user)
    save_users(user_list, FILENAME)

    messagebox.showinfo("Успешная регистрация", "Пользователь успешно зарегистрирован!")
    clear_entries([
        last_name_entry_reg, first_name_entry_reg, middle_name_entry_reg,
        birth_date_entry_reg, city_entry_reg,
        email_entry_reg, login_entry_reg, password_entry_reg,
        password_confirm_entry_reg
    ])
    gender_var.set("")
    show_frame(login_frame)

def handle_logout():
    """Обрабатывает выход пользователя из системы."""
    global current_logged_in_user
    current_logged_in_user = None
    show_frame(login_frame)


# --- Основная функция для запуска приложения ---
def main():
    # Делаем переменные глобальными, чтобы к ним был доступ из других функций GUI
    global window, login_frame, register_frame, user_info_frame, user_info_display_frame
    global login_entry_login, password_entry_login
    global last_name_entry_reg, first_name_entry_reg, middle_name_entry_reg
    global birth_date_entry_reg, gender_var, city_entry_reg, email_entry_reg
    global login_entry_reg, password_entry_reg, password_confirm_entry_reg
    global user_list # user_list также должен быть доступен глобально для функций

    window = tk.Tk()
    window.title("Система регистрации и входа (Простой XOR)")
    window.geometry("450x650")

    # --- Создание фреймов (экранов) ---
    login_frame = tk.Frame(window)
    register_frame = tk.Frame(window)
    user_info_frame = tk.Frame(window) # Фрейм для отображения информации о пользователе

    # --- Виджеты для экрана входа ---
    login_label_login = tk.Label(login_frame, text="Вход в систему", font=("Arial", 16, "bold"))
    login_label_login.pack(pady=20)
    tk.Label(login_frame, text="Логин:", font=("Arial", 12)).pack(pady=5)
    login_entry_login = tk.Entry(login_frame, width=30, font=("Arial", 12))
    login_entry_login.pack(pady=5)
    tk.Label(login_frame, text="Пароль:", font=("Arial", 12)).pack(pady=5)
    password_entry_login = tk.Entry(login_frame, show="*", width=30, font=("Arial", 12))
    password_entry_login.pack(pady=10)
    login_button = tk.Button(login_frame, text="Войти", command=handle_login, width=15, height=2, font=("Arial", 12))
    login_button.pack(pady=10)
    go_to_register_button = tk.Button(login_frame, text="Зарегистрироваться", command=lambda: show_frame(register_frame), width=20, font=("Arial", 10))
    go_to_register_button.pack(pady=5)

    # --- Виджеты для экрана регистрации ---
    register_label_reg = tk.Label(register_frame, text="Регистрация", font=("Arial", 16, "bold"))
    register_label_reg.grid(row=0, column=0, columnspan=3, pady=15, sticky="n")
    current_row = 1
    tk.Label(register_frame, text="Фамилия*:", font=("Arial", 11)).grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
    last_name_entry_reg = tk.Entry(register_frame, width=30, font=("Arial", 11))
    last_name_entry_reg.grid(row=current_row, column=1, padx=5, pady=5)
    current_row += 1
    tk.Label(register_frame, text="Имя*:", font=("Arial", 11)).grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
    first_name_entry_reg = tk.Entry(register_frame, width=30, font=("Arial", 11))
    first_name_entry_reg.grid(row=current_row, column=1, padx=5, pady=5)
    current_row += 1
    tk.Label(register_frame, text="Отчество:", font=("Arial", 11)).grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
    middle_name_entry_reg = tk.Entry(register_frame, width=30, font=("Arial", 11))
    middle_name_entry_reg.grid(row=current_row, column=1, padx=5, pady=5)
    current_row += 1
    tk.Label(register_frame, text="Дата рождения*:", font=("Arial", 11)).grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
    birth_date_entry_reg = tk.Entry(register_frame, width=30, font=("Arial", 11))
    birth_date_entry_reg.grid(row=current_row, column=1, padx=5, pady=5)
    tk.Label(register_frame, text="(ДД.ММ.ГГГГ)", font=("Arial", 9)).grid(row=current_row, column=2, padx=2, pady=5, sticky="w")
    current_row += 1
    tk.Label(register_frame, text="Пол*:", font=("Arial", 11)).grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
    gender_var = tk.StringVar(value="")
    gender_frame_ui = tk.Frame(register_frame) 
    tk.Radiobutton(gender_frame_ui, text="Мужской", variable=gender_var, value="Мужской", font=("Arial", 11)).pack(side=tk.LEFT)
    tk.Radiobutton(gender_frame_ui, text="Женский", variable=gender_var, value="Женский", font=("Arial", 11)).pack(side=tk.LEFT)
    gender_frame_ui.grid(row=current_row, column=1, padx=5, pady=5, sticky="w")
    current_row += 1
    tk.Label(register_frame, text="Город*:", font=("Arial", 11)).grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
    city_entry_reg = tk.Entry(register_frame, width=30, font=("Arial", 11))
    city_entry_reg.grid(row=current_row, column=1, padx=5, pady=5)
    current_row += 1
    tk.Label(register_frame, text="Email*:", font=("Arial", 11)).grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
    email_entry_reg = tk.Entry(register_frame, width=30, font=("Arial", 11))
    email_entry_reg.grid(row=current_row, column=1, padx=5, pady=5)
    current_row += 1
    tk.Label(register_frame, text="Логин*:", font=("Arial", 11)).grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
    login_entry_reg = tk.Entry(register_frame, width=30, font=("Arial", 11))
    login_entry_reg.grid(row=current_row, column=1, padx=5, pady=5)
    current_row += 1
    tk.Label(register_frame, text="Пароль*:", font=("Arial", 11)).grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
    password_entry_reg = tk.Entry(register_frame, width=30, font=("Arial", 11)) # Пароль виден
    password_entry_reg.grid(row=current_row, column=1, padx=5, pady=5)
    current_row += 1
    tk.Label(register_frame, text="Подтвердите пароль*:", font=("Arial", 11)).grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
    password_confirm_entry_reg = tk.Entry(register_frame, width=30, font=("Arial", 11)) # Пароль виден
    password_confirm_entry_reg.grid(row=current_row, column=1, padx=5, pady=5)
    current_row += 1
    tk.Label(register_frame, text="* - обязательные поля", font=("Arial", 9)).grid(row=current_row, column=0, columnspan=3, padx=5, pady=10, sticky="w")
    current_row += 1
    register_button_reg = tk.Button(register_frame, text="Зарегистрироваться", command=handle_register, width=20, height=2, font=("Arial", 12))
    register_button_reg.grid(row=current_row, column=0, columnspan=3, pady=15)
    current_row += 1
    go_to_login_button_reg = tk.Button(register_frame, text="Уже есть аккаунт? Войти", command=lambda: show_frame(login_frame), width=25, font=("Arial", 10))
    go_to_login_button_reg.grid(row=current_row, column=0, columnspan=3, pady=5)

    # --- Виджеты для экрана информации о пользователе ---
    user_info_label = tk.Label(user_info_frame, text="Личный кабинет", font=("Arial", 16, "bold"))
    user_info_label.pack(pady=15)

    user_info_display_frame = tk.Frame(user_info_frame) # Внутренний фрейм для меток с данными
    user_info_display_frame.pack(pady=10, padx=10, fill="x")

    logout_button = tk.Button(user_info_frame, text="Выйти", command=handle_logout, width=15, height=2, font=("Arial", 12))
    logout_button.pack(pady=20)

    # --- Загрузка пользователей и запуск ---
    user_list = load_users(FILENAME)
    print(f"Загружено {len(user_list)} пользователей из файла '{FILENAME}'.")

    show_frame(login_frame) # Показываем сначала экран входа
    window.mainloop()

# --- Точка входа в программу ---
if __name__ == "__main__":
    main()
