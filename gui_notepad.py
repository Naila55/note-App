import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import secure_notepad as core
import json
import os
import bcrypt
from PIL import Image, ImageTk

USER_FILE = "user.json"

BTN_COLOR = "#EFEBE9"      # Creamy button color
BTN_TEXT_COLOR = "#4E342E" # Dark brown text

def show_login_screen(root):
    def try_login():
        entered_password = password_entry.get()
        with open(USER_FILE, "r") as f:
            data = json.load(f)
            stored_hash = data["password"].encode()

        if bcrypt.checkpw(entered_password.encode(), stored_hash):
            messagebox.showinfo("Success", "Login successful!")
            root.destroy()
            open_main_menu(entered_password)
        else:
            messagebox.showerror("Error", "Incorrect password.")

    login_win = tk.Toplevel(root)
    login_win.title("Cozy Login")
    login_win.geometry("500x400")
    login_win.resizable(True, True)

    original_image = Image.open("bg.jpg")

    canvas = tk.Canvas(login_win, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    def resize_bg(event):
        new_width = event.width
        new_height = event.height
        resized_image = original_image.resize((new_width, new_height))
        bg_photo = ImageTk.PhotoImage(resized_image)
        canvas.bg_photo = bg_photo
        canvas.create_image(0, 0, image=bg_photo, anchor="nw")

        # Center widgets dynamically
        canvas.coords(text_window, event.width // 2, event.height // 2 - 80)
        canvas.coords(entry_window, event.width // 2, event.height // 2 - 20)
        canvas.coords(button_window, event.width // 2, event.height // 2 + 40)

    canvas.bind("<Configure>", resize_bg)

    text_window = canvas.create_text(250, 50, text="Welcome to Cozy Notepad", font=("Helvetica", 18, "bold"), fill=BTN_TEXT_COLOR)

    password_entry = tk.Entry(login_win, show="*", width=25, bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Helvetica", 12), relief="flat", highlightthickness=2, highlightbackground=BTN_TEXT_COLOR)
    entry_window = canvas.create_window(250, 150, window=password_entry)

    login_button = tk.Button(login_win, text="Login", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Helvetica", 12, "bold"), width=15, relief="flat", highlightthickness=2, highlightbackground=BTN_TEXT_COLOR, command=try_login)
    button_window = canvas.create_window(250, 220, window=login_button)

def open_main_menu(user_password):
    menu_win = tk.Tk()
    menu_win.title("Cozy Notepad")
    menu_win.geometry("500x600")
    menu_win.resizable(True, True)

    original_image = Image.open("bg.jpg")

    canvas = tk.Canvas(menu_win, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    def resize_bg(event):
        new_width = event.width
        new_height = event.height
        resized_image = original_image.resize((new_width, new_height))
        bg_photo = ImageTk.PhotoImage(resized_image)
        canvas.bg_photo = bg_photo
        canvas.create_image(0, 0, image=bg_photo, anchor="nw")

        # Center title text
        canvas.coords(text_window, event.width // 2, event.height // 2 - (len(button_windows) * 30) - 40)

        # Center buttons
        num_buttons = len(button_windows)
        total_height = num_buttons * 60
        start_y = (event.height // 2) - (total_height // 2) + 40

        for i, w in enumerate(button_windows):
            canvas.coords(w, event.width // 2, start_y + i * 60)
            canvas.lift(w)

    canvas.bind("<Configure>", resize_bg)

    text_window = canvas.create_text(250, 40, text="Cozy Notepad Menu", font=("Helvetica", 18, "bold"), fill=BTN_TEXT_COLOR)

    btn_style = {"bg": BTN_COLOR, "fg": BTN_TEXT_COLOR, "font": ("Helvetica", 12, "bold"), "width": 20, "relief": "flat", "highlightthickness": 2, "highlightbackground": BTN_TEXT_COLOR}

    button_windows = []

    def create_note_gui():
        title = simpledialog.askstring("Create Note", "Enter title:")
        content = simpledialog.askstring("Create Note", "Enter content:")
        if title and content:
            core.create_note(title, content, user_password)
            messagebox.showinfo("Success", f"Note '{title}' created.")

    def read_note_gui():
        title = simpledialog.askstring("Read Note", "Enter title:")
        if title:
            notes = core.load_notes()
            if title in notes:
                try:
                    text = core.decrypt_text(notes[title], user_password)
                    text_win = tk.Toplevel(menu_win)
                    text_win.title(title)
                    st = scrolledtext.ScrolledText(text_win, width=50, height=20, bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Helvetica", 12))
                    st.pack()
                    st.insert(tk.END, text)
                    st.config(state=tk.DISABLED)
                except Exception:
                    messagebox.showerror("Error", "Incorrect password or corrupted data.")
            else:
                messagebox.showerror("Error", "Note not found.")

    def update_note_gui():
        title = simpledialog.askstring("Update Note", "Enter title:")
        new_content = simpledialog.askstring("Update Note", "Enter new content:")
        if title and new_content:
            core.update_note(title, new_content, user_password)
            messagebox.showinfo("Success", f"Note '{title}' updated.")

    def delete_note_gui():
        title = simpledialog.askstring("Delete Note", "Enter title:")
        if title:
            core.delete_note(title)
            messagebox.showinfo("Deleted", f"Note '{title}' deleted.")

    def list_notes_gui():
        notes = core.load_notes()
        if not notes:
            messagebox.showinfo("List Notes", "No notes found.")
            return
        try:
            sample_title = next(iter(notes))
            core.decrypt_text(notes[sample_title], user_password)
            titles = "\n".join(notes.keys())
            text_win = tk.Toplevel(menu_win)
            text_win.title("All Notes")
            st = scrolledtext.ScrolledText(text_win, width=50, height=20, bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Helvetica", 12))
            st.pack()
            st.insert(tk.END, titles)
            st.config(state=tk.DISABLED)
        except Exception:
            messagebox.showerror("Error", "Incorrect password. Cannot list notes.")

    buttons = [
        ("Create Note", create_note_gui),
        ("Read Note", read_note_gui),
        ("Update Note", update_note_gui),
        ("Delete Note", delete_note_gui),
        ("List Notes", list_notes_gui),
        ("Exit", menu_win.destroy),
    ]

    for i, (text, command) in enumerate(buttons):
        btn = tk.Button(menu_win, text=text, command=command, **btn_style)
        w = canvas.create_window(250, 100 + i * 60, window=btn)
        button_windows.append(w)

    menu_win.mainloop()

if __name__ == "__main__":
    if not os.path.exists(USER_FILE):
        print("No master password found. Run `secure_notepad.py` first in console mode to set it up.")
    else:
        root = tk.Tk()
        root.withdraw()
        show_login_screen(root)
        root.mainloop()
