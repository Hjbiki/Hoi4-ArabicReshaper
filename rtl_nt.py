import os
import re
import unicodedata
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

# Translations dictionary
TRANSLATIONS = {
    "Arabic": {
        "title": "معالج ملفات YML للغة العربية - #NT!",
        "input_folder": "اختر مجلد الإدخال:",
        "output_folder": "اختر مجلد الإخراج:",
        "browse": "تصفح",
        "process_files": "معالجة الملفات",
        "warning": "تنبيه",
        "error": "خطأ",
        "info": "معلومات",
        "complete": "اكتمل",
        "select_input": "الرجاء اختيار مجلد الإدخال",
        "select_output": "الرجاء اختيار مجلد الإخراج",
        "no_files": "لم يتم العثور على ملفات YML في المجلد المحدد",
        "processing": "جاري المعالجة: ",
        "processed_success": "تمت معالجة {} بنجاح",
        "processing_error": "خطأ في معالجة {}: {}",
        "processed_files": "تمت معالجة {} من {} ملفات",
        "processing_complete": "اكتملت المعالجة"
    }
}

class ModernTheme:
    # Theme colors
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
    
    # Language setting
    LANGUAGE = "Arabic"
    
    @staticmethod
    def get_text(key):
        return TRANSLATIONS[ModernTheme.LANGUAGE][key]

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

def contains_arabic(text):
    return any(is_arabic_char(char) for char in text)

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

