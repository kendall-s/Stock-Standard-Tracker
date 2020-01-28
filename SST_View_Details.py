import statistics
import os
import sqlite3
import pandas as pd
from time import sleep
import time, calendar
import datetime

from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QDoubleValidator
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QGridLayout, QApplication, QLabel, QPushButton, QLineEdit,
                             QComboBox, QFileDialog, QTabWidget, QDateEdit, QSpinBox, QTableWidgetItem,
                             QTableWidget, QFrame, QMessageBox, QCheckBox)
import icons


class viewDetails(QMainWindow):

    def __init__(self, stock_info, cal_threes):
        super().__init__()
        self.setWindowIcon(QIcon(':/assets/stockflask.svg'))
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.stock_info = stock_info
        print(stock_info)
        self.cal_threes = cal_threes

        self.active_nutrients = list(self.stock_info['nutrient'])
        print(self.active_nutrients)

        self.init_ui()

        try:
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
                    background-color: #FBFBFB;
                    border: 1px solid #EAEAEA;
                    border-radius: 5px;
                    padding: 3px;
                } 
                QFrame[middle=true] {
                    background-color: #FBFBFB;
                    border: 1px solid #EAEAEA;
                    border-radius: 5px;
                    padding: 3px;
                }
                QFrame[right=true] {
                    background-color: #FBFBFB;
                    border: 1px solid #EAEAEA;
                    border-radius: 5px;
                    padding: 3px;
                }     
                QFrame[pass=true] {
                    background-color: #43CB5A;
                    border: 1px solid #EAEAEA;
                    border-radius: 5px;
                    padding: 3px;
                }  
                QLineEdit[pass=true] {
                    background-color: #43CB5A;

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

        close = QPushButton('Close')

        float_validate = QDoubleValidator()

        for nut in self.active_nutrients:

            date = list(self.stock_info['date'].loc[self.stock_info['nutrient'] == nut])
            time_dried = list(self.stock_info['timeDried'].loc[self.stock_info['nutrient'] == nut])
            mass = list(self.stock_info['mass'].loc[self.stock_info['nutrient'] == nut])
            volume = list(self.stock_info['volume'].loc[self.stock_info['nutrient'] == nut])
            flask = list(self.stock_info['flask'].loc[self.stock_info['nutrient'] == nut])
            temp = list(self.stock_info['temp'].loc[self.stock_info['nutrient'] == nut])
            lab = list(self.stock_info['lab'].loc[self.stock_info['nutrient'] == nut])
            ident = list(self.stock_info['ident'].loc[self.stock_info['nutrient'] == nut])

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

            setattr(self, "{}".format(nut + '_ignore_check'), QCheckBox('Ignore analyte?'))
            getattr(self, "{}".format(nut + '_ignore_check')).setDisabled(True)

            setattr(self, "{}".format(nut + '_date_label'), QLabel('Date Made:'))
            setattr(self, "{}".format(nut + '_date_field'), QDateEdit())

            setattr(self, "{}".format(nut + '_complete_label'), QLabel('<b>Enter the following:<b>'))

            setattr(self, "{}".format(nut + '_dried_label'), QLabel('Time Dried (hours):'))
            setattr(self, "{}".format(nut + '_time_dried'), QSpinBox())
            getattr(self, "{}".format(nut + '_time_dried')).setRange(0, 200)
            getattr(self, "{}".format(nut + '_time_dried')).setValue(int(time_dried[0]))

            setattr(self, "{}".format(nut + '_mass_label'), QLabel('Mass Weighed (g):'))
            setattr(self, "{}".format(nut + '_mass_field'), QLineEdit())
            getattr(self, "{}".format(nut + '_mass_field')).setValidator(float_validate)
            getattr(self, "{}".format(nut + '_mass_field')).setText(str(mass[0]))

            setattr(self, "{}".format(nut + '_flask_label'), QLabel('Flask Used:'))
            setattr(self, "{}".format(nut + '_flask_field'), QLineEdit())
            getattr(self, "{}".format(nut + '_flask_field')).setText(flask[0])

            setattr(self, "{}".format(nut + '_volume_label'), QLabel('Volume (mL):'))
            setattr(self, "{}".format(nut + '_volume_field'), QLineEdit())
            getattr(self, "{}".format(nut + '_volume_field')).setValidator(float_validate)
            getattr(self, "{}".format(nut + '_volume_field')).setText(str(volume[0]))

            setattr(self, "{}".format(nut + '_temp_label'), QLabel('Water Temp (C):'))
            setattr(self, "{}".format(nut + '_temp_field'), QLineEdit())
            getattr(self, "{}".format(nut + '_temp_field')).setValidator(float_validate)
            getattr(self, "{}".format(nut + '_temp_field')).setText(str(temp[0]))

            setattr(self, "{}".format(nut + '_location_label'), QLabel('Location: '))
            setattr(self, "{}".format(nut + '_location_combo'), QLineEdit())
            getattr(self, "{}".format(nut + '_location_combo')).setText(lab[0])

            setattr(self, "{}".format(nut + '_ident_label'), QLabel('Ident:'))
            setattr(self, "{}".format(nut + '_ident_field'), QLineEdit())
            getattr(self, "{}".format(nut + '_ident_field')).setText(ident[0])

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

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_middle_frame')),
                0, 4, 13, 4)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_right_frame')),
                                                                       0, 8, 13, 4)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_pass_frame')),
                                                                       8, 8, 3, 4)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_ignore_check')), 1, 1, 1, 2, Qt.AlignCenter)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_complete_label')),
                2, 1)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_date_label')),
                                                                       3, 1)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_date_field')),
                                                                       3, 2)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_dried_label')),
                                                                       4, 1)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_time_dried')),
                                                                       4, 2)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_mass_label')),
                                                                       5, 1)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_mass_field')),
                                                                       5, 2)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_flask_label')),
                                                                       6, 1)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_flask_field')),
                                                                       6, 2)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_volume_label')), 7, 1)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_volume_field')), 7, 2)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_temp_label')),
                                                                       8, 1)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_temp_field')),
                                                                       8, 2)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_location_label')), 9, 1)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_location_combo')), 9, 2)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_ident_label')),
                                                                       10, 1)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_ident_field')),
                                                                       10, 2)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_old_cal_label')), 1, 5, 1, 1)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_old_cal_table')), 2, 5, 10, 1)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_new_cal_label')), 1, 6, 1, 1)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_new_cal_table')), 2, 6, 10, 1)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_old_cal_mean_label')), 1, 9)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_old_cal_mean_field')), 2, 9)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_new_cal_mean_label')), 3, 9)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_new_cal_mean_field')), 4, 9)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_error_label')),
                                                                       5, 9)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(getattr(self, "{}".format(nut + '_error_field')),
                                                                       6, 9)

            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_diff_pct_label')), 8, 9)
            getattr(self, "{}".format(nut + '_grid_layout')).addWidget(
                getattr(self, "{}".format(nut + '_diff_pct_field')), 9, 9)

        grid_layout.addWidget(self.tabs, 1, 0, 1, 4)

        grid_layout.addWidget(close, 3, 3)

        self.centralWidget().setLayout(grid_layout)



