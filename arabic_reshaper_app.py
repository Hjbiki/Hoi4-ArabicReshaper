import tkinter as tk
from tkinter import ttk, filedialog
import arabic_reshaper
from bidi.algorithm import get_display
import re
import os
import threading
import time
from typing import Optional, Dict, List
import json
import codecs

class ModernTheme:
    """Modern theme colors and styling"""
    # Main colors
    BG = "#0a0f13"
    FG = "#E5E7EB" 
    ACCENT = "#86b9b0"
    SECOND_BG = "#0a1920"
    
    # UI States
    HOVER = "#153b46"
    ACTIVE = "#047857"
    DISABLED = "#6B7280"
    
    # Status colors 
    SUCCESS = "#34D399"
    ERROR = "#EF4444"
    WARNING = "#F59E0B"
    INFO = "#60A5FA"
    
    # Fonts
    TITLE_FONT = ("Segoe UI", 24, "bold")
    HEADING_FONT = ("Segoe UI", 16, "bold")
    BODY_FONT = ("Segoe UI", 12)
    MONO_FONT = ("Cascadia Code", 11)
    
    # Dimensions
    PADDING = 20
    BUTTON_HEIGHT = 40
    INPUT_HEIGHT = 36
    BORDER_RADIUS = 8

class AppTranslations:
    """Application translations"""
    def __init__(self):
        self.data = {
            "English": {
                "title": "Arabic Text Reshaper",
                "author": "By Anad Askar",
                "select_input": "Select Input Folder",
                "select_output": "Select Output Folder",
                "start": "Start",
                "processing": "Processing...",
                "completed": "Completed",
                "error": "Error",
                "success": "Success",
                "no_files": "No files found",
                "files_found": "{count} files found",
                "processing_file": "Processing file",
                "config": "Configuration",
                "clear": "Clear Log",
                "settings": "Settings",
                "input_folder": "Input folder: {path}",
                "output_folder": "Output folder: {path}",
                "lines": "lines",
                "processing_stats": """Processing complete:
- Total files: {files}
- Total lines: {lines}
- Total time: {time:.2f}s
- Average time per file: {avg:.2f}s"""
            },
            "Arabic": {
                "title": "معالج النصوص العربية",
                "author": "تطوير عناد عسكر",
                "select_input": "اختيار مجلد المدخلات",
                "select_output": "اختيار مجلد المخرجات",
                "start": "ابدأ",
                "processing": "جاري المعالجة...",
                "completed": "اكتمل",
                "error": "خطأ",
                "success": "تم بنجاح",
                "no_files": "لم يتم العثور على ملفات",
                "files_found": "تم العثور على {count} ملف",
                "processing_file": "جاري معالجة الملف",
                "config": "الإعدادات",
                "clear": "مسح السجل",
                "settings": "الإعدادات",
                "input_folder": "مجلد المدخلات: {path}",
                "output_folder": "مجلد المخرجات: {path}",
                "lines": "سطر",
                "processing_stats": """اكتملت المعالجة:
- عدد الملفات: {files}
- عدد الأسطر: {lines}
- الوقت الكلي: {time:.2f} ثانية
- متوسط الوقت لكل ملف: {avg:.2f} ثانية"""
            }
        }

class CustomButton(tk.Button):
    """Custom styled button"""
    def __init__(self, master, text: str, command=None, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            font=ModernTheme.BODY_FONT,
            bg=ModernTheme.ACCENT,
            fg=ModernTheme.BG,
            activebackground=ModernTheme.HOVER,
            activeforeground=ModernTheme.BG,
            relief="flat",
            bd=0,
            padx=ModernTheme.PADDING,
            height=2,
            cursor="hand2",
            **kwargs
        )
        
        # Bind hover events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
    def _on_enter(self, e):
        self.config(bg=ModernTheme.HOVER)
        
    def _on_leave(self, e):
        self.config(bg=ModernTheme.ACCENT)

class ProcessingLog(tk.Text):
    """Custom styled log widget"""
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
        
    def append(self, message: str, level: str = "info", rtl: bool = False):
        """Append a message to the log with specified level and direction"""
        self.configure(state="normal")
        
        # Get timestamp in local time
        timestamp = time.strftime("%H:%M:%S")
        
        # Format the message with timestamp based on direction
        if rtl:
            # Use Arabic numerals for timestamp in RTL mode
            timestamp = timestamp.replace('0', '٠').replace('1', '١').replace('2', '٢').replace('3', '٣') \
                                .replace('4', '٤').replace('5', '٥').replace('6', '٦').replace('7', '٧') \
                                .replace('8', '٨').replace('9', '٩')
            # Reshape Arabic text and format with timestamp
            message = get_display(arabic_reshaper.reshape(message))
            log_entry = f"[{timestamp}] {message}\n"
        else:
            log_entry = f"[{timestamp}] {message}\n"
            
        # Insert message and apply tag
        self.insert("end", log_entry, (level, "rtl" if rtl else "ltr"))
        self.see("end")
        self.configure(state="disabled")

