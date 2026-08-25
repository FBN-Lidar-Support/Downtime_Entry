# INZ Downtime Entry
Desktop application สำหรับบันทึก Machine Downtime เพื่อใช้เป็นข้อมูลสำหรับการคำนวณ OEE
โปรแกรมพัฒนาด้วย **Python + PyQt6** และบันทึกข้อมูลลงไฟล์ CSV บน Company Shared Drive
---
## 1. Program Overview
โปรแกรมใช้สำหรับ:
- แสดงรายการ Downtime ที่ยังเป็น `Open`
- เพิ่ม Downtime ใหม่
- ระบุ Check In / Check Out Time ย้อนหลังได้
- บันทึก EN ของผู้ Check In
- บันทึก EN ของผู้ Check Out
- คำนวณ Downtime Duration อัตโนมัติ
- แยก Downtime Record ตาม Machine
- แยก Downtime Type ตาม Machine
- ใช้ข้อมูลต่อสำหรับ OEE Reporting
---
## 2. Program Package
ดาวน์โหลดโปรแกรมจาก GitHub:
```text
GitHub Repository
→ Releases
→ INZ_Downtime_Entry.zip
```
หลังจาก Extract จะได้:
```text
INZ_Downtime_Entry/
├── INZ_Downtime_Entry.exe
└── config.ini
```
> `config.ini` ต้องอยู่ใน Folder เดียวกับ `INZ_Downtime_Entry.exe`
เครื่องที่ใช้งานไม่จำเป็นต้องติดตั้ง Python
---
## 3. Shared Drive
Shared Drive หลักของระบบ:
```text
\\Fbn-fs01\global\_A\AtthaphanP\INNOVIZ\OEE\Downtime_Entry
```
โครงสร้าง:
```text
Downtime_Entry/
│
├── Downtime_Type/
│   ├── AA.csv
│   ├── AB2B.csv
│   ├── IEOL LONG.csv
│   └── IEOL SHORT.csv
│
└── Downtime_Record/
    ├── AA.csv
    ├── AB2B.csv
    ├── IEOL LONG.csv
    └── IEOL SHORT.csv
```
### Downtime_Type
ใช้กำหนดรายการ Downtime Type ของแต่ละ Machine
### Downtime_Record
ใช้เก็บประวัติ Downtime จริงของแต่ละ Machine
---
## 4. config.ini
โปรแกรมอ่าน Shared Drive Path จาก `config.ini`
```ini
[PATH]
DOWNTIME_TYPE_DIR = \\Fbn-fs01\global\_A\AtthaphanP\INNOVIZ\OEE\Downtime_Entry\Downtime_Type
DOWNTIME_DIR = \\Fbn-fs01\global\_A\AtthaphanP\INNOVIZ\OEE\Downtime_Entry\Downtime_Record
```
| Setting | Description |
|---|---|
| `DOWNTIME_TYPE_DIR` | Folder สำหรับเก็บ Downtime Type ของแต่ละ Machine |
| `DOWNTIME_DIR` | Folder สำหรับเก็บ Downtime Record |
หาก Shared Drive Path เปลี่ยน สามารถแก้ `config.ini` ได้โดยไม่ต้อง Build `.exe` ใหม่
---
## 5. How to Use
เปิดโปรแกรม:
```text
INZ_Downtime_Entry.exe
```
เมื่อเปิดโปรแกรม ตาราง `Current Open Downtime` จะยังไม่แสดงข้อมูล
ให้เลือก Machine จาก Dropdown ก่อน
ตัวอย่าง:
```text
Machine:
[ AB2B ▼ ]
```
โปรแกรมจะอ่าน:
```text
Downtime_Record\AB2B.csv
```
และแสดงเฉพาะรายการที่:
```text
Status = Open
```
---
## 6. Current Open Downtime
ตัวอย่าง:
| Type Downtime | Detail | EN Check In | Timestamp Check In | Timestamp Check Out | Duration (hr) | Status |
|---|---|---|---|---|---|---|
| Machine Breakdown | Sensor Alarm | 524161 | 25/08/2026 10:00:00 | Editable | | Open |
Status:
- `Open` = สีส้ม
- `Closed` = สีเขียว
ช่อง `Timestamp Check Out` สามารถแก้ไขได้
ค่าเริ่มต้นเป็นเวลาปัจจุบัน แต่สามารถเลือกเวลาย้อนหลังเพื่อระบุเวลาที่ Machine กลับมาใช้งานได้จริง
---
## 7. Close Downtime
เมื่อ Machine กลับมาใช้งานได้ ให้เลือก `Timestamp Check Out`
ตัวอย่าง:
```text
Check In  : 25/08/2026 10:00:00
Check Out : 25/08/2026 10:30:00
```
โปรแกรมจะคำนวณ:
```text
Duration = 0.50 hr
```
และเปลี่ยน Status บนหน้าจอ:
```text
Open
↓
Closed
```
> ข้อมูลยังไม่ถูกเขียนลง CSV จนกว่าจะกด `SAVE`
---
## 8. Save Check Out
หลังจากกำหนด Check Out Time แล้ว กด:
```text
SAVE
```
โปรแกรมจะให้กรอก:
```text
EN Check Out
```
กรอก Employee Number ของผู้บันทึก Check Out แล้ว Confirm
โปรแกรมจะ Update:
- EN Check Out
- Timestamp Check Out
- Duration (hr)
- Status = Closed
ตัวอย่าง:
```csv
Machine,Type Downtime,Detail,EN Check In,Timestamp Check In,EN Check Out,Timestamp Check Out,Duration (hr),Status
AB2B,Machine Breakdown,Sensor Alarm,524161,25/08/2026 10:00:00,524200,25/08/2026 10:30:00,0.50,Closed
```
หลังจาก Save สำเร็จ รายการที่ `Closed` จะหายออกจาก `Current Open Downtime`
---
## 9. Add New Downtime
เลือก Machine ก่อน เช่น:
```text
Machine : AB2B
```
จากนั้นกด:
```text
+ Add Downtime
```
กรอกข้อมูล:
- Type Downtime
- Detail
- EN Check In
- Check In Time
`Check In Time` จะมีค่าเริ่มต้นเป็นเวลาปัจจุบัน แต่สามารถแก้เป็นเวลาย้อนหลังได้
หลังจาก Add สำเร็จ โปรแกรมจะสร้าง Row ใหม่:
```text
Status = Open
```
---
## 10. Downtime Type
Downtime Type ของแต่ละ Machine แยกออกจากกัน
ตัวอย่าง เมื่อเลือก:
```text
Machine = AB2B
```
โปรแกรมจะอ่าน:
```text
\\Fbn-fs01\global\_A\AtthaphanP\INNOVIZ\OEE\Downtime_Entry\Downtime_Type\AB2B.csv
```
ดังนั้นแต่ละ Machine สามารถมี Downtime Type ไม่เหมือนกันได้
---
## 11. Downtime Type File Format
ไฟล์ใน `Downtime_Type` ใช้ Format:
```csv
Type Downtime,Active
```
ตัวอย่าง `AB2B.csv`:
```csv
Type Downtime,Active
Machine Breakdown,1
Material Shortage,1
Waiting Engineering,1
Customer Used,1
```
ค่า `Active`:
```text
1 = Active / แสดงในโปรแกรม
0 = Inactive / ไม่แสดงในโปรแกรม
```
---
## 12. How to Add a New Machine
ไม่ต้องแก้ Python และไม่ต้อง Build EXE ใหม่
Machine Dropdown ถูกสร้างจากชื่อไฟล์ `.csv` ใน:
```text
\\Fbn-fs01\global\_A\AtthaphanP\INNOVIZ\OEE\Downtime_Entry\Downtime_Type
```
ตัวอย่าง ต้องการเพิ่ม Machine:
```text
LASER
```
ให้สร้างไฟล์:
```text
Downtime_Type\LASER.csv
```
ภายในไฟล์:
```csv
Type Downtime,Active
Machine Breakdown,1
Sensor Alarm,1
Network Problem,1
Waiting Engineering,1
Customer Used,1
```
Save ไฟล์แล้วเปิดโปรแกรมใหม่
`LASER` จะปรากฏใน Machine Dropdown โดยอัตโนมัติ
> ชื่อไฟล์ CSV คือชื่อ Machine ที่จะแสดงในโปรแกรม
---
## 13. How to Add a New Downtime Type
ตัวอย่าง ต้องการเพิ่ม:
```text
Network Problem
```
ให้ Machine:
```text
AB2B
```
เปิดไฟล์:
```text
Downtime_Type\AB2B.csv
```
เพิ่ม:
```csv
Network Problem,1
```
ตัวอย่าง:
```csv
Type Downtime,Active
Machine Breakdown,1
Material Shortage,1
Waiting Engineering,1
Customer Used,1
Network Problem,1
```
Save ไฟล์
เมื่อเปิด `Add Downtime` ครั้งถัดไป จะเห็น `Network Problem` ใน Dropdown
ไม่ต้องแก้ Source Code หรือ Build EXE ใหม่
---
## 14. How to Disable a Downtime Type
หากไม่ต้องการใช้ Downtime Type บางรายการแล้ว ไม่แนะนำให้ลบ Row
ให้เปลี่ยน:
```text
Active = 1
```
เป็น:
```text
Active = 0
```
ตัวอย่าง:
```csv
Type Downtime,Active
Machine Breakdown,1
Material Shortage,1
Customer Used,0
```
วิธีนี้ช่วยรักษาชื่อ Downtime Type เดิมไว้สำหรับ Historical Data
---
## 15. Downtime Record Format
ไฟล์ Downtime Record ของแต่ละ Machine อยู่ใน:
```text
\\Fbn-fs01\global\_A\AtthaphanP\INNOVIZ\OEE\Downtime_Entry\Downtime_Record
```
ใช้ Format:
```csv
Machine,Type Downtime,Detail,EN Check In,Timestamp Check In,EN Check Out,Timestamp Check Out,Duration (hr),Status
```
ตัวอย่าง Open:
```csv
AB2B,Machine Breakdown,Sensor Alarm,524161,25/08/2026 10:00:00,,,,Open
```
ตัวอย่าง Closed:
```csv
AB2B,Customer Used,Software Update,524161,25/08/2026 08:00:00,524200,25/08/2026 08:30:00,0.50,Closed
```
---
## 16. Important Notes
### Do not rename CSV columns
Downtime Record ต้องใช้ Column:
```text
Machine
Type Downtime
Detail
EN Check In
Timestamp Check In
EN Check Out
Timestamp Check Out
Duration (hr)
Status
```
Downtime Type ต้องใช้:
```text
Type Downtime
Active
```
Python ใช้ชื่อ Column เหล่านี้ในการอ่านและเขียนข้อมูล
### Avoid manually editing Downtime Record
ไม่แนะนำให้แก้ไฟล์ใน `Downtime_Record` ด้วย Excel ระหว่างที่โปรแกรมกำลังใช้งาน
ควร Add / Check Out ผ่านโปรแกรมเพื่อป้องกันข้อมูลผิด Format หรือ File Conflict
### Machine name
ชื่อไฟล์ใน `Downtime_Type` คือชื่อ Machine
ตัวอย่าง:
```text
AB2B.csv
```
จะแสดงในโปรแกรมเป็น:
```text
AB2B
```
---
## 17. Engineer Quick Guide
### Add New Machine
1. เข้า:
```text
\\Fbn-fs01\global\_A\AtthaphanP\INNOVIZ\OEE\Downtime_Entry\Downtime_Type
```
2. สร้างไฟล์ เช่น:
```text
LASER.csv
```
3. ใส่:
```csv
Type Downtime,Active
Machine Breakdown,1
Sensor Alarm,1
Network Problem,1
Waiting Engineering,1
Customer Used,1
```
4. Save
5. เปิดโปรแกรมใหม่
`LASER` จะขึ้นใน Machine Dropdown อัตโนมัติ
### Add New Downtime Type
เปิดไฟล์ Machine ที่ต้องการ เช่น:
```text
Downtime_Type\AB2B.csv
```
เพิ่ม:
```csv
Safety Interlock,1
```
Save
Downtime Type ใหม่จะพร้อมใช้งานทันที
### Disable Downtime Type
เปลี่ยน:
```csv
Safety Interlock,1
```
เป็น:
```csv
Safety Interlock,0
```
---
## 18. Software Update
Software Version ใหม่สามารถ Download ได้จาก:
```text
GitHub Repository
→ Releases
```
ดาวน์โหลด:
```text
INZ_Downtime_Entry.zip
```
หลัง Extract:
```text
INZ_Downtime_Entry.exe
config.ini
```
หาก Shared Drive Path เดิมยังใช้งานได้ สามารถใช้ `config.ini` เดิมต่อได้
---
## 19. Technology
- Python
- PyQt6
- Pandas
- PyInstaller
- GitHub Actions
Windows `.exe` ถูก Build ผ่าน GitHub Actions และเผยแพร่ผ่าน GitHub Releases
Downtime Data ถูกจัดเก็บบน Company Shared Drive สำหรับใช้งานภายใน Production / OEE Reporting
