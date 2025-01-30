import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import arabic_reshaper
from bidi.algorithm import get_display
import re
import os
import threading
import time
from typing import Optional, Dict, List
import codecs

class ModernTheme:
    """Modern theme colors and styling"""
    # Main colors
    BG = "#1a1a1a"
    FG = "#ffffff"
    ACCENT = "#2563eb"
    SECOND_BG = "#262626"
    
    # UI States
    HOVER = "#3b82f6"
    ACTIVE = "#1d4ed8"
    DISABLED = "#6b7280"
    
    # Status colors
    SUCCESS = "#22c55e"
    ERROR = "#ef4444"
    WARNING = "#f59e0b"
    INFO = "#3b82f6"
    
    # Fonts
    TITLE_FONT = ("Segoe UI", 24, "bold")
    HEADING_FONT = ("Segoe UI", 16, "bold")
    BODY_FONT = ("Segoe UI", 12)
    MONO_FONT = ("Consolas", 11)

class Translations:
    """Application translations"""
    def __init__(self):
        self.data = {
            "English": {
                "title": "Arabic NT Reshaper",
                "select_input": "Select Input Folder",
                "select_output": "Select Output Folder",
                "start": "Start Processing",
                "processing": "Processing...",
                "clear_log": "Clear Log",
                "ready": "Ready",
                "input_folder": "Input folder: {path}",
                "output_folder": "Output folder: {path}",
                "processing_file": "Processing {file}...",
                "success": "✓ Processed {file}: {count} NT lines",
                "error": "✗ Error processing {file}: {error}",
                "no_files": "No files found to process",
                "complete": "Processing complete:\n- Files processed: {files}\n- NT lines processed: {lines}\n- Time taken: {time:.1f}s"
            },
            "Arabic": {
                "title": "معالج النصوص العربية",
                "select_input": "اختيار مجلد المدخلات",
                "select_output": "اختيار مجلد المخرجات", 
                "start": "بدء المعالجة",
                "processing": "جاري المعالجة...",
                "clear_log": "مسح السجل",
                "ready": "جاهز",
                "input_folder": "مجلد المدخلات: {path}",
                "output_folder": "مجلد المخرجات: {path}",
                "processing_file": "معالجة {file}...",
                "success": "✓ تمت معالجة {file}: {count} سطر NT",
                "error": "✗ خطأ في معالجة {file}: {error}",
                "no_files": "لم يتم العثور على ملفات للمعالجة",
                "complete": "اكتملت المعالجة:\n- الملفات المعالجة: {files}\n- أسطر NT المعالجة: {lines}\n- الوقت المستغرق: {time:.1f} ثانية"
            }
        }

class ProcessingLog(tk.Text):
    """Custom log widget with styling"""
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            font=ModernTheme.MONO_FONT,
            bg=ModernTheme.SECOND_BG,
            fg=ModernTheme.FG,
            insertbackground=ModernTheme.FG,
            selectbackground=ModernTheme.ACCENT,
            relief="flat",
            padx=10,
            pady=10,
            wrap=tk.WORD,
            **kwargs
        )
        
        # Configure tags for different message types
        self.tag_configure("error", foreground=ModernTheme.ERROR)
        self.tag_configure("success", foreground=ModernTheme.SUCCESS)
        self.tag_configure("warning", foreground=ModernTheme.WARNING)
        self.tag_configure("info", foreground=ModernTheme.INFO)
        
    def append(self, message: str, level: str = "info"):
        """Append a message to the log with timestamp"""
        self.configure(state="normal")
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.insert("end", log_entry, level)
        self.see("end")
        self.configure(state="disabled")

class CustomButton(tk.Button):
    """Styled button widget"""
    def __init__(self, master, text, command=None, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            font=ModernTheme.BODY_FONT,
            bg=ModernTheme.ACCENT,
            fg=ModernTheme.FG,
            activebackground=ModernTheme.HOVER,
            activeforeground=ModernTheme.FG,
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            **kwargs
        )
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
    def _on_enter(self, e):
        if self["state"] != "disabled":
            self.config(bg=ModernTheme.HOVER)
            
    def _on_leave(self, e):
        if self["state"] != "disabled":
            self.config(bg=ModernTheme.ACCENT)

