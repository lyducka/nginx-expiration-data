import configparser
from cryptography.fernet import Fernet

# * Generate_key
def generate_key():
    key = Fernet.generate_key()
    with open('key.key', 'wb') as key_file:
        key_file.write(key)

# * Load_key
def load_key():
    with open('/home/workspace/key/key.key', 'rb') as key_file:
        key = key_file.read()
    return key

# * Encrypt_config to encrypted_config.ini
def encrypt_config(config_file, key):
    cipher_suite = Fernet(key)

    config = configparser.ConfigParser()
    config.read(config_file)

    encrypted_config = configparser.ConfigParser()
    for section in config.sections():
        encrypted_config.add_section(section)
        for option in config.options(section):
            value = config.get(section, option)
            encrypted_value = cipher_suite.encrypt(value.encode())
            encrypted_config.set(section, option, encrypted_value.decode())

    with open('encrypted_config.ini', 'w') as encrypted_file:
        encrypted_config.write(encrypted_file)

# * Decrypt_config
def decrypt_config(encrypted_file, key):
    cipher_suite = Fernet(key)

    encrypted_config = configparser.ConfigParser()
    encrypted_config.read(encrypted_file)

    config = configparser.ConfigParser()
    for section in encrypted_config.sections():
        config.add_section(section)
        for option in encrypted_config.options(section):
            encrypted_value = encrypted_config.get(section, option)
            decrypted_value = cipher_suite.decrypt(encrypted_value.encode())
            config.set(section, option, decrypted_value.decode())

    return config

# * Create key
# generate_key()

# * Load key
# key = load_key()

# * Encrypt config.ini
# encrypt_config('config.ini', key)

# * Decrypt config.ini
# decrypted_config = decrypt_config('encrypted_config.ini', key)
# print(decrypted_config.get('aliyun', 'access_key'))
# print(decrypted_config.get('aliyun', 'secret_key'))
# print(decrypted_config.get('aliyun', 'sign_name'))
# print(decrypted_config.get('aliyun', 'template_code'))