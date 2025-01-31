import os
import re
import unicodedata
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

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

class ArabicProcessor:
    @staticmethod
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

    @staticmethod
    def contains_arabic(text):
        return any(ArabicProcessor.is_arabic_char(char) for char in text)

    @staticmethod
    def reverse_arabic_text(text):
        if not ArabicProcessor.contains_arabic(text):
            return text
            
        # Split into words while preserving whitespace
        words = re.findall(r'\S+|\s+', text)
        
        # Separate Arabic and non-Arabic words
        arabic_words = [word for word in words if ArabicProcessor.contains_arabic(word)]
        non_arabic_words = [word for word in words if not ArabicProcessor.contains_arabic(word)]
        
        if not arabic_words:
            return text
        
        # Reverse Arabic words order
        reversed_arabic_words = arabic_words[::-1]
        
        # Reconstruct text maintaining original word positions
        result_words = []
        arabic_index = 0
        non_arabic_index = 0
        
        for word in words:
            if ArabicProcessor.contains_arabic(word):
                result_words.append(reversed_arabic_words[arabic_index])
                arabic_index += 1
            else:
                result_words.append(non_arabic_words[non_arabic_index])
                non_arabic_index += 1
        
        return ''.join(result_words)

    @staticmethod
    def process_yml_file(input_file):
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            processed_lines = []
            for line in lines:
                if not line.strip() or '"' not in line:
                    processed_lines.append(line)
                    continue
                
                # Split on first and last quote
                parts = line.split('"')
                if len(parts) >= 2:
                    prefix = parts[0] + '"'
                    text = parts[1].strip().rstrip('"')
                    
                    # Only process if contains Arabic text
                    if ArabicProcessor.contains_arabic(text):
                        text = ArabicProcessor.reverse_arabic_text(text)
                    
                    processed_line = f'{prefix}{text}"\n'
                    processed_lines.append(processed_line)
                else:
                    processed_lines.append(line)
            
            return processed_lines
        except Exception as e:
            raise Exception(f"Error processing file: {str(e)}")

