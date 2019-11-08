import sqlite3
import sys
import os

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (QMainWindow, QWidget, QGridLayout, QApplication, QLabel, QPushButton, QLineEdit,
                             QListWidget, QAction, QFileDialog, QMessageBox)
from SST_New_Entry import newEntry

class stocksTracker(QMainWindow):

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

        self.setGeometry(0, 0, 350, 600)
        qtRectangle = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')

        create_new_db = QAction('Create Database', self)
        create_new_db.triggered.connect(self.create_database)
        file_menu.addAction(create_new_db)

        self.setWindowTitle('Nutrient Stock Standard')

        database_path_label = QLabel('Path to Database File:')

        self.database_path_field = QLineEdit()

        appdata_path = os.getenv('LOCALAPPDATA')

        if os.path.isdir(appdata_path + '/' + 'Stocks Tracker'):
            if os.path.isfile(appdata_path + '/' + 'Stocks Tracker' + '/' + 'path_memory.txt'):
                with open(appdata_path + '/' + 'Stocks Tracker' + '/' + 'path_memory.txt', 'r') as file:
                    remembered_path = file.read()
                    self.database_path_field.setText(remembered_path)
        else:
            os.mkdir(appdata_path + '/' + 'Stocks Tracker')
            with open(appdata_path + '/' + 'Stocks Tracker' + '/' + 'path_memory.txt', 'w+') as file:
                pass

        database_browse = QPushButton('Browse')
        database_browse.clicked.connect(self.path_browse)

        self.standard_entries = QListWidget()

        self.view_entry = QPushButton('View')

        new_entry = QPushButton('New')
        new_entry.clicked.connect(self.enter_new)

        grid_layout.addWidget(database_path_label, 0, 0, 1, 2)
        grid_layout.addWidget(self.database_path_field, 1, 0)
        grid_layout.addWidget(database_browse, 1, 1)

        grid_layout.addWidget(self.standard_entries, 2, 0, 6, 2)

        grid_layout.addWidget(self.view_entry, 9, 0, 1, 2)
        grid_layout.addWidget(new_entry, 10, 0, 1, 2)

        self.centralWidget().setLayout(grid_layout)

        self.show()

    def enter_new(self):
        self.new = newEntry()


    def path_browse(self):
        dia = QFileDialog.getOpenFileName(self, 'Open Database', 'C:/', 'Database (*.db)')
        if dia[0]:
            self.database_path_field.setText(dia[0])
            appdata_path = os.getenv('LOCALAPPDATA')
            with open(appdata_path + '/' + 'Stocks Tracker' + '/' + 'path_memory.txt', 'w+') as file:
                file.write(dia[0])

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
                      timeDried INTEGER,
                      nutrient TEXT,
                      mass FLOAT,
                      volume FLOAT,
                      flask TEXT,
                      temp FLOAT,
                      lab TEXT,
                      ident TEXT,
                      UNIQUE(date, salt, weight))''')

            c.execute('''CREATE TABLE IF NOT EXISTS calThreeMeasurements
                      (date TEXT,
                      nutrient TEXT, 
                      id TEXT,
                      peakNumber INTEGER,
                      concentration FLOAT,
                      peakHeight FLOAT,
                      UNIQUE(date, salt, peakNumber))''')

            c.execute('''CREATE TABLE IF NOT EXISTS rmnsMeasurements 
                    (date TEXT,
                    nutrient TEXT,
                    id TEXT,
                    peakNumber INTEGER,
                    concentration FLOAT,
                    peakHeight FLOAT,
                    UNIQUE(date, salt, peakNumber))''')



            messagebox = QMessageBox(QMessageBox.Information, 'Success',
                                     "Database file created succesfully",
                                     buttons=QMessageBox.Ok, parent=self)
            messagebox.setFont(QFont('Segoe UI'))
            messagebox.setStyleSheet('QLabel { font: 15px; } QPushButton { font: 15px; }')
            messagebox.exec_()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = stocksTracker()
    sys.exit(app.exec_())
