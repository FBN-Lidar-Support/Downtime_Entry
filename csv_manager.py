from pathlib import Path
import pandas as pd

CSV_COLUMNS = [
    "Machine",
    "Type Downtime",
    "Detail",
    "EN Check In",
    "Timestamp Check In",
    "EN Check Out",
    "Timestamp Check Out",
    "Duration (hr)",
    "Status"
]

class CSVManager:
    def __init__(self, downtime_dir, downtime_type_dir):
        self.downtime_dir = Path(downtime_dir)
        self.downtime_type_dir = Path(downtime_type_dir)
    # ========================================================
    # GET CSV PATH
    # ========================================================
    def get_machine_file(self, machine):
        return self.downtime_dir / f"{machine}.csv"
    
    # ========================================================
    # READ MACHINE CSV
    # ========================================================
    def read_machine(self, machine):
        file_path = self.get_machine_file(machine)
        # ถ้ายังไม่มีไฟล์
        if not file_path.exists():
            return pd.DataFrame(columns=CSV_COLUMNS)
        df = pd.read_csv(file_path, dtype=str)
        df.columns = (df.columns.astype(str).str.strip())
        return df
    
    # ========================================================
    # GET OPEN DOWNTIME
    # ========================================================
    def get_open_downtime(self, machine):
        df = self.read_machine(machine)
        if df.empty:
            return df
        
        open_df = df[df["Status"].fillna("").str.strip().str.upper() == "OPENED"].copy()
        open_df["_csv_index"] = open_df.index
        return open_df.reset_index(drop=True)
        
    # ============================================================
    # GET DOWNTIME TYPES
    # ============================================================
    def get_downtime_types(self, machine):
        type_file = self.downtime_type_dir / f"{machine}.csv"
        if not type_file.exists():
            return []
        df = pd.read_csv(type_file, dtype=str, encoding="utf-8-sig")
        df.columns = df.columns.str.strip()
        if "Type Downtime" not in df.columns:
            return []
        # ถ้ามี Active ก็เอาเฉพาะ Active = 1
        if "Active" in df.columns:
            df = df[df["Active"].fillna("").str.strip() == "1"]
        return (df["Type Downtime"].dropna().astype(str).str.strip().loc[lambda x: x != ""].tolist())
    
    # ============================================================
    # ADD NEW DOWNTIME
    # ============================================================
    def add_downtime(self, machine, downtime_type, detail, en_checkin, checkin_time):
        file_path = self.get_machine_file(machine)
        df = self.read_machine(machine)
        new_row = {
            "Machine": machine,
            "Type Downtime": downtime_type,
            "Detail": detail,
            "EN Check In": en_checkin,
            "Timestamp Check In": checkin_time,
            "EN Check Out": "",
            "Timestamp Check Out": "",
            "Duration (hr)": "",
            "Status": "OPENED"
        }
        df.loc[len(df)] = new_row
        file_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        
    # ============================================================
    # CLOSE DOWNTIME
    # ============================================================
    def close_downtime(self, machine, pending_close, en_checkout):
        file_path = self.get_machine_file(machine)
        df = self.read_machine(machine)

        updateed_count = 0

        print(f"Closing downtime file: {file_path}")
        print(f"Pending close: {pending_close}")

        for csv_index, update in pending_close.items():
            csv_index = int(csv_index)
            if csv_index not in df.index:
                raise ValueError(f"CSV row {csv_index} not found in {machine}.csv")
            current_status = str(df.at[csv_index, "Status"]).strip().upper()
            if current_status != "OPENED":
                raise ValueError(f"CSV row {csv_index} is not OPENED.", f"Current Status = {current_status}")

            df.at[csv_index, "EN Check Out"] = str(en_checkout)
            df.at[csv_index, "Timestamp Check Out"] = update["checkout"]
            df.at[csv_index, "Duration (hr)"] = str(update["duration"])
            df.at[csv_index, "Status"] = "CLOSED"

            updateed_count += 1

        if updateed_count == 0:
            raise RuntimeError("No downtime record was updated.")
            
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        return updateed_count