import sqlite3
import sys
import os
import pandas
import pandas as pd

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (QMainWindow, QWidget, QGridLayout, QApplication, QLabel, QPushButton, QLineEdit,
                             QListWidget, QAction, QFileDialog, QMessageBox, QFrame)
from SST_New_Entry import newEntry
from SST_Plots import plotterWindow

import icons

class stocksTracker(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(':/assets/stockflask.svg'))
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

        self.setGeometry(0, 0, 385, 750)
        qtRectangle = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')
        plot_menu = menu_bar.addMenu('Plots')

        create_new_db = QAction('Create Database', self)
        create_new_db.triggered.connect(self.create_database)
        file_menu.addAction(create_new_db)

        self.create_plots = QAction('View Plots', self)
        self.create_plots.triggered.connect(self.generate_plots)
        plot_menu.addAction(self.create_plots)

        self.create_plots.setDisabled(True)

        self.setWindowTitle('Nutrient Stock Standard Tracker')

        database_path_label = QLabel('Path to Database File:')

        self.database_path_field = QLineEdit()

        database_browse = QPushButton('Browse')
        database_browse.clicked.connect(self.path_browse)

        linesep1 = QFrame()
        linesep1.setFrameShape(QFrame.HLine)
        linesep1.setFrameShadow(QFrame.Sunken)

        past_entries_label = QLabel('Previous Entries: ')

        self.standard_entries = QListWidget()

        self.view_entry = QPushButton('View')

        self.view_entry.setDisabled(True)

        self.new_entry = QPushButton('New')
        self.new_entry.clicked.connect(self.enter_new)
        self.new_entry.setDisabled(True)

        grid_layout.addWidget(database_path_label, 0, 0, 1, 2)
        grid_layout.addWidget(self.database_path_field, 1, 0, 1, 2)
        grid_layout.addWidget(database_browse, 2, 1, 1, 1)

        grid_layout.addWidget(linesep1, 3, 0, 1, 2)

        grid_layout.addWidget(past_entries_label, 4, 0, 1, 2)
        grid_layout.addWidget(self.standard_entries, 5, 0, 8, 2)

        grid_layout.addWidget(self.view_entry, 13, 0, 1, 2)
        grid_layout.addWidget(self.new_entry, 14, 0, 1, 2)

        self.centralWidget().setLayout(grid_layout)

        appdata_path = os.getenv('LOCALAPPDATA')

        if os.path.isdir(appdata_path + '/' + 'Stocks Tracker'):
            if os.path.isfile(appdata_path + '/' + 'Stocks Tracker' + '/' + 'path_memory.txt'):
                with open(appdata_path + '/' + 'Stocks Tracker' + '/' + 'path_memory.txt', 'r') as file:
                    remembered_path = file.read()
                    self.database_path_field.setText(remembered_path)
                    self.populate_list()

        else:
            os.mkdir(appdata_path + '/' + 'Stocks Tracker')
            with open(appdata_path + '/' + 'Stocks Tracker' + '/' + 'path_memory.txt', 'w+') as file:
                pass

        self.show()

    def enter_new(self):
        self.new = newEntry()

    def generate_plots(self):
        self.plot = plotterWindow()

    def populate_list(self):
        db_path = self.database_path_field.text()
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()

            stock_info = pd.read_sql_query('SELECT * from stockInformation ORDER BY date', conn)

            print(stock_info)

            if len(stock_info) > 0:
                unique_stocks = stock_info.drop_duplicates(['resultsFile', 'lab'])

                for entry in unique_stocks.iterrows():
                    nuts_in_entry = []
                    #nuts_in_entry.append(entry[1]['date'])
                    for all_entries in stock_info.iterrows():
                        if entry[1]['resultsFile'] == all_entries[1]['resultsFile'] and entry[1]['lab'] == all_entries[1]['lab']:
                            nuts_in_entry.append("    ∟ " + all_entries[1]['date'] + ': ' + all_entries[1]['nutrient'] + '\n')

                    entry_string = str(entry[1]['resultsFile']) + ': \n'
                    nut_string = "".join(nuts_in_entry)
                    self.standard_entries.addItem(entry_string + nut_string)

            self.view_entry.setEnabled(True)
            self.new_entry.setEnabled(True)
            self.create_plots.setEnabled(True)

            c.close()

        except sqlite3.Error:
            pass
        except pandas.io.sql.DatabaseError:
            pass

    def path_browse(self):
        """
        Allows the user to browse for the path of the Database file
        :return:
        """
        dia = QFileDialog.getOpenFileName(self, 'Open Database', 'C:/', 'Database (*.db)')
        if dia[0]:
            self.standard_entries.clear()
            self.database_path_field.setText(dia[0])
            appdata_path = os.getenv('LOCALAPPDATA')
            with open(appdata_path + '/' + 'Stocks Tracker' + '/' + 'path_memory.txt', 'w+') as file:
                file.write(dia[0])

            self.populate_list()


    def create_database(self):
        """
        Creates a database file in the location specified, if one is not already created.
        :return:
        """
        dia = QFileDialog.getSaveFileName(self, 'Create Database File', '', '.db')
        print(dia)
        if dia[0]:
            conn = sqlite3.connect(dia[0] + dia[1])

            c = conn.cursor()

            c.execute('''CREATE TABLE IF NOT EXISTS stockInformation
                      (date TEXT,
                      resultsFile TEXT,
                      timeDried INTEGER,
                      nutrient TEXT,
                      mass FLOAT,
                      volume FLOAT,
                      flask TEXT,
                      temp FLOAT,
                      lab TEXT,
                      ident TEXT,
                      UNIQUE(date, nutrient, mass, lab))''')

            c.execute('''CREATE TABLE IF NOT EXISTS calThreeMeasurements
                      (date TEXT,
                      resultsFile TEXT,
                      nutrient TEXT, 
                      id TEXT,
                      peakNumber INTEGER,
                      concentration FLOAT,
                      peakHeight FLOAT,
                      UNIQUE(date, nutrient, peakNumber))''')

            c.execute('''CREATE TABLE IF NOT EXISTS rmnsMeasurements 
                    (date TEXT,
                    resultsFile TEXT,
                    nutrient TEXT,
                    id TEXT,
                    peakNumber INTEGER,
                    concentration FLOAT,
                    peakHeight FLOAT,
                    UNIQUE(date, nutrient, peakNumber))''')
            c.execute('''CREATE TABLE IF NOT EXISTS rmnsValues 
                    (rmnsLot TEXT,
                    nitrateConc FLOAT,
                    nitrateError FLOAT,
                    phosphateConc FLOAT,
                    phosphateError FLOAT,
                    silicateConc FLOAT,
                    silicateError FLOAT,
                    nitriteConc FLOAT,
                    nitriteError FLOAT,
                    UNIQUE(rmnsLot))''')

            c.close()

            messagebox = QMessageBox(QMessageBox.Information, 'Success',
                                     "Database file created succesfully",
                                     buttons=QMessageBox.Ok, parent=self)
            messagebox.setFont(QFont('Segoe UI'))
            messagebox.setStyleSheet('QLabel { font: 15px; } QPushButton { font: 15px; }')
            messagebox.exec_()

            self.database_path_field.setText(dia[0] + dia[1])
            appdata_path = os.getenv('LOCALAPPDATA')
            with open(appdata_path + '/' + 'Stocks Tracker' + '/' + 'path_memory.txt', 'w+') as file:
                file.write(dia[0] + dia[1])

            self.populate_list()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = stocksTracker()
    sys.exit(app.exec_())
