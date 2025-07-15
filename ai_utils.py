


import language_tool_python
import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
import config


def check_grammar(textbox):
    """
    Check grammar and spelling, show suggestions in a popup.
    """
    tool = language_tool_python.LanguageTool('en-US')
    text = textbox.get("1.0", tk.END)
    matches = tool.check(text)

    if not matches:
        messagebox.showinfo("Grammar Check", "No errors found. Great job!")
    else:
        issues = ""
        for match in matches:
            issues += f"• {match.context}\n→ {match.message}\n\n"

        grammar_win = tk.Toplevel()
        grammar_win.title("Grammar Suggestions")
        grammar_win.geometry("600x400")

        suggestion_text = scrolledtext.ScrolledText(grammar_win, wrap=tk.WORD, font=("Helvetica", 12))
        suggestion_text.pack(fill=tk.BOTH, expand=True)
        suggestion_text.insert(tk.END, issues)
        suggestion_text.config(state=tk.DISABLED)



def auto_fix_grammar(textbox):
    """
    Automatically correct grammar and spelling directly in the textbox.
    The corrected text will remain in the textbox for review before saving.
    """
    tool = language_tool_python.LanguageTool('en-US')
    text = textbox.get("1.0", tk.END)
    matches = tool.check(text)

    fixed_text = language_tool_python.utils.correct(text, matches)


    textbox.delete("1.0", tk.END)
    textbox.insert(tk.END, fixed_text)
    messagebox.showinfo("Auto Fix", "Grammar and spelling issues have been auto-corrected!\nPlease review before clicking Save.")





HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
HF_API_TOKEN = config.HF_API_TOKEN

headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

def summarize_text(text):
    payload = {
        "inputs": text,
        "parameters": {"max_length": 130, "min_length": 30, "do_sample": False},
    }
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        summary = response.json()[0]['summary_text']
        return summary
    else:
        return "Error: Unable to summarize. Check API or token."

def show_summary_popup(textbox):
    text = textbox.get("1.0", tk.END)
    summary = summarize_text(text)
    summary_win = tk.Toplevel()
    summary_win.title("Smart Summary")
    summary_win.geometry("600x300")

    summary_text = scrolledtext.ScrolledText(summary_win, wrap=tk.WORD, font=("Helvetica", 12))
    summary_text.pack(fill=tk.BOTH, expand=True)
    summary_text.insert(tk.END, summary)
    summary_text.config(state=tk.DISABLED)


import speech_recognition as sr
from tkinter import messagebox, filedialog



def record_and_transcribe(textbox):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            messagebox.showinfo("Recording", "Start speaking now...")
            audio = recognizer.listen(source)
        text = recognizer.recognize_google(audio)
        textbox.insert(tk.END, text + "\n")
        messagebox.showinfo("Success", "Recorded voice transcribed and inserted!")
    except sr.UnknownValueError:
        messagebox.showerror("Error", "Could not understand audio.")
    except sr.RequestError:
        messagebox.showerror("Error", "Could not connect to service.")


def transcribe_file(textbox):
    recognizer = sr.Recognizer()
    audio_path = filedialog.askopenfilename(
        title="Select Audio File",
        filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
    )
    if not audio_path:
        return

    try:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        textbox.insert(tk.END, text + "\n")
        messagebox.showinfo("Success", "File transcribed and inserted!")
    except sr.UnknownValueError:
        messagebox.showerror("Error", "Could not understand audio.")
    except sr.RequestError:
        messagebox.showerror("Error", "Could not connect to service.")




HF_NLI_URL   = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
HF_API_TOKEN = config.HF_API_TOKEN
HF_HEADERS   = {"Authorization": f"Bearer {HF_API_TOKEN}"}

def extract_todo_items(text):
    """
    Splits the note into sentences, classifies each as 'task' or 'other',
    and returns only the ones labeled 'task'.
    """
    # crude sentence splitter—you can improve later
    sentences = [s.strip() for s in text.split(".") if s.strip()]
    tasks = []
    for sent in sentences:
        payload = {
            "inputs": sent,
            "parameters": {"candidate_labels": ["task", "other"]},
        }
        resp = requests.post(HF_NLI_URL, headers=HF_HEADERS, json=payload)
        if resp.status_code != 200:
            continue
        result = resp.json()
        # Hugging Face returns labels sorted by score:
        if result["labels"][0] == "task":
            tasks.append(sent)
    return tasks

def show_todo_extraction(textbox):
    """
    Reads all text from the editor, extracts to-dos, and shows them in a popup.
    """
    full_text = textbox.get("1.0", tk.END)
    tasks = extract_todo_items(full_text)

    todo_win = tk.Toplevel()
    todo_win.title("🔖 Extracted To-Dos")
    todo_win.geometry("400x300")

    st = scrolledtext.ScrolledText(todo_win, wrap=tk.WORD, font=("Helvetica", 12))
    st.pack(fill="both", expand=True, padx=10, pady=10)

    if not tasks:
        st.insert(tk.END, "No to-do items found.")
    else:
        for i, t in enumerate(tasks, 1):
            st.insert(tk.END, f"{i}. {t}\n")
    st.config(state=tk.DISABLED)
