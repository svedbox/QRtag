from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QGraphicsScene, QStyleFactory, QDialog, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QObject, QEvent, QRectF, QSizeF
from ui_qrtag import Ui_MainWindow
from string import ascii_uppercase
import qrcode
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPalette, QColor, QFont, QTransform
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
import tempfile
import subprocess
from PIL import Image

class DigitOnlyFilter(QObject):
    def __init__(self, parent=None, max_length=5):
        super().__init__(parent)
        self.max_length = max_length
        self.enabled = True

    def eventFilter(self, obj, event):
        if not self.enabled:
            return False

            allowed_keys = (
                Qt.Key_Backspace, Qt.Key_Delete,
                Qt.Key_Left, Qt.Key_Right,
                Qt.Key_Home, Qt.Key_End,
                Qt.Key_Tab, Qt.Key_Return, Qt.Key_Enter
            )

            if key in allowed_keys:
                return False

            if text.isdigit():
                current_text = obj.toPlainText()
                cursor = obj.textCursor()
                if len(current_text) < self.max_length or cursor.hasSelection():
                    return False
                else:
                    return True
            return True
        return False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.checkBox_2.setChecked(True)
        self.super_string = ""
        
        self.ui.checkBox_3.toggled.connect(self.on_checkbox3_toggled)
        self.ui.plainTextEdit_2.textChanged.connect(self.on_manual_text_changed)
         # Устанавливаем начальное состояние (если чекбокс уже checked)
        

        self.ui.checkBox.setChecked(True)
        self.limit_plainTextEdit_length(True)

        # SKU поле (6 цифр)
        self.digit_filter = DigitOnlyFilter(self, max_length=6)
        self.ui.plainTextEdit.installEventFilter(self.digit_filter)
        self.ui.plainTextEdit.textChanged.connect(self.clean_plainTextEdit)

        # Новые поля (5 цифр)
        self.digit_filter_3 = DigitOnlyFilter(self, max_length=5)
        self.digit_filter_4 = DigitOnlyFilter(self, max_length=5)
        self.ui.plainTextEdit_3.installEventFilter(self.digit_filter_3)
        self.ui.plainTextEdit_4.installEventFilter(self.digit_filter_4)
        self.ui.plainTextEdit_3.textChanged.connect(lambda: self.trim_text(self.ui.plainTextEdit_3, 5))
        self.ui.plainTextEdit_4.textChanged.connect(lambda: self.trim_text(self.ui.plainTextEdit_4, 5))

        self.ui.checkBox.toggled.connect(self.on_sku_toggled)
        self.ui.plainTextEdit.textChanged.connect(self.on_plainTextEdit_changed)

        self.allowed_letters = list(ascii_uppercase)
        self.ui.comboBox.setEditable(True)
        self.ui.comboBox.clear()
        self.ui.comboBox.addItem("")  
        self.ui.comboBox.addItems(self.allowed_letters)
        self.ui.comboBox.setCurrentIndex(-1)  
        self.on_checkbox3_toggled(self.ui.checkBox_3.isChecked())
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
        self.ui.plainTextEdit_3.textChanged.connect(self.update_code)
        self.ui.plainTextEdit_4.textChanged.connect(self.update_code)
        self.ui.pushButton.clicked.connect(self.print_label)
        self.ui.actionAbout.triggered.connect(self.show_about)
        
        self.ui.plainTextEdit_3.textChanged.connect(self.on_plainTextEdit_3_changed)
        self.on_plainTextEdit_3_changed()

         # Радиокнопки выбора принтера
        self.ui.radioButton_15.setChecked(True)        # DYMO — выбран по умолчанию
        self.ui.radioButton_16.setEnabled(False)       # Zebra — отображается, но неактивна

    
    def on_manual_text_changed(self):
        if self.ui.checkBox_3.isChecked():  # manual включён
            self.super_string = self.ui.plainTextEdit_2.toPlainText().strip()
            self.update_qr_code()
    
    def update_qr_code(self):
        data = self.super_string.strip()
        if not data:
            self.ui.label_qr.clear()
            return

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=12,  # увеличь для качества
            border=1,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        # PIL Image -> QByteArray -> QImage
        img_data = img.tobytes("raw", "RGB")
        qimg = QImage(img_data, img.size[0], img.size[1], QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(qimg)

        # Получаем размер QLabel
        label_size = self.ui.label_qr.size()

        # Масштабируем pixmap под размер QLabel с сохранением пропорций
        scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.ui.label_qr.setPixmap(scaled_pixmap)
        self.ui.label_qr.setAlignment(Qt.AlignCenter)

        
    def on_checkbox3_toggled(self, checked):
         # Если включен — редактируемое, иначе только чтение
        self.ui.plainTextEdit_2.setReadOnly(not checked)    
        
        if checked:
            self.ui.checkBox_3.setStyleSheet("color: red;")
            # Копируем текущее значение суперпеременной в поле для ручного редактирования,
            text_to_copy = self.ui.plainTextEdit.toPlainText().strip()
            self.ui.plainTextEdit_2.blockSignals(True)
            self.ui.plainTextEdit_2.setPlainText(self.super_string)
            self.ui.plainTextEdit_2.blockSignals(False)
            self.ui.plainTextEdit.blockSignals(True)
            self.ui.plainTextEdit.clear()
            self.ui.plainTextEdit.blockSignals(False)

        # Обновляем super_string и QR код (на всякий случай)
            self.super_string = self.ui.plainTextEdit_2.toPlainText().strip()
            self.update_qr_code()
        else:
            self.ui.checkBox_3.setStyleSheet("")
            self.update_code()
        
    def on_plainTextEdit_3_changed(self):
        text = self.ui.plainTextEdit_3.toPlainText().strip()
        self.ui.plainTextEdit_4.setEnabled(bool(text))

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

    def trim_text(self, widget, max_length):
        text = widget.toPlainText()
        filtered = ''.join(c for c in text if c.isdigit())[:max_length]
        if text != filtered:
            cursor = widget.textCursor()
            pos = cursor.position()
            widget.blockSignals(True)
            widget.setPlainText(filtered)
            widget.blockSignals(False)
            cursor.setPosition(min(pos, len(filtered)))
            widget.setTextCursor(cursor)

    def print_label(self):
        # Проверяем, выбран ли DYMO радиобокс
        if self.ui.radioButton_15.isChecked():
            self.print_label_dymo()
        else:
            QMessageBox.information(self, "Печать", "Печать для выбранного принтера пока не реализована.")

    def print_label_dymo(self):
        if not self.super_string.strip():
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните поле Item Code перед печатью.")
            return
        dpi = 300  # для DYMO
        mm_to_px = lambda mm: int((mm / 25.4) * dpi)

        width_mm, height_mm = 62, 31  # альбом
        width_px = mm_to_px(width_mm)
        height_px = mm_to_px(height_mm)

        image = QImage(width_px, height_px, QImage.Format_RGB32)
        image.fill(Qt.white)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)

        # --- QR-код ---
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=1,
            border=0
        )
        qr.add_data(self.super_string.strip() or "TEST-QR")
        qr.make(fit=True)
        matrix = qr.get_matrix()

        qr_size_mm = 10
        qr_size_px = mm_to_px(qr_size_mm)
        cell_size = qr_size_px // len(matrix)

        qr_img = QImage(qr_size_px, qr_size_px, QImage.Format_RGB32)
        qr_img.fill(Qt.white)
        qp = QPainter(qr_img)
        qp.setPen(Qt.NoPen)
        qp.setBrush(Qt.black)

        for y, row in enumerate(matrix):
            for x, val in enumerate(row):
                if val:
                    qp.drawRect(x * cell_size, y * cell_size, cell_size, cell_size)
        qp.end()

        # Отрисовать QR в (3мм, 3мм)
        qr_x = mm_to_px(2)#--to right
        qr_y = mm_to_px(6.5)#--to down
        sku_y = qr_y + qr_size_px  # дефолтное значение, если SKU нет
        painter.drawImage(qr_x, qr_y, qr_img)

                # --- Надпись Cut! ---
        if self.ui.checkBox_2.isChecked():
            cut_font = QFont("Arial", 22)#--exactly size
            cut_font.setBold(True)
            painter.setFont(cut_font)
            painter.setPen(Qt.black)

            cut_lines = ["Cut!", "Do", "NOT", "pull!"]
            line_spacing = mm_to_px(2.5)  # расстояние между строками
            base_x = qr_x + qr_size_px + mm_to_px(0)  # немного правее от QR
            base_y = qr_y + qr_size_px + mm_to_px(-8.5)

            for i, line in enumerate(cut_lines):
                painter.drawText(base_x, base_y + i * line_spacing, line)

        # --- SKU ниже QR ---
        sku_text = self.ui.plainTextEdit.toPlainText().strip()
        if sku_text:
            sku_font = QFont("Arial", 32)
            sku_font.setBold(False)
            painter.setFont(sku_font)
            
            sku_x = qr_x  # на том же уровне по X, что и QR
            sku_y = qr_y + qr_size_px + mm_to_px(5)  # немного ниже QR
            
            sku_text = self.ui.plainTextEdit.toPlainText().strip()
            painter.drawText(sku_x, sku_y, sku_text)

        # --- Содержимое textEdit_2 (сгенерированная строка) ---
        code_text = self.ui.plainTextEdit_2.toPlainText().strip()
        if code_text:
            code_font = QFont("Arial", 24)
            code_font.setBold(False)
            painter.setFont(code_font)

            code_y = sku_y + mm_to_px(3.5)  # немного ниже SKU

            text_width = painter.fontMetrics().horizontalAdvance(code_text)
            code_x = qr_x 

            painter.drawText(code_x, code_y, code_text)

        painter.end()

        # Предпросмотр
        #        pixmap = QPixmap.fromImage(image)
        #        self.show_label_preview(pixmap)
        # --- Rotate image 90 degrees ---
        rotated_image = image.transformed(QTransform().rotate(90), Qt.SmoothTransformation)

        # --- Save to PNG file ---
        output_path = "label_output.png"
        if not rotated_image.save(output_path, "PNG"):
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить изображение в файл.")

        # --- Setup printer ---
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPrinterName("DYMO LabelWriter")  # set your exact printer name
        printer.setPageSizeMM(QSizeF(31, 62))       # same as image size
        printer.setFullPage(True)
        printer.setOrientation(QPrinter.Portrait)  # even with rotated image, keep Portrait
        printer.setPageMargins(0, 0, 0, 0, QPrinter.Millimeter)

        # --- Start printing ---
        painter = QPainter()
        if not painter.begin(printer):
            QMessageBox.critical(self, "Ошибка", "Не удалось начать печать.")
            return

        target_rect = printer.pageRect()  # This MUST be called AFTER painter.begin()
        painter.drawImage(target_rect, rotated_image)
        painter.end()


    def show_label_preview(self, pixmap):
        preview = QDialog(self)
        preview.setWindowTitle("Предпросмотр этикетки")
        preview.setModal(False)
        preview.setAttribute(Qt.WA_DeleteOnClose)
        preview.resize(pixmap.width() + 20, pixmap.height() + 20)

        layout = QVBoxLayout()
        label = QLabel()
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        preview.setLayout(layout)
        preview.show()

    
    def update_code(self):
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

        item_code = self.ui.plainTextEdit.toPlainText().strip()

        letter = self.ui.comboBox.currentText().strip().upper()
        if not (letter == "" or (len(letter) == 1 and letter in self.allowed_letters)):
            letter = ""
        suffix = self.ui.plainTextEdit_3.toPlainText().strip()
        amp = self.ui.plainTextEdit_4.toPlainText().strip()

        result = f"{grade}{color}{suffix}"
        if amp:
            result += f"&{amp}"

        result+= letter
        self.ui.plainTextEdit_2.setPlainText(result)
        
        
        # Формируем суперстроку: SKU / результат
        sku = self.ui.plainTextEdit.toPlainText().strip()
        self.super_string = f"{sku}/{result}" if sku else result

        self.update_qr_code()

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
