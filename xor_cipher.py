import base64

def xor_base64_cipher(text_to_process, key, action='encode'):
    """
    Шифрует или дешифрует текст, используя XOR, а затем Base64.
    Упрощенная версия без try-except.

    :param text_to_process: Строка для шифрования или строка Base64 для дешифрования.
    :param key: Ключ для операции XOR (строка).
    :param action: 'encode' для шифрования, 'decode' для дешифрования.
    :return: Зашифрованная строка Base64 или расшифрованная исходная строка.
             Вернет None или вызовет ошибку, если действие некорректно или данные неверны.
    """
    # Преобразуем ключ в байты один раз
    key_bytes = key.encode('utf-8')
    key_len = len(key_bytes)

    if action == 'encode':
        # 1. Преобразовать исходный текст в байты
        text_bytes = text_to_process.encode('utf-8')

        # 2. Применить XOR. Создаем список байтов результата XOR
        xor_result_bytes_list = []
        for i, b in enumerate(text_bytes):
            xor_result_bytes_list.append(b ^ key_bytes[i % key_len])
        xor_result_bytes = bytes(xor_result_bytes_list) # Преобразуем список в байтовую строку

        # 3. Закодировать результат XOR в Base64
        base64_encoded_bytes = base64.b64encode(xor_result_bytes)

        # 4. Преобразовать байты Base64 в строку для возврата
        return base64_encoded_bytes.decode('utf-8')

    elif action == 'decode':
        # 1. Преобразовать строку Base64 (которая является text_to_process) в байты
        base64_to_decode_bytes = text_to_process.encode('utf-8')

        # 2. Декодировать из Base64 (результат - байты после XOR)
        # Если text_to_process не является корректной Base64 строкой, здесь будет ошибка.
        xor_result_bytes_after_b64decode = base64.b64decode(base64_to_decode_bytes)

        # 3. Применить XOR еще раз к результату (байты)
        # Создаем список байтов результата XOR
        original_bytes_list = []
        for i, b in enumerate(xor_result_bytes_after_b64decode):
            original_bytes_list.append(b ^ key_bytes[i % key_len])
        original_bytes_after_xor = bytes(original_bytes_list) # Преобразуем список в байтовую строку

        # 4. Преобразовать исходные байты обратно в строку
        # Если байты не являются корректной UTF-8 последовательностью, здесь будет ошибка.
        return original_bytes_after_xor.decode('utf-8')
    else:
        print(f"Ошибка: Некорректное действие '{action}'. Используйте 'encode' или 'decode'.")
        return None 

if __name__ == "__main__":
    my_secret_text = "Это мой секретный пароль! 123 @#$%^"
    my_key = "ОченьСложныйКлюч"

    print(f"Исходный текст: {my_secret_text}")
    print(f"Ключ: {my_key}\n")

    # Шифрование
    encrypted_text = xor_base64_cipher(my_secret_text, my_key, action='encode')
    if encrypted_text: # Проверяем, что шифрование вернуло результат
        print(f"Зашифрованный текст (XOR + Base64): {encrypted_text}")

        # Дешифрование
        decrypted_text = xor_base64_cipher(encrypted_text, my_key, action='decode')
        if decrypted_text: # Проверяем, что дешифрование вернуло результат
            print(f"Расшифрованный текст: {decrypted_text}\n")

            if my_secret_text == decrypted_text:
                print("Проверка: Шифрование и дешифрование прошли успешно!")
            else:
                print("Проверка: Ошибка! Исходный и расшифрованный тексты не совпадают.")
        else:
            print("Ошибка при дешифровании.")
    else:
        print("Ошибка при шифровании.")

