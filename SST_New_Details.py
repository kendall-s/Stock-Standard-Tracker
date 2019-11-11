import statistics
import os
import sqlite3
from time import sleep

from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QDoubleValidator, QIntValidator
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (QMainWindow, QWidget, QGridLayout, QApplication, QLabel, QPushButton, QLineEdit,
                             QComboBox, QFileDialog, QTabWidget, QDateEdit, QSpinBox, QTableWidgetItem,
                             QTableWidget, QFrame, QMessageBox)

cal_three_old_variants = ['Cal 3 old', 'Cal 3 Old', 'Cal 3Old', 'Cal 3old', 'Old Cal 3',
                          'old Cal 3', 'Cal3 Old', 'Cal3 old', 'comp Cal 3 Old', 'comp Cal3 Old', 'comp Cal 3Old',
                          'Comp Cal 3 Old', 'Comp Cal3 Old', 'Comp Cal 3 old', 'comp Cal 3 old']
cal_three_new_variants = ['Cal 3 new', 'Cal 3 New', 'Cal 3New', 'Cal 3new', 'New Cal 3',
                          'new Cal 3', 'Cal3 New', 'Cal3 new', 'comp Cal 3 New', 'comp Cal3 New', 'comp Cal 3New',
                          'Comp Cal 3 New', 'Comp Cal3 New', 'Comp Cal 3 new', 'comp Cal 3 new']

fields_list = ['_mass_field', '_flask_field', '_volume_field', '_temp_field', '_ident_field']

