import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import nidaqmx
from nidaqmx.constants import TerminalConfiguration, AcquisitionType
from calibration import findLinParams, voltToTemp, emisComp
import pandas as pd
import os
from collections import deque


class LiveTemperatureMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("NI-DAQmx Temperature Monitor")
        self.root.geometry("1000x800")

        # DAQ Configuration
        self.task = None
        self.sample_rate = 1000  # Hz
        self.samples_per_chunk = 100
        self.max_data_points = 5000  # Points to show in plot
        self.running = False

        # Data buffers
        self.time_buffer = deque(maxlen=self.max_data_points)
        self.voltage_buffer = deque(maxlen=self.max_data_points)
        self.temp_buffer = deque(maxlen=self.max_data_points)

        # Calibration parameters
        self.gradient = 1.0
        self.y_intercept = 0.0
        self.emissivity = 1.0
        self.temp_units = "C"  # C or K

        # UI Setup
        self.setup_ui()

        # Animation
        self.ani = None

    def setup_ui(self):
        """Configure the user interface"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Plot Frame
        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.fig, self.ax = plt.subplots(figsize=(10, 5))
        self.line, = self.ax.plot([], [], 'r-')
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel(f'Temperature (°{self.temp_units})')
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Control Frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        # DAQ Settings
        ttk.Label(control_frame, text="DAQ Settings:").grid(row=0, column=0, sticky='w')

        ttk.Label(control_frame, text="Device:").grid(row=1, column=0)
        self.device_var = tk.StringVar(value="Dev1")
        self.device_entry = ttk.Entry(control_frame, textvariable=self.device_var, width=10)
        self.device_entry.grid(row=1, column=1)

        ttk.Label(control_frame, text="Channel:").grid(row=1, column=2)
        self.channel_var = tk.StringVar(value="ai0")
        self.channel_entry = ttk.Entry(control_frame, textvariable=self.channel_var, width=10)
        self.channel_entry.grid(row=1, column=3)

        ttk.Label(control_frame, text="Sample Rate (Hz):").grid(row=1, column=4)
        self.sample_rate_var = tk.StringVar(value="1000")
        self.sample_rate_entry = ttk.Entry(control_frame, textvariable=self.sample_rate_var, width=10)
        self.sample_rate_entry.grid(row=1, column=5)

        # Calibration Settings
        ttk.Label(control_frame, text="Calibration:").grid(row=2, column=0, sticky='w', pady=(10, 0))

        ttk.Label(control_frame, text="Gradient:").grid(row=3, column=0)
        self.gradient_var = tk.StringVar(value="1.0")
        self.gradient_entry = ttk.Entry(control_frame, textvariable=self.gradient_var, width=10)
        self.gradient_entry.grid(row=3, column=1)

        ttk.Label(control_frame, text="Y-Intercept:").grid(row=3, column=2)
        self.yint_var = tk.StringVar(value="0.0")
        self.yint_entry = ttk.Entry(control_frame, textvariable=self.yint_var, width=10)
        self.yint_entry.grid(row=3, column=3)

        ttk.Label(control_frame, text="Emissivity:").grid(row=3, column=4)
        self.emis_var = tk.StringVar(value="1.0")
        self.emis_entry = ttk.Entry(control_frame, textvariable=self.emis_var, width=10)
        self.emis_entry.grid(row=3, column=5)

        # Temperature Units
        self.unit_var = tk.StringVar(value="C")
        ttk.Radiobutton(control_frame, text="°C", variable=self.unit_var, value="C").grid(row=3, column=6)
        ttk.Radiobutton(control_frame, text="K", variable=self.unit_var, value="K").grid(row=3, column=7)

        # Calibration Buttons
        ttk.Button(control_frame, text="Calibrate from CSV", command=self.calibrate_from_csv).grid(row=4, column=0,
                                                                                                   columnspan=2)
        ttk.Button(control_frame, text="Save Calibration", command=self.save_calibration).grid(row=4, column=2,
                                                                                               columnspan=2)
        ttk.Button(control_frame, text="Load Calibration", command=self.load_calibration).grid(row=4, column=4,
                                                                                               columnspan=2)

        # Control Buttons
        self.start_button = ttk.Button(control_frame, text="Start", command=self.start_acquisition)
        self.start_button.grid(row=5, column=0, pady=10)

        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_acquisition, state=tk.DISABLED)
        self.stop_button.grid(row=5, column=1, pady=10)

        ttk.Button(control_frame, text="Save Data", command=self.save_data).grid(row=5, column=2, pady=10)
        ttk.Button(control_frame, text="Clear Plot", command=self.clear_plot).grid(row=5, column=3, pady=10)

    def start_acquisition(self):
        """Start reading from the DAQ device"""
        if self.running:
            return

        try:
            self.sample_rate = float(self.sample_rate_var.get())
            self.gradient = float(self.gradient_var.get())
            self.y_intercept = float(self.yint_var.get())
            self.emissivity = float(self.emis_var.get())
            self.temp_units = self.unit_var.get()

            # Create DAQ task
            self.task = nidaqmx.Task()
            channel = f"{self.device_var.get()}/{self.channel_var.get()}"
            self.task.ai_channels.add_ai_voltage_chan(
                channel,
                terminal_config=TerminalConfiguration.DIFF
            )
            self.task.timing.cfg_samp_clk_timing(
                rate=self.sample_rate,
                sample_mode=AcquisitionType.CONTINUOUS,
                samps_per_chan=self.samples_per_chunk
            )

            self.running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            # Start animation
            self.ani = FuncAnimation(
                self.fig,
                self.update_plot,
                interval=50,
                blit=True,
                cache_frame_data=False
            )
            self.canvas.draw()

            # Start reading thread
            self.root.after(100, self.read_data)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start acquisition:\n{str(e)}")
            if self.task:
                self.task.close()
            self.running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def stop_acquisition(self):
        """Stop the DAQ acquisition"""
        self.running = False
        if self.task:
            self.task.close()
            self.task = None
        if self.ani:
            self.ani.event_source.stop()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def read_data(self):
        """Read data from DAQ in chunks"""
        if not self.running or not self.task:
            return

        try:
            # Read a chunk of data
            data = self.task.read(
                number_of_samples_per_channel=self.samples_per_chunk,
                timeout=1.0
            )

            # Process data
            current_time = len(self.time_buffer) / self.sample_rate
            time_chunk = np.linspace(
                current_time,
                current_time + (len(data) - 1) / self.sample_rate,
                len(data)
            )

            # Apply emissivity compensation
            voltage_chunk = emisComp(data, self.emissivity)

            # Convert to temperature
            temp_chunk = voltToTemp(
                celsius=(self.temp_units == "C"),
                m=self.gradient,
                c=self.y_intercept,
                vArr=voltage_chunk
            )

            # Update buffers
            self.time_buffer.extend(time_chunk)
            self.voltage_buffer.extend(voltage_chunk)
            self.temp_buffer.extend(temp_chunk)

            # Schedule next read
            self.root.after(10, self.read_data)

        except Exception as e:
            self.stop_acquisition()
            messagebox.showerror("Error", f"Acquisition error:\n{str(e)}")

    def update_plot(self, frame):
        """Update the plot with new data"""
        if len(self.time_buffer) > 0:
            self.line.set_data(self.time_buffer, self.temp_buffer)
            self.ax.relim()
            self.ax.autoscale_view()
            self.ax.set_ylabel(f'Temperature (°{self.temp_units})')
        return self.line,

    def clear_plot(self):
        """Clear the plot data"""
        self.time_buffer.clear()
        self.voltage_buffer.clear()
        self.temp_buffer.clear()
        self.line.set_data([], [])
        self.canvas.draw()

    def save_data(self):
        """Save collected data to CSV"""
        if not self.time_buffer:
            messagebox.showwarning("Warning", "No data to save")
            return

        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")]
            )
            if file_path:
                df = pd.DataFrame({
                    'Time (s)': list(self.time_buffer),
                    'Voltage (V)': list(self.voltage_buffer),
                    f'Temperature (°{self.temp_units})': list(self.temp_buffer)
                })
                df.to_csv(file_path, index=False)
                messagebox.showinfo("Success", f"Data saved to {file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data:\n{str(e)}")

    def calibrate_from_csv(self):
        """Calibrate using CSV files"""
        try:
            folder = filedialog.askdirectory()
            if not folder:
                return

            # Get calibration parameters from dialog
            popup = tk.Toplevel(self.root)
            popup.title("Calibration Parameters")

            ttk.Label(popup, text="Minimum Temp:").grid(row=0, column=0)
            min_temp = ttk.Entry(popup)
            min_temp.grid(row=0, column=1)

            ttk.Label(popup, text="Maximum Temp:").grid(row=1, column=0)
            max_temp = ttk.Entry(popup)
            max_temp.grid(row=1, column=1)

            ttk.Label(popup, text="Temperature Step:").grid(row=2, column=0)
            temp_step = ttk.Entry(popup)
            temp_step.grid(row=2, column=1)

            ttk.Label(popup, text="Samples per File:").grid(row=3, column=0)
            samples = ttk.Entry(popup)
            samples.grid(row=3, column=1)

            def do_calibration():
                try:
                    grad, yint = findLinParams(
                        folderStr=folder,
                        samples=int(samples.get()),
                        lowestTemp=int(min_temp.get()),
                        highestTemp=int(max_temp.get()),
                        increment=int(temp_step.get()),
                        celsius=(self.temp_units == "C")
                    )
                    self.gradient_var.set(f"{grad:.4f}")
                    self.yint_var.set(f"{yint:.4f}")
                    popup.destroy()
                    messagebox.showinfo("Success", "Calibration completed successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Calibration failed:\n{str(e)}")

            ttk.Button(popup, text="Calibrate", command=do_calibration).grid(row=4, column=0, columnspan=2)

        except Exception as e:
            messagebox.showerror("Error", f"Calibration failed:\n{str(e)}")

    def save_calibration(self):
        """Save calibration parameters to file"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".cal",
                filetypes=[("Calibration Files", "*.cal")]
            )
            if file_path:
                with open(file_path, 'w') as f:
                    f.write(f"gradient={self.gradient_var.get()}\n")
                    f.write(f"y_intercept={self.yint_var.get()}\n")
                    f.write(f"emissivity={self.emis_var.get()}\n")
                    f.write(f"units={self.unit_var.get()}\n")
                messagebox.showinfo("Success", f"Calibration saved to {file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save calibration:\n{str(e)}")

    def load_calibration(self):
        """Load calibration parameters from file"""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("Calibration Files", "*.cal")]
            )
            if file_path:
                with open(file_path, 'r') as f:
                    for line in f:
                        if line.startswith("gradient="):
                            self.gradient_var.set(line.split('=')[1].strip())
                        elif line.startswith("y_intercept="):
                            self.yint_var.set(line.split('=')[1].strip())
                        elif line.startswith("emissivity="):
                            self.emis_var.set(line.split('=')[1].strip())
                        elif line.startswith("units="):
                            self.unit_var.set(line.split('=')[1].strip())
                messagebox.showinfo("Success", f"Calibration loaded from {file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load calibration:\n{str(e)}")

    def on_closing(self):
        """Handle window closing"""
        self.stop_acquisition()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = LiveTemperatureMonitor(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()