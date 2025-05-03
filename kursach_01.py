import csv
import tkinter as tk
from tkinter import messagebox # Для всплывающих окон с сообщениями

# --- Константы и глобальные переменные ---
FILENAME = "users.data"
XOR_KEY = "SimpleKey"
user_list = [] # Список для хранения пользователей в памяти

# --- Функции для работы с данными ---

def xor_cipher(text, key):
  """Кодирует/декодирует текст с помощью XOR."""
  repeated_key = (key * (len(text) // len(key) + 1))[:len(text)]
  result = ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(text, repeated_key))
  return result

def load_users(filename):
  """Загружает список пользователей из файла (без try-except)."""
  users = []
  # Открываем файл в режиме 'a+' (создаст, если нет), затем читаем.
  # Ошибка FileNotFoundError или другие IOError приведут к падению программы.
  with open(filename, 'a+', newline='', encoding='utf-8') as file:
      file.seek(0) # Перемещаем курсор в начало файла для чтения
      reader = csv.reader(file, delimiter=';')
      for row in reader:
          # Проверяем, что строка не пустая и содержит нужное число полей
          # Обновлено: теперь ожидаем 9 полей (Фамилия, Имя, Отчество, ... Пароль)
          if row and len(row) == 9:
              user_data = {
                  "last_name": row[0], # Фамилия
                  "first_name": row[1], # Имя
                  "middle_name": row[2], # Отчество
                  "birth_date": row[3],
                  "gender": row[4],
                  "city": row[5],
                  "email": row[6],
                  "login": row[7],
                  "password_encoded": row[8]
              }
              users.append(user_data)
  return users


def save_users(users, filename):
  """Сохраняет список пользователей в файл (без try-except)."""
  # Открываем файл в режиме 'w' (перезапись или создание).
  # Ошибка IOError (например, нет прав на запись) приведет к падению программы.
  with open(filename, 'w', newline='', encoding='utf-8') as file:
      writer = csv.writer(file, delimiter=';')
      for user in users:
          writer.writerow([
              user["last_name"], # Фамилия
              user["first_name"], # Имя
              user["middle_name"], # Отчество
              user["birth_date"],
              user["gender"],
              user["city"],
              user["email"],
              user["login"],
              user["password_encoded"]
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
        # Проверяем, является ли объект полем ввода перед очисткой
        if isinstance(entry, tk.Entry):
            entry.delete(0, tk.END)
    # Сбрасываем выбор пола (если переменная существует)
    if 'gender_var' in globals() and isinstance(gender_var, tk.StringVar):
        gender_var.set("") # Сбрасываем значение переменной Radiobutton

def show_frame(frame_to_show):
    """Показывает выбранный фрейм и скрывает остальные."""
    login_frame.pack_forget()
    register_frame.pack_forget()
    frame_to_show.pack(fill="both", expand=True, padx=20, pady=20)

def handle_login():
    """Обрабатывает попытку входа."""
    login = login_entry_login.get()
    password = password_entry_login.get()

    if not login or not password:
        messagebox.showerror("Ошибка входа", "Пожалуйста, введите логин и пароль.")
        return

    user = find_user_by_login(user_list, login)

    if user:
        stored_password_decoded = xor_cipher(user["password_encoded"], XOR_KEY)
        if password == stored_password_decoded:
            # Формируем полное имя для приветствия
            full_name = f"{user.get('last_name', '')} {user.get('first_name', '')} {user.get('middle_name', '')}".strip()
            messagebox.showinfo("Успешный вход", f"Добро пожаловать, {full_name}!")
            # Очищаем поля после успешного входа
            clear_entries([login_entry_login, password_entry_login])
            # Можно добавить переход на другой экран приложения здесь
        else:
            messagebox.showerror("Ошибка входа", "Неверный пароль.")
    else:
        messagebox.showerror("Ошибка входа", "Пользователь с таким логином не найден.")

def handle_register():
    """Обрабатывает попытку регистрации."""
    # Собираем данные из полей ввода
    last_name = last_name_entry_reg.get()
    first_name = first_name_entry_reg.get()
    middle_name = middle_name_entry_reg.get() # Отчество может быть пустым
    birth_date = birth_date_entry_reg.get()
    gender = gender_var.get() # Получаем значение из Radiobutton
    city = city_entry_reg.get()
    email = email_entry_reg.get()
    login = login_entry_reg.get()
    password = password_entry_reg.get()
    password_confirm = password_confirm_entry_reg.get()

    # Проверка на пустые обязательные поля (фамилия, имя, дата, пол, город, email, логин, пароль, подтверждение)
    # Отчество не является обязательным
    if not all([last_name, first_name, birth_date, gender, city, email, login, password, password_confirm]):
        messagebox.showerror("Ошибка регистрации", "Пожалуйста, заполните все обязательные поля (кроме Отчества).")
        return

    # Проверка совпадения паролей
    if password != password_confirm:
        messagebox.showerror("Ошибка регистрации", "Пароли не совпадают.")
        return

    # Проверка существования логина
    if find_user_by_login(user_list, login):
        messagebox.showerror("Ошибка регистрации", f"Пользователь с логином '{login}' уже существует.")
        return

    # Кодирование пароля
    password_encoded = xor_cipher(password, XOR_KEY)

    # Создание нового пользователя
    new_user = {
        "last_name": last_name,
        "first_name": first_name,
        "middle_name": middle_name,
        "birth_date": birth_date,
        "gender": gender,
        "city": city,
        "email": email,
        "login": login,
        "password_encoded": password_encoded
    }

    # Добавление и сохранение
    user_list.append(new_user)
    save_users(user_list, FILENAME)

    messagebox.showinfo("Успешная регистрация", "Пользователь успешно зарегистрирован!")
    # Очистка полей регистрации
    clear_entries([
        last_name_entry_reg, first_name_entry_reg, middle_name_entry_reg, # Очищаем новые поля
        birth_date_entry_reg, city_entry_reg,
        email_entry_reg, login_entry_reg, password_entry_reg,
        password_confirm_entry_reg
    ])
    gender_var.set("") # Сброс Radiobutton
    # Переход на экран входа после регистрации
    show_frame(login_frame)


# --- Настройка основного окна ---
window = tk.Tk()
window.title("Система регистрации и входа")
# Увеличим высоту окна для доп. полей
window.geometry("450x650")

# --- Создание фреймов (экранов) ---
login_frame = tk.Frame(window)
register_frame = tk.Frame(window)

# --- Виджеты для экрана входа ---
login_label_login = tk.Label(login_frame, text="Вход в систему", font=("Arial", 16, "bold"))
login_label_login.pack(pady=20)

tk.Label(login_frame, text="Логин:", font=("Arial", 12)).pack(pady=5)
login_entry_login = tk.Entry(login_frame, width=30, font=("Arial", 12))
login_entry_login.pack(pady=5)

tk.Label(login_frame, text="Пароль:", font=("Arial", 12)).pack(pady=5)
password_entry_login = tk.Entry(login_frame, show="*", width=30, font=("Arial", 12)) # show="*" скрывает пароль
password_entry_login.pack(pady=10)

login_button = tk.Button(login_frame, text="Войти", command=handle_login, width=15, height=2, font=("Arial", 12))
login_button.pack(pady=10)

go_to_register_button = tk.Button(login_frame, text="Зарегистрироваться", command=lambda: show_frame(register_frame), width=20, font=("Arial", 10))
go_to_register_button.pack(pady=5)

# --- Виджеты для экрана регистрации ---
register_label_reg = tk.Label(register_frame, text="Регистрация", font=("Arial", 16, "bold"))
# Увеличиваем columnspan т.к. добавилась колонка для подсказки даты
register_label_reg.grid(row=0, column=0, columnspan=3, pady=15, sticky="n")

# Используем grid для лучшего выравнивания
# Добавляем отдельные поля для Фамилии, Имени, Отчества
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
tk.Label(register_frame, text="(ДД.ММ.ГГГГ)", font=("Arial", 9)).grid(row=current_row, column=2, padx=2, pady=5, sticky="w") # Подсказка формата
current_row += 1

tk.Label(register_frame, text="Пол*:", font=("Arial", 11)).grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
gender_var = tk.StringVar(value="") # Переменная для хранения выбранного пола
gender_frame = tk.Frame(register_frame) # Фрейм для Radiobutton
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
# Убираем show="*" чтобы пароль был виден при регистрации
password_entry_reg = tk.Entry(register_frame, width=30, font=("Arial", 11))
password_entry_reg.grid(row=current_row, column=1, padx=5, pady=5)
current_row += 1

tk.Label(register_frame, text="Подтвердите пароль*:", font=("Arial", 11)).grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
# Убираем show="*" чтобы пароль был виден при регистрации
password_confirm_entry_reg = tk.Entry(register_frame, width=30, font=("Arial", 11))
password_confirm_entry_reg.grid(row=current_row, column=1, padx=5, pady=5)
current_row += 1

# Добавляем пояснение про звездочку
tk.Label(register_frame, text="* - обязательные поля", font=("Arial", 9)).grid(row=current_row, column=0, columnspan=3, padx=5, pady=10, sticky="w")
current_row += 1


register_button_reg = tk.Button(register_frame, text="Зарегистрироваться", command=handle_register, width=20, height=2, font=("Arial", 12))
# Увеличиваем columnspan т.к. добавилась колонка для подсказки даты
register_button_reg.grid(row=current_row, column=0, columnspan=3, pady=15)
current_row += 1

go_to_login_button = tk.Button(register_frame, text="Уже есть аккаунт? Войти", command=lambda: show_frame(login_frame), width=25, font=("Arial", 10))
# Увеличиваем columnspan т.к. добавилась колонка для подсказки даты
go_to_login_button.grid(row=current_row, column=0, columnspan=3, pady=5)

# --- Запуск приложения ---
# Если load_users вызовет ошибку (например, файла нет и создать не удалось),
# программа завершится здесь.
user_list = load_users(FILENAME)
print(f"Загружено {len(user_list)} пользователей из файла '{FILENAME}'.") # Оставим вывод в консоль для информации

show_frame(login_frame) # Показываем сначала экран входа
window.mainloop() # Запускаем главный цикл Tkinter
