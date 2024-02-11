import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QWidget, QMessageBox


class DBCoffee(QMainWindow):
    def __init__(self):
        super(DBCoffee, self).__init__()
        uic.loadUi('main.ui', self)
        self.con = sqlite3.connect('coffee.sqlite')
        self.updateButton.clicked.connect(self.select_data)
        self.editButton.clicked.connect(self.open_edit_form)
        self.textEdit.setPlainText('SELECT * FROM Coffee')
        self.header = None
        self.edit_form = AddEditCoffee(self.con, self.statusBar)
        self.select_data()

    def open_edit_form(self):
        self.edit_form.show()

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

    def closeEvent(self, event):
        self.con.close()


class AddEditCoffee(QWidget):
    def __init__(self, connection, status):
        super(AddEditCoffee, self).__init__()
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.con = connection
        self.statusBar = status
        self.check_boxes = [
            self.checkBox,
            self.checkBox_2,
            self.checkBox_3,
            self.checkBox_4,
            self.checkBox_5,
            self.checkBox_6,
            self.checkBox_7,
            self.checkBox_8
        ]
        for i in range(len(self.check_boxes)):
            self.check_boxes[i].hide()
        self.addButton.clicked.connect(self.add_data)
        self.changeButton.clicked.connect(self.item_changed)
        self.delButton.clicked.connect(self.delete_data)
        self.comboBox.currentTextChanged.connect(self.select_data)
        self.select_data()

    def select_data(self):
        for i in range(len(self.check_boxes)):
            self.check_boxes[i].hide()
        cur = self.con.cursor()
        res = cur.execute(f'SELECT * FROM '
                          f'{self.comboBox.currentText()}').fetchall()
        self.spinBox.setMaximum(len(res))
        header = [description[0] for description in cur.description]
        for i in range(len(res[0])):
            self.check_boxes[i].show()
            self.check_boxes[i].setText(header[i])

    def add_data(self):
        columns = []
        for check_box in self.check_boxes:
            if check_box.isChecked():
                columns.append(check_box.text())
        table = self.comboBox.currentText()
        columns = ", ".join(columns)
        values = ', '.join([f"'{val}'"
                            for val in self.lineEdit.text().split(', ')])
        cur = self.con.cursor()
        que = f'INSERT INTO {table}' \
              f'({columns}) ' \
              f'VALUES ({values})'
        cur.execute(que)
        self.con.commit()
        self.statusBar().showMessage(f'{table} добавлена запись в колонки: {columns}')

    def item_changed(self):
        cur = self.con.cursor()
        modified = {}
        table = self.comboBox.currentText()
        values = self.lineEdit.text().split(', ')
        for check_box in self.check_boxes:
            if check_box.isChecked():
                modified[check_box.text()] = values.pop(0)
        que = f"UPDATE {table} SET\n"
        que += ", ".join([f"{key}='{modified.get(key)}'"
                          for key in modified.keys()])
        que += "WHERE id = ?"
        cur.execute(que, (self.spinBox.text(),))
        self.con.commit()
        self.statusBar().showMessage(f'{table} изменена запись с ID: {self.spinBox.text()}')

    def delete_data(self):
        table = self.comboBox.currentText()
        row = self.spinBox.text()
        valid = QMessageBox.question(
            self, 'Подтверждение', "Действительно удалить элементы с id " + row,
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            cur = self.con.cursor()
            cur.execute(f"DELETE FROM {table} WHERE id = {row}")
            self.con.commit()
            self.statusBar().showMessage(f'{table} удалена запись с ID: {row}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    coffee = DBCoffee()
    coffee.show()
    sys.exit(app.exec())
