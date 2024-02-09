import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem


class DBCoffee(QMainWindow):
    def __init__(self):
        super(DBCoffee, self).__init__()
        self.modified = {}
        self.id_row = None
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.con = sqlite3.connect('coffee.sqlite')
        self.updateButton.clicked.connect(self.select_data)
        self.saveButton.clicked.connect(self.save_results)
        self.tableWidget.itemChanged.connect(self.item_changed)
        self.textEdit.setPlainText('SELECT * FROM Coffee')
        self.header = None
        self.select_data()

    def select_data(self):
        query = self.textEdit.toPlainText()
        cur = self.con.cursor()
        res = cur.execute(query).fetchall()
        self.tableWidget.setRowCount(len(res))
        if not res:
            self.statusBar().showMessage('Ничего не нашлось')
            return
        else:
            self.statusBar().showMessage(f'Количество строк по запросу: {len(res)}')
        self.tableWidget.setColumnCount(len(res[0]))
        self.header = [description[0] for description in cur.description]
        self.tableWidget.setHorizontalHeaderLabels(self.header)
        for i, row in enumerate(res):
            for j, elem in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))
        self.modified = {}

    def item_changed(self, item):
        if 'ID' in self.header:
            self.modified[self.header[item.column()]] = item.text()
            self.id_row = self.tableWidget.item(item.row(), self.header.index('ID')).text()

    def save_results(self):
        if self.modified:
            cur = self.con.cursor()
            query = 'UPDATE Coffee SET\n'
            titles = ', '.join([f"{col}='{self.modified.get(col)}'"
                               for col in self.modified.keys()])
            query += titles + f"WHERE ID = {self.id_row}"
            cur.execute(query)
            self.con.commit()
            self.modified.clear()
            self.statusBar().showMessage(f'Изменения в {titles} c ID: {self.id_row} сохранены')
        elif 'ID' not in self.header:
            self.statusBar().showMessage('Для изменения добавте колонку с ID')
        else:
            self.statusBar().showMessage('Изменений не обнаружено')

    def closeEvent(self, event):
        self.con.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    coffee = DBCoffee()
    coffee.show()
    sys.exit(app.exec())
