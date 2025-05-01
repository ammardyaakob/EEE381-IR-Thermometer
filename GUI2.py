import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QRadioButton, QButtonGroup,
                             QCheckBox, QFileDialog, QMessageBox, QGroupBox, QDialog,
                             QFormLayout, QDialogButtonBox, QListWidget, QListWidgetItem, QToolBar, QAction)
from PyQt5.QtCore import Qt
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from averaging import simpleAvg
from calibration import findLinParams, voltToTemp, emisComp
from peakdetect import simplePeakDetect
import matplotlib.colors as mcolors
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSpinBox, QInputDialog
from collections import OrderedDict



class PlotWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Temperature Plot")
        self.setGeometry(100, 100, 800, 600)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)
        self.axes.grid(True)

        self.setCentralWidget(self.canvas)

        # Add toolbar with title editor
        self.toolbar = QToolBar("Plot Tools")
        self.addToolBar(self.toolbar)

        # Add title edit field
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter plot title")
        self.title_edit.returnPressed.connect(self.update_plot_title)
        self.toolbar.addWidget(QLabel("Title:"))
        self.toolbar.addWidget(self.title_edit)

        # Add save button
        save_button = QAction(QIcon.fromTheme("document-save"), "Save Plot", self)
        save_button.triggered.connect(self.save_plot)
        self.toolbar.addAction(save_button)

    def update_plot_title(self):
        """Update plot title from user input"""
        title = self.title_edit.text()
        if title:
            self.axes.set_title(title)
            self.canvas.draw()

    def update_plot(self, datasets, units='C'):
        self.axes.clear()
        colors = list(mcolors.TABLEAU_COLORS.values())

        # Clear previous legend if exists
        if self.axes.get_legend():
            self.axes.get_legend().remove()

        # Plot in exact received order
        lines = []
        labels = []
        for i, (time, temp, label) in enumerate(datasets):
            color = colors[i % len(colors)]
            line = self.axes.plot(time, temp, '-', color=color, zorder=len(datasets) - i)
            lines.append(line[0])
            labels.append(label)

        # Set up plot labels and formatting
        self.axes.set_xlabel('Time (s)')
        self.axes.set_ylabel(f'Temperature (°{units})')
        self.axes.set_title(self.title_edit.text() or 'Temperature Data')
        self.axes.grid(True)
        self.axes.yaxis.set_major_formatter(plt.FormatStrFormatter('%.1f'))

        # Create legend outside below the plot
        if len(datasets) > 1:
            # Place legend below the plot
            leg = self.axes.legend(
                lines,
                labels,
                loc='upper center',  # Anchor point for positioning
                bbox_to_anchor=(0.5, -0.15),  # (horizontal, vertical) position
                ncol=len(datasets),  # Number of columns for legend entries
                fancybox=True,
                shadow=True,
                prop={'size': 8}
            )

            # Adjust plot margins to make room for the legend
            self.figure.subplots_adjust(bottom=0.25)

        self.canvas.draw()

    def save_plot(self):
        """Save the current plot to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Plot", "",
            "PNG Image (*.png);;JPEG Image (*.jpg);;SVG Vector (*.svg);;PDF Document (*.pdf)"
        )
        if file_path:
            try:
                self.figure.savefig(file_path, dpi=300, bbox_inches='tight')
                QMessageBox.information(self, "Success", f"Plot saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save plot:\n{str(e)}")

class CalibrationDialog(QDialog):
    def __init__(self, parent=None, current_units='C'):
        super().__init__(parent)
        self.setWindowTitle("Calibration Settings")
        self.setModal(True)
        self.folder_path = ""
        self.current_units = current_units

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Folder selection
        folder_group = QGroupBox("Calibration Folder")
        folder_layout = QVBoxLayout()

        self.folder_edit = QLineEdit()
        self.folder_edit.setReadOnly(True)
        browse_button = QPushButton("Browse Folder")
        browse_button.clicked.connect(self.browse_folder)

        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(browse_button)
        folder_group.setLayout(folder_layout)
        layout.addWidget(folder_group)

        # Calibration parameters
        params_group = QGroupBox("Calibration Parameters")
        form_layout = QFormLayout()

        unit_symbol = '°C' if self.current_units == 'C' else 'K'

        self.min_temp_edit = QLineEdit()
        self.min_temp_edit.setPlaceholderText(f"Minimum temperature ({unit_symbol})")
        form_layout.addRow(f"Minimum Temperature ({unit_symbol}):", self.min_temp_edit)

        self.max_temp_edit = QLineEdit()
        self.max_temp_edit.setPlaceholderText(f"Maximum temperature ({unit_symbol})")
        form_layout.addRow(f"Maximum Temperature ({unit_symbol}):", self.max_temp_edit)

        self.step_temp_edit = QLineEdit()
        self.step_temp_edit.setPlaceholderText(f"Temperature step ({unit_symbol})")
        form_layout.addRow(f"Temperature Step ({unit_symbol}):", self.step_temp_edit)

        self.samples_edit = QLineEdit()
        self.samples_edit.setPlaceholderText("Number of samples per file")
        form_layout.addRow("Samples per File:", self.samples_edit)

        params_group.setLayout(form_layout)
        layout.addWidget(params_group)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self, "Select Calibration Folder",
            os.path.dirname(os.path.realpath(__file__)))
        if folder_path:
            self.folder_path = folder_path
            self.folder_edit.setText(folder_path)

    def validate_and_accept(self):
        try:
            # Convert inputs to integers
            self.min_temp = int(self.min_temp_edit.text())
            self.max_temp = int(self.max_temp_edit.text())
            self.step_temp = int(self.step_temp_edit.text())
            self.samples = int(self.samples_edit.text())

            if not self.folder_path:
                raise ValueError("Please select a calibration folder")

            if self.max_temp <= self.min_temp:
                raise ValueError("Maximum temperature must be greater than minimum")

            if self.step_temp <= 0:
                raise ValueError("Temperature step must be positive")

            if self.samples <= 0:
                raise ValueError("Number of samples must be positive")

            self.accept()

        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))

class DraggableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QListWidget.InternalMove)
        self.setSelectionMode(QListWidget.SingleSelection)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def dropEvent(self, event):
        super().dropEvent(event)
        # Notify parent that order has changed
        if hasattr(self.parent(), 'update_file_order'):
            self.parent().update_file_order()


class TemperatureProcessor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Temperature Processor")
        self.setGeometry(100, 100, 800, 600)

        # Use OrderedDict to maintain file order
        self.datasets = OrderedDict()  # Changed to OrderedDict
        self.file_order = []

        # Data variables - now stores multiple datasets
        self.current_file = None
        self.calibration_params = {'gradient': None, 'y_intercept': None}
        self.units = 'C'  # Default to Celsius

        # Plot window
        self.plot_window = PlotWindow(self)



        # UI Setup
        self.init_ui()


    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # File selection - modified for multiple files
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout()

        # File list widget
        self.file_list = DraggableListWidget()
        self.file_list.itemSelectionChanged.connect(self.file_selection_changed)
        file_layout.addWidget(QLabel("Loaded Files:"))
        file_layout.addWidget(self.file_list)

        # Emissivity control for selected file
        self.emissivity_layout = QHBoxLayout()
        self.emissivity_label = QLabel("Selected File Emissivity:")
        # Emissivity editor for selected files
        self.emissivity_edit = QLineEdit()
        #self.emissivity_edit.setPlaceholderText("0.01-1.00")
        #self.emissivity_edit.setValidator(QDoubleValidator( 1.0, 2))
        self.emissivity_edit.editingFinished.connect(self.update_selected_emissivity)  # Changed to returnPressed

        emissivity_layout = QHBoxLayout()
        emissivity_layout.addWidget(QLabel("Selected File Emissivity:"))
        emissivity_layout.addWidget(self.emissivity_edit)
        file_layout.addLayout(emissivity_layout)

        # Buttons for file operations
        button_layout = QHBoxLayout()
        browse_button = QPushButton("Add CSV Files")
        browse_button.clicked.connect(self.browse_files)
        button_layout.addWidget(browse_button)

        rename_button = QPushButton("Rename Selected")
        rename_button.clicked.connect(self.rename_selected_file)
        button_layout.addWidget(rename_button)

        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(self.remove_selected_file)
        button_layout.addWidget(remove_button)

        clear_button = QPushButton("Clear All")
        clear_button.clicked.connect(self.clear_files)
        button_layout.addWidget(clear_button)

        file_layout.addLayout(button_layout)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Temperature units
        units_group = QGroupBox("Temperature Units")
        units_layout = QHBoxLayout()

        self.units_group = QButtonGroup()
        self.celsius_radio = QRadioButton("Celsius (°C)")
        self.kelvin_radio = QRadioButton("Kelvin (K)")
        self.units_group.addButton(self.celsius_radio, 0)
        self.units_group.addButton(self.kelvin_radio, 1)
        self.celsius_radio.setChecked(True)
        self.units_group.buttonClicked.connect(self.change_units)

        units_layout.addWidget(self.celsius_radio)
        units_layout.addWidget(self.kelvin_radio)
        units_group.setLayout(units_layout)
        layout.addWidget(units_group)

        # Calibration
        calib_group = QGroupBox("Calibration")
        calib_layout = QVBoxLayout()


        # Manual calibration
        manual_calib_layout = QHBoxLayout()
        manual_calib_layout.addWidget(QLabel("Gradient:"))
        self.gradient_edit = QLineEdit()
        self.gradient_edit.setPlaceholderText("Enter gradient")
        manual_calib_layout.addWidget(self.gradient_edit)

        manual_calib_layout.addWidget(QLabel("Y-Intercept:"))
        self.yint_edit = QLineEdit()
        self.yint_edit.setPlaceholderText("Enter y-intercept")
        manual_calib_layout.addWidget(self.yint_edit)

        calib_layout.addLayout(manual_calib_layout)

        # CSV calibration
        csv_calib_button = QPushButton("Calibrate from CSV Folder")
        csv_calib_button.clicked.connect(self.open_calibration_dialog)
        calib_layout.addWidget(csv_calib_button)

        calib_group.setLayout(calib_layout)
        layout.addWidget(calib_group)

        calib_button_layout = QHBoxLayout()

        save_calib_button = QPushButton("Save Calibration")
        save_calib_button.clicked.connect(self.save_calibration)
        calib_button_layout.addWidget(save_calib_button)

        load_calib_button = QPushButton("Load Calibration")
        load_calib_button.clicked.connect(self.load_calibration)
        calib_button_layout.addWidget(load_calib_button)

        calib_layout.addLayout(calib_button_layout)

        # Processing options
        options_group = QGroupBox("Processing Options")
        options_layout = QVBoxLayout()

        # Peak detection
        self.peak_detect_check = QCheckBox("Enable Peak Detection")
        self.peak_detect_check.stateChanged.connect(self.toggle_peak_detection)
        options_layout.addWidget(self.peak_detect_check)

        self.time_const_edit = QLineEdit()
        self.time_const_edit.setPlaceholderText("Time constant (s)")
        self.time_const_edit.setEnabled(False)
        options_layout.addWidget(self.time_const_edit)

        # Averaging
        self.averaging_check = QCheckBox("Enable Averaging")
        self.averaging_check.stateChanged.connect(self.toggle_averaging)
        options_layout.addWidget(self.averaging_check)

        self.samples_edit = QLineEdit()
        self.samples_edit.setPlaceholderText("Number of samples")
        self.samples_edit.setEnabled(False)
        options_layout.addWidget(self.samples_edit)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Create a horizontal layout for process controls
        process_layout = QHBoxLayout()

        # Add sample range control
        sample_range_layout = QHBoxLayout()
        sample_range_layout.addWidget(QLabel("Sample Range:"))

        # Start index
        self.start_sample = QSpinBox()
        self.start_sample.setRange(0, 999999)
        self.start_sample.setValue(0)
        self.start_sample.setToolTip("Starting sample index (0-based)")
        sample_range_layout.addWidget(self.start_sample)

        # To label
        sample_range_layout.addWidget(QLabel("to"))

        # End index
        self.end_sample = QSpinBox()
        self.end_sample.setRange(1, 1000000)
        self.end_sample.setValue(1000)
        self.end_sample.setToolTip("Ending sample index (0-based)")
        sample_range_layout.addWidget(self.end_sample)

        process_layout.addLayout(sample_range_layout)

        # Process button
        process_button = QPushButton("Process All Data")
        process_button.clicked.connect(self.process_all_data)
        process_layout.addWidget(process_button)

        # Add the process layout to main layout
        layout.addLayout(process_layout)

        # Show Plot button
        show_plot_button = QPushButton("Show Plot Window")
        show_plot_button.clicked.connect(self.show_plot_window)
        layout.addWidget(show_plot_button)


    def browse_files(self):
        """Browse and add multiple CSV files"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Open CSV Files", os.path.dirname(os.path.realpath(__file__)),
            "CSV Files (*.csv)"
        )
        if file_paths:
            for file_path in file_paths:
                self.add_file(file_path)

    def add_file(self, file_path):
        """Add file while maintaining order"""
        if file_path in self.datasets:
            QMessageBox.information(self, "Info", f"File already loaded: {os.path.basename(file_path)}")
            return

        try:
            raw_data = pd.read_csv(file_path)
            basename = os.path.basename(file_path)

            # Convert time to seconds
            raw_data['Time'] = pd.to_datetime(raw_data.iloc[:, 0], format="mixed")
            time_data = (raw_data['Time'] - raw_data['Time'].iloc[0]).dt.total_seconds().values

            # Add to both OrderedDict and file_order
            self.datasets[file_path] = {
                'raw_data': raw_data,
                'time': time_data,
                'temperature': None,
                'original_basename': basename,
                'basename': basename,
                'display_name': basename,
                'emissivity': 1.0
            }
            self.file_order.append(file_path)

            # Add to list widget
            item = QListWidgetItem(f"{basename} (ε=1.00)")
            item.setData(Qt.UserRole, file_path)
            self.file_list.addItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load CSV file {file_path}:\n{str(e)}")

    def remove_selected_file(self):
        """Remove selected file from dataset"""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            file_path = item.data(Qt.UserRole)
            if file_path in self.datasets:
                del self.datasets[file_path]
            if file_path in self.file_order:
                self.file_order.remove(file_path)
            self.file_list.takeItem(self.file_list.row(item))

    def clear_files(self):
        """Clear all loaded files"""
        self.datasets.clear()
        self.file_order.clear()
        self.file_list.clear()

    def file_selection_changed(self):
        """Update UI when file selection changes"""
        selected_items = self.file_list.selectedItems()
        if selected_items:
            self.current_file = selected_items[0].data(Qt.UserRole)
            # Block signals temporarily to prevent recursive updates
            self.emissivity_edit.blockSignals(True)
            self.emissivity_edit.setText(f"{self.datasets[self.current_file]['emissivity']:.2f}")
            self.emissivity_edit.blockSignals(False)
        else:
            self.current_file = None
            self.emissivity_edit.clear()

    def update_selected_file_emissivity(self):
        """Update emissivity for currently selected file"""
        if self.current_file and self.emissivity_edit.text():
            try:
                new_emis = float(self.emissivity_edit.text())
                if 0 < new_emis <= 1.0:
                    self.datasets[self.current_file]['emissivity'] = new_emis
                    # Update list item text
                    for i in range(self.file_list.count()):
                        item = self.file_list.item(i)
                        if item.data(Qt.UserRole) == self.current_file:
                            item.setText(f"{self.datasets[self.current_file]['basename']} (ε={new_emis:.3f})")
                            break
                else:
                    QMessageBox.warning(self, "Warning", "Emissivity must be between 0 and 1")
            except ValueError:
                pass

    def update_selected_emissivity(self):
        """Update emissivity when Enter is pressed"""
        if not self.current_file:
            return

        try:
            new_emis = float(self.emissivity_edit.text())
            if 0 < new_emis <= 1.0:
                # Update the dataset
                data = self.datasets[self.current_file]
                data['emissivity'] = new_emis

                # Update the list display using display_name if available
                display_name = data.get('display_name', data['basename'])
                for i in range(self.file_list.count()):
                    item = self.file_list.item(i)
                    if item.data(Qt.UserRole) == self.current_file:
                        item.setText(f"{display_name} (ε={new_emis:.2f})")
                        break

                # Clear any previous error highlights
                self.emissivity_edit.setStyleSheet("")
            else:
                raise ValueError("Emissivity must be between >0 and 1.0")

        except ValueError as e:
            # Show error and reset to previous value
            self.emissivity_edit.setStyleSheet("background-color: #ffdddd;")
            QMessageBox.warning(self, "Invalid Value", str(e))
            prev_emis = self.datasets[self.current_file]['emissivity']
            self.emissivity_edit.setText(f"{prev_emis:.2f}")

    def update_current_file_emissivity(self):
        """Update emissivity for currently selected file"""
        if self.current_file and self.emissivity_edit.text():
            try:
                new_emis = float(self.emissivity_edit.text())
                if 0.01 <= new_emis <= 1.0:
                    # Update dataset
                    self.datasets[self.current_file]['emissivity'] = new_emis

                    # Update list item display
                    for i in range(self.file_list.count()):
                        item = self.file_list.item(i)
                        if item.data(Qt.UserRole) == self.current_file:
                            item.setText(f"{self.datasets[self.current_file]['basename']} (ε={new_emis:.2f})")
                            break
                else:
                    QMessageBox.warning(self, "Invalid Emissivity", "Emissivity must be between 0.01 and 1.0")
                    # Reset to previous value
                    prev_emis = self.datasets[self.current_file]['emissivity']
                    self.emissivity_edit.setText(f"{prev_emis:.2f}")
            except ValueError:
                # Reset to previous value if invalid number entered
                if self.current_file:
                    prev_emis = self.datasets[self.current_file]['emissivity']
                    self.emissivity_edit.setText(f"{prev_emis:.2f}")

    def process_all_data(self):
        """Process all loaded files"""
        if not self.datasets:
            QMessageBox.warning(self, "Warning", "No CSV files loaded!")
            return

        if self.calibration_params['gradient'] is None:
            try:
                grad = float(self.gradient_edit.text())
                yint = float(self.yint_edit.text())
                self.calibration_params = {'gradient': grad, 'y_intercept': yint}
            except ValueError:
                QMessageBox.warning(self, "Warning", "Invalid calibration parameters!")
                return

        for file_path, data in self.datasets.items():
            self.process_single_file(file_path, data)

        self.update_plot()

    def process_single_file(self, file_path, data):
        """Process temperature data for a single file with sample range"""
        try:
            emissivity = data['emissivity']
            voltages = emisComp(vArr=data['raw_data'].iloc[:, 1].values, emis=emissivity)

            # Always calculate in Celsius first
            temp_data = voltToTemp(
                celsius=True,
                m=self.calibration_params['gradient'],
                c=self.calibration_params['y_intercept'],
                vArr=voltages
            )

            # Get time and temperature data
            time_data = data['time']

            # Apply sample range if specified
            start_idx = self.start_sample.value()
            end_idx = self.end_sample.value()

            # Ensure valid range
            if end_idx > len(time_data):
                end_idx = len(time_data)
            if start_idx >= end_idx:
                start_idx = 0

            time_data = time_data[start_idx:end_idx]
            temp_data = temp_data[start_idx:end_idx]

            # Convert to Kelvin if needed
            if self.units == 'K':
                temp_data = [t + 273.15 for t in temp_data]

            if self.peak_detect_check.isChecked():
                temp_data = simplePeakDetect(time_data, temp_data, int(self.time_const_edit.text()))
            if self.averaging_check.isChecked():
                temp_data = simpleAvg(temp_data, int(self.samples_edit.text()))

            # Store the processed data
            data['temperature'] = temp_data
            data['time_processed'] = time_data  # Store the processed time range

        except Exception as e:
            QMessageBox.warning(self, "Warning",
                                f"Error processing file {data['basename']}:\n{str(e)}")

    def load_csv_data(self, file_path):
        try:
            self.raw_data = pd.read_csv(file_path)
            voltages = self.raw_data.iloc[:, 1].values

            # Convert time to seconds
            self.raw_data['Time'] = pd.to_datetime(self.raw_data.iloc[:, 0], format="mixed")
            self.time_data = (self.raw_data['Time'] - self.raw_data['Time'].iloc[0]).dt.total_seconds().values

            # Convert to temperature if we have calibration
            if self.calibration_params['gradient'] is not None:
                self.update_temperature()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load CSV file:\n{str(e)}")

    def save_calibration(self):
        """Save calibration parameters to a .cal file"""
        if not self.calibration_params['gradient']:
            QMessageBox.warning(self, "Warning", "No calibration parameters to save!")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Calibration", "", "Calibration Files (*.cal)"
        )

        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(f"gradient={self.calibration_params['gradient']}\n")
                    f.write(f"y_intercept={self.calibration_params['y_intercept']}\n")
                    f.write(f"units={self.units}\n")
                QMessageBox.information(self, "Success", "Calibration saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save calibration:\n{str(e)}")

    def load_calibration(self):
        """Load calibration parameters from a .cal file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Calibration", "", "Calibration Files (*.cal)"
        )

        if file_path:
            try:
                params = {}
                with open(file_path, 'r') as f:
                    for line in f:
                        key, value = line.strip().split('=')
                        params[key] = value

                # Update calibration parameters
                self.calibration_params = {
                    'gradient': float(params['gradient']),
                    'y_intercept': float(params['y_intercept'])
                }

                # Update UI fields
                self.gradient_edit.setText(params['gradient'])
                self.yint_edit.setText(params['y_intercept'])

                # Update units if present in file
                if 'units' in params:
                    self.units = params['units']
                    if params['units'] == 'C':
                        self.celsius_radio.setChecked(True)
                    else:
                        self.kelvin_radio.setChecked(True)

                QMessageBox.information(self, "Success", "Calibration loaded successfully!")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load calibration:\n{str(e)}")

    def update_temperature(self):
        if self.raw_data is None:
            return

        try:
            emissivity = float(self.emissivity_edit.text())
            voltages = emisComp(vArr=self.raw_data.iloc[:, 1].values, emis=emissivity)

            self.temperature_data = voltToTemp(
                celsius=(self.units == 'C'),
                m=self.calibration_params['gradient'],
                c=self.calibration_params['y_intercept'],
                vArr=voltages
            )
            if self.peak_detect_check.isChecked():
                self.temperature_data = simplePeakDetect(self.time_data,self.temperature_data,int(self.time_const_edit.text()))
            if self.averaging_check.isChecked():
                self.temperature_data = simpleAvg(self.temperature_data, int(self.samples_edit.text()))

            self.plot_window.update_plot(self.time_data, self.temperature_data, self.units)

        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Error updating temperature:\n{str(e)}")

    def rename_selected_file(self):
        """Rename the selected file's display name"""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No file selected!")
            return

        item = selected_items[0]
        file_path = item.data(Qt.UserRole)
        data = self.datasets[file_path]

        # Get current display name (without emissivity if present)
        current_text = item.text()
        current_emis = data['emissivity']  # Get current emissivity

        # Show input dialog with current display name (or basename if no display name set)
        current_name = data.get('display_name', data['basename'])
        new_name, ok = QInputDialog.getText(
            self, "Rename File",
            "Enter new display name:",
            text=current_name
        )

        if ok and new_name:
            # Update both display_name and basename in the dataset
            data['display_name'] = new_name
            data['basename'] = new_name  # Update basename as well

            # Update the list item text with new name and current emissivity
            item.setText(f"{new_name} (ε={current_emis:.2f})")

            # Update plot if it exists
            if hasattr(self, 'plot_window') and self.plot_window.isVisible():
                self.update_plot()

    def change_units(self):
        """Handle unit conversion between Celsius and Kelvin"""
        new_units = 'C' if self.celsius_radio.isChecked() else 'K'

        # Only convert if units actually changed
        if new_units != self.units:
            self.units = new_units

            # Convert existing temperatures if we have data
            if hasattr(self, 'datasets') and self.datasets:
                try:
                    if new_units == 'K':
                        # Convert from C to K
                        for file_data in self.datasets.values():
                            if file_data['temperature'] is not None:
                                file_data['temperature'] = [t + 273.15 for t in file_data['temperature']]
                    else:
                        # Convert from K to C
                        for file_data in self.datasets.values():
                            if file_data['temperature'] is not None:
                                file_data['temperature'] = [t - 273.15 for t in file_data['temperature']]

                    # Update plot if we have processed data
                    if any(data['temperature'] is not None for data in self.datasets.values()):
                        self.update_plot()

                except Exception as e:
                    QMessageBox.critical(self, "Conversion Error",
                                         f"Failed to convert temperatures:\n{str(e)}")
                    # Revert the radio buttons if conversion fails
                    if new_units == 'K':
                        self.celsius_radio.setChecked(True)
                    else:
                        self.kelvin_radio.setChecked(True)
                    self.units = 'C' if self.celsius_radio.isChecked() else 'K'

    def toggle_peak_detection(self, state):
        self.time_const_edit.setEnabled(state == Qt.Checked)

    def toggle_averaging(self, state):
        self.samples_edit.setEnabled(state == Qt.Checked)

    def open_calibration_dialog(self):
        dialog = CalibrationDialog(self, self.units)
        if dialog.exec_() == QDialog.Accepted:
            try:
                # Always calculate calibration in Celsius
                grad, yint = findLinParams(
                    folderStr=dialog.folder_path,
                    samples=dialog.samples,
                    lowestTemp=dialog.min_temp,
                    highestTemp=dialog.max_temp,
                    increment=dialog.step_temp,
                    celsius=True  # Always calibrate in Celsius
                )

                self.calibration_params = {'gradient': grad, 'y_intercept': yint}
                self.gradient_edit.setText(f"{grad:.4f}")
                self.yint_edit.setText(f"{yint:.4f}")

                if hasattr(self, 'datasets') and self.datasets:
                    self.process_all_data()

            except Exception as e:
                QMessageBox.critical(self, "Calibration Error", f"Failed to calibrate:\n{str(e)}")

    def process_data(self):
        if self.raw_data is None:
            QMessageBox.warning(self, "Warning", "No CSV file loaded!")
            return

        if self.calibration_params['gradient'] is None:
            try:
                grad = float(self.gradient_edit.text())
                yint = float(self.yint_edit.text())
                self.calibration_params = {'gradient': grad, 'y_intercept': yint}
            except ValueError:
                QMessageBox.warning(self, "Warning", "Invalid calibration parameters!")
                return

        self.update_temperature()

    def show_plot_window(self):
        self.update_plot()  # Ensure plot is up to date
        self.plot_window.show()

    def update_plot(self):
        """Update plot using guaranteed order from OrderedDict"""
        if not any(data['temperature'] is not None for data in self.datasets.values()):
            QMessageBox.warning(self, "Warning", "No processed data available to plot")
            return

        # Plot data in exact order from OrderedDict
        plot_data = []
        for file_path, data in self.datasets.items():
            if data['temperature'] is not None:
                plot_data.append((
                    data.get('time_processed', data['time']),
                    data['temperature'],
                    data.get('display_name', data['basename'])
                ))

        # Explicitly force legend order match
        self.plot_window.update_plot(plot_data, self.units)

    def update_file_order(self):
        """Update both visual and data order with guaranteed ordering"""
        # Get new order from list widget
        new_order = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            file_path = item.data(Qt.UserRole)
            new_order.append(file_path)

        # Create new OrderedDict with correct order
        ordered_datasets = OrderedDict()
        for file_path in new_order:
            ordered_datasets[file_path] = self.datasets[file_path]

        # Replace datasets and file_order
        self.datasets = ordered_datasets
        self.file_order = new_order

        # Force full plot refresh
        if hasattr(self, 'plot_window') and self.plot_window.isVisible():
            self.update_plot()
            self.plot_window.canvas.draw_idle()  # Immediate GUI update


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TemperatureProcessor()
    window.show()
    sys.exit(app.exec_())