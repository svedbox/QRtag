import qrcode, os, sys, platform
os.environ["QT_QPA_PLATFORM"] = "xcb"
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QStyleFactory
from PyQt6.QtCore import Qt, QObject, QSizeF
from ui_qrtag import Ui_MainWindow
from string import ascii_uppercase
from PyQt6.QtGui import QPixmap, QImage, QPainter, QFont, QTransform, QIcon
from PyQt6.QtPrintSupport import QPrinter, QPrinterInfo

system = platform.system()

def resource_path(filename):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)
try:
    with open(resource_path("version.txt"), "r", encoding="utf-8") as f:
        app_version = f.read().strip()
except Exception:
    app_version = "unknown"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("QRtag -Jewelry label generator")

        # Window icon:
        if getattr(sys, 'frozen', False):
            basedir = sys._MEIPASS
        else:
            basedir = os.path.dirname(__file__)
        icon_path = os.path.join(basedir, "qrtag.ico")
        self.setWindowIcon(QIcon(icon_path))

        self.ui.checkBox_2.setChecked(True)
        self.super_string = ""
        # Manual mode toggle
        self.ui.checkBox_3.toggled.connect(self.on_checkbox3_toggled)
        self.ui.plainTextEdit_2.textChanged.connect(self.on_manual_text_changed)
        self.ui.checkBox.setChecked(True)
        self.limit_plainTextEdit_length(True)

        # SKU field (6 digits)
        self.ui.plainTextEdit.textChanged.connect(self.clean_plainTextEdit)

        # Additional fields (5 digits each)
        self.ui.plainTextEdit_3.textChanged.connect(lambda: self.trim_text(self.ui.plainTextEdit_3, 5))
        self.ui.plainTextEdit_4.textChanged.connect(lambda: self.trim_text(self.ui.plainTextEdit_4, 5))
        # SKU toggle and input restriction
        self.ui.checkBox.toggled.connect(self.on_sku_toggled)
        self.ui.plainTextEdit.textChanged.connect(self.on_plainTextEdit_changed)
        # Dropdown setup for allowed letters
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

        # Karat radio buttons
        self.ui.radioButton.toggled.connect(self.update_code)
        self.ui.radioButton_2.toggled.connect(self.update_code)
        self.ui.radioButton_6.toggled.connect(self.update_code)
        self.ui.radioButton_5.toggled.connect(self.update_code)
        self.ui.radioButton_4.toggled.connect(self.update_code)
        self.ui.radioButton_3.toggled.connect(self.update_code)

        # Color radio buttons
        self.ui.radioButton_7.toggled.connect(self.update_code)
        self.ui.radioButton_8.toggled.connect(self.update_code)
        self.ui.radioButton_10.toggled.connect(self.update_code)
        self.ui.radioButton_9.toggled.connect(self.update_code)
        self.ui.radioButton_11.toggled.connect(self.update_code)
        self.ui.radioButton_13.toggled.connect(self.update_code)
        self.ui.radioButton_14.toggled.connect(self.update_code)
        self.ui.radioButton_12.toggled.connect(self.update_code)

        # SKU and code fields
        self.ui.plainTextEdit.textChanged.connect(self.update_code)
        self.ui.plainTextEdit_3.textChanged.connect(self.update_code)
        self.ui.plainTextEdit_4.textChanged.connect(self.update_code)
        self.ui.pushButton.clicked.connect(self.print_label)
        self.ui.actionAbout.triggered.connect(self.show_about)
        
        # Enable second suffix field only if first is filled
        self.ui.plainTextEdit_3.textChanged.connect(self.on_plainTextEdit_3_changed)
        self.on_plainTextEdit_3_changed()

         # Printer selection defaults
        self.ui.radioButton_15.setChecked(True)        # DYMO selected by default
        self.ui.radioButton_16.setEnabled(False)       # Zebra is shown but disabled

    def get_version(self):
        try:
            with open("version.txt", "r") as f:
                return f.read().strip()
        except Exception:
            return "Unknown"

    def clear_color_selection(self):
        for btn in [
            self.ui.radioButton_7, self.ui.radioButton_8, self.ui.radioButton_10, self.ui.radioButton_9,
            self.ui.radioButton_11, self.ui.radioButton_13, self.ui.radioButton_14, self.ui.radioButton_12
        ]:
            btn.setAutoExclusive(False)
            btn.setChecked(False)
            btn.setAutoExclusive(True)

    def set_color_buttons_enabled(self, enabled):
        for btn in [
            self.ui.radioButton_7, self.ui.radioButton_8, self.ui.radioButton_10, self.ui.radioButton_9,
            self.ui.radioButton_11, self.ui.radioButton_13, self.ui.radioButton_14, self.ui.radioButton_12
        ]:
            btn.setEnabled(enabled)

    
    def on_manual_text_changed(self):
        if self.ui.checkBox_3.isChecked():  
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
            box_size=12,  # increase for quality
            border=1,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        # PIL Image -> QByteArray -> QImage
        img_data = img.tobytes("raw", "RGB")
        qimg = QImage(img_data, img.size[0], img.size[1], QImage.Format.Format_RGB888)

        pixmap = QPixmap.fromImage(qimg)

        # Receiving lable size
        label_size = self.ui.label_qr.size()

        # Scaling pixmap to QLabel size
        scaled_pixmap = pixmap.scaled(label_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        self.ui.label_qr.setPixmap(scaled_pixmap)
        self.ui.label_qr.setAlignment(Qt.AlignmentFlag.AlignCenter)

        
    def on_checkbox3_toggled(self, checked):
         # If ebabled - editing, else read only
        self.ui.plainTextEdit_2.setReadOnly(not checked)    
        
        if checked:
            self.ui.checkBox_3.setStyleSheet("color: red;")
            # Copy ammount super variable to manual place
            text_to_copy = self.ui.plainTextEdit.toPlainText().strip()
            self.ui.plainTextEdit_2.blockSignals(True)
            self.ui.plainTextEdit_2.setPlainText(self.super_string)
            self.ui.plainTextEdit_2.blockSignals(False)
            self.ui.plainTextEdit.blockSignals(True)
            self.ui.plainTextEdit.clear()
            self.ui.plainTextEdit.blockSignals(False)

            # Renew super_string and QR code
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
        filtered = ''.join(c for c in text.upper() if c.isalnum())
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
        allowed_chars = "0123456789."
        result = ""
        dot_seen = False

        for c in text:
            if c not in allowed_chars:
                continue
            if c == ".":
                if dot_seen:
                    continue  # second point - ignore
                dot_seen = True
            result += c
            if len(result) >= max_length:
                break

        if text != result:
            cursor = widget.textCursor()
            pos = cursor.position()
            widget.blockSignals(True)
            widget.setPlainText(result)
            widget.blockSignals(False)
            cursor.setPosition(min(pos, len(result)))
            widget.setTextCursor(cursor)

    def print_label(self):
        # Checking is enable DYMO checkbox
        if self.ui.radioButton_15.isChecked():
            self.print_label_dymo()
        else:
            QMessageBox.information(self, "Print", "Print for this printer not available yet.")

    def print_label_dymo(self):
        if not self.super_string.strip():
            QMessageBox.warning(self, "Error", "Please enter Item Code place before printing")
            return
        dpi = 300  # Dpi for DYMO
        mm_to_px = lambda mm: int((mm / 25.4) * dpi)

        width_mm, height_mm = 62, 31  # Landscape (62x31mm)
        width_px = mm_to_px(width_mm)
        height_px = mm_to_px(height_mm)

        image = QImage(width_px, height_px, QImage.Format.Format_RGB32)
        image.fill(Qt.GlobalColor.white)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

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

        qr_size_mm = 10 #QR size
        qr_size_px = mm_to_px(qr_size_mm)
        cell_size = qr_size_px // len(matrix)

        qr_img = QImage(qr_size_px, qr_size_px, QImage.Format.Format_RGB32)
        qr_img.fill(Qt.GlobalColor.white)
        qp = QPainter(qr_img)
        qp.setPen(Qt.PenStyle.NoPen)
        qp.setBrush(Qt.GlobalColor.black)

        for y, row in enumerate(matrix):
            for x, val in enumerate(row):
                if val:
                    qp.drawRect(x * cell_size, y * cell_size, cell_size, cell_size)
        qp.end()

        # Creating QR в (10mm, 10mm)
        qr_x = mm_to_px(2)#--align to right
        qr_y = mm_to_px(6.5)#--align to down
        sku_y = qr_y + qr_size_px  # default, if no SKU
        painter.drawImage(qr_x, qr_y, qr_img)

                # --- Row Cut! ---
        if self.ui.checkBox_2.isChecked():
            cut_font = QFont("Arial", 22)#--exactly text size
            cut_font.setBold(False)
            painter.setFont(cut_font)
            painter.setPen(Qt.GlobalColor.black)

            cut_lines = ["Cut!", "Do", "NOT", "pull!"]
            line_spacing = mm_to_px(2.5)  # distance between rows
            base_x = qr_x + qr_size_px + mm_to_px(0)  # right of QR
            base_y = qr_y + qr_size_px + mm_to_px(-8.5)

            for i, line in enumerate(cut_lines):
                painter.drawText(base_x, base_y + i * line_spacing, line)

        # --- SKU below QR ---
        sku_text = self.ui.plainTextEdit.toPlainText().strip()
        if sku_text:
            sku_font = QFont("Arial", 32)
            sku_font.setBold(False)
            painter.setFont(sku_font)
            
            sku_x = qr_x  # X the same level with QR
            sku_y = qr_y + qr_size_px + mm_to_px(5)  # below QR
            
            sku_text = self.ui.plainTextEdit.toPlainText().strip()
            painter.drawText(sku_x, sku_y, sku_text)

        # --- textEdit_2 (generated row) ---
        code_text = self.ui.plainTextEdit_2.toPlainText().strip()
        if code_text:
            code_font = QFont("Arial", 24)
            code_font.setBold(False)
            painter.setFont(code_font)

            code_y = sku_y + mm_to_px(3.5)  # below SKU

            text_width = painter.fontMetrics().horizontalAdvance(code_text)
            code_x = qr_x 

            painter.drawText(code_x, code_y, code_text)

                # --- IF checkbox LAB is enabled — print "LAB" below second row ---
        if self.ui.checkBox_4.isChecked():
            lab_text = "LAB"

            # Font setting
            lab_font = QFont("Arial", 22)
            lab_font.setBold(False)
            painter.setFont(lab_font)
            painter.setPen(Qt.GlobalColor.black)

            # Text coordinates
            lab_y = code_y + mm_to_px(3)  # below of second row
            lab_x = qr_x + mm_to_px(1)

            # Receiving length and width of text
            metrics = painter.fontMetrics()
            text_width = metrics.horizontalAdvance(lab_text)
            text_height = metrics.height()

            padding = mm_to_px(0.5)  # inside align frame
            rect_x = lab_x - padding
            rect_y = lab_y - text_height + metrics.descent() - padding // 2
            rect_width = text_width + 2 * padding
            rect_height = text_height + padding

            # Painting frame with round corners
            pen = painter.pen()
            pen.setWidth(2)  # thick of line
            painter.setPen(pen)
            painter.drawRoundedRect(rect_x, rect_y, rect_width, rect_height, 5, 5)

            # Painting text over frame
            painter.drawText(lab_x, lab_y, lab_text)

        painter.end()

        rotated_image = image.transformed(QTransform().rotate(90), Qt.TransformationMode.SmoothTransformation)

        # --- Setup printer ---
        dymo_printer_info = None
        for p in QPrinterInfo.availablePrinters():
            if "DYMO" in p.printerName().upper():
                dymo_printer_info = p
                break

        if not dymo_printer_info:
            QMessageBox.critical(self, "Error", "DYMO printer is not found!")
            return

        printer = QPrinter(dymo_printer_info)
        printer.setPageSizeMM(QSizeF(31, 62))
        printer.setFullPage(True)
        printer.setOrientation(QPrinter.Orientation.Portrait)
        printer.setPageMargins(0, 0, 0, 0, QPrinter.Unit.Millimeter)

        # --- Start printing ---
        painter = QPainter()
        if not painter.begin(printer):
            QMessageBox.critical(self, "Error", "Cannot start printing")
            return

        target_rect = printer.pageRect()  # This MUST be called AFTER painter.begin()
        painter.drawImage(target_rect, rotated_image)
        painter.end()
    
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
            
        # Check if one of special metals selected
        if self.ui.radioButton_3.isChecked() or self.ui.radioButton_4.isChecked() or self.ui.radioButton_5.isChecked():
            self.clear_color_selection()
            self.set_color_buttons_enabled(False)
            color = ""
        else:
            self.set_color_buttons_enabled(True)
    

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
        
        
        # Create superrow: SKU / result
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
        global app_version
        about_box = QMessageBox(self)
        about_box.setWindowFlags(about_box.windowFlags() | Qt.WindowType.Window)
        about_box.setWindowTitle("About")
        about_box.setTextFormat(Qt.TextFormat.RichText)
        about_box.setText(
            "<b>QR Tag Generator</b><br>"
            f"Version: {app_version}<br><br>"
            "<b>Developer:</b> Sergey Vedmetskiy<br>"
            "<b>Assistant Developer:</b> Viktoriya Yevsyukova<br><br>"
            "License: GNU AGPL v3.0<br>"
            "<i>This software is provided without any warranty.</i><br>"
            "Use at your own risk.<br><br>"
            "© 2025 Sergey Vedmetskiy"
        )
        about_box.setIcon(QMessageBox.Icon.Information)
        about_box.exec()

if __name__ == "__main__":
    app = QApplication([])
    if system == "Windows":
        if "WindowsVista" in QStyleFactory.keys():
            app.setStyle(QStyleFactory.create("WindowsVista"))
        else:
            app.setStyle(QStyleFactory.create("Windows"))  # fallback
    elif system == "Linux":
        app.setStyle(QStyleFactory.create("Fusion"))
    elif system == "Darwin":  # macOS
        app.setStyle(QStyleFactory.create("Macintosh"))
    else:
        app.setStyle(QStyleFactory.create("Fusion"))  # безопасный дефолт

    window = MainWindow()
    window.show()
    app.exec()
    
