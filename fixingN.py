import os
import shutil
import codecs
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

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

class NewlineFixerApp:
    def __init__(self, root):
        self.root = root
        self.setup_gui()
        
    def setup_gui(self):
        # Configure window
        self.root.title("YML \\N Character Fixer")
        self.root.geometry("800x600")
        self.root.configure(bg=ModernTheme.BG)
        
        # Configure styles
        style = ttk.Style()
        
        # Configure common elements
        style.configure("TFrame", background=ModernTheme.BG)
        style.configure("TLabel", 
                       background=ModernTheme.BG, 
                       foreground=ModernTheme.FG,
                       font=("Segoe UI", 10))
        style.configure("TLabelframe", 
                       background=ModernTheme.BG,
                       foreground=ModernTheme.FG)
        style.configure("TLabelframe.Label", 
                       background=ModernTheme.BG,
                       foreground=ModernTheme.FG,
                       font=("Segoe UI", 10))
        
        # Configure entry fields
        style.configure("TEntry", 
                       fieldbackground=ModernTheme.SECOND_BG,
                       foreground=ModernTheme.FG,
                       insertcolor=ModernTheme.FG)
        
        # Configure buttons
        style.configure("TButton",
                       background=ModernTheme.ACCENT,
                       foreground=ModernTheme.BG,
                       padding=(10, 5),
                       font=("Segoe UI", 10))
        
        # Configure progress bar
        style.configure("Horizontal.TProgressbar",
                       background=ModernTheme.ACCENT,
                       troughcolor=ModernTheme.SECOND_BG)
        
        # Button hover effect
        style.map("TButton",
                 background=[("active", ModernTheme.ACCENT_DARK),
                           ("pressed", ModernTheme.ACCENT_LIGHT)],
                 relief=[("pressed", "sunken")])
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label with Arabic
        title_label = ttk.Label(
            main_frame, 
            text="YML \\N Character Fixer - مصحح الأسطر الجديدة", 
            font=("Segoe UI", 16, "bold"),
            foreground=ModernTheme.ACCENT
        )
        title_label.pack(pady=(0, 20))
        
        # Input selection frame
        input_frame = ttk.LabelFrame(main_frame, text="Input Directory", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.input_path = tk.StringVar()
        input_entry = ttk.Entry(input_frame, textvariable=self.input_path)
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        input_button = ttk.Button(
            input_frame, 
            text="Browse...", 
            command=self.browse_input
        )
        input_button.pack(side=tk.RIGHT)
        
        # Output selection frame
        output_frame = ttk.LabelFrame(main_frame, text="Output Directory", padding="10")
        output_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.output_path = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        output_button = ttk.Button(
            output_frame, 
            text="Browse...", 
            command=self.browse_output
        )
        output_button.pack(side=tk.RIGHT)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.pack(fill=tk.BOTH, expand=True)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Status text
        self.status_text = tk.Text(
            progress_frame, 
            height=15, 
            wrap=tk.WORD, 
            font=("Consolas", 10),
            bg=ModernTheme.SECOND_BG,
            fg=ModernTheme.FG,
            insertbackground=ModernTheme.FG,
            relief="flat",
            borderwidth=1
        )
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar to status text
        scrollbar = ttk.Scrollbar(progress_frame, command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        # Process button
        self.process_button = ttk.Button(
            main_frame,
            text="Start Processing",
            command=self.start_processing,
            style="Accent.TButton"
        )
        self.process_button.pack(pady=(20, 0))
        
        # Configure style
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Segoe UI", 11))
        
    def browse_input(self):
        directory = filedialog.askdirectory(title="Select Input Directory")
        if directory:
            self.input_path.set(directory)
            if not self.output_path.get():
                # Set default output directory
                self.output_path.set(os.path.join(directory, "processed_yml"))
                
    def browse_output(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_path.set(directory)
            
    def log_message(self, message, message_type="info"):
        # Define tags for different message types if not already defined
        if not hasattr(self, 'tags_configured'):
            self.status_text.tag_configure("error", foreground=ModernTheme.ERROR)
            self.status_text.tag_configure("success", foreground=ModernTheme.SUCCESS)
            self.status_text.tag_configure("warning", foreground=ModernTheme.WARNING)
            self.status_text.tag_configure("info", foreground=ModernTheme.FG)
            self.tags_configured = True
        
        self.status_text.insert(tk.END, message + "\n", message_type)
        self.status_text.see(tk.END)
        self.root.update_idletasks()
        
    def fix_newlines_in_file(self, input_path, output_path):
        """Fix newline characters in a single file"""
        try:
            with codecs.open(input_path, 'r', encoding='utf-8-sig') as file:
                content = file.read()
            
            count_underscore = content.count('_ن')
            count_backslash = content.count('\\ن')
            total_original = count_underscore + count_backslash
            
            content = content.replace('_ن', '\\n')
            content = content.replace('\\ن', '\\n')
            
            with codecs.open(output_path, 'w', encoding='utf-8-sig') as file:
                file.write(content)
                
            return total_original
            
        except Exception as e:
            self.log_message(f"Error processing {input_path}: {str(e)}")
            return 0
            
    def process_directory(self, input_dir, output_dir):
        """Process all .yml files in the directory"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        total_files = 0
        total_replacements = 0
        
        self.log_message(f"Starting to process .yml files in {input_dir}")
        self.log_message(f"Output directory: {output_dir}\n")
        
        # Count total files first for progress bar
        yml_files_count = sum(1 for root, _, files in os.walk(input_dir) 
                            if "processed_yml" not in root
                            for f in files if f.lower().endswith('.yml'))
        
        processed_count = 0
        
        for root, dirs, files in os.walk(input_dir):
            if "processed_yml" in root:
                continue
                
            yml_files = [f for f in files if f.lower().endswith('.yml')]
            
            for yml_file in yml_files:
                rel_path = os.path.relpath(root, input_dir)
                output_subdir = os.path.join(output_dir, rel_path)
                
                if not os.path.exists(output_subdir):
                    os.makedirs(output_subdir)
                
                input_path = os.path.join(root, yml_file)
                output_path = os.path.join(output_subdir, yml_file)
                
                replacements = self.fix_newlines_in_file(input_path, output_path)
                
                if replacements > 0:
                    self.log_message(f"Fixed {replacements} newline characters in {yml_file}")
                    total_replacements += replacements
                    total_files += 1
                else:
                    shutil.copy2(input_path, output_path)
                
                processed_count += 1
                self.progress_var.set((processed_count / yml_files_count) * 100)
                self.root.update_idletasks()
        
        return total_files, total_replacements
    
    def start_processing(self):
        input_dir = self.input_path.get()
        output_dir = self.output_path.get()
        
        if not input_dir or not output_dir:
            messagebox.showerror("Error", "Please select both input and output directories")
            return
            
        self.status_text.delete(1.0, tk.END)
        self.process_button.state(['disabled'])
        
        try:
            processed_files, total_fixes = self.process_directory(input_dir, output_dir)
            
            self.log_message("\nProcessing complete!")
            self.log_message(f"Processed files with fixes: {processed_files}")
            self.log_message(f"Total replacements made: {total_fixes}")
            
            messagebox.showinfo("Complete", 
                              f"Processing complete!\n\n"
                              f"Files processed: {processed_files}\n"
                              f"Total fixes: {total_fixes}")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
        finally:
            self.process_button.state(['!disabled'])
            self.progress_var.set(0)

def main():
    root = tk.Tk()
    app = NewlineFixerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()