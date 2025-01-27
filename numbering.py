import os
import codecs
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from datetime import datetime

class ModernTheme:
    # Modern dark theme colors
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

class TranslationProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Numbering fix between files")
        self.root.geometry("1000x800")
        self.root.configure(bg=ModernTheme.BG)
        
        # Configure style
        self.setup_styles()
        
        # Folder paths
        self.original_folder = tk.StringVar()
        self.translated_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        
        self.setup_gui()
        
    def setup_styles(self):
        style = ttk.Style()
        style.configure("Modern.TFrame", background=ModernTheme.BG)
        style.configure("Modern.TLabelframe", background=ModernTheme.BG, foreground=ModernTheme.FG)
        style.configure("Modern.TLabelframe.Label", 
                       background=ModernTheme.BG, 
                       foreground=ModernTheme.ACCENT,
                       font=('Segoe UI', 10, 'bold'))
        
        # Custom rounded button class
        class RoundedButton(tk.Button):
            def __init__(self, master=None, **kwargs):
                super().__init__(master, **kwargs)
                self['background'] = ModernTheme.ACCENT
                self['foreground'] = ModernTheme.BG
                self['font'] = ('Segoe UI', 9)
                self['borderwidth'] = 0
                self['cursor'] = 'hand2'
                self['relief'] = 'flat'
                self['padx'] = 20
                self['pady'] = 8
                
                # Bind hover events
                self.bind("<Enter>", self.on_enter)
                self.bind("<Leave>", self.on_leave)
                
            def on_enter(self, event):
                self['background'] = ModernTheme.ACCENT_LIGHT
                
            def on_leave(self, event):
                self['background'] = ModernTheme.ACCENT
        
        # Store the custom button class
        self.RoundedButton = RoundedButton
        
        # Progress bar style
        style.configure("Modern.Horizontal.TProgressbar",
                       troughcolor=ModernTheme.SECOND_BG,
                       background=ModernTheme.ACCENT,
                       bordercolor=ModernTheme.BORDER,
                       lightcolor=ModernTheme.ACCENT,
                       darkcolor=ModernTheme.ACCENT_DARK)
        
        # Label style
        style.configure("Modern.TLabel",
                       background=ModernTheme.BG,
                       foreground=ModernTheme.FG,
                       font=('Segoe UI', 9))
                       
    def setup_gui(self):
        # Main container
        main_frame = ttk.Frame(self.root, style="Modern.TFrame", padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, 
                             text="Translation File Processor",
                             bg=ModernTheme.BG,
                             fg=ModernTheme.ACCENT,
                             font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Folder selection section
        folder_frame = ttk.LabelFrame(main_frame, 
                                    text="Folder Selection", 
                                    style="Modern.TLabelframe",
                                    padding="15")
        folder_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Folder selection entries
        self.create_folder_entry(folder_frame, "Original Files:", self.original_folder, 0)
        self.create_folder_entry(folder_frame, "Translated Files:", self.translated_folder, 1)
        self.create_folder_entry(folder_frame, "Output Folder:", self.output_folder, 2)
        
        # Example section
        example_frame = ttk.LabelFrame(main_frame, 
                                     text="File Format Examples",
                                     style="Modern.TLabelframe",
                                     padding="15")
        example_frame.pack(fill=tk.X, padx=5, pady=15)
        
        # Original file example
        self.create_example_section(example_frame, "Original File Example:",
            'l_english:\n KEY1:0 "Original text 1"\n KEY2:1 "Original text 2"\n',
            0)
            
        # Translated file example
        self.create_example_section(example_frame, "Translated File Example:",
            'l_english:\n KEY1: "النص المترجم 1"\n KEY2: "النص المترجم 2"\n',
            1)
            
        # Output file example
        self.create_example_section(example_frame, "Output File Example:",
            'l_english:\n KEY1:0 "النص المترجم 1"\n KEY2:1 "النص المترجم 2"\n',
            2)
        
        # Process section
        process_frame = ttk.Frame(main_frame, style="Modern.TFrame")
        process_frame.pack(fill=tk.X, padx=5, pady=15)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(process_frame, 
                                          variable=self.progress_var,
                                          maximum=100,
                                          style="Modern.Horizontal.TProgressbar",
                                          length=300)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Process button
        process_btn = self.RoundedButton(process_frame,
                               text="Process Files",
                               command=self.start_processing)
        process_btn.pack(pady=5)
        
        # Log section
        log_frame = ttk.LabelFrame(main_frame,
                                 text="Processing Log",
                                 style="Modern.TLabelframe",
                                 padding="15")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Log text widget
        self.log_text = ScrolledText(log_frame,
                                   height=10,
                                   wrap=tk.WORD,
                                   font=('Consolas', 9),
                                   bg=ModernTheme.SECOND_BG,
                                   fg=ModernTheme.FG,
                                   insertbackground=ModernTheme.FG)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def create_folder_entry(self, parent, label_text, var, row):
        container = ttk.Frame(parent, style="Modern.TFrame")
        container.pack(fill=tk.X, pady=5)
        
        ttk.Label(container, 
                 text=label_text,
                 style="Modern.TLabel").pack(side=tk.LEFT, padx=(0, 10))
                 
        entry = tk.Entry(container,
                        textvariable=var,
                        bg=ModernTheme.SECOND_BG,
                        fg=ModernTheme.FG,
                        insertbackground=ModernTheme.FG,
                        relief='flat',
                        font=('Segoe UI', 9))
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.RoundedButton(container,
                  text="Browse",
                  command=lambda: self.browse_folder(var)).pack(side=tk.LEFT)
                  
    def create_example_section(self, parent, title, content, column):
        frame = ttk.Frame(parent, style="Modern.TFrame")
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(frame,
                 text=title,
                 style="Modern.TLabel").pack(anchor=tk.W, pady=(0, 5))
                 
        example = ScrolledText(frame,
                             height=4,
                             width=40,
                             wrap=tk.WORD,
                             font=('Consolas', 9),
                             bg=ModernTheme.SECOND_BG,
                             fg=ModernTheme.FG)
        example.pack(fill=tk.BOTH, expand=True)
        example.insert(tk.END, content)
        example.configure(state='disabled')
        
    def browse_folder(self, var):
        folder = filedialog.askdirectory()
        if folder:
            var.set(folder)
            
    def log_message(self, message, level="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding based on message level
        colors = {
            "info": ModernTheme.FG,
            "success": ModernTheme.SUCCESS,
            "error": ModernTheme.ERROR,
            "warning": ModernTheme.WARNING
        }
        
        self.log_text.tag_config(level, foreground=colors.get(level, ModernTheme.FG))
        
        self.log_text.insert(tk.END, f"[{timestamp}] ", "info")
        self.log_text.insert(tk.END, f"{message}\n", level)
        self.log_text.see(tk.END)
        self.root.update()
        
    def start_processing(self):
        # Validate folders
        if not all([self.original_folder.get(), self.translated_folder.get(), self.output_folder.get()]):
            messagebox.showerror("Error", "Please select all folders first")
            return
            
        try:
            self.process_files()
            messagebox.showinfo("Success", "Processing completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    def process_files(self):
        original_folder = self.original_folder.get()
        translated_folder = self.translated_folder.get()
        output_folder = self.output_folder.get()
        
        # Create output folder if needed
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            self.log_message(f"Created output folder: {output_folder}", "info")
            
        self.log_message("Starting to process files...", "info")
        
        # Get list of files
        original_files = os.listdir(original_folder)
        translated_files = os.listdir(translated_folder)
        matching_files = [f for f in original_files if f in translated_files]
        
        if not matching_files:
            self.log_message("No matching files found in both folders!", "warning")
            return
            
        self.log_message(f"Found {len(matching_files)} files to process", "info")
        
        # Update progress bar setup
        self.progress_var.set(0)
        total_files = len(matching_files)
        
        for index, filename in enumerate(matching_files):
            self.log_message(f"Processing {filename}...", "info")
            
            try:
                # Read original file to get the numbers
                number_dict = {}
                with codecs.open(os.path.join(original_folder, filename), 'r', 'utf-8-sig') as f:
                    for line in f:
                        if ':' in line and '"' in line:
                            parts = line.split(':', 1)
                            if len(parts) == 2:
                                key = parts[0].strip()
                                match = re.search(r':(\d+)\s*"', line)
                                if match:
                                    number_dict[key] = match.group(1)

                # Process translated file
                output_lines = []
                with codecs.open(os.path.join(translated_folder, filename), 'r', 'utf-8-sig') as f:
                    for line in f:
                        if not line.strip() or 'l_english' in line:
                            output_lines.append(line)
                            continue
                        
                        if ':' in line and '"' in line:
                            parts = line.split(':', 1)
                            if len(parts) == 2:
                                key = parts[0].strip()
                                if key in number_dict:
                                    match = re.search(r'"([^"]*)"', line)
                                    if match:
                                        translated_text = match.group(1)
                                        new_line = f' {key}:{number_dict[key]} "{translated_text}"\n'
                                        output_lines.append(new_line)
                                        continue
                        
                        output_lines.append(line)

                # Write output file
                output_path = os.path.join(output_folder, filename)
                with codecs.open(output_path, 'w', 'utf-8-sig') as f:
                    f.writelines(output_lines)
                
                self.log_message(f"Successfully processed {filename}", "success")
                
            except Exception as e:
                self.log_message(f"Error processing {filename}: {str(e)}", "error")
                continue
                
            # Update progress
            progress = (index + 1) / total_files * 100
            self.progress_var.set(progress)
            
        self.log_message("Processing completed successfully!", "success")

def main():
    root = tk.Tk()
    app = TranslationProcessor(root)
    root.mainloop()

if __name__ == "__main__":
    main()