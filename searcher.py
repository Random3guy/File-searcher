import os
import string
import threading
import tkinter as tk
from tkinter import ttk, messagebox

def get_all_drives():
    drives = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(drive)
    return drives

def list_startup_files(output_box):
    startup_path = os.path.expandvars(r"%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, "Startup Folder Files:\n\n")

    try:
        for item in os.listdir(startup_path):
            output_box.insert(tk.END, f"- {item}\n")
    except FileNotFoundError:
        output_box.insert(tk.END, "Startup folder not found.\n")

def search_file(root, target, output_box, progress, search_button):
    drives = get_all_drives()
    total_drives = len(drives)

    def ui_set_max():
        progress["maximum"] = total_drives
        progress["value"] = 0
    root.after(0, ui_set_max)

    def ignore_errors(error):
        pass

    for i, drive in enumerate(drives, start=1):
        def ui_log_drive(d=drive):
            output_box.insert(tk.END, f"Scanning {d}...\n")
            output_box.see(tk.END)
        root.after(0, ui_log_drive)

        for root_dir, dirs, files in os.walk(drive, topdown=True, onerror=ignore_errors):
            if target in files:
                def ui_found(r=root_dir):
                    output_box.insert(tk.END, f"\nFound in directory: {r}\n")
                    output_box.see(tk.END)
                    search_button.config(state=tk.NORMAL)
                    progress["value"] = progress["maximum"]
                root.after(0, ui_found)
                return

        def ui_step(i_val=i):
            progress["value"] = i_val
        root.after(0, ui_step)

    def ui_not_found():
        output_box.insert(tk.END, "\nFile not found on any drive.\n")
        output_box.see(tk.END)
        search_button.config(state=tk.NORMAL)
    root.after(0, ui_not_found)

def start_search(root, entry, output_box, progress, search_button):
    target = entry.get().strip()
    if not target:
        messagebox.showwarning("Input Error", "Please enter a file name.")
        return

    output_box.delete(1.0, tk.END)
    progress["value"] = 0
    search_button.config(state=tk.DISABLED)

    thread = threading.Thread(
        target=search_file,
        args=(root, target, output_box, progress, search_button),
        daemon=True
    )
    thread.start()

def apply_theme(root, style, theme):
    if theme == "Light":
        root.configure(bg="white")
        style.configure("TLabel", background="white", foreground="black")
        style.configure("TButton", background="white", foreground="black")
        style.configure("TEntry", fieldbackground="white", foreground="black")
    else:
        root.configure(bg="#2b2b2b")
        style.configure("TLabel", background="#2b2b2b", foreground="white")
        style.configure("TButton", background="#2b2b2b", foreground="white")
        style.configure("TEntry", fieldbackground="#3c3f41", foreground="white")

def build_gui():
    root = tk.Tk()
    root.title("System File Searcher")
    root.geometry("750x550")

    style = ttk.Style(root)
    apply_theme(root, style, "Light")

    menubar = tk.Menu(root)

    theme_menu = tk.Menu(menubar, tearoff=0)
    theme_menu.add_command(label="Light Mode", command=lambda: apply_theme(root, style, "Light"))
    theme_menu.add_command(label="Dark Mode", command=lambda: apply_theme(root, style, "Dark"))
    menubar.add_cascade(label="Theme", menu=theme_menu)

    tools_menu = tk.Menu(menubar, tearoff=0)
    tools_menu.add_command(label="List Startup Files", command=lambda: list_startup_files(output_box))
    menubar.add_cascade(label="Tools", menu=tools_menu)

    about_menu = tk.Menu(menubar, tearoff=0)
    about_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "System File Searcher v1.0"))
    menubar.add_cascade(label="Help", menu=about_menu)

    root.config(menu=menubar)

    header = tk.Frame(root, bg=root["bg"])
    header.pack(pady=10)

    logo = tk.Canvas(header, width=60, height=60, bg=root["bg"], highlightthickness=0)
    logo.pack(side="left", padx=10)

    logo.create_rectangle(10, 10, 40, 50, outline="#4a90e2", width=2)
    logo.create_oval(35, 35, 55, 55, outline="#4a90e2", width=2)
    logo.create_line(48, 48, 60, 60, fill="#4a90e2", width=2)

    title_label = ttk.Label(header, text="System File Searcher", font=("Segoe UI", 18, "bold"))
    title_label.pack(side="left", padx=10)

    input_frame = tk.Frame(root, bg=root["bg"])
    input_frame.pack(pady=10)

    ttk.Label(input_frame, text="Enter file name:", font=("Segoe UI", 11)).pack()

    entry = ttk.Entry(input_frame, width=50)
    entry.pack(pady=5)

    search_button = ttk.Button(
        input_frame,
        text="Search",
        command=lambda: start_search(root, entry, output_box, progress, search_button)
    )
    search_button.pack(pady=10)

    progress = ttk.Progressbar(root, length=650, mode="determinate")
    progress.pack(pady=10)

    output_frame = tk.Frame(root, bg=root["bg"], bd=2, relief="groove")
    output_frame.pack(pady=10)

    output_box = tk.Text(output_frame, height=15, width=85, font=("Consolas", 10))
    output_box.pack(padx=5, pady=5)

    root.mainloop()

build_gui()