class ArabicReshaper:
    """Core text processing functionality"""
    def __init__(self):
        self.arabic_pattern = re.compile(
            r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\u200C\u200D]+'
        )
        
    def process_line(self, line: str) -> str:
        """Process a single line of text"""
        def reshape_match(match):
            text = match.group(0)
            return get_display(arabic_reshaper.reshape(text))
            
        return self.arabic_pattern.sub(reshape_match, line)
        
    def process_file(self, input_path: str, output_path: str) -> tuple[int, int]:
        """Process a single file and return lines processed and time taken"""
        start_time = time.time()
        
        with codecs.open(input_path, 'r', 'utf-8') as infile:
            lines = infile.readlines()
            
        processed_lines = [self.process_line(line) for line in lines]
        
        with codecs.open(output_path, 'w', 'utf-8-sig') as outfile:
            outfile.writelines(processed_lines)
            
        return len(lines), time.time() - start_time

class Application:
    """Main application class"""
    def __init__(self):
        self.root = tk.Tk()
        self.translations = AppTranslations()
        self.reshaper = ArabicReshaper()
        self.current_language = tk.StringVar(value="English")
        
        self.setup_window()
        self.create_widgets()
        self.setup_bindings()
        
        # Processing state
        self.processing = False
        self.input_dir = ""
        self.output_dir = ""
        
    def setup_window(self):
        """Configure the main window"""
        self.root.title(self.translations.data[self.current_language.get()]["title"])
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        self.root.configure(bg=ModernTheme.BG)
        
        # Center window
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - 800) // 2
        y = (screen_h - 600) // 2
        self.root.geometry(f"800x600+{x}+{y}")
        
    def create_widgets(self):
        """Create all UI widgets"""
        # Main container
        self.main_frame = tk.Frame(
            self.root,
            bg=ModernTheme.BG,
            padx=ModernTheme.PADDING,
            pady=ModernTheme.PADDING
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.create_header()
        
        # Toolbar
        self.create_toolbar()
        
        # Log area
        self.create_log_area()
        
        # Status bar
        self.create_status_bar()
        
    def create_header(self):
        """Create header section"""
        header = tk.Frame(self.main_frame, bg=ModernTheme.BG)
        header.pack(fill=tk.X, pady=(0, ModernTheme.PADDING))
        
        # Title container
        title_container = tk.Frame(header, bg=ModernTheme.BG)
        title_container.pack(side=tk.LEFT)
        
        # Title
        self.title_label = tk.Label(
            title_container,
            text=self.translations.data[self.current_language.get()]["title"],
            font=ModernTheme.TITLE_FONT,
            bg=ModernTheme.BG,
            fg=ModernTheme.ACCENT
        )
        self.title_label.pack(anchor="w")
        
        # Author
        self.author_label = tk.Label(
            title_container,
            text=self.translations.data[self.current_language.get()]["author"],
            font=ModernTheme.BODY_FONT,
            bg=ModernTheme.BG,
            fg=ModernTheme.FG
        )
        self.author_label.pack(anchor="w")
        
        # Language selector
        lang_frame = tk.Frame(header, bg=ModernTheme.BG)
        lang_frame.pack(side=tk.RIGHT, pady=10)
        
        for lang, display_text in [
            ("English", "English"), 
            ("Arabic", "العربية")
        ]:
            rb = tk.Radiobutton(
                lang_frame,
                text=display_text,
                value=lang,
                variable=self.current_language,
                bg=ModernTheme.BG,
                fg=ModernTheme.FG,
                selectcolor=ModernTheme.SECOND_BG,
                font=ModernTheme.BODY_FONT
            )
            rb.pack(side=tk.LEFT, padx=5)
            
    def create_toolbar(self):
        """Create toolbar with action buttons"""
        toolbar = tk.Frame(self.main_frame, bg=ModernTheme.BG)
        toolbar.pack(fill=tk.X, pady=(0, ModernTheme.PADDING))
        
        # Input folder button
        self.input_btn = CustomButton(
            toolbar,
            text=self.translations.data[self.current_language.get()]["select_input"],
            command=self.select_input_folder
        )
        self.input_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Output folder button
        self.output_btn = CustomButton(
            toolbar,
            text=self.translations.data[self.current_language.get()]["select_output"],
            command=self.select_output_folder
        )
        self.output_btn.pack(side=tk.LEFT, padx=5)
        
        # Start button
        self.process_btn = CustomButton(
            toolbar,
            text=self.translations.data[self.current_language.get()]["start"],
            command=self.start_processing
        )
        self.process_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear log button
        self.clear_btn = CustomButton(
            toolbar,
            text=self.translations.data[self.current_language.get()]["clear"],
            command=self.clear_log
        )
        self.clear_btn.pack(side=tk.RIGHT)
        
    def create_log_area(self):
        """Create log display area"""
        # Frame for log with border
        log_frame = tk.Frame(
            self.main_frame,
            bg=ModernTheme.SECOND_BG,
            bd=1,
            relief="solid"
        )
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Log widget
        self.log = ProcessingLog(log_frame)
        self.log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log.configure(yscrollcommand=scrollbar.set)
        
    def create_status_bar(self):
        """Create status bar"""
        status = tk.Frame(self.main_frame, bg=ModernTheme.SECOND_BG, height=25)
        status.pack(fill=tk.X, pady=(ModernTheme.PADDING, 0))
        
        self.status_label = tk.Label(
            status,
            text="Ready",
            bg=ModernTheme.SECOND_BG,
            fg=ModernTheme.FG,
            font=ModernTheme.BODY_FONT
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
    def setup_bindings(self):
        """Setup event bindings"""
        self.current_language.trace("w", self.on_language_change)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def on_language_change(self, *args):
        """Handle language change"""
        lang = self.current_language.get()
        translations = self.translations.data[lang]
        
        # Update window title
        self.root.title(translations["title"])
        
        # Update header
        self.title_label.configure(text=translations["title"])
        self.author_label.configure(text=translations["author"])
        
        # Update buttons
        self.input_btn.configure(text=translations["select_input"])
        self.output_btn.configure(text=translations["select_output"])
        self.process_btn.configure(
            text=translations["processing"] if self.processing else translations["start"]
        )
        self.clear_btn.configure(text=translations["clear"])
        
        # Update text direction for log
        text_direction = "rtl" if lang == "Arabic" else "ltr"
        self.log.configure(state="normal")
        self.log.tag_configure("rtl", justify="right")
        self.log.tag_configure("ltr", justify="left")
        self.log.tag_add(text_direction, "1.0", "end")
        self.log.configure(state="disabled")
        
        # Update status
        if hasattr(self, 'status_label'):
            self.status_label.configure(
                text=translations["processing"] if self.processing else translations["start"]
            )
        
    def select_input_folder(self):
        """Select input folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.input_dir = folder
            self.log.append(f"Input folder: {folder}", "info")
            
    def select_output_folder(self):
        """Select output folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir = folder
            self.log.append(f"Output folder: {folder}", "info")
            
    def clear_log(self):
        """Clear the log display"""
        self.log.configure(state="normal")
        self.log.delete(1.0, tk.END)
        self.log.configure(state="disabled")
        
    def start_processing(self):
        """Start the file processing"""
        if self.processing:
            return
            
        if not self.input_dir or not self.output_dir:
            self.log.append("Please select input and output folders first", "error")
            return
            
        self.processing = True
        self.process_btn.configure(
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
                    if file.endswith(('.txt', '.yml', '.yaml')):
                        input_path = os.path.join(root, file)
                        rel_path = os.path.relpath(input_path, self.input_dir)
                        output_path = os.path.join(self.output_dir, rel_path)
                        files_to_process.append((input_path, output_path))
                        
            total_files = len(files_to_process)
            if total_files == 0:
                self.log.append("No files found to process", "warning")
                return
                
            self.log.append(f"Found {total_files} files to process", "info")
            
            # Process each file
            total_lines = 0
            total_time = 0
            
            for input_path, output_path in files_to_process:
                try:
                    # Create output directory if needed
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    # Process file and get statistics
                    lines, process_time = self.reshaper.process_file(input_path, output_path)
                    total_lines += lines
                    total_time += process_time
                    
                    # Log progress
                    rel_path = os.path.relpath(input_path, self.input_dir)
                    self.log.append(
                        f"Processed {rel_path}: {lines} lines in {process_time:.2f}s",
                        "success"
                    )
                    
                except Exception as e:
                    self.log.append(f"Error processing {rel_path}: {str(e)}", "error")
                    
            # Log final statistics
            self.log.append(f"""
Processing complete:
- Total files: {total_files}
- Total lines: {total_lines}
- Total time: {total_time:.2f}s
- Average time per file: {total_time/total_files:.2f}s
""", "info")
                    
        except Exception as e:
            self.log.append(f"Processing error: {str(e)}", "error")
            
        finally:
            self.processing = False
            self.process_btn.configure(
                text=self.translations.data[self.current_language.get()]["process"],
                state="normal"
            )
            
    def on_closing(self):
        """Handle window closing"""
        if self.processing:
            if tk.messagebox.askokcancel("Quit", "Processing is still running. Do you want to quit?"):
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