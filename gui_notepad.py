import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, colorchooser
import secure_notepad as core
import cloud_utils
import json
import os
import bcrypt
from PIL import Image, ImageTk
import ai_utils


USER_FILE = "user.json"

BTN_COLOR = "#EFEBE9"
BTN_TEXT_COLOR = "#4E342E"

drive = cloud_utils.authenticate_drive()

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
    login_win.geometry("900x700")
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

    canvas.bind("<Configure>", resize_bg)

    button_frame = tk.Frame(login_win, bg=None)
    button_frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(button_frame, text="Welcome to Cozy Notepad", fg=BTN_TEXT_COLOR, font=("Helvetica", 18, "bold")).pack(pady=10)

    password_entry = tk.Entry(button_frame, show="*", width=25, font=("Helvetica", 12), bg="#f9f5f0", fg=BTN_TEXT_COLOR, relief="flat", highlightthickness=2, highlightbackground="#D7CCC8")
    password_entry.pack(pady=10)

    login_button = tk.Button(button_frame, text="Login", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Helvetica", 12, "bold"), width=15, relief="flat", highlightthickness=2, highlightbackground="#D7CCC8", command=try_login)
    login_button.pack(pady=15)

def open_main_menu(user_password):
    menu_win = tk.Tk()
    menu_win.title("Cozy Notepad")
    menu_win.geometry("900x700")
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

    canvas.bind("<Configure>", resize_bg)

    button_frame = tk.Frame(menu_win, bg=None)
    button_frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(button_frame, text="Cozy Notepad Menu", fg=BTN_TEXT_COLOR, font=("Helvetica", 18, "bold")).pack(pady=10)

    btn_style = {
        "bg": BTN_COLOR,
        "fg": BTN_TEXT_COLOR,
        "font": ("Helvetica", 12, "bold"),
        "width": 20,
        "relief": "flat",
        "highlightthickness": 2,
        "highlightbackground": "#D7CCC8",
    }

    buttons = [
        ("Create Note", lambda: build_note_editor(user_password, is_update=False)),
        ("Read Note", lambda: read_note_gui(user_password)),
        ("Update Note", lambda: build_note_editor(user_password, is_update=True)),
        ("Delete Note", lambda: delete_note_gui(user_password)),
        ("List Notes", lambda: list_notes_gui(user_password)),
        ("Upload to Cloud", upload_to_cloud),
        ("Download from Cloud", download_from_cloud),
        ("Exit", menu_win.destroy),
    ]

    for text, command in buttons:
        tk.Button(button_frame, text=text, command=command, **btn_style).pack(pady=5)

def build_note_editor(user_password, is_update=False):
    new_win = create_styled_window("Update Note" if is_update else "Create Note")

    editor_frame = tk.Frame(new_win, bg=None)
    editor_frame.place(relx=0.5, rely=0.5, anchor="center")

    title_entry = tk.Entry(editor_frame, width=30, font=("Helvetica", 14), bg="#f9f5f0", fg=BTN_TEXT_COLOR, relief="flat", highlightthickness=2, highlightbackground="#D7CCC8")
    title_entry.pack(pady=5)

    toolbar = tk.Frame(editor_frame, bg=None)
    toolbar.pack(pady=5)

    font_family_var = tk.StringVar(value="Helvetica")
    font_dropdown = tk.OptionMenu(toolbar, font_family_var, "Helvetica", "Arial", "Courier", "Times", "Comic Sans MS")
    font_dropdown.pack(side=tk.LEFT, padx=5)

    color_btn = tk.Button(toolbar, text="Font Color", command=lambda: choose_color())
    color_btn.pack(side=tk.LEFT, padx=5)

    bold_on = tk.BooleanVar()
    underline_on = tk.BooleanVar()

    bold_btn = tk.Checkbutton(toolbar, text="Bold", variable=bold_on)
    bold_btn.pack(side=tk.LEFT, padx=5)

    underline_btn = tk.Checkbutton(toolbar, text="Underline", variable=underline_on)
    underline_btn.pack(side=tk.LEFT, padx=5)

    content_text = scrolledtext.ScrolledText(editor_frame, width=60, height=15, font=("Helvetica", 12), bg="#f9f5f0", fg=BTN_TEXT_COLOR, relief="flat", highlightthickness=2, highlightbackground="#D7CCC8")
    content_text.pack(pady=10)
    grammar_btn = tk.Button(toolbar, text="Check Grammar", command=lambda: ai_utils.check_grammar(content_text))
    grammar_btn.pack(side=tk.LEFT, padx=5)
    auto_fix_btn = tk.Button(toolbar, text="Auto Fix", command=lambda: ai_utils.auto_fix_grammar(content_text))
    auto_fix_btn.pack(side=tk.LEFT, padx=5)
    summary_btn = tk.Button(toolbar, text="Summarize", command=lambda: ai_utils.show_summary_popup(content_text))
    summary_btn.pack(side=tk.LEFT, padx=5)

    record_btn = tk.Button(toolbar, text="Record Voice", command=lambda: ai_utils.record_and_transcribe(content_text))
    record_btn.pack(side=tk.LEFT, padx=5)

    file_btn = tk.Button(toolbar, text="Upload Audio", command=lambda: ai_utils.transcribe_file(content_text))
    file_btn.pack(side=tk.LEFT, padx=5)
    todo_btn = tk.Button(toolbar,
                         text="Extract To-Dos",
                         command=lambda: ai_utils.show_todo_extraction(content_text))
    todo_btn.pack(side=tk.LEFT, padx=5)

    def choose_color():
        color_code = colorchooser.askcolor(title="Choose font color")[1]
        if color_code:
            content_text.tag_configure("styled", foreground=color_code)

    def apply_style():
        current_font = (font_family_var.get(), 12, "bold" if bold_on.get() else "normal")
        if underline_on.get():
            current_font = (font_family_var.get(), 12, "bold underline" if bold_on.get() else "underline")
        content_text.tag_configure("styled", font=current_font)
        try:
            content_text.tag_add("styled", "sel.first", "sel.last")
        except tk.TclError:
            messagebox.showerror("Error", "Please select text to style.")

    style_btn = tk.Button(toolbar, text="Apply Style", command=apply_style)
    style_btn.pack(side=tk.LEFT, padx=5)

    def upload_image():
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")])
        if file_path:
            try:
                img = Image.open(file_path)
                img = img.resize((100, 100))
                img_tk = ImageTk.PhotoImage(img)
                content_text.image_create(tk.END, image=img_tk)
                content_text.image = img_tk  # Keep reference
            except Exception as e:
                messagebox.showerror("Error", str(e))

    upload_btn = tk.Button(toolbar, text="Upload Image", command=upload_image)
    upload_btn.pack(side=tk.LEFT, padx=5)

    def save_note():
        title = title_entry.get()
        content = content_text.get("1.0", tk.END).strip()
        if title and content:
            if is_update:
                core.update_note(title, content, user_password)
                messagebox.showinfo("Success", f"Note '{title}' updated.")
            else:
                core.create_note(title, content, user_password)
                messagebox.showinfo("Success", f"Note '{title}' created.")
            new_win.destroy()
        else:
            messagebox.showerror("Error", "Title and content cannot be empty.")

    action_text = "Update Note" if is_update else "Save Note"
    save_button = tk.Button(editor_frame, text=action_text, bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Helvetica", 12, "bold"), width=15, relief="flat", highlightthickness=2, highlightbackground="#D7CCC8", command=save_note)
    save_button.pack(pady=10)

def read_note_gui(user_password):
    new_win = create_styled_window("Read Note")
    title_entry, content_text, load_button = common_note_widgets(new_win, button_text="Load Note")

    def load_note():
        title = title_entry.get()
        notes = core.load_notes()
        if title in notes:
            try:
                text = core.decrypt_text(notes[title], user_password)
                content_text.delete("1.0", tk.END)
                content_text.insert(tk.END, text)
            except Exception:
                messagebox.showerror("Error", "Incorrect password or corrupted data.")
        else:
            messagebox.showerror("Error", "Note not found.")

    load_button.config(command=load_note)

def delete_note_gui(user_password):
    new_win = create_styled_window("Delete Note")
    title_entry = tk.Entry(new_win, width=30, font=("Helvetica", 14), bg="#f9f5f0", fg=BTN_TEXT_COLOR, relief="flat", highlightthickness=2, highlightbackground="#D7CCC8")
    title_entry.pack(pady=20)

    def delete_note():
        title = title_entry.get()
        if title:
            core.delete_note(title)
            messagebox.showinfo("Deleted", f"Note '{title}' deleted.")
            new_win.destroy()

    delete_button = tk.Button(new_win, text="Delete", bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Helvetica", 12, "bold"), width=15, relief="flat", highlightthickness=2, highlightbackground="#D7CCC8", command=delete_note)
    delete_button.pack(pady=20)

def list_notes_gui(user_password):
    new_win = create_styled_window("All Notes")
    notes = core.load_notes()
    content_text = scrolledtext.ScrolledText(new_win, width=50, height=25, font=("Helvetica", 12), bg="#f9f5f0", fg=BTN_TEXT_COLOR, relief="flat", highlightthickness=2, highlightbackground="#D7CCC8")
    content_text.pack(pady=10)

    if notes:
        titles = "\n".join(notes.keys())
        content_text.insert(tk.END, titles)
        content_text.config(state=tk.DISABLED)
    else:
        content_text.insert(tk.END, "No notes found.")

def create_styled_window(title):
    new_win = tk.Toplevel()
    new_win.title(title)
    new_win.geometry("900x700")
    new_win.resizable(True, True)

    original_image = Image.open("bg.jpg")
    canvas = tk.Canvas(new_win, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    def resize_bg(event):
        new_width = event.width
        new_height = event.height
        resized_image = original_image.resize((new_width, new_height))
        bg_photo = ImageTk.PhotoImage(resized_image)
        canvas.bg_photo = bg_photo
        canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    canvas.bind("<Configure>", resize_bg)
    return new_win

def common_note_widgets(win, button_text="Save"):
    title_entry = tk.Entry(win, width=30, font=("Helvetica", 14), bg="#f9f5f0", fg=BTN_TEXT_COLOR, relief="flat", highlightthickness=2, highlightbackground="#D7CCC8")
    title_entry.pack(pady=10)

    content_text = scrolledtext.ScrolledText(win, width=50, height=15, font=("Helvetica", 12), bg="#f9f5f0", fg=BTN_TEXT_COLOR, relief="flat", highlightthickness=2, highlightbackground="#D7CCC8")
    content_text.pack(pady=10)

    action_button = tk.Button(win, text=button_text, bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Helvetica", 12, "bold"), width=15, relief="flat", highlightthickness=2, highlightbackground="#D7CCC8")
    action_button.pack(pady=15)

    return title_entry, content_text, action_button

def upload_to_cloud():
    cloud_utils.upload_notes(drive)
    messagebox.showinfo("Cloud", "Notes uploaded to Google Drive!")

def download_from_cloud():
    cloud_utils.download_notes(drive)
    messagebox.showinfo("Cloud", "Notes downloaded from Google Drive!")

if __name__ == "__main__":
    if not os.path.exists(USER_FILE):
        print("No master password found. Run `secure_notepad.py` first in console mode to set it up.")
    else:
        root = tk.Tk()
        root.withdraw()
        show_login_screen(root)
        root.mainloop()