class newDetails(QMainWindow):

    def __init__(self, active_nutrients, data_df):
        super().__init__()
        self.setWindowIcon(QIcon('assets/icon.svg'))
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.active_nutrients = active_nutrients
        self.data_df = data_df

        self.init_ui()

        try:
            self.calculations()
            self.extract_rmns()
            self.populate_tables()
            self.determine_pass()

            self.show()

        except statistics.StatisticsError:
            messagebox = QMessageBox(QMessageBox.Information, 'Error',
                                     'Could not find replicate Cal 3 measurements, please ensure the correct '
                                     'naming convention is followed, i.e. comp Cal 3 Old and comp Cal 3 New.',
                                     buttons=QMessageBox.Ok, parent=self)
            messagebox.setFont(QFont('Segoe UI'))
            messagebox.setStyleSheet('QLabel { font: 15px; } QPushButton { width: 50px; font: 15px; }')
            messagebox.exec_()
            self.close()

        self.setStyleSheet('''
                QLabel {
                    font: 14px;
                    padding: 2px;
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
                    font: 12px;
                }
                QCheckBox {
                    font: 14px;
                }
                QLineEdit {
                    font: 14px;
                }
                QSpinBox {
                    font: 14px;
                }
                QTabWidget {
                    font: 16px;
                }
                QDateEdit {
                    font: 14px;
                }
                QFrame[left=true] {
                    background-color: #F4F4F4;
                    border: 2px solid #EAEAEA;
                    border-radius: 5px;
                    padding: 3px;
                } 
                QFrame[middle=true] {
                    background-color: #E1E1E1;
                    border: 2px solid #929292;
                    border-radius: 5px;
                    padding: 3px;
                }
                QFrame[right=true] {
                    background-color: #F4F4F4;
                    border: 2px solid #EAEAEA;
                    border-radius: 5px;
                    padding: 3px;
                }     
                QFrame[pass=true] {
                    background-color: #43CB5A;
                    border: 2px solid #EAEAEA;
                    border-radius: 5px;
                    padding: 3px;
                }   
                ''')

    def init_ui(self):
        self.setFont(QFont('Segoe UI'))

        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)

        self.setGeometry(0, 0, 620, 550)
        qtRectangle = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.setWindowTitle('Stock Standard Details')

        self.tabs = QTabWidget()

        date_label = QLabel('Date Made:')
        self.date_field = QDateEdit()

        curr_date = QDate.currentDate()
        self.date_field.setDate(curr_date)

        load_raps_label = QLabel('Load RAPS:')
        self.load_raps_path = QLineEdit()
        browse_raps = QPushButton('Browse')
        browse_raps.clicked.connect(self.browse_raps_path)

        save = QPushButton('Save')
        save.clicked.connect(self.save_fields)

        float_validate = QDoubleValidator()

        for nut in self.active_nutrients:
            setattr(self, "{}".format(nut + '_tab'), QWidget())
            self.tabs.addTab(getattr(self, "{}".format(nut + '_tab')), str(nut))

            setattr(self, "{}".format(nut + '_grid_layout'), QGridLayout())
            for r in range(14):
                getattr(self, "{}".format(nut + '_grid_layout')).setRowStretch(r, 1)
            getattr(self, "{}".format(nut + '_grid_layout')).setSpacing(10)

            getattr(self, "{}".format(nut + '_tab')).setLayout(getattr(self, "{}".format(nut + '_grid_layout')))

            setattr(self, "{}".format(nut + '_left_frame'), QFrame())
            getattr(self, "{}".format(nut + '_left_frame')).setProperty('left', True)

            setattr(self, "{}".format(nut + '_middle_frame'), QFrame())
            getattr(self, "{}".format(nut + '_middle_frame')).setProperty('middle', True)

            setattr(self, "{}".format(nut + '_pass_frame'), QFrame())
            getattr(self, "{}".format(nut + '_pass_frame')).setProperty('pass', True)

            setattr(self, "{}".format(nut + '_right_frame'), QFrame())
            getattr(self, "{}".format(nut + '_right_frame')).setProperty('right', True)

            setattr(self, "{}".format(nut + '_complete_label'), QLabel('Enter the following:'))

            setattr(self, "{}".format(nut + '_dried_label'), QLabel('Time Dried (hours):'))
            setattr(self, "{}".format(nut + '_time_dried'), QSpinBox())
            getattr(self, "{}".format(nut + '_time_dried')).setRange(0, 100)

            setattr(self, "{}".format(nut + '_mass_label'), QLabel('Mass Weighed (g):'))
            setattr(self, "{}".format(nut + '_mass_field'), QLineEdit())
            getattr(self, "{}".format(nut + '_mass_field')).setValidator(float_validate)

            setattr(self, "{}".format(nut + '_flask_label'), QLabel('Flask Used:'))
            setattr(self, "{}".format(nut + '_flask_field'), QLineEdit())

            setattr(self, "{}".format(nut + '_volume_label'), QLabel('Volume (mL):'))
            setattr(self, "{}".format(nut + '_volume_field'), QLineEdit())
            getattr(self, "{}".format(nut + '_volume_field')).setValidator(float_validate)

            setattr(self, "{}".format(nut + '_temp_label'), QLabel('Water Temp (C):'))
            setattr(self, "{}".format(nut + '_temp_field'), QLineEdit())
            getattr(self, "{}".format(nut + '_temp_field')).setValidator(float_validate)

            setattr(self, "{}".format(nut + '_location_label'), QLabel('Location: '))
            setattr(self, "{}".format(nut + '_location_combo'), QComboBox())
            getattr(self, "{}".format(nut + '_location_combo')).addItems(['Ship', 'Shore'])

            setattr(self, "{}".format(nut + '_ident_label'), QLabel('Ident:'))
            setattr(self, "{}".format(nut + '_ident_field'), QLineEdit())

            setattr(self, "{}".format(nut + '_old_cal_label'), QLabel('Old Cal 3 Results:'))
            setattr(self, "{}".format(nut + '_old_cal_table'), QTableWidget())

            setattr(self, "{}".format(nut + '_new_cal_label'), QLabel('New Cal 3 Results:'))
            setattr(self, "{}".format(nut + '_new_cal_table'), QTableWidget())

            setattr(self, "{}".format(nut + '_old_cal_mean_label'), QLabel('Old Cal 3 Mean: '))
            setattr(self, "{}".format(nut + '_old_cal_mean_field'), QLineEdit())

            setattr(self, "{}".format(nut + '_new_cal_mean_label'), QLabel('New Cal 3 Mean: '))
            setattr(self, "{}".format(nut + '_new_cal_mean_field'), QLineEdit())

            setattr(self, "{}".format(nut + '_error_label'), QLabel('Absolute Error: '))
            setattr(self, "{}".format(nut + '_error_field'), QLineEdit())

            setattr(self, "{}".format(nut + '_diff_pct_label'), QLabel('<b>Percent Diff: <b>'))
            setattr(self, "{}".format(nut + '_diff_pct_field'), QLineEdit())

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_left_frame')),
                                                                       0, 0, 13, 4)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_middle_frame')),
                                                                       0, 4, 13, 4)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_right_frame')),
                                                                       0, 8, 13, 4)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_pass_frame')),
                                                                       7, 8, 3, 4)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_complete_label')),
                                                                       1, 1)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_dried_label')),
                                                                       2, 1)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_time_dried')),
                                                                       2, 2)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_mass_label')),
                                                                       3, 1)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_mass_field')),
                                                                       3, 2)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_flask_label')),
                                                                       4, 1)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_flask_field')),
                                                                       4, 2)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_volume_label')), 5, 1)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_volume_field')), 5, 2)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_temp_label')),
                                                                       6, 1)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_temp_field')),
                                                                       6, 2)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_location_label')), 7, 1)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_location_combo')), 7, 2)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_ident_label')),
                                                                       8, 1)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_ident_field')),
                                                                       8, 2)


            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_old_cal_label')), 1, 5, 1, 1)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_old_cal_table')), 2, 5, 10, 1)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_new_cal_label')), 1, 6, 1, 1)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_new_cal_table')), 2, 6, 10, 1)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_old_cal_mean_label')), 1, 9)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_old_cal_mean_field')), 2, 9)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_new_cal_mean_label')), 3, 9)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_new_cal_mean_field')), 4, 9)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_error_label')), 5, 9)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_error_field')), 6, 9)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_diff_pct_label')), 7, 9)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_diff_pct_field')), 8, 9)


        grid_layout.addWidget(date_label, 0, 0)
        grid_layout.addWidget(self.date_field, 0, 1)

        grid_layout.addWidget(self.tabs, 1, 0, 1, 4)

        grid_layout.addWidget(load_raps_label, 2, 0)
        grid_layout.addWidget(self.load_raps_path, 2, 1, 1, 2)
        grid_layout.addWidget(browse_raps, 2, 3)

        grid_layout.addWidget(save, 3, 3)

        self.centralWidget().setLayout(grid_layout)



    def calculations(self):

        for nut in self.active_nutrients:
            setattr(self, "{}".format(nut + '_cal_three_old'),
                    self.data_df.loc[(self.data_df['SampleIDs'].isin(cal_three_old_variants)) &
                                     (self.data_df['Analyte'] == nut)])

            setattr(self, "{}".format(nut + '_cal_three_new'),
                    self.data_df.loc[(self.data_df['SampleIDs'].isin(cal_three_new_variants)) &
                                     (self.data_df['Analyte'] == nut)])
            setattr(self, "{}".format(nut + '_cal_three_old_mean'),
                    statistics.mean(
                        [float(x) for x in getattr(self, "{}".format(nut + '_cal_three_old'))['Concentration']]))

            setattr(self, "{}".format(nut + '_cal_three_new_mean'),
                    statistics.mean(
                        [float(x) for x in getattr(self, "{}".format(nut + '_cal_three_new'))['Concentration']]))

            setattr(self, "{}".format(nut + '_error'), abs(getattr(self, "{}".format(nut + '_cal_three_old_mean')) - getattr(self, "{}".format(
                nut + '_cal_three_new_mean'))))

            setattr(self, "{}".format(nut + '_percentage'), (getattr(self, "{}".format(nut + '_error')) / getattr(self, "{}".format(nut + '_cal_three_old_mean'))) * 100)


    def extract_rmns(self):
        for nut in self.active_nutrients:
            setattr(self, "{}".format(nut + '_rmns'), self.data_df.loc[(self.data_df['SampleIDs'].str.contains('RMNS')) &
                                                                   (self.data_df['Analyte'] == nut)])
            print(getattr(self, "{}".format(nut + '_rmns')))

    def populate_tables(self):
        for nut in self.active_nutrients:
            getattr(self, "{}".format(nut + '_old_cal_table')).setColumnCount(1)
            getattr(self, "{}".format(nut + '_old_cal_table')).setHorizontalHeaderLabels(['Conc'])
            getattr(self, "{}".format(nut + '_old_cal_table')).setRowCount(
                len(getattr(self, "{}".format(nut + '_cal_three_old'))['Concentration']))

            getattr(self, "{}".format(nut + '_new_cal_table')).setColumnCount(1)
            getattr(self, "{}".format(nut + '_new_cal_table')).setHorizontalHeaderLabels(['Conc'])
            getattr(self, "{}".format(nut + '_new_cal_table')).setRowCount(
                len(getattr(self, "{}".format(nut + '_cal_three_new'))['Concentration']))

            for i, x in enumerate(getattr(self, "{}".format(nut + '_cal_three_old'))['Concentration']):
                getattr(self, "{}".format(nut + '_old_cal_table')).setItem(i, 0, QTableWidgetItem(str(x)))

            for i, x in enumerate(getattr(self, "{}".format(nut + '_cal_three_new'))['Concentration']):
                getattr(self, "{}".format(nut + '_new_cal_table')).setItem(i, 0, QTableWidgetItem(str(x)))

            getattr(self, "{}".format(nut + '_old_cal_mean_field')).setText(str(round(getattr(self, "{}".format(nut + '_cal_three_old_mean')), 3)))
            getattr(self, "{}".format(nut + '_old_cal_mean_field')).setReadOnly(True)
            getattr(self, "{}".format(nut + '_new_cal_mean_field')).setText(str(round(getattr(self, "{}".format(nut + '_cal_three_new_mean')), 3)))
            getattr(self, "{}".format(nut + '_new_cal_mean_field')).setReadOnly(True)
            getattr(self, "{}".format(nut + '_error_field')).setText(str(round(getattr(self, "{}".format(nut + '_error')), 3)))
            getattr(self, "{}".format(nut + '_error_field')).setReadOnly(True)
            getattr(self, "{}".format(nut + '_diff_pct_field')).setText(str(round(getattr(self, "{}".format(nut + '_percentage')), 3)))
            getattr(self, "{}".format(nut + '_error_field')).setReadOnly(True)

    def determine_pass(self):
        for nut in self.active_nutrients:
            perc = getattr(self, "{}".format(nut + '_percentage'))
            if getattr(self, "{}".format(nut + '_error')) > 0.02 or (getattr(self, "{}".format(nut + '_error')) > 0.2 and nut == 'Silicate'):
                if nut != 'Ammonia':
                    if perc < 1:
                        pass
                    elif perc > 1 and perc < 2:
                        getattr(self, "{}".format(nut + '_pass_frame')).setStyleSheet('''QFrame[pass=true]{background-color: #E4A415;}''')
                    elif perc > 2:
                        getattr(self, "{}".format(nut + '_pass_frame')).setStyleSheet('''QFrame[pass=true]{background-color: #CB4F46;}''')

                if nut == 'Ammonia':
                    if perc < 2:
                        pass
                    elif perc > 2 and perc < 3:
                        getattr(self, "{}".format(nut + '_pass_frame')).setStyleSheet('''QFrame[pass=true]{background-color: #E4A415;}''')
                    elif perc > 3:
                        getattr(self, "{}".format(nut + '_pass_frame')).setStyleSheet('''QFrame[pass=true]{background-color: #CB4F46;}''')

    def validate_fields(self):
        complete = True
        for nut in self.active_nutrients:
            for field in fields_list:
                if getattr(self, "{}".format(nut + field)).text() == '':
                    messagebox = QMessageBox(QMessageBox.Information, 'Error',
                                            'One of the required fields is empty',
                                            buttons=QMessageBox.Ok, parent=self)
                    messagebox.setFont(QFont('Segoe UI'))
                    messagebox.setStyleSheet('QLabel { font: 15px; } QPushButton { width: 50px; font: 15px; }')
                    messagebox.exec_()
                    complete = False
                    break

                if field == '_mass_field' or field == 'volume_field' or field == 'temp_field':
                    val = getattr(self, "{}".format(nut + field)).text()
                    try:
                        check = float(val)
                    except ValueError:
                        messagebox = QMessageBox(QMessageBox.Information, 'Error',
                                                 'A value other than a number has been entered into: ' + field,
                                                 buttons=QMessageBox.Ok, parent=self)
                        messagebox.setFont(QFont('Segoe UI'))
                        messagebox.setStyleSheet('QLabel { font: 15px; } QPushButton { width: 50px; font: 15px; }')
                        messagebox.exec_()
                        complete = False
                        break
            if not complete:
                # Break because we have already found 1 missing field
                break

        return complete

    def save_fields(self):
        appdata_path = os.getenv('LOCALAPPDATA')
        with open(appdata_path + '/' + 'Stocks Tracker' + '/' + 'path_memory.txt', 'r') as file:
            reader = file.read()

        conn = sqlite3.connect(reader)
        c = conn.cursor()

        complete = self.validate_fields()
        #complete = True

        if complete:

            date = str(self.date_field.date().toPyDate())

            print(date)
            for nut in self.active_nutrients:
                time_dried = getattr(self, "{}".format(nut + '_time_dried')).value()
                mass = getattr(self, "{}".format(nut + '_mass_field')).text()
                flask = getattr(self, "{}".format(nut + '_flask_field')).text()
                volume = getattr(self, "{}".format(nut + '_volume_field')).text()
                temp = getattr(self, "{}".format(nut + '_temp_field')).text()
                ident = getattr(self, "{}".format(nut + '_ident_field')).text()

                lab = getattr(self, "{}".format(nut + '_location_combo')).currentText()

                package = (date, time_dried, nut, mass, volume, flask, temp, lab, ident)

                c.execute('INSERT or REPLACE into stockInformation VALUES (?,?,?,?,?,?,?,?,?)', package)

                for cal3 in ['_cal_three_old', '_cal_three_new']:
                    concentrations = getattr(self, "{}".format(nut + cal3))['Concentration']
                    peak_heights = getattr(self, "{}".format(nut + cal3))['PeakHeight']
                    nutrient = getattr(self, "{}".format(nut + cal3))['Analyte']
                    peak_number = getattr(self, "{}".format(nut + cal3))['PeakNumber']
                    sample_id = getattr(self, "{}".format(nut + cal3))['SampleIDs']

                    date_list = [date for x in concentrations]

                    package = tuple(zip(date_list, nutrient, sample_id, peak_number, concentrations, peak_heights))
                    print(package)
                    c.executemany('INSERT or REPLACE into calThreeMeasurements VALUES (?,?,?,?,?,?)', package)

                sample_id = getattr(self, "{}".format(nut + '_rmns'))['SampleIDs']
                peak_number = getattr(self, "{}".format(nut + '_rmns'))['PeakNumber']
                nutrient = getattr(self, "{}".format(nut + '_rmns'))['Analyte']
                peak_height = getattr(self, "{}".format(nut + '_rmns'))['PeakHeight']
                concentration = getattr(self, "{}".format(nut + '_rmns'))['Concentration']
                date_list = [date for x in sample_id]

                package = tuple(zip(date_list, nutrient, sample_id, peak_number, concentration, peak_height))

                c.executemany('INSERT or REPLACE into rmnsMeasurements VALUES (?,?,?,?,?,?)', package)


            conn.commit()
            conn.close()

            messagebox = QMessageBox(QMessageBox.Information, 'Success',
                                     'Data successfully saved to the database.',
                                     buttons=QMessageBox.Ok, parent=self)
            messagebox.setFont(QFont('Segoe UI'))
            messagebox.setStyleSheet('QLabel { font: 15px; } QPushButton { width: 50px; font: 15px; }')
            messagebox.exec_()

            sleep(0.3)

            self.close()

    def browse_raps_path(self):
        dia = QFileDialog.getOpenFileName(self, 'Open RAPS', 'C:/', 'PDF (*.pdf)')
        if dia[0]:
            self.load_raps_path.setText(dia[0])