def process_yml_file(input_file):
    try:
        with open(input_file, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
        
        processed_lines = []
        for line in lines:
            # Skip empty lines
            if not line.strip():
                processed_lines.append(line)
                continue
                
            # Check for #NT! tag
            is_nt_line = line.strip().endswith('#NT!')
            
            # If no #NT! tag or no quotes, add line as is
            if not is_nt_line or '"' not in line:
                processed_lines.append(line)
                continue
            
            # Process lines with #NT! tag
            parts = line.split('"')
            if len(parts) >= 2:
                prefix = parts[0] + '"'
                # Remove #NT! tag for processing
                text = parts[1].strip().rstrip('"').strip()
                text = text.replace(' #NT!', '')
                
                reversed_text = reverse_arabic_text(text)
                processed_line = f'{prefix}{reversed_text}" #NT!\n'
                processed_lines.append(processed_line)
            else:
                processed_lines.append(line)
        
        return processed_lines
    except Exception as e:
        raise Exception(f"Error in file {input_file}: {str(e)}")

class YMLProcessorApp:
    def __init__(self, master):
        self.master = master
        master.title(ModernTheme.get_text("title"))
        # Set window icon if needed
        try:
            master.iconbitmap('icon.ico')
        except:
            pass  # Skip if icon not found
        master.geometry("800x600")
        master.configure(bg=ModernTheme.BG)
        
        # Make window resizable
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)

        # Main container
        container = ttk.Frame(master, padding="10")
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(1, weight=1)

        # Input Folder Selection
        ttk.Label(container, text=ModernTheme.get_text("input_folder")).grid(row=0, column=0, sticky="w", pady=5)
        self.input_path = tk.StringVar()
        ttk.Entry(container, textvariable=self.input_path).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(container, text=ModernTheme.get_text("browse"), 
                  command=self.select_input_folder).grid(row=0, column=2, padx=5)

        # Output Folder Selection
        ttk.Label(container, text=ModernTheme.get_text("output_folder")).grid(row=1, column=0, sticky="w", pady=5)
        self.output_path = tk.StringVar()
        ttk.Entry(container, textvariable=self.output_path).grid(row=1, column=1, sticky="ew", padx=5)
        ttk.Button(container, text=ModernTheme.get_text("browse"), 
                  command=self.select_output_folder).grid(row=1, column=2, padx=5)

        # Process Button
        ttk.Button(container, text=ModernTheme.get_text("process_files"),
                  command=self.process_yml_files, style='Accent.TButton').grid(row=2, column=0, 
                  columnspan=3, pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(container, orient="horizontal", mode="determinate")
        self.progress.grid(row=3, column=0, columnspan=3, sticky="ew", pady=5)

        # Status Label
        self.status_label = ttk.Label(container, text="")
        self.status_label.grid(row=4, column=0, columnspan=3, pady=5)

        # Log Area
        self.log_area = ScrolledText(container, height=15, bg=ModernTheme.SECOND_BG,
                                   fg=ModernTheme.FG, font=('Consolas', 9))
        self.log_area.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=5)
        container.rowconfigure(5, weight=1)

    def select_input_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_path.set(folder)

    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_path.set(folder)

    def log_message(self, message, level="info"):
        colors = {
            "info": ModernTheme.FG,
            "success": ModernTheme.SUCCESS,
            "error": ModernTheme.ERROR,
            "warning": ModernTheme.WARNING
        }
        
        timestamp = time.strftime("%H:%M:%S")
        self.log_area.tag_config(level, foreground=colors.get(level, ModernTheme.FG))
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n", level)
        self.log_area.see(tk.END)
        self.master.update_idletasks()

    def process_yml_files(self):
        input_folder = self.input_path.get()
        output_folder = self.output_path.get()

        if not input_folder:
            messagebox.showwarning(ModernTheme.get_text("warning"), 
                                 ModernTheme.get_text("select_input"))
            return
        if not output_folder:
            messagebox.showwarning(ModernTheme.get_text("warning"), 
                                 ModernTheme.get_text("select_output"))
            return

        try:
            # Get all YML files recursively from all subfolders
            yml_files = []
            for root, dirs, files in os.walk(input_folder):
                for file in files:
                    if file.lower().endswith('.yml'):
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, input_folder)
                        yml_files.append((full_path, rel_path))

            if not yml_files:
                messagebox.showinfo(ModernTheme.get_text("info"), 
                                  ModernTheme.get_text("no_files"))
                return

            self.progress["maximum"] = len(yml_files)
            self.progress["value"] = 0
            processed_count = 0

            for input_file, rel_path in yml_files:
                try:
                    # Create output path maintaining folder structure
                    output_file = os.path.join(output_folder, rel_path)
                    
                    # Create necessary subdirectories
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    
                    processed_lines = process_yml_file(input_file)
                    if processed_lines is not None:
                        # Write with UTF-8 BOM
                        with open(output_file, 'wb') as f:
                            f.write(b'\xef\xbb\xbf')
                            content = ''.join(processed_lines)
                            f.write(content.encode('utf-8'))
                        processed_count += 1
                        
                        self.status_label.config(
                            text=ModernTheme.get_text("processing").format(rel_path))
                        self.log_message(
                            ModernTheme.get_text("processed_success").format(rel_path), 
                            "success")
                    
                    self.progress["value"] += 1
                    self.master.update_idletasks()
                
                except Exception as e:
                    self.log_message(
                        ModernTheme.get_text("processing_error").format(rel_path, str(e)), 
                        "error")

            messagebox.showinfo(
                ModernTheme.get_text("complete"),
                ModernTheme.get_text("processed_files").format(processed_count, len(yml_files)))
            
            self.status_label.config(text=ModernTheme.get_text("processing_complete"))
            self.progress["value"] = 0

        except Exception as e:
            messagebox.showerror(ModernTheme.get_text("error"), str(e))

def apply_styles():
    style = ttk.Style()
    style.theme_use('clam')
    
    style.configure('.',
        background=ModernTheme.BG,
        foreground=ModernTheme.FG,
        fieldbackground=ModernTheme.SECOND_BG,
        bordercolor=ModernTheme.BORDER,
        darkcolor=ModernTheme.SECOND_BG,
        lightcolor=ModernTheme.SECOND_BG,
        troughcolor=ModernTheme.SECOND_BG,
        relief='flat')

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
        foreground=ModernTheme.BG)

    style.map('TButton',
        background=[('active', ModernTheme.ACCENT_DARK),
                   ('pressed', ModernTheme.ACCENT_LIGHT)])

    style.configure('Accent.TButton',
        font=('Arial', 10, 'bold'),
        padding=5)

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