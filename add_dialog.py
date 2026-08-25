import sys
from pathlib import Path
from PyQt6 import uic
from PyQt6.QtCore import QDateTime
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import QDialog, QMessageBox

def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent
    return base_path / relative_path
UI_PATH = resource_path("UI/add_downtime.ui")

class AddDowntimeDialog(QDialog):
    def __init__(self, machine, downtime_types, parent=None):
        super().__init__(parent)
        uic.loadUi(UI_PATH, self)
        self.machine = machine
        # ==========================================
        # TYPE DOWNTIME
        # ==========================================
        self.typeComboBox.clear()
        self.typeComboBox.addItem("-- Select Type --")
        self.typeComboBox.addItems(downtime_types)
        # ==========================================
        # EN
        # ==========================================
        self.enCheckInEdit.setValidator(QIntValidator())
        # ==========================================
        # CHECK IN TIME
        # Default = เวลาปัจจุบัน
        # แต่ Operator สามารถแก้ย้อนหลังได้
        # ==========================================
        self.checkInDateTimeEdit.setCalendarPopup(True)
        self.checkInDateTimeEdit.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.checkInDateTimeEdit.setDateTime(QDateTime.currentDateTime())
        # ==========================================
        # BUTTON
        # ==========================================
        self.addButton.clicked.connect(self.validate_and_accept)
        self.cancelButton.clicked.connect(self.reject)
    
    def validate_and_accept(self):
        downtime_type = (self.typeComboBox.currentText().strip())
        detail = (self.detailTextEdit.text().strip())
        en = (self.enCheckInEdit.text().strip())
        # ==========================================
        # VALIDATION
        # ==========================================
        if downtime_type == "-- Select Type --":
            QMessageBox.warning(self, "Missing Information", "Please select Downtime Type.")
            return
        if not detail:
            QMessageBox.warning(self, "Missing Information", "Please enter Detail.")
            return
        if not en:
            QMessageBox.warning(self, "Missing Information", "Please enter EN Check In.")
            return
        self.accept()
    
    # ==============================================
    # RETURN DATA
    # ==============================================
    def get_data(self):
        return {
            "type": (self.typeComboBox.currentText().strip()),
            "detail": (self.detailTextEdit.text().strip()),
            "en_checkin": (self.enCheckInEdit.text().strip()),
            "checkin": (self.checkInDateTimeEdit.dateTime().toPyDateTime().strftime("%d/%m/%Y %H:%M"))
        }