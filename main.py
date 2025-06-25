from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt
from ui_qrtag import Ui_MainWindow
from string import ascii_uppercase
from PyQt5.QtCore import QObject, QEvent, Qt

class DigitOnlyFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            key = event.key()
            text = event.text()
          
            if text in "0123456789" or key in (
                Qt.Key_Backspace, Qt.Key_Delete,
                Qt.Key_Left, Qt.Key_Right,
                Qt.Key_Home, Qt.Key_End,
                Qt.Key_Tab, Qt.Key_Return, Qt.Key_Enter
            ):
                return False 
            else:
                return True  

        return False
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            key = event.key()
            text = event.text()
            
            if text.isdigit() or key in (
                Qt.Key_Backspace, Qt.Key_Delete,
                Qt.Key_Left, Qt.Key_Right,
                Qt.Key_Home, Qt.Key_End,
                Qt.Key_Tab, Qt.Key_Return, Qt.Key_Enter
            ):
                return False  
            else:
                return True  
        return False  

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
       
        self.ui.checkBox.setChecked(True)
        self.limit_plainTextEdit_length(True)
       
        self.digit_filter = DigitOnlyFilter(self)
        self.ui.plainTextEdit.installEventFilter(self.digit_filter)
        self.ui.plainTextEdit.textChanged.connect(self.clean_plainTextEdit)

        self.ui.checkBox.toggled.connect(self.on_sku_toggled)
        self.ui.plainTextEdit.textChanged.connect(self.on_plainTextEdit_changed)

        self.allowed_letters = list(ascii_uppercase)
        self.ui.comboBox.setEditable(True)
        self.ui.comboBox.clear()
        self.ui.comboBox.addItem("")  
        self.ui.comboBox.addItems(self.allowed_letters)
        self.ui.comboBox.setCurrentIndex(-1)  
       
        self.ui.comboBox.lineEdit().textEdited.connect(self.on_letter_edited)
        self.ui.comboBox.currentIndexChanged.connect(self.update_code)
        self.ui.comboBox.lineEdit().textChanged.connect(self.update_code)

        # Karat
        self.ui.radioButton.toggled.connect(self.update_code)
        self.ui.radioButton_2.toggled.connect(self.update_code)
        self.ui.radioButton_6.toggled.connect(self.update_code)
        self.ui.radioButton_5.toggled.connect(self.update_code)
        self.ui.radioButton_4.toggled.connect(self.update_code)
        self.ui.radioButton_3.toggled.connect(self.update_code)

        # Color
        self.ui.radioButton_7.toggled.connect(self.update_code)
        self.ui.radioButton_8.toggled.connect(self.update_code)
        self.ui.radioButton_10.toggled.connect(self.update_code)
        self.ui.radioButton_9.toggled.connect(self.update_code)
        self.ui.radioButton_11.toggled.connect(self.update_code)
        self.ui.radioButton_13.toggled.connect(self.update_code)
        self.ui.radioButton_14.toggled.connect(self.update_code)
        self.ui.radioButton_12.toggled.connect(self.update_code)

        # SKU
        self.ui.plainTextEdit.textChanged.connect(self.update_code)

        self.ui.pushButton.clicked.connect(self.on_print)
        self.ui.actionAbout.triggered.connect(self.show_about)

    def clean_plainTextEdit(self):
        text = self.ui.plainTextEdit.toPlainText()
        filtered = ''.join(c for c in text if c in "0123456789")
        if text != filtered:
            cursor = self.ui.plainTextEdit.textCursor()
            pos = cursor.position()
            self.ui.plainTextEdit.blockSignals(True)
            self.ui.plainTextEdit.setPlainText(filtered)
            self.ui.plainTextEdit.blockSignals(False)
            cursor.setPosition(min(pos, len(filtered)))
            self.ui.plainTextEdit.setTextCursor(cursor)

    def on_print(self):
        value1 = self.ui.lineEdit.text()
        value2 = self.ui.lineEdit_2.text()
        print("Print:")
        print("Size 1:", value1)
        print("Size 2:", value2)

    def update_code(self):
        # karat
        if self.ui.radioButton.isChecked():
            grade = "10"
        elif self.ui.radioButton_2.isChecked():
            grade = "14"
        elif self.ui.radioButton_6.isChecked():
            grade = "18"
        elif self.ui.radioButton_5.isChecked():
            grade = "SS"
        elif self.ui.radioButton_4.isChecked():
            grade = "PL"
        elif self.ui.radioButton_3.isChecked():
            grade = "ST"
        else:
            grade = ""

        # color
        if self.ui.radioButton_7.isChecked():
            color = "YE"
        elif self.ui.radioButton_8.isChecked():
            color = "WH"
        elif self.ui.radioButton_10.isChecked():
            color = "RO"
        elif self.ui.radioButton_9.isChecked():
            color = "WY"
        elif self.ui.radioButton_11.isChecked():
            color = "WR"
        elif self.ui.radioButton_13.isChecked():
            color = "YR"
        elif self.ui.radioButton_14.isChecked():
            color = "BL"
        elif self.ui.radioButton_12.isChecked():
            color = "TT"
        else:
            color = ""

        # SKU
        item_code = self.ui.plainTextEdit.toPlainText().strip()

        # Letter
        letter = self.ui.comboBox.currentText().strip().upper()
        if not (letter == "" or (len(letter) == 1 and letter in self.allowed_letters)):
            letter = ""

        # String
        result = f"{grade}{color}{letter}".strip()
        self.ui.plainTextEdit_2.setPlainText(result)

    def on_letter_edited(self, text):
        text = text.strip().upper()

        if text == "":
            return  

        if len(text) == 1 and text in self.allowed_letters:
            pass
        else:
            self.ui.comboBox.setCurrentIndex(0)  
    def on_sku_toggled(self, checked):
        self.limit_plainTextEdit_length(checked)

    def on_plainTextEdit_changed(self):
        if self.ui.checkBox.isChecked():
            self.limit_plainTextEdit_length(True)

    def limit_plainTextEdit_length(self, limit):
        if limit:
            text = self.ui.plainTextEdit.toPlainText()
            if len(text) > 6:
                text = text[:6]
                cursor = self.ui.plainTextEdit.textCursor()
                pos = cursor.position()
                self.ui.plainTextEdit.blockSignals(True)
                self.ui.plainTextEdit.setPlainText(text)
                self.ui.plainTextEdit.blockSignals(False)
                cursor.setPosition(min(pos, 6))
                self.ui.plainTextEdit.setTextCursor(cursor)


    def show_about(self):
        about_box = QMessageBox(self)
        about_box.setWindowFlags(about_box.windowFlags() | Qt.Window)
        about_box.setWindowTitle("About")
        about_box.setTextFormat(Qt.RichText)
        about_box.setText(
            "<b>QR Tag Generator</b><br>"
            "Version: 1.0.0<br><br>"
            "<b>Developer:</b> Sergey Vedmetskiy<br>"
            "<b>Assistant Developer:</b> Viktoriya Yevsyukova<br><br>"
            "License: GNU AGPL v3.0<br>"
            "<i>This software is provided without any warranty.</i><br>"
            "Use at your own risk.<br><br>"
            "© 2025 Sergey Vedmetskiy"
        )
        about_box.setIcon(QMessageBox.Information)
        about_box.exec_()

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

