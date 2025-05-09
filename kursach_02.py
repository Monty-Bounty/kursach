import csv # Модуль для работы с CSV файлами (хранение данных пользователей)
import tkinter as tk # Модуль для создания графического интерфейса пользователя (GUI)
from tkinter import messagebox # Модуль для отображения стандартных диалоговых окон (сообщения, ошибки)

# --- Константы и глобальные переменные ---
FILENAME = "users.data" # Имя файла для хранения данных пользователей. Файл будет в папке запуска скрипта.
XOR_KEY = "SimpleKey"   # Простой ключ для XOR "шифрования". В реальных системах использовать нельзя!
user_list = []          # Глобальный список для хранения данных всех пользователей в памяти.
current_logged_in_user = None # Переменная для хранения данных текущего вошедшего пользователя.

# --- Функции для работы с данными ---

def xor_cipher(text, key):
  """
  Кодирует или декодирует текст с помощью битовой операции XOR.
  Принимает строку 'text' и строку 'key'.
  Возвращает строку, являющуюся результатом операции XOR.
  Внимание: результат может содержать непечатные символы,
  так как операция XOR применяется к кодам символов.
  """
  # Если ключ короче текста, он будет циклически повторяться.
  repeated_key = (key * (len(text) // len(key) + 1))[:len(text)]
  # Применяем операцию XOR к кодам Unicode каждого символа текста и ключа.
  # ord(char) - возвращает Unicode код символа.
  # chr(code) - возвращает символ по его Unicode коду.
  # ^ - оператор XOR.
  result = ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(text, repeated_key))
  return result

def load_users(filename):
  """
  Загружает список пользователей из указанного файла.
  Если файл не существует, он будет создан при первой попытке записи (режим 'a+').
  """
  users = [] # Локальный список для загруженных пользователей
  # Открываем файл в режиме 'a+' (добавление и чтение).
  # Файл создается, если не существует.
  # newline='' и encoding='utf-8' важны для корректной работы с CSV и кириллицей.
  with open(filename, 'a+', newline='', encoding='utf-8') as file:
      file.seek(0) # Перемещаем курсор в начало файла для чтения существующих записей.
      reader = csv.reader(file, delimiter=';') # Создаем объект для чтения CSV, разделитель - точка с запятой.
      for row in reader: # Читаем файл построчно
          if row and len(row) == 9: # Проверяем, что строка не пустая и содержит 9 полей
              # Создаем словарь с данными пользователя
              user_data = {
                  "last_name": row[0],
                  "first_name": row[1],
                  "middle_name": row[2],
                  "birth_date": row[3],
                  "gender": row[4],
                  "city": row[5],
                  "email": row[6],
                  "login": row[7],
                  "password_xor_encoded": row[8] # Пароль хранится в "зашифрованном" XOR виде
              }
              users.append(user_data) # Добавляем пользователя в список
  return users


def save_users(users, filename):
  """
  Сохраняет текущий список пользователей в указанный файл.
  Файл перезаписывается при каждом сохранении (режим 'w').
  """
  # Открываем файл в режиме 'w' (запись). Если файл существует, он будет перезаписан.
  with open(filename, 'w', newline='', encoding='utf-8') as file:
      writer = csv.writer(file, delimiter=';') # Создаем объект для записи CSV.
      for user_data_item in users: # Проходим по каждому пользователю в списке
          # Записываем данные пользователя в файл одной строкой
          writer.writerow([
              user_data_item["last_name"],
              user_data_item["first_name"],
              user_data_item["middle_name"],
              user_data_item["birth_date"],
              user_data_item["gender"],
              user_data_item["city"],
              user_data_item["email"],
              user_data_item["login"],
              user_data_item["password_xor_encoded"] # Сохраняем XOR "зашифрованный" пароль
          ])


def find_user_by_login(users_list_to_search, login_to_find):
  """
  Ищет пользователя в предоставленном списке по логину.
  Возвращает словарь с данными пользователя, если найден, иначе None.
  """
  for user_data_item in users_list_to_search:
    if user_data_item["login"] == login_to_find:
      return user_data_item # Пользователь найден
  return None # Пользователь не найден

# --- Функции для GUI (Графического Интерфейса Пользователя) ---

def clear_entries(entries_list_to_clear):
    """Очищает содержимое полей ввода (tk.Entry) из предоставленного списка."""
    for entry_widget in entries_list_to_clear:
        if isinstance(entry_widget, tk.Entry): # Проверяем, что это поле ввода
            entry_widget.delete(0, tk.END) # Удаляем текст от начала (0) до конца (END)
    # Специальная очистка для Radiobutton выбора пола
    if 'gender_var' in globals() and isinstance(gender_var, tk.StringVar):
        gender_var.set("") # Сбрасываем значение переменной, управляющей Radiobutton

def show_frame(frame_to_display):
    """
    Показывает указанный фрейм (экран) и скрывает все остальные основные фреймы.
    """
    login_frame.pack_forget()      # Скрываем фрейм входа
    register_frame.pack_forget()   # Скрываем фрейм регистрации
    user_info_frame.pack_forget()  # Скрываем фрейм информации о пользователе
    # Отображаем нужный фрейм, растягивая его на все доступное пространство
    frame_to_display.pack(fill="both", expand=True, padx=20, pady=20)

def display_user_info(user_data_to_display):
    """
    Заполняет и отображает экран с информацией о вошедшем пользователе.
    """
    global current_logged_in_user # Обращаемся к глобальной переменной
    current_logged_in_user = user_data_to_display # Сохраняем данные вошедшего пользователя

    # Очищаем предыдущие метки с данными пользователя, если они были
    # Это нужно, чтобы при повторном входе информация не дублировалась
    for widget in user_info_display_frame.winfo_children(): # Получаем всех потомков фрейма
        # Удаляем только те метки, которые мы пометили как 'is_data_label'
        if isinstance(widget, tk.Label) and hasattr(widget, 'is_data_label'):
            widget.destroy()

    # Список кортежей: (Текст метки, Значение из данных пользователя)
    info_labels_config = [
        ("Фамилия:", user_data_to_display.get("last_name", "N/A")),
        ("Имя:", user_data_to_display.get("first_name", "N/A")),
        ("Отчество:", user_data_to_display.get("middle_name", "N/A") or "Отсутствует"),
        ("Дата рождения:", user_data_to_display.get("birth_date", "N/A")),
        ("Пол:", user_data_to_display.get("gender", "N/A")),
        ("Город:", user_data_to_display.get("city", "N/A")),
        ("Email:", user_data_to_display.get("email", "N/A")),
        ("Логин:", user_data_to_display.get("login", "N/A")),
    ]

    # Динамически создаем и размещаем метки с информацией
    for i, (text, value) in enumerate(info_labels_config):
        # Метка с названием поля
        label_text = tk.Label(user_info_display_frame, text=text, font=("Arial", 11), anchor="w")
        label_text.grid(row=i, column=0, padx=5, pady=2, sticky="w") # Размещаем в сетке
        label_text.is_data_label = True # Помечаем метку для последующей очистки

        # Метка со значением поля
        label_value = tk.Label(user_info_display_frame, text=value, font=("Arial", 11, "bold"), anchor="w")
        label_value.grid(row=i, column=1, padx=5, pady=2, sticky="w")
        label_value.is_data_label = True # Помечаем метку

    show_frame(user_info_frame) # Показываем фрейм с информацией


def handle_login():
    """Обрабатывает нажатие кнопки 'Войти'."""
    login_attempt = login_entry_login.get() # Получаем введенный логин
    password_attempt = password_entry_login.get() # Получаем введенный пароль

    # Проверка, что поля не пустые
    if not login_attempt or not password_attempt:
        messagebox.showerror("Ошибка входа", "Пожалуйста, введите логин и пароль.")
        return

    # Ищем пользователя по логину
    user_account = find_user_by_login(user_list, login_attempt)

    if user_account: # Если пользователь найден
        # "Дешифруем" сохраненный пароль (применяем XOR еще раз)
        stored_password_decoded = xor_cipher(user_account["password_xor_encoded"], XOR_KEY)

        if password_attempt == stored_password_decoded: # Сравниваем пароли
            # Формируем имя для приветствия
            user_name_for_greeting = user_account.get('first_name', 'Пользователь')
            if user_account.get('last_name'):
                 user_name_for_greeting = f"{user_account.get('first_name', '')} {user_account.get('last_name', '')}".strip()
            
            # Показываем сообщение об успешном входе
            messagebox.showinfo("Успешный вход", f"Добро пожаловать, {user_name_for_greeting}!")
            
            clear_entries([login_entry_login, password_entry_login]) # Очищаем поля ввода
            display_user_info(user_account) # Показываем информацию о пользователе
        else:
            messagebox.showerror("Ошибка входа", "Неверный пароль.") # Пароли не совпали
    else:
        messagebox.showerror("Ошибка входа", "Пользователь с таким логином не найден.") # Пользователь не найден

def handle_register():
    """Обрабатывает нажатие кнопки 'Зарегистрироваться' на форме регистрации."""
    # Получаем данные из всех полей ввода на форме регистрации
    last_name = last_name_entry_reg.get()
    first_name = first_name_entry_reg.get()
    middle_name = middle_name_entry_reg.get()
    birth_date = birth_date_entry_reg.get()
    gender = gender_var.get() # Значение из Radiobutton
    city = city_entry_reg.get()
    email = email_entry_reg.get()
    login = login_entry_reg.get()
    password = password_entry_reg.get()
    password_confirm = password_confirm_entry_reg.get()

    # Проверка на заполненность обязательных полей
    if not all([last_name, first_name, birth_date, gender, city, email, login, password, password_confirm]):
        messagebox.showerror("Ошибка регистрации", "Пожалуйста, заполните все обязательные поля (кроме Отчества).")
        return

    # Проверка совпадения паролей
    if password != password_confirm:
        messagebox.showerror("Ошибка регистрации", "Пароли не совпадают.")
        return

    # Проверка, не занят ли логин
    if find_user_by_login(user_list, login):
        messagebox.showerror("Ошибка регистрации", f"Пользователь с логином '{login}' уже существует.")
        return

    # "Шифрование" пароля с помощью XOR
    password_xor_encoded = xor_cipher(password, XOR_KEY)

    # Создание словаря с данными нового пользователя
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

    user_list.append(new_user) # Добавляем нового пользователя в общий список
    save_users(user_list, FILENAME) # Сохраняем обновленный список в файл

    messagebox.showinfo("Успешная регистрация", "Пользователь успешно зарегистрирован!")
    # Очищаем все поля на форме регистрации
    clear_entries([
        last_name_entry_reg, first_name_entry_reg, middle_name_entry_reg,
        birth_date_entry_reg, city_entry_reg,
        email_entry_reg, login_entry_reg, password_entry_reg,
        password_confirm_entry_reg
    ])
    gender_var.set("") # Сброс выбора пола
    show_frame(login_frame) # Переход на экран входа

def handle_logout():
    """Обрабатывает нажатие кнопки 'Выйти' на экране информации о пользователе."""
    global current_logged_in_user
    current_logged_in_user = None # Сбрасываем данные о вошедшем пользователе
    show_frame(login_frame) # Показываем экран входа


# --- Основная функция для настройки GUI и запуска приложения ---
def main():
    # Объявляем глобальными переменные, которые используются в других функциях (обработчиках)
    # Это необходимо, так как эти виджеты и списки создаются в main(),
    # а используются в функциях, вызываемых по событиям.
    global window, login_frame, register_frame, user_info_frame, user_info_display_frame
    global login_entry_login, password_entry_login
    global last_name_entry_reg, first_name_entry_reg, middle_name_entry_reg
    global birth_date_entry_reg, gender_var, city_entry_reg, email_entry_reg
    global login_entry_reg, password_entry_reg, password_confirm_entry_reg
    global user_list # user_list загружается здесь и используется глобально

    # --- Создание главного окна ---
    window = tk.Tk()
    window.title("Система регистрации и входа (Простой XOR)")
    window.geometry("450x650") # Устанавливаем размер окна

    # --- Создание основных фреймов (экранов) ---
    login_frame = tk.Frame(window)      # Фрейм для экрана входа
    register_frame = tk.Frame(window)   # Фрейм для экрана регистрации
    user_info_frame = tk.Frame(window)  # Фрейм для отображения информации о пользователе

    # --- Виджеты для экрана входа (login_frame) ---
    login_label_login = tk.Label(login_frame, text="Вход в систему", font=("Arial", 16, "bold"))
    login_label_login.pack(pady=20) # pack - менеджер геометрии, размещает виджеты друг под другом
    
    tk.Label(login_frame, text="Логин:", font=("Arial", 12)).pack(pady=5)
    login_entry_login = tk.Entry(login_frame, width=30, font=("Arial", 12))
    login_entry_login.pack(pady=5)
    
    tk.Label(login_frame, text="Пароль:", font=("Arial", 12)).pack(pady=5)
    password_entry_login = tk.Entry(login_frame, show="*", width=30, font=("Arial", 12)) # show="*" скрывает вводимые символы
    password_entry_login.pack(pady=10)
    
    login_button = tk.Button(login_frame, text="Войти", command=handle_login, width=15, height=2, font=("Arial", 12))
    login_button.pack(pady=10)
    
    go_to_register_button = tk.Button(login_frame, text="Зарегистрироваться", command=lambda: show_frame(register_frame), width=20, font=("Arial", 10))
    go_to_register_button.pack(pady=5)

    # --- Виджеты для экрана регистрации (register_frame) ---
    # Используем grid - менеджер геометрии, который размещает виджеты в виде таблицы (строки и столбцы)
    register_label_reg = tk.Label(register_frame, text="Регистрация", font=("Arial", 16, "bold"))
    register_label_reg.grid(row=0, column=0, columnspan=3, pady=15, sticky="n") # columnspan=3 - занять 3 колонки
    
    current_row = 1 # Переменная для отслеживания текущей строки в grid
    # Поля для ФИО
    tk.Label(register_frame, text="Фамилия*:", font=("Arial", 11)).grid(row=current_row, column=0, padx=5, pady=5, sticky="w") # sticky="w" - прижать к западу (левому краю)
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
    
    # Остальные поля
    tk.Label(register_frame, text="Дата рождения*:", font=("Arial", 11)).grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
    birth_date_entry_reg = tk.Entry(register_frame, width=30, font=("Arial", 11))
    birth_date_entry_reg.grid(row=current_row, column=1, padx=5, pady=5)
    tk.Label(register_frame, text="(ДД.ММ.ГГГГ)", font=("Arial", 9)).grid(row=current_row, column=2, padx=2, pady=5, sticky="w") # Подсказка формата
    current_row += 1
    
    tk.Label(register_frame, text="Пол*:", font=("Arial", 11)).grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
    gender_var = tk.StringVar(value="") # Переменная для хранения значения Radiobutton
    gender_frame_ui = tk.Frame(register_frame) # Фрейм для группировки Radiobutton
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
    password_entry_reg = tk.Entry(register_frame, width=30, font=("Arial", 11)) # Пароль виден при регистрации
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

    # --- Виджеты для экрана информации о пользователе (user_info_frame) ---
    user_info_label = tk.Label(user_info_frame, text="Личный кабинет", font=("Arial", 16, "bold"))
    user_info_label.pack(pady=15)

    user_info_display_frame = tk.Frame(user_info_frame) # Внутренний фрейм для динамического размещения меток с данными
    user_info_display_frame.pack(pady=10, padx=10, fill="x")

    logout_button = tk.Button(user_info_frame, text="Выйти", command=handle_logout, width=15, height=2, font=("Arial", 12))
    logout_button.pack(pady=20)

    # --- Загрузка пользователей и запуск главного цикла приложения ---
    user_list = load_users(FILENAME) # Загружаем пользователей из файла
    print(f"Загружено {len(user_list)} пользователей из файла '{FILENAME}'.") # Информационное сообщение в консоль

    show_frame(login_frame) # Показываем начальный экран (вход)
    window.mainloop() # Запускаем главный цикл обработки событий Tkinter

# --- Точка входа в программу ---
# Этот блок гарантирует, что функция main() будет вызвана только тогда,
# когда скрипт запускается напрямую (а не импортируется как модуль).
if __name__ == "__main__":
    main()
