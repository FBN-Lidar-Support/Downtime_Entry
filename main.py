import sys
import configparser
from pathlib import Path
from datetime import datetime
import pandas as pd
from PyQt6 import uic
from PyQt6.QtCore import QDateTime
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDateTimeEdit, QMessageBox, QHeaderView, QSizePolicy, QDialog, QInputDialog
from csv_manager import CSVManager
from add_dialog import AddDowntimeDialog

BASE_DIR = Path(__file__).resolve().parent
UI_PATH = BASE_DIR / "UI" / "downtime_entry.ui"
CONFIG_PATH = BASE_DIR / "config.ini"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        print(UI_PATH)
        uic.loadUi(UI_PATH, self)
        self.pending_close = {}
        
        self.load_machine_list()
        self.setup_csv_manager()
        
        header = self.currentTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.saveButton.setEnabled(False)
        
        self.addButton.clicked.connect(self.add_new_downtime)
        self.saveButton.clicked.connect(self.save_changes)
        self.MachineComboBox.currentTextChanged.connect(self.machine_changed)
        
    def load_machine_list(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)
        downtime_type_dir = Path(config["PATH"]["DOWNTIME_TYPE_DIR"])
        machines = sorted([file.stem for file in downtime_type_dir.glob("*.csv")])
        self.MachineComboBox.clear()
        self.MachineComboBox.addItem("-- Select Machine --")
        self.MachineComboBox.addItems(machines)
        
    def machine_changed(self, machine):
        if machine == "-- Select Machine --":
            print("No machine selected")
            self.currentTable.setRowCount(0)
            return
        print(f"Selected Machine: {machine}")
        self.load_open_downtime(machine)
    
    def setup_csv_manager(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)
        
        downtime_dir = config["PATH"]["DOWNTIME_DIR"]
        downtime_type_dir = config["PATH"]["DOWNTIME_TYPE_DIR"]
        self.csv_manager = CSVManager(downtime_dir, downtime_type_dir)
        
    def load_open_downtime(self, machine):
        # ========================================================
        # GET OPEN DOWNTIME
        # ========================================================
        open_df = self.csv_manager.get_open_downtime(machine)
        # Clear table ก่อนโหลดใหม่
        self.currentTable.setRowCount(0)
        # Clear pending close
        self.pending_close.clear()
        # ยังไม่มีอะไรแก้ไข -> Disable Save
        self.saveButton.setEnabled(False)
        # ========================================================
        # TABLE COLUMNS
        # ========================================================
        display_columns = [
            "Type Downtime",
            "Detail",
            "EN Check In",
            "Timestamp Check In",
            "Timestamp Check Out",
            "Duration (hr)",
            "Status"
        ]
        self.currentTable.setColumnCount(len(display_columns))
        self.currentTable.setHorizontalHeaderLabels(display_columns)
        # ========================================================
        # HEADER SIZE
        # ========================================================
        header = self.currentTable.horizontalHeader()
        # Column ปกติ
        # ความกว้างตาม Header หรือ Value ที่ยาวที่สุด
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        # Column 4 = Timestamp Check Out
        # เป็น QDateTimeEdit จึงให้กำหนดขนาดเอง
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        # ========================================================
        # NO OPEN DOWNTIME
        # ========================================================
        if open_df.empty:
            print(f"No open downtime: {machine}")
            return
        # ========================================================
        # LOAD DATA TO TABLE
        # ========================================================
        for table_row, (_, data) in enumerate(open_df.iterrows()):
            self.currentTable.insertRow(table_row)
            # CSV index จริง
            # ใช้ตอน Save เพื่อรู้ว่าต้อง Update Row ไหน
            csv_index = int(data["_csv_index"])
            # ----------------------------------------------------
            # Type Downtime
            # ----------------------------------------------------
            type_downtime = data.get("Type Downtime", "")
            if pd.isna(type_downtime):
                type_downtime = ""
            self.currentTable.setItem(table_row, 0, QTableWidgetItem(str(type_downtime)))
            # ----------------------------------------------------
            # Detail
            # ----------------------------------------------------
            detail = data.get("Detail", "")
            if pd.isna(detail):
                detail = ""
            self.currentTable.setItem(table_row, 1, QTableWidgetItem(str(detail)))
            # ----------------------------------------------------
            # EN Check In
            # ----------------------------------------------------
            en_checkin = data.get("EN Check In", "")
            if pd.isna(en_checkin):
                en_checkin = ""
            self.currentTable.setItem(table_row, 2, QTableWidgetItem(str(en_checkin)))
            # ----------------------------------------------------
            # Timestamp Check In
            # ----------------------------------------------------
            checkin_text = data.get("Timestamp Check In", "")
            if pd.isna(checkin_text):
                checkin_text = ""
            checkin_text = str(checkin_text)
            self.currentTable.setItem(table_row, 3, QTableWidgetItem(checkin_text))
            # ====================================================
            # Timestamp Check Out
            # ====================================================
            checkout_edit = QDateTimeEdit()
            checkout_edit.setCalendarPopup(True)
            checkout_edit.setDisplayFormat("dd/MM/yyyy HH:mm")
            checkout_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.currentTable.setRowHeight(table_row, 36)
            checkout_edit.setMinimumHeight(36)
            checkout_edit.setDateTime(QDateTime.currentDateTime())
            checkout_edit.setStyleSheet("""
                QDateTimeEdit {
                    background-color: #FFF3CD;
                    color: black;
                    border: none;
                    padding-left: 6px;
                    padding-right: 4px;
                    margin: 0px;
                    font-weight: "Segoe UI";
                    font-weight: bold;
                    font-size: 15px;
                }
            """)
            # ----------------------------------------------------
            # เก็บข้อมูลของ Row ไว้ใน Widget
            # ----------------------------------------------------
            checkout_edit.setProperty("csv_index", csv_index)
            checkout_edit.setProperty("table_row", table_row)
            checkout_edit.setProperty("checkin_text", checkin_text)
            # ----------------------------------------------------
            # เมื่อเปลี่ยน Check Out Time
            # ----------------------------------------------------
            checkout_edit.dateTimeChanged.connect(self.checkout_changed)
            # ----------------------------------------------------
            # Add Widget เข้า Table
            # ----------------------------------------------------
            self.currentTable.setCellWidget(table_row, 4, checkout_edit)
            # ----------------------------------------------------
            # ปรับ Column Check Out ให้กว้างพอดีกับ Widget
            # ----------------------------------------------------
            checkout_width = (checkout_edit.sizeHint().width() + 30)
            checkout_edit.setMinimumWidth(checkout_width)
            if (self.currentTable.columnWidth(4) < checkout_width):
                self.currentTable.setColumnWidth(4, checkout_width)
            # ----------------------------------------------------
            # Duration
            # ----------------------------------------------------
            self.currentTable.setItem(table_row, 5, QTableWidgetItem(""))
            # ----------------------------------------------------
            # Status
            # ----------------------------------------------------
            self.currentTable.setItem(table_row, 6, QTableWidgetItem("Open"))
            status_item = QTableWidgetItem("open")
            status_item.setBackground(QColor("#FFA500"))
            status_item.setForeground(QColor("#000000"))
            self.currentTable.setItem(table_row, 6, status_item)

    def checkout_changed(self, qdatetime):
        checkout_edit = self.sender()
        table_row = checkout_edit.property("table_row")
        csv_index = checkout_edit.property("csv_index")
        checkin_text = checkout_edit.property("checkin_text")
        # ค่า default = ยังไม่ได้เลือก
        if qdatetime == checkout_edit.minimumDateTime():
            return
        try:
            checkin = datetime.strptime(checkin_text, "%d/%m/%Y %H:%M")
            checkout = qdatetime.toPyDateTime()
        except ValueError as e:
            print("Invalid datetime:", e)
            return
        # --------------------------------------------------------
        # Validate
        # --------------------------------------------------------
        if checkout < checkin:
            print("Check Out cannot be before Check In")
            checkout_edit.blockSignals(True)
            checkout_edit.setDateTime(checkout_edit.minimumDateTime())
            checkout_edit.blockSignals(False)
            return
        # --------------------------------------------------------
        # Duration
        # --------------------------------------------------------
        duration_hr = (checkout - checkin).total_seconds() / 3600
        duration_hr = round(duration_hr, 2)
        # แสดง Duration
        self.currentTable.item(table_row, 5).setText(str(duration_hr))
        # เปลี่ยน Status เฉพาะใน UI
        self.currentTable.item(table_row, 6).setText("Closed")
        status_item = self.currentTable.item(table_row, 6)
        status_item.setText("Closed")
        status_item.setBackground(QColor("#28A745"))
        status_item.setForeground(QColor("#FFFFFF"))
        checkout_edit.setStyleSheet("""
                                        QDateTimeEdit {
                                            background-color: #D4EDDA;
                                            color: black;
                                            border: none;
                                            padding-left: 6px;
                                            padding-right: 4px;
                                            margin: 0px;
                                            font-weight: "Segoe UI";
                                            font-weight: bold;
                                            font-size: 15px;
                                        }
                                    """)
        checkout_text = checkout.strftime("%d/%m/%Y %H:%M")
        # --------------------------------------------------------
        # Pending Update
        # --------------------------------------------------------
        self.pending_close[csv_index] = {
            "checkout": checkout_text,
            "duration": duration_hr
        }
        print(f"Pending Close Row {csv_index}:", self.pending_close[csv_index])
        # มีข้อมูลที่รอ Save
        self.saveButton.setEnabled(True)

    def add_new_downtime(self):
        # ========================================================
        # MACHINE
        # ========================================================
        machine = (self.MachineComboBox.currentText().strip())
        if (not machine or machine == "-- Select Machine --"):
            QMessageBox.warning(self, "Machine Required", "Please select Machine first.")
            return
        # ========================================================
        # GET TYPE FROM SHARED DRIVE
        # ========================================================
        downtime_types = (self.csv_manager.get_downtime_types(machine))
        if not downtime_types:
            QMessageBox.warning(self, "Downtime Type",(f"No Downtime Type found for " f"{machine}."))
            return
        # ========================================================
        # OPEN DIALOG
        # ========================================================
        dialog = AddDowntimeDialog(machine=machine, downtime_types=downtime_types, parent=self)
        if (dialog.exec() != QDialog.DialogCode.Accepted):
            return
        # ========================================================
        # GET DATA
        # ========================================================
        data = dialog.get_data()
        # ========================================================
        # ADD CSV
        # ========================================================
        try:
            self.csv_manager.add_downtime(
                machine=machine,
                downtime_type=data["type"],
                detail=data["detail"],
                en_checkin=data["en_checkin"],
                checkin_time=data["checkin"]
            )
        except Exception as e:
            QMessageBox.critical(self, "Add Downtime Error", str(e))
            return
        # ========================================================
        # SUCCESS
        # ========================================================
        QMessageBox.information(self, "Success", "Downtime added successfully.")
        # Reload Open Downtime
        self.load_open_downtime(machine)

    def save_changes(self):
        # ========================================================
        # CHECK PENDING
        # ========================================================
        if not self.pending_close:
            QMessageBox.information(self, "No Changes", "There is no downtime to save.")
            return
        machine = (self.MachineComboBox.currentText().strip())
        # ========================================================
        # ASK EN CHECK OUT
        # ========================================================
        en_checkout, ok = (QInputDialog.getText(self, "EN Check Out", "Enter EN Check Out:"))
        if not ok:
            return
        en_checkout = en_checkout.strip()
        # ========================================================
        # VALIDATE
        # ========================================================
        if not en_checkout:
            QMessageBox.warning(self, "EN Required", "Please enter EN Check Out.")
            return
        if not en_checkout.isdigit():
            QMessageBox.warning(self, "Invalid EN", "EN must contain numbers only.")
            return
        # ========================================================
        # CONFIRM
        # ========================================================
        reply = QMessageBox.question(self, "Confirm Save",
            (
                f"Machine: {machine}\n"
                f"Close Downtime: "
                f"{len(self.pending_close)} item(s)\n"
                f"EN Check Out: {en_checkout}\n\n"
                f"Save changes?"
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if (reply != QMessageBox.StandardButton.Yes):
            return
        # ========================================================
        # WRITE CSV
        # ========================================================
        try:
            self.csv_manager.close_downtime(machine=machine, pending_close=self.pending_close, en_checkout=en_checkout)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))
            return
        # ========================================================
        # SUCCESS
        # ========================================================
        self.pending_close.clear()
        self.saveButton.setEnabled(False)
        QMessageBox.information(self, "Success", "Downtime saved successfully.")
        # Reload
        # Row ที่ Closed แล้วจะหายจาก Current Open
        self.load_open_downtime(machine)
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())