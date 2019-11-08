import sqlite3
import sys
import os
import csv
import pandas as pd

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (QMainWindow, QWidget, QGridLayout, QApplication, QLabel, QPushButton, QLineEdit,
                             QListWidget, QAction, QFileDialog, QMessageBox)


class newEntry(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('assets/icon.svg'))
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.init_ui()

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

        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)

        self.setGeometry(0, 0, 400, 300)
        qtRectangle = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.setWindowTitle('New Stock Standard')

        load_qc_table_label = QLabel('Load QC Table from HyPro:')

        self.qc_table_path_field = QLineEdit()

        qc_table_browse = QPushButton('Browse')
        qc_table_browse.clicked.connect(self.qc_table_browse_path)

        qc_table_load = QPushButton('Load')
        qc_table_load.clicked.connect(self.load_qc_table)


        grid_layout.addWidget(load_qc_table_label, 0, 0, 1, 2)
        grid_layout.addWidget(self.qc_table_path_field, 1, 0)
        grid_layout.addWidget(qc_table_browse, 1, 1)

        grid_layout.addWidget(qc_table_load, 2, 0, 1, 2)

        self.centralWidget().setLayout(grid_layout)

        self.show()


    def qc_table_browse_path(self):
        dia = QFileDialog.getOpenFileName(self, 'Open QCTable', 'C:/', 'CSV (*.csv)')
        if dia[0]:
            self.qc_table_path_field.setText(dia[0])

    def load_qc_table(self):
        with open(self.qc_table_path_field.text(), 'r') as file:
            csv_read = csv.reader(file)

            sample_ids = [x[4] for x in csv_read]
            peak_number = [x[5] for x in csv_read]
            analyte = [x[6] for x in csv_read]
            peak_height = [x[7] for x in csv_read]
            concentration = [x[8] for x in csv_read]

            data_df = pd.DataFrame((sample_ids, peak_number, analyte, peak_height, concentration),
                                   columns=['SampleIDs', 'PeakNumber', 'Analyte', 'PeakHeight', 'Concentration'])
