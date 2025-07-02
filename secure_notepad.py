import os
import json
import base64
import bcrypt
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

NOTES_FILE = "notes.json"
USER_FILE = "user.json"


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 32 bytes = 256 bits key
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def encrypt_text(text: str, password: str) -> dict:
    salt = os.urandom(16)
    iv = os.urandom(16)
    key = derive_key(password, salt)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    pad_len = 16 - len(text.encode()) % 16
    padded_text = text + chr(pad_len) * pad_len

    ct = encryptor.update(padded_text.encode()) + encryptor.finalize()
    return {
        'salt': base64.b64encode(salt).decode(),
        'iv': base64.b64encode(iv).decode(),
        'ciphertext': base64.b64encode(ct).decode()
    }

def decrypt_text(data: dict, password: str) -> str:
    salt = base64.b64decode(data['salt'])
    iv = base64.b64decode(data['iv'])
    ct = base64.b64decode(data['ciphertext'])
    key = derive_key(password, salt)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    padded_text = decryptor.update(ct) + decryptor.finalize()
    pad_len = padded_text[-1]
    return padded_text[:-pad_len].decode()


def load_notes():
    if not os.path.exists(NOTES_FILE):
        return {}
    with open(NOTES_FILE, "r") as f:
        return json.load(f)

def save_notes(notes):
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, indent=4)

def create_note(title, content, password):
    notes = load_notes()
    encrypted = encrypt_text(content, password)
    notes[title] = encrypted
    save_notes(notes)
    print(f"Note '{title}' created and encrypted.")

def read_note(title, password):
    notes = load_notes()
    if title in notes:
        try:
            decrypted = decrypt_text(notes[title], password)
            print(f"Content of '{title}':\n{decrypted}")
        except Exception:
            print("Incorrect password or corrupted data.")
    else:
        print("Note not found.")

def update_note(title, new_content, password):
    notes = load_notes()
    if title in notes:
        encrypted = encrypt_text(new_content, password)
        notes[title] = encrypted
        save_notes(notes)
        print(f"Note '{title}' updated.")
    else:
        print("Note not found.")

def delete_note(title):
    notes = load_notes()
    if title in notes:
        del notes[title]
        save_notes(notes)
        print(f"Note '{title}' deleted.")
    else:
        print("Note not found.")

def list_notes(password):
    notes = load_notes()
    if not notes:
        print("No notes found.")
        return

    # Verify password using first note
    sample_title = next(iter(notes))
    try:
        decrypt_text(notes[sample_title], password)
        print("\nYour Notes:")
        for title in notes.keys():
            print("- " + title)
    except Exception:
        print("Incorrect password. Cannot list notes.")


def set_master_password():
    password = input("Create a master password: ")
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    with open(USER_FILE, "w") as f:
        json.dump({"password": hashed.decode()}, f)
    print("Master password set successfully.")

def verify_master_password():
    if not os.path.exists(USER_FILE):
        print("No master password found. Let's set it up first.")
        set_master_password()

    with open(USER_FILE, "r") as f:
        data = json.load(f)
        stored_hash = data["password"].encode()

    for attempt in range(3):
        password = input("Enter your master password: ")
        if bcrypt.checkpw(password.encode(), stored_hash):
            print("Access granted.")
            return password
        else:
            print("Incorrect password.")
    print("Too many failed attempts. Exiting.")
    exit()

def change_master_password():
    with open(USER_FILE, "r") as f:
        data = json.load(f)
        stored_hash = data["password"].encode()

    current_password = input("Enter your current master password: ")

    if not bcrypt.checkpw(current_password.encode(), stored_hash):
        print("Incorrect current password. Cannot change.")
        return

    new_password = input("Enter new master password: ")
    confirm_password = input("Confirm new master password: ")

    if new_password != confirm_password:
        print("New passwords do not match. Try again.")
        return


    new_hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
    with open(USER_FILE, "w") as f:
        json.dump({"password": new_hashed.decode()}, f)
    print("Master password changed successfully.")


    reencrypt_all_notes(current_password, new_password)

    def reencrypt_all_notes(old_password, new_password):
        notes = load_notes()
        updated_notes = {}

        for title, data in notes.items():
            try:

                plain_text = decrypt_text(data, old_password)

                new_encrypted = encrypt_text(plain_text, new_password)
                updated_notes[title] = new_encrypted
            except Exception:
                print(f"Warning: Could not decrypt note '{title}'. Skipping.")
                updated_notes[title] = data

        save_notes(updated_notes)
        print("All notes have been re-encrypted with the new password.")




