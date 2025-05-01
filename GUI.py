import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
import pandas as pd
import os
from matplotlib import pyplot as plt
from calibration import findLinParams, voltToTemp, emisComp

# UI Configuration Variables
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 700
ENTRY_WIDTH = 50
NUM_ENTRY_WIDTH = 15
STANDARD_PAD_Y = 5
SECTION_PAD_Y = 10
CALIB_POPUP_WIDTH = 400
CALIB_POPUP_HEIGHT = 300


def dummy_calibration_function(folder, t_min, t_max, t_step, n_samples, temp_units):
    grad, yint = findLinParams(folderStr=folder, samples=n_samples,
                               lowestTemp=t_min, highestTemp=t_max,
                               increment=t_step, celsius=temp_units)
    return grad, yint


def process_data(raw_file, calibration_folder, use_manual_calibration, gradient, y_intercept,
                 emissivity, apply_peak_detection, time_constant, apply_averaging, num_samples, temp_units):
    is_celsius = (temp_units == "C")
    raw_data = pd.read_csv(raw_file)
    voltages = raw_data.iloc[:, 1]
    voltages = emisComp(vArr=voltages, emis=emissivity)
    raw_data['Time'] = pd.to_datetime(raw_data.iloc[:, 0], format="mixed")
    time = (raw_data['Time'] - raw_data['Time'].iloc[0]).dt.total_seconds()
    temperature = voltToTemp(celsius=is_celsius, m=gradient, c=y_intercept, vArr=voltages)

    plt.figure(figsize=(8, 5))
    plt.plot(time, temperature)
    plt.title("Thermometer Temperature")
    plt.xlabel("Time (s)")
    plt.ylabel(f"Temperature (°{'C' if is_celsius else 'K'})")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


class TemperatureProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Temperature Data Processor")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        # Variables
        self.raw_file_path = tk.StringVar()
        self.gradient_value = tk.StringVar()
        self.y_intercept_value = tk.StringVar()
        self.emissivity_value = tk.StringVar(value="1")
        self.peak_detection_enabled = tk.BooleanVar()
        self.averaging_enabled = tk.BooleanVar()
        self.time_constant_value = tk.StringVar()
        self.num_samples_value = tk.StringVar()
        self.calibration_folder_path = None
        self.used_csv_calibration = False
        self.temp_units = tk.StringVar(value="C")

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Temperature Data Processor", font=("Helvetica", 16)).pack(pady=SECTION_PAD_Y)

        # Raw File
        tk.Label(self.root, text="Raw Temperature CSV:").pack(pady=STANDARD_PAD_Y)
        tk.Entry(self.root, textvariable=self.raw_file_path, width=ENTRY_WIDTH, state='readonly').pack()
        tk.Button(self.root, text="Browse Raw CSV", command=self.browse_raw_file).pack(pady=STANDARD_PAD_Y)

        # Temperature Units
        tk.Label(self.root, text="Temperature Units:").pack(pady=(SECTION_PAD_Y, 0))
        unit_frame = tk.Frame(self.root)
        unit_frame.pack()
        tk.Radiobutton(unit_frame, text="Celsius (°C)", variable=self.temp_units, value="C").pack(side="left",
                                                                                                  padx=STANDARD_PAD_Y)
        tk.Radiobutton(unit_frame, text="Kelvin (K)", variable=self.temp_units, value="K").pack(side="left",
                                                                                                padx=STANDARD_PAD_Y)

        # Calibration
        tk.Label(self.root, text="Calibration (Gradient and Y-Intercept):").pack(pady=SECTION_PAD_Y)
        calibration_frame = tk.Frame(self.root)
        calibration_frame.pack()

        tk.Label(calibration_frame, text="Gradient:").grid(row=0, column=0, sticky="e", padx=STANDARD_PAD_Y)
        tk.Entry(calibration_frame, textvariable=self.gradient_value, width=NUM_ENTRY_WIDTH).grid(row=0, column=1,
                                                                                                  padx=STANDARD_PAD_Y)

        tk.Label(calibration_frame, text="Y-Intercept:").grid(row=1, column=0, sticky="e", padx=STANDARD_PAD_Y)
        tk.Entry(calibration_frame, textvariable=self.y_intercept_value, width=NUM_ENTRY_WIDTH).grid(row=1, column=1,
                                                                                                     padx=STANDARD_PAD_Y)

        tk.Button(calibration_frame, text="Calibrate with CSV Files", command=self.open_calibration_popup).grid(
            row=2, column=0, columnspan=2, pady=STANDARD_PAD_Y)

        # Emissivity
        tk.Label(self.root, text="Emissivity Value:").pack(pady=STANDARD_PAD_Y)
        tk.Entry(self.root, textvariable=self.emissivity_value, width=NUM_ENTRY_WIDTH).pack()

        # Peak Detection
        tk.Checkbutton(self.root, text="Enable Peak Detection", variable=self.peak_detection_enabled,
                       command=self.toggle_time_constant).pack(pady=STANDARD_PAD_Y)
        tk.Label(self.root, text="Time Constant (s):").pack(pady=STANDARD_PAD_Y)
        self.time_constant_entry = tk.Entry(self.root, textvariable=self.time_constant_value, width=NUM_ENTRY_WIDTH,
                                            state="disabled")
        self.time_constant_entry.pack()

        # Averaging
        tk.Checkbutton(self.root, text="Enable Averaging", variable=self.averaging_enabled,
                       command=self.toggle_num_samples).pack(pady=STANDARD_PAD_Y)
        tk.Label(self.root, text="Number of Samples for Averaging:").pack(pady=STANDARD_PAD_Y)
        self.num_samples_entry = tk.Entry(self.root, textvariable=self.num_samples_value, width=NUM_ENTRY_WIDTH,
                                          state="disabled")
        self.num_samples_entry.pack()

        # Process Button
        tk.Button(self.root, text="Process Data", command=self.process_data).pack(pady=SECTION_PAD_Y)

    def toggle_time_constant(self):
        state = "normal" if self.peak_detection_enabled.get() else "disabled"
        self.time_constant_entry.config(state=state)
        if state == "disabled":
            self.time_constant_value.set('')

    def toggle_num_samples(self):
        state = "normal" if self.averaging_enabled.get() else "disabled"
        self.num_samples_entry.config(state=state)
        if state == "disabled":
            self.num_samples_value.set('')

    def browse_raw_file(self):
        initial_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = filedialog.askopenfilename(initialdir=initial_dir, filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.raw_file_path.set(file_path)

    def open_calibration_popup(self):
        popup = Toplevel(self.root)
        popup.title("Calibration via CSV Files")
        popup.geometry(f"{CALIB_POPUP_WIDTH}x{CALIB_POPUP_HEIGHT}")

        popup.grab_set()
        popup.lift()

        temp_min = tk.StringVar()
        temp_max = tk.StringVar()
        temp_step = tk.StringVar()
        num_samples = tk.StringVar()
        folder_path = tk.StringVar()

        self.popup_labels = {}

        def select_folder():
            initial_dir = os.path.dirname(os.path.realpath(__file__))
            path = filedialog.askdirectory(initialdir=initial_dir)
            if path:
                folder_path.set(path)

        def run_calibration():
            try:
                tmin = int(temp_min.get())
                tmax = int(temp_max.get())
                tstep = int(temp_step.get())
                nsamp = int(num_samples.get())
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid numerical values.")
                return

            if not folder_path.get():
                messagebox.showerror("No Folder", "Please select a calibration folder.")
                return

            is_celsius = (self.temp_units.get() == "C")
            grad, yint = dummy_calibration_function(
                folder_path.get(), tmin, tmax, tstep, nsamp, is_celsius)

            self.gradient_value.set(f"{grad:.4f}")
            self.y_intercept_value.set(f"{yint:.4f}")
            self.calibration_folder_path = folder_path.get()
            self.used_csv_calibration = True
            popup.destroy()

        tk.Label(popup, text="Select Calibration Folder").pack(pady=STANDARD_PAD_Y)
        tk.Entry(popup, textvariable=folder_path, state='readonly', width=ENTRY_WIDTH).pack()
        tk.Button(popup, text="Browse Folder", command=select_folder).pack(pady=STANDARD_PAD_Y)

        unit = "°C" if self.temp_units.get() == "C" else "K"

        self.popup_labels["min"] = tk.Label(popup, text=f"Min Temp ({unit}):")
        self.popup_labels["min"].pack()
        tk.Entry(popup, textvariable=temp_min, width=NUM_ENTRY_WIDTH).pack()

        self.popup_labels["max"] = tk.Label(popup, text=f"Max Temp ({unit}):")
        self.popup_labels["max"].pack()
        tk.Entry(popup, textvariable=temp_max, width=NUM_ENTRY_WIDTH).pack()

        self.popup_labels["step"] = tk.Label(popup, text=f"Temp Step ({unit}):")
        self.popup_labels["step"].pack()
        tk.Entry(popup, textvariable=temp_step, width=NUM_ENTRY_WIDTH).pack()

        tk.Label(popup, text="Number of Samples per File:").pack()
        tk.Entry(popup, textvariable=num_samples, width=NUM_ENTRY_WIDTH).pack()

        tk.Button(popup, text="Calibrate", command=run_calibration).pack(pady=SECTION_PAD_Y)

    def update_temp_labels(self):
        unit = "°C" if self.temp_units.get() == "C" else "K"
        if hasattr(self, "popup_labels"):
            self.popup_labels["min"].config(text=f"Min Temp ({unit}):")
            self.popup_labels["max"].config(text=f"Max Temp ({unit}):")
            self.popup_labels["step"].config(text=f"Temp Step ({unit}):")

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
                messagebox.showerror("Error", "Please enter a valid time constant.")
                return

        num_samples = None
        if self.averaging_enabled.get():
            try:
                num_samples = int(self.num_samples_value.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number of samples.")
                return

        try:
            gradient = float(self.gradient_value.get())
            y_intercept = float(self.y_intercept_value.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid values for gradient and y-intercept.")
            return

        process_data(
            raw_file=self.raw_file_path.get(),
            calibration_folder=self.calibration_folder_path,
            use_manual_calibration=not self.used_csv_calibration,
            gradient=gradient,
            y_intercept=y_intercept,
            emissivity=emissivity,
            apply_peak_detection=self.peak_detection_enabled.get(),
            time_constant=time_constant,
            apply_averaging=self.averaging_enabled.get(),
            num_samples=num_samples,
            temp_units=self.temp_units.get()
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = TemperatureProcessingApp(root)
    root.mainloop()