class YMLProcessorApp:
    def __init__(self, master):
        self.master = master
        self.setup_window()
        self.create_styles()
        self.create_widgets()
        self.setup_bindings()

    def setup_window(self):
        self.master.title("Arabic YML Processor")
        self.master.geometry("800x600")
        self.master.configure(bg=ModernTheme.BG)
        
        # Make window resizable
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

    def create_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        # Configure common styles
        style.configure('.',
            background=ModernTheme.BG,
            foreground=ModernTheme.FG,
            fieldbackground=ModernTheme.SECOND_BG,
            bordercolor=ModernTheme.BORDER,
            darkcolor=ModernTheme.SECOND_BG,
            lightcolor=ModernTheme.SECOND_BG,
            troughcolor=ModernTheme.SECOND_BG,
            relief='flat')

        # Label style
        style.configure('TLabel',
            font=('Segoe UI', 10),
            padding=5)

        # Entry style
        style.configure('TEntry',
            font=('Segoe UI', 10),
            padding=5)

        # Button styles
        style.configure('TButton',
            font=('Segoe UI', 10),
            padding=5,
            relief='flat',
            background=ModernTheme.ACCENT,
            foreground=ModernTheme.BG)

        style.map('TButton',
            background=[('active', ModernTheme.ACCENT_DARK),
                       ('pressed', ModernTheme.ACCENT_LIGHT)])

        # Accent button style
        style.configure('Accent.TButton',
            font=('Segoe UI', 10, 'bold'),
            padding=5,
            relief='flat',
            background=ModernTheme.ACCENT,
            foreground=ModernTheme.BG)

        # Progress bar style
        style.configure('TProgressbar',
            thickness=10,
            background=ModernTheme.ACCENT,
            troughcolor=ModernTheme.SECOND_BG)

    def create_widgets(self):
        # Main container
        self.main_frame = ttk.Frame(self.master, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.columnconfigure(1, weight=1)

        # Input folder selection
        ttk.Label(self.main_frame, text="أختر مجلد الإدخال:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.input_path = tk.StringVar()
        self.input_entry = ttk.Entry(self.main_frame, textvariable=self.input_path)
        self.input_entry.grid(row=0, column=1, sticky="ew", padx=(5, 5))
        self.input_button = ttk.Button(self.main_frame, text="تصفح", command=self.select_input_folder)
        self.input_button.grid(row=0, column=2, padx=(5, 0))

        # Output folder selection
        ttk.Label(self.main_frame, text="أختر مجلد الإخراج:").grid(row=1, column=0, sticky="w", pady=(0, 5))
        self.output_path = tk.StringVar()
        self.output_entry = ttk.Entry(self.main_frame, textvariable=self.output_path)
        self.output_entry.grid(row=1, column=1, sticky="ew", padx=(5, 5))
        self.output_button = ttk.Button(self.main_frame, text="تصفح", command=self.select_output_folder)
        self.output_button.grid(row=1, column=2, padx=(5, 0))

        # Process button
        self.process_button = ttk.Button(self.main_frame, text="بدأ", 
                                       command=self.process_files, style='Accent.TButton')
        self.process_button.grid(row=2, column=0, columnspan=3, pady=10)

        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame, orient="horizontal", mode="determinate")
        self.progress.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0, 5))

        # Status label
        self.status_label = ttk.Label(self.main_frame, text="جاهز")
        self.status_label.grid(row=4, column=0, columnspan=3, pady=(0, 5))

        # Log area
        self.log_frame = ttk.Frame(self.main_frame)
        self.log_frame.grid(row=5, column=0, columnspan=3, sticky="nsew")
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.rowconfigure(0, weight=1)

        self.log_area = ScrolledText(self.log_frame, height=15, wrap=tk.WORD,
                                   bg=ModernTheme.SECOND_BG, fg=ModernTheme.FG,
                                   font=('Consolas', 9))
        self.log_area.grid(row=0, column=0, sticky="nsew")

    def setup_bindings(self):
        # Allow the log frame to expand
        self.main_frame.rowconfigure(5, weight=1)

    def select_input_folder(self):
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_path.set(folder)
            # Auto-set output folder to input_folder/processed
            default_output = os.path.join(folder, "processed")
            self.output_path.set(default_output)

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_path.set(folder)

    def log_message(self, message, level="info"):
        # Add timestamp
        import time
        timestamp = time.strftime("%H:%M:%S")
        
        # Color coding based on message level
        colors = {
            "info": ModernTheme.FG,
            "success": ModernTheme.SUCCESS,
            "error": ModernTheme.ERROR,
            "warning": ModernTheme.WARNING
        }
        
        self.log_area.tag_config(level, foreground=colors.get(level, ModernTheme.FG))
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n", level)
        self.log_area.see(tk.END)
        self.master.update_idletasks()

    def process_files(self):
        input_folder = self.input_path.get()
        output_folder = self.output_path.get()

        if not input_folder or not output_folder:
            messagebox.showwarning("Warning", "Please select both input and output folders.")
            return

        try:
            # Find all YML files recursively
            yml_files = []
            for root, dirs, files in os.walk(input_folder):
                for file in files:
                    if file.lower().endswith('.yml'):
                        # Get full path and relative path
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, input_folder)
                        yml_files.append((full_path, rel_path))

            if not yml_files:
                messagebox.showinfo("Info", "No YML files found in the selected folder and its subdirectories.")
                return

            self.progress["maximum"] = len(yml_files)
            self.progress["value"] = 0
            processed_count = 0
            error_count = 0

            self.log_message(f"Found {len(yml_files)} YML files to process", "info")
            self.log_message(f"Input folder: {input_folder}", "info")
            self.log_message(f"Output folder: {output_folder}", "info")

            for input_file, rel_path in yml_files:
                try:
                    # Create output path maintaining folder structure
                    output_file = os.path.join(output_folder, rel_path)
                    
                    # Create necessary subdirectories
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    
                    # Process the file
                    processed_lines = ArabicProcessor.process_yml_file(input_file)
                    
                    # Write the processed content
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.writelines(processed_lines)
                    
                    processed_count += 1
                    self.status_label.config(text=f"Processing: {rel_path}")
                    self.log_message(f"Processed: {rel_path}", "success")
                    
                except Exception as e:
                    error_count += 1
                    self.log_message(f"Error processing {rel_path}: {str(e)}", "error")
                
                self.progress["value"] += 1
                self.master.update_idletasks()

            # Final status update
            completion_message = f"Completed! Processed {processed_count} files"
            if error_count > 0:
                completion_message += f" ({error_count} errors)"
            self.status_label.config(text=completion_message)
            self.log_message(completion_message, "success" if error_count == 0 else "warning")
            
            # Reset progress bar
            self.progress["value"] = 0

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.log_message(f"Critical error: {str(e)}", "error")

def main():
    root = tk.Tk()
    app = YMLProcessorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
