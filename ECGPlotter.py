import sys
import numpy as np
import pyqtgraph as pg
from PyQt6 import QtWidgets, QtCore
import serial
import re

class ECGPlotter(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Animated ECG Signal Plotter")
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.start_button = QtWidgets.QPushButton("Start Animation", self)
        self.start_button.clicked.connect(self.start_animation)
        self.layout.addWidget(self.start_button)

        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        
        self.serial_port = None
        self.bpm = 0 
        self.read_serial_data()  

        self.duration = 10  
        self.visible_duration = 2  
        self.sampling_rate = 1000  
        self.time = np.linspace(0, self.duration, self.sampling_rate * self.duration, endpoint=False)
        self.ecg_signal = None
        self.index = 0  

    def read_serial_data(self):
        ''' Reads the BPM data from the serial port.'''
        self.serial_port = serial.Serial('COM3', 9600, timeout=1)  

        self.serial_timer = QtCore.QTimer()
        self.serial_timer.timeout.connect(self.fetch_serial_data)
        self.serial_timer.start(1000)  

    def fetch_serial_data(self):
        ''' Fetches the BPM data from the serial port.'''
        if self.serial_port.in_waiting > 0:
            line = self.serial_port.readline().decode('utf-8').strip()
            print(line)  
            
            match = re.search(r'bpm\s*:\s*([0-9]*\.?[0-9]+)', line)
            if match:
                self.bpm = float(match.group(1))*20
                print(f"Detected BPM: {self.bpm}")

    def start_animation(self):
        if self.bpm <= 0:
            print("Invalid BPM value, please ensure the Arduino is sending data.")
            return
        
        self.ecg_signal = self.generate_ecg_signal(self.bpm)
        self.index = 0  
        self.plot_widget.clear()
        self.plot_widget.setTitle('Animated ECG Signal')
        self.plot_widget.setLabel('left', 'Amplitude')
        self.plot_widget.setLabel('bottom', 'Time (seconds)')
        self.plot_widget.showGrid(x=True, y=True)
        
        self.plot_widget.setXRange(0, self.visible_duration)
        
        self.timer.start(int(1000 / self.sampling_rate))  

    def update_plot(self):
        ''' Updates the plot with the next ECG signal data point. '''
        if self.index < len(self.ecg_signal):
            
            self.plot_widget.plot(self.time[:self.index + 1], self.ecg_signal[:self.index + 1], pen='g')
            
            current_time = self.time[self.index]
            self.plot_widget.setXRange(current_time - self.visible_duration, current_time)
            
            self.index += 1

    def generate_ecg_signal(self, frequency):
        ''' Generates an ECG signal based on the given frequency (beats per minute). '''
        ecg_signal = (0.5 * np.sin(2 * np.pi * frequency / 60 * self.time) +  
                      0.5 * np.sin(4 * np.pi * frequency / 60 * self.time) * (np.abs(np.sin(8 * np.pi * self.time)) ** 2))
        return ecg_signal

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ECGPlotter()
    window.show()
    sys.exit(app.exec())
