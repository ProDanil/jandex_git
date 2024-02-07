import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem


class DBCoffee(QMainWindow):
    def __init__(self):
        super(DBCoffee, self).__init__()
        uic.loadUi('main.ui', self)
        self.con = sqlite3.connect('coffee.sqlite')
        self.pushButton.clicked.connect(self.select_data)
        self.textEdit.setPlainText('SELECT * FROM Coffee')
        self.select_data()

    def select_data(self):
        query = self.textEdit.toPlainText()
        res = self.con.cursor().execute(query).fetchall()
        header = query[7:query.index('FROM')].strip().split(', ')
        print(header)
        if header == ['*']:
            header = ['ID', 'name', 'variety', 'roasting', 'type', 'description', 'price', 'size']
        self.tableWidget.setColumnCount(len(header))
        self.tableWidget.setHorizontalHeaderLabels(header)
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))

    def closeEvent(self, event):
        self.con.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    coffee = DBCoffee()
    coffee.show()
    sys.exit(app.exec())
