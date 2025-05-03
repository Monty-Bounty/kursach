import base64

def xor_cipher(text, key):
  """Применяет XOR к тексту. Важно: работает с байтами!"""
  # Преобразуем текст и ключ в байты (используя utf-8)
  text_bytes = text.encode('utf-8')
  key_bytes = key.encode('utf-8')
  key_len = len(key_bytes)
  # Применяем XOR
  result_bytes = bytes([b ^ key_bytes[i % key_len] for i, b in enumerate(text_bytes)])
  return result_bytes # Возвращаем байты

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

# --- Пример использования для расшифровки ---

# Предположим, это ваш ключ (должен быть тем же, что и при шифровании)
XOR_KEY = "SimpleKey"

# Предположим, это закодированный пароль, который вы прочитали из файла users.data
encoded_password_from_file = "IwgeAw==" # Замените на реальный закодированный пароль

# Расшифровываем пароль
decoded_password = decode_password(encoded_password_from_file, XOR_KEY)

# Выводим результат
print(f"Закодированный пароль: {encoded_password_from_file}")
print(f"Расшифрованный пароль: {decoded_password}")

# Если вы зашифровали слово "password123" этим ключом,
# то после расшифровки вы снова получите "password123".


