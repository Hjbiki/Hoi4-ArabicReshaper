import os
import re
import unicodedata
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

# Define the ModernTheme class with color constants
class ModernTheme:
    BG = "#1E1E2E"  # Dark background
    FG = "#CDD6F4"  # Light text
    ACCENT = "#89B4FA"  # Blue accent
    ACCENT_DARK = "#74C7EC"  # Darker blue for hover
    ACCENT_LIGHT = "#B4BEFE"  # Lighter blue for hover
    SECOND_BG = "#313244"  # Secondary background
    SUCCESS = "#A6E3A1"  # Green for success
    ERROR = "#F38BA8"  # Red for errors
    WARNING = "#FAB387"  # Orange for warnings
    BORDER = "#45475A"  # Border color

# Function to check if a character is an Arabic character
def is_arabic_char(char):
    if not char:
        return False
    return unicodedata.category(char) in ['Lo', 'Mn'] and any([
        0x0600 <= ord(char) <= 0x06FF,  # Arabic
        0x0750 <= ord(char) <= 0x077F,  # Arabic Supplement
        0x08A0 <= ord(char) <= 0x08FF,  # Arabic Extended-A
        0xFB50 <= ord(char) <= 0xFDFF,  # Arabic Presentation Forms-A
        0xFE70 <= ord(char) <= 0xFEFF   # Arabic Presentation Forms-B
    ])

# Function to check if text contains any Arabic characters
def contains_arabic(text):
    return any(is_arabic_char(char) for char in text)

# Function to reverse the word order of Arabic text
def reverse_arabic_text(text):
    if not contains_arabic(text):
        return text
    words = re.findall(r'\S+|\s+', text)
    arabic_words = [word for word in words if contains_arabic(word)]
    non_arabic_words = [word for word in words if not contains_arabic(word)]
    
    if not arabic_words:
        return text
    
    reversed_arabic_words = arabic_words[::-1]
    result_words = []
    arabic_index = 0
    non_arabic_index = 0
    
    for word in words:
        if contains_arabic(word):
            result_words.append(reversed_arabic_words[arabic_index])
            arabic_index += 1
        else:
            result_words.append(non_arabic_words[non_arabic_index])
            non_arabic_index += 1
    
    return ''.join(result_words)

