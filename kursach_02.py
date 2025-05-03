import csv
import tkinter as tk
from tkinter import messagebox
import base64 # Импортируем модуль для Base64

# --- Константы и глобальные переменные ---
FILENAME = "users.data" # Файл будет в папке запуска скрипта
XOR_KEY = "SimpleKey"
user_list = []

# --- Функции для работы с данными ---

def xor_cipher(text, key):
  """Применяет XOR к тексту. Важно: работает с байтами!"""
  # Преобразуем текст и ключ в байты (используя utf-8)
  text_bytes = text.encode('utf-8')
  key_bytes = key.encode('utf-8')
  key_len = len(key_bytes)
  # Применяем XOR
  result_bytes = bytes([b ^ key_bytes[i % key_len] for i, b in enumerate(text_bytes)])
  return result_bytes # Возвращаем байты

def encode_password(password, key):
    """Шифрует пароль: XOR -> Base64"""
    xor_result_bytes = xor_cipher(password, key)
    # Кодируем байты результата XOR в Base64 и преобразуем в строку utf-8
    base64_encoded_bytes = base64.b64encode(xor_result_bytes)
    base64_string = base64_encoded_bytes.decode('utf-8')
    return base64_string # Возвращаем строку Base64

def decode_password(base64_string, key):
    """Дешифрует пароль: Base64 -> XOR"""
    # Преобразуем строку Base64 обратно в байты
    base64_encoded_bytes = base64_string.encode('utf-8')
    # Декодируем из Base64
    xor_result_bytes = base64.b64decode(base64_encoded_bytes)
    # Применяем XOR еще раз (теперь к байтам)
    # Важно: результат xor_cipher для дешифровки - это байты исходной строки
    original_bytes = xor_cipher(xor_result_bytes.decode('utf-8', errors='ignore'), key) # Декодируем байты XOR в строку перед повторным XOR
                                                                                        # errors='ignore' на случай если исходные байты не были валидным utf-8
                                                                                        # но для паролей это маловероятно
    # Декодируем финальные байты обратно в строку
    original_password = original_bytes.decode('utf-8')
    return original_password

def load_users(filename):
  """Загружает список пользователей из файла."""
  users = []
  with open(filename, 'a+', newline='', encoding='utf-8') as file:
      file.seek(0)
      reader = csv.reader(file, delimiter=';')
      for row in reader:
          if row and len(row) == 9:
              user_data = {
                  "last_name": row[0],
                  "first_name": row[1],
                  "middle_name": row[2],
                  "birth_date": row[3],
                  "gender": row[4],
                  "city": row[5],
                  "email": row[6],
                  "login": row[7],
                  # Пароль хранится как строка Base64
                  "password_encoded_base64": row[8]
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
              # Сохраняем пароль в формате Base64
              user["password_encoded_base64"]
          ])


def find_user_by_login(users, login):
  """Ищет пользователя по логину."""
  for user in users:
    if user["login"] == login:
      return user
  return None

# --- Функции для GUI ---

def clear_entries(entries):
    """Очищает поля ввода."""
    for entry in entries:
        if isinstance(entry, tk.Entry):
            entry.delete(0, tk.END)
    if 'gender_var' in globals() and isinstance(gender_var, tk.StringVar):
        gender_var.set("")

def show_frame(frame_to_show):
    """Показывает выбранный фрейм и скрывает остальные."""
    login_frame.pack_forget()
    register_frame.pack_forget()
    frame_to_show.pack(fill="both", expand=True, padx=20, pady=20)

def handle_login():
    """Обрабатывает попытку входа."""
    login = login_entry_login.get()
    password_attempt = password_entry_login.get() # Введенный пользователем пароль

    if not login or not password_attempt:
        messagebox.showerror("Ошибка входа", "Пожалуйста, введите логин и пароль.")
        return

    user = find_user_by_login(user_list, login)

    if user:
        # Декодируем сохраненный пароль (Base64 -> XOR)
        try:
            stored_password_decoded = decode_password(user["password_encoded_base64"], XOR_KEY)
        except Exception as e:
            # Ошибка декодирования Base64 или XOR (например, если данные в файле повреждены)
            print(f"Ошибка декодирования пароля для {login}: {e}") # Вывод в консоль для отладки
            messagebox.showerror("Ошибка входа", "Не удалось проверить пароль. Данные могут быть повреждены.")
            return

        # Сравниваем введенный пароль с расшифрованным
        if password_attempt == stored_password_decoded:
            full_name = f"{user.get('last_name', '')} {user.get('first_name', '')} {user.get('middle_name', '')}".strip()
            messagebox.showinfo("Успешный вход", f"Добро пожаловать, {full_name}!")
            clear_entries([login_entry_login, password_entry_login])
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

    # Кодирование пароля (XOR -> Base64)
    password_encoded_base64 = encode_password(password, XOR_KEY)

    new_user = {
        "last_name": last_name,
        "first_name": first_name,
        "middle_name": middle_name,
        "birth_date": birth_date,
        "gender": gender,
        "city": city,
        "email": email,
        "login": login,
        # Сохраняем закодированный пароль Base64
        "password_encoded_base64": password_encoded_base64
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


# --- Настройка основного окна ---
window = tk.Tk()
window.title("Система регистрации и входа (XOR + Base64)")
window.geometry("450x650")

# --- Создание фреймов (экранов) ---
login_frame = tk.Frame(window)
register_frame = tk.Frame(window)

# --- Виджеты для экрана входа ---
# (Код виджетов остается таким же, как в предыдущей версии)
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
# (Код виджетов остается таким же, как в предыдущей версии)
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
gender_frame = tk.Frame(register_frame)
tk.Radiobutton(gender_frame, text="Мужской", variable=gender_var, value="Мужской", font=("Arial", 11)).pack(side=tk.LEFT)
tk.Radiobutton(gender_frame, text="Женский", variable=gender_var, value="Женский", font=("Arial", 11)).pack(side=tk.LEFT)
gender_frame.grid(row=current_row, column=1, padx=5, pady=5, sticky="w")
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
password_entry_reg = tk.Entry(register_frame, width=30, font=("Arial", 11))
password_entry_reg.grid(row=current_row, column=1, padx=5, pady=5)
current_row += 1

tk.Label(register_frame, text="Подтвердите пароль*:", font=("Arial", 11)).grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
password_confirm_entry_reg = tk.Entry(register_frame, width=30, font=("Arial", 11))
password_confirm_entry_reg.grid(row=current_row, column=1, padx=5, pady=5)
current_row += 1

tk.Label(register_frame, text="* - обязательные поля", font=("Arial", 9)).grid(row=current_row, column=0, columnspan=3, padx=5, pady=10, sticky="w")
current_row += 1

register_button_reg = tk.Button(register_frame, text="Зарегистрироваться", command=handle_register, width=20, height=2, font=("Arial", 12))
register_button_reg.grid(row=current_row, column=0, columnspan=3, pady=15)
current_row += 1

go_to_login_button = tk.Button(register_frame, text="Уже есть аккаунт? Войти", command=lambda: show_frame(login_frame), width=25, font=("Arial", 10))
go_to_login_button.grid(row=current_row, column=0, columnspan=3, pady=5)

# --- Запуск приложения ---
user_list = load_users(FILENAME)
print(f"Загружено {len(user_list)} пользователей из файла '{FILENAME}'.")

show_frame(login_frame)
window.mainloop()


'''
1. добавить if name == main
2. сделавть шифратор и дешифратор одной функцией
3. сделать окно с информацией пользователя после входа
'''