class ArabicNTReshaper:
    """Core text processing functionality"""
    def __init__(self):
        self.arabic_pattern = re.compile(
            r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\u200C\u200D]+'
        )
        
    def process_line(self, line: str) -> str:
        """Process a single line of text if it ends with #NT!"""
        # Skip lines that don't end with #NT!
        if not line.strip().endswith("#NT!"):
            return line
            
        def reshape_match(match):
            text = match.group(0)
            return get_display(arabic_reshaper.reshape(text))
            
        return self.arabic_pattern.sub(reshape_match, line)
        
    def process_file(self, input_path: str, output_path: str) -> tuple[int, float]:
        """Process a single file and return NT lines processed and time taken"""
        start_time = time.time()
        
        # Read input file with UTF-8 encoding
        with codecs.open(input_path, 'r', 'utf-8') as infile:
            lines = infile.readlines()
            
        # Process lines and count NT lines
        processed_lines = []
        nt_count = 0
        for line in lines:
            if line.strip().endswith("#NT!"):
                nt_count += 1
            processed_lines.append(self.process_line(line))
            
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write output with UTF-8-BOM encoding
        with codecs.open(output_path, 'w', 'utf-8-sig') as outfile:
            outfile.writelines(processed_lines)
            
        return nt_count, time.time() - start_time

