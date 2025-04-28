import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

# Dummy function placeholder
def process_data(raw_file, calibration_files, emissivity, apply_peak_detection, time_constant, apply_averaging, num_samples):
    print(f"Processing:\nRaw File: {raw_file}\nCalibration Files: {calibration_files}\n"
          f"Emissivity: {emissivity}\nPeak Detection: {apply_peak_detection}\n"
          f"Time Constant: {time_constant}\nAveraging: {apply_averaging}\n"
          f"Number of Samples: {num_samples}")
    raw_data = pd.read_csv(raw_file)
    messagebox.showinfo("Processing Complete", "Data has been processed successfully!")

class TemperatureProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Temperature Data Processor")
        self.root.geometry("500x600")

        # Variables
        self.raw_file_path = tk.StringVar()
        self.calibration_file_paths = []
        self.emissivity_value = tk.StringVar()
        self.peak_detection_enabled = tk.BooleanVar()
        self.averaging_enabled = tk.BooleanVar()
        self.time_constant_value = tk.StringVar()
        self.num_samples_value = tk.StringVar()

        # Widgets
        self.create_widgets()

    def create_widgets(self):
        # Title
        tk.Label(self.root, text="Temperature Data Processor", font=("Helvetica", 16)).pack(pady=10)

        # Raw File
        tk.Label(self.root, text="Raw Temperature CSV:").pack(pady=5)
        tk.Entry(self.root, textvariable=self.raw_file_path, width=50, state='readonly').pack()
        tk.Button(self.root, text="Browse Raw CSV", command=self.browse_raw_file).pack(pady=5)

        # Calibration Files
        tk.Label(self.root, text="Calibration CSV Files:").pack(pady=5)
        self.calibration_label = tk.Label(self.root, text="No calibration files selected")
        self.calibration_label.pack()
        tk.Button(self.root, text="Browse Calibration CSV(s)", command=self.browse_calibration_files).pack(pady=5)

        # Emissivity
        tk.Label(self.root, text="Emissivity Value:").pack(pady=5)
        tk.Entry(self.root, textvariable=self.emissivity_value).pack()

        # Peak Detection
        tk.Checkbutton(self.root, text="Enable Peak Detection", variable=self.peak_detection_enabled, command=self.toggle_time_constant).pack(pady=5)

        # Time Constant (enabled only if peak detection checked)
        tk.Label(self.root, text="Time Constant (s):").pack(pady=5)
        self.time_constant_entry = tk.Entry(self.root, textvariable=self.time_constant_value, state="disabled")
        self.time_constant_entry.pack()

        # Averaging
        tk.Checkbutton(self.root, text="Enable Averaging", variable=self.averaging_enabled, command=self.toggle_num_samples).pack(pady=5)

        # Number of Samples (enabled only if averaging checked)
        tk.Label(self.root, text="Number of Samples for Averaging:").pack(pady=5)
        self.num_samples_entry = tk.Entry(self.root, textvariable=self.num_samples_value, state="disabled")
        self.num_samples_entry.pack()

        # Process Button
        tk.Button(self.root, text="Process Data", command=self.process_data).pack(pady=20)

    def toggle_time_constant(self):
        if self.peak_detection_enabled.get():
            self.time_constant_entry.config(state="normal")
        else:
            self.time_constant_entry.config(state="disabled")
            #self.time_constant_value.set('')

    def toggle_num_samples(self):
        if self.averaging_enabled.get():
            self.num_samples_entry.config(state="normal")
        else:
            self.num_samples_entry.config(state="disabled")
            #self.num_samples_value.set('')

    def browse_raw_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.raw_file_path.set(file_path)

    def browse_calibration_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("CSV Files", "*.csv")])
        if file_paths:
            self.calibration_file_paths = list(file_paths)
            self.calibration_label.config(text=f"{len(self.calibration_file_paths)} file(s) selected")

    def process_data(self):
        if not self.raw_file_path.get():
            messagebox.showerror("Error", "Please select a raw temperature CSV file.")
            return

        try:
            emissivity = float(self.emissivity_value.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid emissivity value.")
            return

        time_constant = None
        if self.peak_detection_enabled.get():
            try:
                time_constant = float(self.time_constant_value.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid time constant value.")
                return

        num_samples = None
        if self.averaging_enabled.get():
            try:
                num_samples = int(self.num_samples_value.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid integer for number of samples.")
                return

        process_data(
            raw_file=self.raw_file_path.get(),
            calibration_files=self.calibration_file_paths,
            emissivity=emissivity,
            apply_peak_detection=self.peak_detection_enabled.get(),
            time_constant=time_constant,
            apply_averaging=self.averaging_enabled.get(),
            num_samples=num_samples
        )

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = TemperatureProcessingApp(root)
    root.mainloop()
