from cryptography.fernet import Fernet

# Get key from the file
file = open('key.txt', 'rb')
key = file.read() # the key will be type bytes
file.close()

# open the file to encrypt
with open('testing_encrypt.txt', 'rb') as f:
    data = f.read()

fernet = Fernet(key)
encrypted = fernet.decrypt(data)


# Write the encrypted file
with open('testing_decrypt.txt', 'wb') as f:
    f.write(encrypted)
