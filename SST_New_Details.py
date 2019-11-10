import statistics
import os
import sqlite3

from PyQt5.QtGui import QIcon, QFont, QColor, QPalette
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (QMainWindow, QWidget, QGridLayout, QApplication, QLabel, QPushButton, QLineEdit,
                             QComboBox, QFileDialog, QTabWidget, QDateEdit, QSpinBox, QTableWidgetItem,
                             QTableWidget, QFrame)

cal_three_old_variants = ['Cal 3 old', 'Cal 3 Old', 'Cal 3Old', 'Cal 3old', 'Old Cal 3',
                          'old Cal 3', 'Cal3 Old', 'Cal3 old']
cal_three_new_variants = ['Cal 3 new', 'Cal 3 New', 'Cal 3New', 'Cal 3new', 'New Cal 3',
                          'new Cal 3', 'Cal3 New', 'Cal3 new']


class newDetails(QMainWindow):

    def __init__(self, active_nutrients, data_df):
        super().__init__()
        self.setWindowIcon(QIcon('assets/icon.svg'))
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.active_nutrients = active_nutrients
        self.data_df = data_df

        self.init_ui()

        self.calculations()

        self.populate_tables()

        self.determine_pass()

        self.setStyleSheet('''
                QLabel {
                    font: 14px;
                    padding: 2px;
                }   
                QPushButton {
                    font: 14px;
                    padding: 2px;
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

        self.setGeometry(0, 0, 620, 385)
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

        for nut in self.active_nutrients:
            setattr(self, "{}".format(nut + '_tab'), QWidget())
            self.tabs.addTab(getattr(self, "{}".format(nut + '_tab')), str(nut))

            setattr(self, "{}".format(nut + '_grid_layout'), QGridLayout())
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

            setattr(self, "{}".format(nut + '_flask_label'), QLabel('Flask Used:'))
            setattr(self, "{}".format(nut + '_flask_field'), QLineEdit())

            setattr(self, "{}".format(nut + '_volume_label'), QLabel('Volume (mL):'))
            setattr(self, "{}".format(nut + '_volume_field'), QLineEdit())

            setattr(self, "{}".format(nut + '_temp_label'), QLabel('Water Temp (C):'))
            setattr(self, "{}".format(nut + '_temp_field'), QLineEdit())

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

            setattr(self, "{}".format(nut + '_diff_pct_label'), QLabel('Percent Diff: '))
            setattr(self, "{}".format(nut + '_diff_pct_field'), QLineEdit())

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_left_frame')),
                                                                       0, 0, 10, 4)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_middle_frame')),
                                                                       0, 4, 10, 4)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_right_frame')),
                                                                       0, 8, 10, 4)

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
                getattr(self, "{}".format(nut + '_old_cal_table')), 2, 5, 7, 1)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_new_cal_label')), 1, 6, 1, 1)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_new_cal_table')), 2, 6, 7, 1)

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

        self.show()


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
            print(nut)
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


    def save_fields(self):
        appdata_path = os.getenv('LOCALAPPDATA')
        with open(appdata_path + '/' + 'Stocks Tracker' + '/' + 'path_memory.txt', 'w+') as file:
            reader = file.read()
        db_path = reader[0]

        conn = sqlite3.connect(db_path)
        c = conn.cursor()


    def browse_raps_path(self):
        dia = QFileDialog.getOpenFileName(self, 'Open RAPS', 'C:/', 'PDF (*.pdf)')
        if dia[0]:
            self.load_raps_path.setText(dia[0])