# Function to process YML file
def process_yml_file(input_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        processed_lines = []
        for line in lines:
            if not line.strip() or '"' not in line:
                processed_lines.append(line)
                continue
            
            parts = line.split('"')
            prefix = parts[0] + '"'
            text = parts[1].strip().rstrip('"')
            
            reversed_text = reverse_arabic_text(text)
            processed_line = f'{prefix}{reversed_text}"\n'
            processed_lines.append(processed_line)
        
        return processed_lines
    except Exception as e:
        messagebox.showerror("Error", f"Error processing file {input_file}: {str(e)}")
        return None

# Main Application Class
class YMLProcessorApp:
    def __init__(self, master):
        self.master = master
        master.title("Arabic YML Text Processor")
        master.geometry("600x400")
        master.configure(bg=ModernTheme.BG)

        # Input Folder Selection
        self.input_label = ttk.Label(master, text="Select Input Folder:", style='TLabel')
        self.input_label.pack(pady=(10, 0))
        self.input_path = tk.StringVar()
        self.input_entry = ttk.Entry(master, textvariable=self.input_path, width=50, style='TEntry')
        self.input_entry.pack(pady=(0, 5))
        self.input_button = ttk.Button(master, text="Browse", command=self.select_input_folder, style='TButton')
        self.input_button.pack(pady=(0, 10))

        # Output Folder Selection
        self.output_label = ttk.Label(master, text="Select Output Folder:", style='TLabel')
        self.output_label.pack(pady=(10, 0))
        self.output_path = tk.StringVar()
        self.output_entry = ttk.Entry(master, textvariable=self.output_path, width=50, style='TEntry')
        self.output_entry.pack(pady=(0, 5))
        self.output_button = ttk.Button(master, text="Browse", command=self.select_output_folder, style='TButton')
        self.output_button.pack(pady=(0, 10))

        # Process Button
        self.process_button = ttk.Button(master, text="Process YML Files", command=self.process_yml_files, style='Accent.TButton')
        self.process_button.pack(pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(master, orient="horizontal", length=400, mode="determinate", style='TProgressbar')
        self.progress.pack(pady=10)

        # Status Label
        self.status_label = ttk.Label(master, text="", style='TLabel')
        self.status_label.pack(pady=10)

        # Log Area
        self.log_area = ScrolledText(master, height=10, wrap=tk.WORD, bg=ModernTheme.SECOND_BG, fg=ModernTheme.FG)
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def select_input_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.input_path.set(folder_selected)

    def select_output_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_path.set(folder_selected)

    def log_message(self, message):
        self.log_area.insert(tk.END, message + '\n')
        self.log_area.yview(tk.END)

    def process_yml_files(self):
        input_folder = self.input_path.get()
        output_folder = self.output_path.get()

        if not input_folder:
            messagebox.showwarning("Warning", "Please select an input folder.")
            return
        if not output_folder:
            messagebox.showwarning("Warning", "Please select an output folder.")
            return

        os.makedirs(output_folder, exist_ok=True)
        yml_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.yml')]
        
        if not yml_files:
            messagebox.showinfo("Info", "No YML files found in the selected folder.")
            return

        self.progress["maximum"] = len(yml_files)
        self.progress["value"] = 0
        processed_count = 0

        for filename in yml_files:
            try:
                input_file = os.path.join(input_folder, filename)
                output_file = os.path.join(output_folder, filename)
                
                processed_lines = process_yml_file(input_file)
                if processed_lines is not None:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.writelines(processed_lines)
                    processed_count += 1
                
                self.progress["value"] += 1
                self.status_label.config(text=f"Processing: {filename}")
                self.log_message(f"Processed {filename} successfully.")
                self.master.update_idletasks()
            except Exception as e:
                self.log_message(f"Error processing {filename}: {str(e)}")
                messagebox.showerror("Error", f"Error processing {filename}: {str(e)}")

        messagebox.showinfo("Complete", f"Processed {processed_count} out of {len(yml_files)} files.")
        self.status_label.config(text="Processing complete")
        self.progress["value"] = 0

# Apply styles
def apply_styles():
    style = ttk.Style()
    style.theme_use('clam')

    # Configure global styles
    style.configure('.', 
                    background=ModernTheme.BG,
                    foreground=ModernTheme.FG,
                    fieldbackground=ModernTheme.SECOND_BG,
                    bordercolor=ModernTheme.BORDER,
                    darkcolor=ModernTheme.SECOND_BG,
                    lightcolor=ModernTheme.SECOND_BG,
                    troughcolor=ModernTheme.SECOND_BG,
                    relief='flat')

    # Configure specific widget styles
    style.configure('TLabel',
                    font=('Arial', 10),
                    padding=5)

    style.configure('TEntry',
                    font=('Arial', 10),
                    padding=5)

    style.configure('TButton',
                    font=('Arial', 10),
                    padding=5,
                    relief='flat',
                    background=ModernTheme.ACCENT,
                    foreground=ModernTheme.FG)

    style.map('TButton',
              background=[('active', ModernTheme.ACCENT_DARK), ('pressed', ModernTheme.ACCENT_LIGHT)])

    style.configure('Accent.TButton',
                    font=('Arial', 10, 'bold'),
                    padding=5,
                    relief='flat',
                    background=ModernTheme.ACCENT,
                    foreground=ModernTheme.FG)

    style.map('Accent.TButton',
              background=[('active', ModernTheme.ACCENT_DARK), ('pressed', ModernTheme.ACCENT_LIGHT)])

    style.configure('TProgressbar',
                    thickness=10,
                    background=ModernTheme.ACCENT,
                    troughcolor=ModernTheme.SECOND_BG)

def main():
    root = tk.Tk()
    apply_styles()
    app = YMLProcessorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()