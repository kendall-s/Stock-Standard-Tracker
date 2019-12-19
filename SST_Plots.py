from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from pylab import get_current_fig_manager
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QAction, QVBoxLayout, QFileDialog, QApplication, QComboBox,
                             QGridLayout, QLabel, QListWidget, QCheckBox, QPushButton, QAbstractItemView, QFrame)
from PyQt5.QtGui import QFont, QIcon, QImage
import io
import os
import sqlite3
import statistics

import icons

class plotterWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.setWindowIcon(QIcon(':/assets/stockflask.svg'))

        self.init_ui()

        self.populate_list()

        self.setStyleSheet('''
                      QLabel {
                          font: 14px;
                      }   
                      QPushButton {
                          font: 14px;
                      }
                      QComboBox {
                          font: 14px;
                      }
                      QListWidget {
                          font: 14px;
                      }
                      QTableWidget {
                          font: 14px;
                      }
                      QCheckBox {
                          font: 14px;
                      }
                      QLineEdit {
                          font: 14px;
                      }
                      ''')

    def init_ui(self):
        self.setFont(QFont('Segoe UI'))

        self.setGeometry(0, 0, 950, 800)
        qtRectangle = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.setWindowTitle('HyPro - Plotting Window')

        self.qvbox_layout = QVBoxLayout()
        self.qvbox_frame_holder = QFrame()
        self.qvbox_frame_holder.setLayout(self.qvbox_layout)
        self.grid_layout = QGridLayout()


        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')

        exportPlot = QAction('Export Plot', self)
        exportPlot.triggered.connect(self.export_plot)
        fileMenu.addAction(exportPlot)

        copyPlot = QAction('Copy', self)
        copyPlot.triggered.connect(self.copy_plot)
        editMenu.addAction(copyPlot)

        nutrient_label = QLabel('Nutrient:')
        self.nutrient_combo = QComboBox()
        self.nutrient_combo.addItems(['NOx', 'Phosphate', 'Silicate', 'Nitrite', 'Ammonia'])
        self.nutrient_combo.currentIndexChanged.connect(self.populate_list)


        run_list_label = QLabel('Select Run:', self)
        self.run_list = QListWidget(self)
        self.run_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        #self.run_list.setMaximumWidth(120)

        plot_fields_label = QLabel('Plot the following:')

        self.weights_check = QCheckBox('Mass Weighed')
        self.time_dried_check = QCheckBox('Time Dried')
        self.volume_check = QCheckBox('Volume')
        self.temp_check = QCheckBox('Temperature')
        self.ident_check = QCheckBox('Ident')

        self.error_percent_check = QCheckBox('Cal 3 Error')
        self.cal3_new_mean_conc_check = QCheckBox('New Cal 3 Mean Conc')
        self.cal3_new_mean_height_check = QCheckBox('New Cal 3 Mean Height')

        self.cal3_old_mean_conc_check = QCheckBox('Old Cal 3 Mean Conc')
        self.cal3_old_mean_height_check = QCheckBox('Old Cal 3 Mean Height')

        self.rmns_mean_conc_check = QCheckBox('RMNS Mean')

        self.apply_button = QPushButton('Apply', self)
        self.apply_button.clicked.connect(self.apply)

        self.figure = plt.figure()
        self.figure.set_tight_layout(tight=True)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)

        self.main_plot = self.figure.add_subplot(111)
        self.main_plot.grid(alpha=0.7)
        self.main_plot.set_xlabel('Date')
        self.main_plot.set_ylabel('Values')

        for x in self.main_plot.get_xticklabels():
            x.set_fontsize(12)
        for y in self.main_plot.get_yticklabels():
            y.set_fontsize(12)

        self.grid_layout.addWidget(self.canvas, 0, 1, 1, 10)
        self.grid_layout.addWidget(self.qvbox_frame_holder, 0, 0)

        self.qvbox_layout.addWidget(nutrient_label)
        self.qvbox_layout.addWidget(self.nutrient_combo)
        self.qvbox_layout.addWidget(run_list_label)
        self.qvbox_layout.addWidget(self.run_list)

        self.qvbox_layout.addWidget(plot_fields_label)

        self.qvbox_layout.addWidget(self.weights_check)
        self.qvbox_layout.addWidget(self.volume_check)
        self.qvbox_layout.addWidget(self.temp_check)
        self.qvbox_layout.addWidget(self.time_dried_check)
        self.qvbox_layout.addWidget(self.ident_check)
        self.qvbox_layout.addWidget(self.error_percent_check)
        self.qvbox_layout.addWidget(self.cal3_new_mean_conc_check)
        self.qvbox_layout.addWidget(self.cal3_new_mean_height_check)
        self.qvbox_layout.addWidget(self.cal3_old_mean_conc_check)
        self.qvbox_layout.addWidget(self.cal3_old_mean_height_check)

        self.rmns_mean_conc_check = QCheckBox('RMNS Mean')

        self.qvbox_layout.addWidget(self.apply_button)

        self.centralWidget().setLayout(self.grid_layout)

        clicker = self.figure.canvas.mpl_connect("button_press_event", self.on_click)

        self.show()

    def populate_list(self):

        self.run_list.clear()

        appdata_path = os.getenv('LOCALAPPDATA')
        with open(appdata_path + '/' + 'Stocks Tracker' + '/' + 'path_memory.txt', 'r') as file:
            reader = file.read()

        conn = sqlite3.connect(reader)
        c = conn.cursor()

        c.execute('SELECT DISTINCT date, lab from stockInformation where nutrient=?', (self.nutrient_combo.currentText(),))

        data = list(c.fetchall())
        if len(data) > 0:
            for item in data:
                print(item)
                self.run_list.addItem(str(item[0] + ' | ' + item[1]))

        conn.close()

    def export_plot(self):
        filedialog = QFileDialog.getSaveFileName(None, 'Save Plot', '', '.png')
        if filedialog[0]:
            self.figure.savefig(filedialog[0] + filedialog[1], dpi=400)

    def copy_plot(self):
        buffer = io.BytesIO()
        self.figure.savefig(buffer, dpi=400)
        QApplication.clipboard().setImage(QImage.fromData(buffer.getvalue()))

    def on_click(self, event):
        tb = get_current_fig_manager().toolbar
        if event.button == 1 and event.inaxes and tb.mode == '':
            print(event.xdata)

    def apply(self):
        appdata_path = os.getenv('LOCALAPPDATA')
        with open(appdata_path + '/' + 'Stocks Tracker' + '/' + 'path_memory.txt', 'r') as file:
            reader = file.read()

        conn = sqlite3.connect(reader)
        c = conn.cursor()

        selected = self.run_list.selectedItems()
        selected_runs = [item.text() for item in selected]
        selected_dates = [x[:10] for x in selected_runs]
        selected_labs = [x[13:] for x in selected_runs]

        selected_nutrient = [self.nutrient_combo.currentText() for x in selected_dates]

        selected_pack = list(zip(selected_dates, selected_labs, selected_nutrient))

        if len(self.main_plot.lines) > 0:
            del self.main_plot.lines[:]

        if self.weights_check.isChecked():
            self.plot_weight(selected_pack, c)
        if self.temp_check.isChecked():
            self.plot_temp(selected_pack, c)
        if self.time_dried_check.isChecked():
            self.plot_time(selected_pack, c)
        if self.error_percent_check.isChecked():
            self.plot_error(selected_pack, c)
        if self.cal3_new_mean_conc_check.isChecked():
            self.plot_cal_three(selected_pack, c, 'New', 'Conc')
        if self.cal3_new_mean_height_check.isChecked():
            self.plot_cal_three(selected_pack, c, 'New', 'Height')
        if self.cal3_old_mean_conc_check.isChecked():
            self.plot_cal_three(selected_pack, c, 'Old', 'Conc')
        if self.cal3_old_mean_height_check.isChecked():
            self.plot_cal_three(selected_pack, c, 'Old', 'Height')

        self.canvas.draw()

        if self.ident_check.isChecked():
            self.plot_ident(selected_pack, c)

        self.main_plot.legend()
        self.canvas.draw()
        
    def plot_weight(self, selected_pack, c):
        dates = []
        mass = []
        for selection in selected_pack:
            c.execute('SELECT date, mass from stockInformation WHERE date=? AND lab=? AND nutrient=?', selection)
            data = c.fetchall()
            print(data)
            if len(data) > 0:
                dates.append(data[0][0])
                mass.append(float(data[0][1]))

        self.main_plot.plot(dates, mass, marker='o', lw=0.5, linestyle='--', color='#423D6B', label='Mass (g)')
        self.canvas.draw()

    def plot_temp(self, selected_pack, c):
        dates = []
        temp = []
        for selection in selected_pack:
            c.execute('SELECT date, temp from stockInformation WHERE date=? AND lab=? AND nutrient=?', selection)
            data = c.fetchall()
            print(data)
            if len(data) > 0:
                dates.append(data[0][0])
                temp.append(float(data[0][1]))

        self.main_plot.plot(dates, temp, marker='o', lw=0.5, linestyle='--', color='#476DA5', label='Temp (°C)')
        self.canvas.draw()

    def plot_time(self, selected_pack, c):
        dates = []
        time = []
        for selection in selected_pack:
            c.execute('SELECT date, timeDried from stockInformation WHERE date=? AND lab=? AND nutrient=?', selection)
            data = c.fetchall()
            print(data)
            if len(data) > 0:
                dates.append(data[0][0])
                time.append(int(data[0][1]))

        self.main_plot.plot(dates, time, marker='o', lw=0.5, linestyle='--', color='#D2682B', label='Time Dried (hrs)')
        self.canvas.draw()

    def plot_ident(self, selected_pack, c):
        dates = []
        ident = []
        for selection in selected_pack:
            c.execute('SELECT date, ident from stockInformation WHERE date=? AND lab=? AND nutrient=?', selection)
            data = c.fetchall()
            print(data)
            if len(data) > 0:
                ident.append(data[0][0])
                dates.append(data[0][1])
            ymin, ymax = self.main_plot.get_ylim()
            print(ymin, ymax)
            ymid = ((ymax - ymin) * 0.2) + ymin
            self.main_plot.annotate(str(data[0][1]), xy=(data[0][0], ymid), xycoords='data')

        self.canvas.draw()

    def plot_error(self, selected_pack, c):
        dates = []
        error = []
        for selection in selected_pack:
            c.execute('SELECT date, id, concentration from calThreeMeasurements WHERE date=? AND nutrient=?', (selection[0], selection[2]))
            data = c.fetchall()
            print(data)
            cals = set([x[1] for x in data])
            for cal in cals:
                if 'old' in cal or 'Old' in cal:
                    old_cal_id = cal
                if 'new' in cal or 'New' in cal:
                    new_cal_id = cal
            old_cal_concs = []
            new_cal_concs = []
            for cal_data in data:
                print(cal_data)
                if cal_data[1] == old_cal_id:
                    old_cal_concs.append(cal_data[2])
                if cal_data[1] == new_cal_id:
                    new_cal_concs.append(cal_data[2])

            old_cal_mean = statistics.mean(old_cal_concs)
            new_cal_mean = statistics.mean(new_cal_concs)
            error_dif = old_cal_mean - new_cal_mean
            error_percent = (error_dif/old_cal_mean) * 100

            dates.append(data[0][0])
            error.append(error_percent)

        self.main_plot.plot(dates, error, marker='o', lw=0.5, linestyle='--', color='#CDD92C', label='Error Percent')
        self.canvas.draw()


    def plot_cal_three(self, selected_pack, c, age, type):
        vals = []
        dates =[]
        for selection in selected_pack:
            if type == 'Conc':
                c.execute('SELECT date, id, concentration from calThreeMeasurements WHERE date=? AND nutrient=?', (selection[0], selection[2]))
            else:
                c.execute('SELECT date, id, peakHeight from calThreeMeasurements WHERE date=? AND nutrient=?', (selection[0], selection[2]))

            data = c.fetchall()
            cals = set([x[1] for x in data])

            for cal in cals:
                if 'old' in cal or 'Old' in cal:
                    old_cal_id = cal
                if 'new' in cal or 'New' in cal:
                    new_cal_id = cal
            old_cal_concs = []
            new_cal_concs = []
            for cal_data in data:
                print(cal_data)
                if cal_data[1] == old_cal_id:
                    old_cal_concs.append(cal_data[2])
                if cal_data[1] == new_cal_id:
                    new_cal_concs.append(cal_data[2])

            old_cal_mean = statistics.mean(old_cal_concs)
            new_cal_mean = statistics.mean(new_cal_concs)

            if age == 'New':
                vals.append(new_cal_mean)
                colour = '#62BAC6'
            else:
                vals.append(old_cal_mean)
                colour = '#72D271'
            dates.append(data[0][0])

        plot_label = age + ' ' + 'Cal 3' + ' ' + 'Mean' + ' ' + type

        self.main_plot.plot(dates, vals, marker='o', lw=0.5, linestyle='--', color=colour, label=plot_label)
        self.main_plot.relim()
        self.main_plot.autoscale()
        self.canvas.draw()