class Application:
    """Main application class"""
    def __init__(self):
        self.root = tk.Tk()
        self.translations = Translations()
        self.reshaper = ArabicNTReshaper()
        self.current_language = tk.StringVar(value="English")
        
        # Initialize state
        self.processing = False
        self.input_dir = ""
        self.output_dir = ""
        
        self.setup_window()
        self.create_widgets()
        self.setup_bindings()
        
    def setup_window(self):
        """Configure the main window"""
        self.root.title(self.translations.data[self.current_language.get()]["title"])
        self.root.geometry("900x600")
        self.root.minsize(600, 400)
        self.root.configure(bg=ModernTheme.BG)
        
        # Center window
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - 900) // 2
        y = (screen_h - 600) // 2
        self.root.geometry(f"900x600+{x}+{y}")
        
    def create_widgets(self):
        """Create all UI elements"""
        # Main container with padding
        main = tk.Frame(self.root, bg=ModernTheme.BG, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = tk.Label(
            main,
            text=self.translations.data[self.current_language.get()]["title"],
            font=ModernTheme.TITLE_FONT,
            bg=ModernTheme.BG,
            fg=ModernTheme.FG
        )
        title.pack(pady=(0, 20))
        
        # Buttons container
        buttons = tk.Frame(main, bg=ModernTheme.BG)
        buttons.pack(fill=tk.X, pady=(0, 10))
        
        # Input folder button
        self.input_btn = CustomButton(
            buttons,
            text=self.translations.data[self.current_language.get()]["select_input"],
            command=self.select_input
        )
        self.input_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Output folder button  
        self.output_btn = CustomButton(
            buttons,
            text=self.translations.data[self.current_language.get()]["select_output"],
            command=self.select_output
        )
        self.output_btn.pack(side=tk.LEFT, padx=5)
        
        # Start button
        self.start_btn = CustomButton(
            buttons,
            text=self.translations.data[self.current_language.get()]["start"],
            command=self.start_processing
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear log button
        self.clear_btn = CustomButton(
            buttons,
            text=self.translations.data[self.current_language.get()]["clear_log"],
            command=self.clear_log
        )
        self.clear_btn.pack(side=tk.RIGHT)
        
        # Language selector
        lang_frame = tk.Frame(buttons, bg=ModernTheme.BG)
        lang_frame.pack(side=tk.RIGHT, padx=10)
        
        for lang, text in [("English", "English"), ("Arabic", "العربية")]:
            rb = tk.Radiobutton(
                lang_frame,
                text=text,
                value=lang,
                variable=self.current_language,
                bg=ModernTheme.BG,
                fg=ModernTheme.FG,
                selectcolor=ModernTheme.SECOND_BG,
                font=ModernTheme.BODY_FONT
            )
            rb.pack(side=tk.LEFT)
        
        # Log area with border
        log_frame = tk.Frame(
            main,
            bg=ModernTheme.SECOND_BG,
            bd=1,
            relief="solid"
        )
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log = ProcessingLog(log_frame)
        self.log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log.configure(yscrollcommand=scrollbar.set)
        
        # Status bar
        self.status = tk.Label(
            main,
            text=self.translations.data[self.current_language.get()]["ready"],
            bg=ModernTheme.SECOND_BG,
            fg=ModernTheme.FG,
            font=ModernTheme.BODY_FONT,
            anchor="w",
            padx=10,
            pady=5
        )
        self.status.pack(fill=tk.X, pady=(10, 0))
        
    def setup_bindings(self):
        """Setup event bindings"""
        self.current_language.trace("w", self.on_language_change)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def on_language_change(self, *args):
        """Handle language change"""
        lang = self.current_language.get()
        texts = self.translations.data[lang]
        
        # Update all text elements
        self.root.title(texts["title"])
        self.input_btn.configure(text=texts["select_input"])
        self.output_btn.configure(text=texts["select_output"])
        self.start_btn.configure(text=texts["start"])
        self.clear_btn.configure(text=texts["clear_log"])
        self.status.configure(text=texts["ready"])
        
    def select_input(self):
        """Select input folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.input_dir = folder
            self.log.append(
                self.translations.data[self.current_language.get()]["input_folder"].format(
                    path=folder
                )
            )
            
    def select_output(self):
        """Select output folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir = folder
            self.log.append(
                self.translations.data[self.current_language.get()]["output_folder"].format(
                    path=folder
                )
            )
            
    def clear_log(self):
        """Clear the log display"""
        self.log.configure(state="normal")
        self.log.delete(1.0, tk.END)
        self.log.configure(state="disabled")
        
    def start_processing(self):
        """Start the processing operation"""
        if self.processing:
            return
            
        if not self.input_dir or not self.output_dir:
            messagebox.showwarning(
                "Missing Folders",
                "Please select both input and output folders first."
            )
            return
            
        self.processing = True
        self.start_btn.configure(
            text=self.translations.data[self.current_language.get()]["processing"],
            state="disabled"
        )
        
        # Start processing in separate thread
        thread = threading.Thread(target=self.process_files)
        thread.daemon = True
        thread.start()
        
    def process_files(self):
        """Process all files in the input directory"""
        try:
            # Get all files recursively
            files_to_process = []
            for root, dirs, files in os.walk(self.input_dir):
                for file in files:
                    if file.endswith(('.yml', '.yaml')):
                        input_path = os.path.join(root, file)
                        rel_path = os.path.relpath(input_path, self.input_dir)
                        output_path = os.path.join(self.output_dir, rel_path)
                        files_to_process.append((input_path, output_path, rel_path))
                        
            if not files_to_process:
                self.log.append(
                    self.translations.data[self.current_language.get()]["no_files"],
                    "warning"
                )
                return
            
            # Process each file
            total_files = len(files_to_process)
            total_nt_lines = 0
            start_time = time.time()
            texts = self.translations.data[self.current_language.get()]
            
            for input_path, output_path, rel_path in files_to_process:
                try:
                    # Update status
                    self.status.configure(
                        text=texts["processing_file"].format(file=rel_path)
                    )
                    
                    # Process file
                    nt_count, process_time = self.reshaper.process_file(input_path, output_path)
                    total_nt_lines += nt_count
                    
                    # Log success
                    self.log.append(
                        texts["success"].format(
                            file=rel_path,
                            count=nt_count
                        ),
                        "success"
                    )
                    
                except Exception as e:
                    self.log.append(
                        texts["error"].format(
                            file=rel_path,
                            error=str(e)
                        ),
                        "error"
                    )
            
            # Log completion status
            total_time = time.time() - start_time
            self.log.append(
                texts["complete"].format(
                    files=total_files,
                    lines=total_nt_lines,
                    time=total_time
                ),
                "info"
            )
            
        except Exception as e:
            self.log.append(f"Error: {str(e)}", "error")
            
        finally:
            self.processing = False
            self.start_btn.configure(
                text=self.translations.data[self.current_language.get()]["start"],
                state="normal"
            )
            self.status.configure(
                text=self.translations.data[self.current_language.get()]["ready"]
            )
            
    def on_closing(self):
        """Handle application closing"""
        if self.processing:
            if messagebox.askokcancel(
                "Quit",
                "Processing is still running. Do you want to quit?"
            ):
                self.root.destroy()
        else:
            self.root.destroy()
            
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    app = Application()
    app.run()

if __name__ == "__main__":
    main()