#!/usr/bin/env python3
"""
Database setup script - Convert MySQL schema to SQLite and populate with sample data
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "portnet.db"

def setup_database():
    """Create and populate SQLite database from MySQL schema"""
    
    # Remove existing database
    if DB_PATH.exists():
        DB_PATH.unlink()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Creating SQLite database...")
    
    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # VESSEL table
    cursor.execute('''
        CREATE TABLE vessel (
            vessel_id INTEGER PRIMARY KEY AUTOINCREMENT,
            imo_no INTEGER NOT NULL UNIQUE,
            vessel_name TEXT NOT NULL,
            call_sign TEXT,
            operator_name TEXT,
            flag_state TEXT,
            built_year INTEGER,
            capacity_teu INTEGER,
            loa_m REAL,       
            beam_m REAL,
            draft_m REAL,
            last_port TEXT,            
            next_port TEXT,            
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert vessels
    vessels = [
        (9300001,'MV Lion City 01','9VLC1','Oceanic Shipping','Singapore',2010,14000,366.00,51.00,15.00,'CNSHA','SGSIN'),
        (9300002,'MV Lion City 02','9VLC2','BlueWave Lines','Panama',2011,14500,368.50,51.20,15.20,'HKHKG','CNSHA'),
        (9300003,'MV Lion City 03','9VLC3','HarborStar','Liberia',2012,15000,370.00,52.00,15.50,'SGSIN','MYTPP'),
        (9300004,'MV Lion City 04','9VLC4','Oceanic Shipping','Marshall Islands',2013,15500,372.00,52.10,15.60,'JPTYO','SGSIN'),
        (9300005,'MV Lion City 05','9VLC5','BlueWave Lines','Denmark',2014,16000,375.00,53.00,15.80,'SGSIN','HKHKG'),
        (9300006,'MV Lion City 06','9VLC6','HarborStar','Malta',2015,16500,377.00,53.50,16.00,'CNSZX','CNSHA'),
        (9300007,'MV Lion City 07','9VLC7','Trident Global','Hong Kong',2016,17000,380.00,54.00,16.00,'SGSIN','IDJKT'),
        (9300008,'MV Lion City 08','9VLC8','Oceanic Shipping','Singapore',2017,17500,382.00,54.20,16.20,'MYTPP','SGSIN'),
        (9300009,'MV Lion City 09','9VLC9','BlueWave Lines','Germany',2018,18000,384.00,55.00,16.50,'SGSIN','JPTYO'),
        (9300010,'MV Lion City 10','9VLA0','HarborStar','UK',2019,18500,386.00,55.10,16.50,'KRPTK','SGSIN'),
        (9300011,'MV Merlion 11','9VML1','Trident Global','Singapore',2020,19000,388.00,56.00,16.50,'SGSIN','HKHKG'),
        (9300012,'MV Merlion 12','9VML2','Oceanic Shipping','Panama',2020,19000,388.00,56.00,16.50,'HKHKG','SGSIN'),
        (9300013,'MV Merlion 13','9VML3','BlueWave Lines','Liberia',2021,19500,390.00,56.50,16.60,'CNSHA','SGSIN'),
        (9300014,'MV Merlion 14','9VML4','HarborStar','Marshall Islands',2021,19500,390.00,56.50,16.60,'SGSIN','CAXMN'),
        (9300015,'MV Merlion 15','9VML5','Trident Global','Denmark',2022,20000,395.00,57.00,16.80,'SGSIN','USLAX'),
        (9300016,'MV Merlion 16','9VML6','Oceanic Shipping','Malta',2022,20000,395.00,57.00,16.80,'USLAX','SGSIN'),
        (9300017,'MV Merlion 17','9VML7','BlueWave Lines','Hong Kong',2023,20500,398.00,58.00,17.00,'SGSIN','AEMAA'),
        (9300018,'MV Merlion 18','9VML8','HarborStar','Singapore',2023,20500,398.00,58.00,17.00,'AEMAA','SGSIN'),
        (9300019,'MV Merlion 19','9VML9','Trident Global','Germany',2024,21000,400.00,58.60,17.20,'SGSIN','INNSA'),
        (9300020,'MV Merlion 20','9VMA0','Oceanic Shipping','Liberia',2024,21000,400.00,58.60,17.20,'INNSA','SGSIN')
    ]
    
    cursor.executemany('''
        INSERT INTO vessel (imo_no, vessel_name, call_sign, operator_name, flag_state, built_year, capacity_teu, loa_m, beam_m, draft_m, last_port, next_port)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    ''', vessels)
    
    # CONTAINER table
    cursor.execute('''
        CREATE TABLE container (
            container_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cntr_no TEXT NOT NULL,      
            iso_code TEXT NOT NULL,          
            size_type TEXT NOT NULL,      
            gross_weight_kg REAL,
            status TEXT NOT NULL CHECK (status IN ('IN_YARD','ON_VESSEL','GATE_OUT','GATE_IN','DISCHARGED','LOADED','TRANSHIP')),
            origin_port TEXT NOT NULL,
            tranship_port TEXT NOT NULL DEFAULT 'SGSIN',
            destination_port TEXT NOT NULL,
            hazard_class TEXT,          
            vessel_id INTEGER,
            eta_ts DATETIME,
            etd_ts DATETIME,
            last_free_day DATE,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vessel_id) REFERENCES vessel(vessel_id)
        )
    ''')
    
    # Insert containers
    containers = [
        ('MSKU0000001','22G1','20GP', 12000,'TRANSHIP','CNSHA','SGSIN','MYTPP',None, 1,'2025-10-04 12:00','2025-10-05 18:00','2025-10-10'),
        ('MSKU0000002','45R1','40RF',  8000,'IN_YARD','HKHKG','SGSIN','IDJKT',None, 2,'2025-10-05 08:00','2025-10-06 20:00','2025-10-11'),
        ('MSKU0000003','22G1','20GP', 11000,'DISCHARGED','CNSZX','SGSIN','SGSIN',None, 3,'2025-10-03 16:00',None,'2025-10-09'),
        ('MSKU0000004','22G1','20GP', 13000,'LOADED','MYTPP','SGSIN','JPTYO',None, 4,'2025-10-06 10:00','2025-10-06 22:00','2025-10-12'),
        ('MSKU0000005','45G1','40HQ', 15000,'TRANSHIP','JPTYO','SGSIN','CNSHA',None, 5,'2025-10-04 18:00','2025-10-05 23:00','2025-10-10'),
        ('MSCU0000006','45G1','40HQ', 14500,'IN_YARD','SGSIN','SGSIN','USLAX',None, 6,'2025-10-07 06:00','2025-10-08 02:00','2025-10-13'),
        ('MSCU0000007','22G1','20GP', 10000,'TRANSHIP','CNSHA','SGSIN','HKHKG',None, 7,'2025-10-05 05:00','2025-10-05 20:00','2025-10-11'),
        ('MSCU0000008','22G1','20GP', 11500,'GATE_IN','HKHKG','SGSIN','SGSIN',None, 8,'2025-10-04 09:00',None,'2025-10-09'),
        ('MSCU0000009','22G1','20GP', 12500,'ON_VESSEL','SGSIN','SGSIN','CAXMN',None, 9,None,'2025-10-06 12:00','2025-10-12'),
        ('MSCU0000010','45R1','40RF',  9000,'TRANSHIP','CAXMN','SGSIN','SGSIN','9', 10,'2025-10-05 14:00','2025-10-06 14:00','2025-10-11'),
        ('OOLU0000011','45G1','40HQ', 14800,'TRANSHIP','KRPTK','SGSIN','AEMAA',None, 1,'2025-10-06 02:00','2025-10-07 01:00','2025-10-13'),
        ('OOLU0000012','22G1','20GP', 10800,'DISCHARGED','AEMAA','SGSIN','SGSIN',None, 2,'2025-10-03 22:00',None,'2025-10-09'),
        ('OOLU0000013','22G1','20GP', 11800,'LOADED','SGSIN','SGSIN','INNSA',None, 3,None,'2025-10-05 21:00','2025-10-12'),
        ('OOLU0000014','22G1','20GP', 11200,'GATE_OUT','SGSIN','SGSIN','SGSIN',None, 4,None,None,'2025-10-08'),
        ('TEMU0000015','45G1','40HQ', 15100,'TRANSHIP','INNSA','SGSIN','CNSHA',None, 5,'2025-10-04 20:00','2025-10-06 00:00','2025-10-11'),
        ('TEMU0000016','45R1','40RF',  8600,'IN_YARD','CNSHA','SGSIN','MYTPP','3', 6,'2025-10-07 08:00','2025-10-08 03:00','2025-10-13'),
        ('TEMU0000017','22G1','20GP', 12200,'TRANSHIP','HKHKG','SGSIN','JPTYO',None, 7,'2025-10-05 11:00','2025-10-05 23:59','2025-10-11'),
        ('TEMU0000018','22G1','20GP', 11900,'ON_VESSEL','JPTYO','SGSIN','SGSIN',None, 8,None,'2025-10-06 03:00','2025-10-12'),
        ('CMAU0000019','45G1','40HQ', 14950,'TRANSHIP','USLAX','SGSIN','SGSIN',None, 9,'2025-10-05 16:00','2025-10-06 18:00','2025-10-11'),
        ('CMAU0000020','22G1','20GP', 10990,'DISCHARGED','CAXMN','SGSIN','SGSIN',None, 10,'2025-10-03 13:00',None,'2025-10-09')
    ]
    
    cursor.executemany('''
        INSERT INTO container (cntr_no, iso_code, size_type, gross_weight_kg, status, origin_port, tranship_port, destination_port, hazard_class, vessel_id, eta_ts, etd_ts, last_free_day)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', containers)
    
    # EDI_MESSAGE table
    cursor.execute('''
        CREATE TABLE edi_message (
            edi_id INTEGER PRIMARY KEY AUTOINCREMENT,
            container_id INTEGER, 
            vessel_id INTEGER, 
            message_type TEXT NOT NULL CHECK (message_type IN ('COPARN','COARRI','CODECO','IFTMCS','IFTMIN')),
            direction TEXT NOT NULL CHECK (direction IN ('IN','OUT')),
            status TEXT NOT NULL DEFAULT 'RECEIVED' CHECK (status IN ('RECEIVED','PARSED','ACKED','ERROR')),
            message_ref TEXT NOT NULL,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            sent_at DATETIME NOT NULL,
            ack_at DATETIME,
            error_text TEXT,
            raw_text TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (container_id) REFERENCES container(container_id),
            FOREIGN KEY (vessel_id) REFERENCES vessel(vessel_id)
        )
    ''')
    
    # Insert EDI messages with intentional errors for testing
    edi_messages = [
        (1,1,'COPARN','IN','PARSED','REF-COP-0001','LINE-PSA','PSA-TOS','2025-10-03 08:01','2025-10-03 08:02',None,'UNA:+.? \\nUNB+...'),
        (2,2,'COPARN','IN','PARSED','REF-COP-0002','LINE-PSA','PSA-TOS','2025-10-03 08:05','2025-10-03 08:06',None,'UNA:+.? \\nUNB+...'),
        (3,3,'COARRI','OUT','ACKED','REF-ARR-0003','PSA-TOS','LINE-PSA','2025-10-03 17:10','2025-10-03 17:12',None,'UNH+...'),
        (4,4,'COARRI','OUT','ACKED','REF-ARR-0004','PSA-TOS','LINE-PSA','2025-10-04 06:40','2025-10-04 06:41',None,'UNH+...'),
        (5,5,'CODECO','OUT','ACKED','REF-DEC-0005','PSA-DEPOT','LINE-PSA','2025-10-04 09:00','2025-10-04 09:01',None,'UNH+...'),
        (6,6,'IFTMIN','IN','PARSED','REF-IFT-0006','LINE-PSA','PSA-TOS','2025-10-04 12:20','2025-10-04 12:21',None,'UNH+...'),
        (7,7,'IFTMIN','IN','ERROR','REF-IFT-0007','LINE-PSA','PSA-TOS','2025-10-04 12:25',None,'Segment missing','UNH+...'),
        (8,8,'COPARN','IN','PARSED','REF-COP-0008','LINE-PSA','PSA-TOS','2025-10-04 13:10','2025-10-04 13:11',None,'UNH+...'),
        (9,9,'COARRI','OUT','ACKED','REF-ARR-0009','PSA-TOS','LINE-PSA','2025-10-04 14:33','2025-10-04 14:34',None,'UNH+...'),
        (10,10,'CODECO','OUT','ERROR','REF-DEC-0010','PSA-DEPOT','LINE-PSA','2025-10-04 15:00',None,'Connection timeout','UNH+...'),
        (11,1,'COPARN','IN','PARSED','REF-COP-0011','LINE-PSA','PSA-TOS','2025-10-05 07:05','2025-10-05 07:06',None,'UNH+...'),
        (12,2,'IFTMIN','IN','ERROR','REF-IFT-0012','LINE-PSA','PSA-TOS','2025-10-05 07:15',None,'Duplicate entry detected','UNH+...'),
        (13,3,'COARRI','OUT','ACKED','REF-ARR-0013','PSA-TOS','LINE-PSA','2025-10-05 08:20','2025-10-05 08:21',None,'UNH+...'),
        (14,4,'CODECO','OUT','ACKED','REF-DEC-0014','PSA-DEPOT','LINE-PSA','2025-10-05 09:20','2025-10-05 09:22',None,'UNH+...'),
        (15,5,'IFTMIN','IN','PARSED','REF-IFT-0015','LINE-PSA','PSA-TOS','2025-10-05 10:10','2025-10-05 10:11',None,'UNH+...'),
        (16,6,'COPARN','IN','PARSED','REF-COP-0016','LINE-PSA','PSA-TOS','2025-10-05 10:30','2025-10-05 10:31',None,'UNH+...'),
        (17,7,'COARRI','OUT','ERROR','REF-ARR-0017','PSA-TOS','LINE-PSA','2025-10-05 11:00',None,'Status mismatch detected','UNH+...'),
        (18,8,'CODECO','OUT','ACKED','REF-DEC-0018','PSA-DEPOT','LINE-PSA','2025-10-05 12:00','2025-10-05 12:01',None,'UNH+...'),
        (19,9,'IFTMIN','IN','PARSED','REF-IFT-0019','LINE-PSA','PSA-TOS','2025-10-05 12:30','2025-10-05 12:31',None,'UNH+...'),
        (20,10,'COPARN','IN','PARSED','REF-COP-0020','LINE-PSA','PSA-TOS','2025-10-05 13:00','2025-10-05 13:02',None,'UNH+...')
    ]
    
    cursor.executemany('''
        INSERT INTO edi_message (container_id, vessel_id, message_type, direction, status, message_ref, sender, receiver, sent_at, ack_at, error_text, raw_text)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    ''', edi_messages)
    
    # API_EVENT table
    cursor.execute('''
        CREATE TABLE api_event (
            api_id INTEGER PRIMARY KEY AUTOINCREMENT,
            container_id INTEGER,
            vessel_id INTEGER,
            event_type TEXT NOT NULL CHECK (event_type IN ('GATE_IN','GATE_OUT','LOAD','DISCHARGE','CUSTOMS_CLEAR','HOLD','RELEASE')),
            source_system TEXT NOT NULL,    
            http_status INTEGER,
            correlation_id TEXT,
            event_ts DATETIME NOT NULL,
            payload_json TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (container_id) REFERENCES container(container_id),
            FOREIGN KEY (vessel_id) REFERENCES vessel(vessel_id)
        )
    ''')
    
    # Insert API events
    api_events = [
        (1,1,'DISCHARGE','TOS',200,'corr-0001','2025-10-03 17:20', '{"bay":"12","row":"04","tier":"06"}'),
        (2,2,'GATE_IN','CMS',201,'corr-0002','2025-10-03 18:05', '{"gate":"C3"}'),
        (3,3,'DISCHARGE','TOS',200,'corr-0003','2025-10-03 18:30', '{"crane":"QC-05"}'),
        (4,4,'LOAD','TOS',200,'corr-0004','2025-10-04 06:55', '{"stow":"23-08-04"}'),
        (5,5,'LOAD','TOS',200,'corr-0005','2025-10-04 23:10', '{"stow":"25-02-02"}'),
        (6,6,'GATE_IN','CMS',200,'corr-0006','2025-10-05 01:15', '{"truck":"SGL1234Z"}'),
        (7,7,'LOAD','TOS',200,'corr-0007','2025-10-05 05:25', '{"stow":"11-06-07"}'),
        (8,8,'GATE_OUT','CMS',200,'corr-0008','2025-10-05 08:40', '{"gate":"A1"}'),
        (9,9,'LOAD','TOS',200,'corr-0009','2025-10-05 12:05', '{"stow":"07-10-03"}'),
        (10,10,'DISCHARGE','TOS',200,'corr-0010','2025-10-05 14:20', '{"crane":"QC-02"}'),
        (11,1,'LOAD','TOS',200,'corr-0011','2025-10-06 01:05', '{"stow":"18-04-01"}'),
        (12,2,'DISCHARGE','TOS',200,'corr-0012','2025-10-06 02:30', '{"crane":"QC-07"}'),
        (13,3,'LOAD','TOS',200,'corr-0013','2025-10-06 03:10', '{"stow":"15-12-06"}'),
        (14,4,'GATE_OUT','CMS',200,'corr-0014','2025-10-06 04:00', '{"truck":"SGK5678A"}'),
        (15,5,'LOAD','TOS',200,'corr-0015','2025-10-06 05:45', '{"stow":"09-03-09"}'),
        (16,6,'GATE_IN','CMS',200,'corr-0016','2025-10-06 07:05', '{"gate":"B2"}'),
        (17,7,'LOAD','TOS',200,'corr-0017','2025-10-06 09:20', '{"stow":"03-01-02"}'),
        (18,8,'DISCHARGE','TOS',200,'corr-0018','2025-10-06 12:15', '{"crane":"QC-03"}'),
        (19,9,'LOAD','TOS',200,'corr-0019','2025-10-06 15:40', '{"stow":"05-08-10"}'),
        (20,10,'DISCHARGE','TOS',200,'corr-0020','2025-10-06 16:55', '{"crane":"QC-09"}')
    ]
    
    cursor.executemany('''
        INSERT INTO api_event (container_id, vessel_id, event_type, source_system, http_status, correlation_id, event_ts, payload_json)
        VALUES (?,?,?,?,?,?,?,?)
    ''', api_events)
    
    # VESSEL_ADVICE table
    cursor.execute('''
        CREATE TABLE vessel_advice (
            vessel_advice_no INTEGER PRIMARY KEY AUTOINCREMENT,
            vessel_name TEXT NOT NULL,
            system_vessel_name TEXT NOT NULL,          
            effective_start_datetime DATETIME NOT NULL,
            effective_end_datetime DATETIME,                 
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # BERTH_APPLICATION table  
    cursor.execute('''
        CREATE TABLE berth_application (
            application_no INTEGER PRIMARY KEY AUTOINCREMENT,
            vessel_advice_no INTEGER NOT NULL,
            vessel_close_datetime DATETIME,
            deleted TEXT NOT NULL DEFAULT 'N' CHECK (deleted IN ('Y','N')),
            berthing_status TEXT NOT NULL DEFAULT 'A',
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vessel_advice_no) REFERENCES vessel_advice(vessel_advice_no)
        )
    ''')
    
    # Insert vessel advice data
    vessel_advice_data = [
        (1000010960, 'MV Lion City 07', 'MV Lion City 07', '2025-10-01 00:00:00', None),
        (1000010500, 'MV Lion City 08', 'MV Lion City 08', '2025-09-15 00:00:00', '2025-10-01 00:00:00'),
        (1000010961, 'MV Lion City 08', 'MV Lion City 08', '2025-10-01 00:00:00', None),
        (1000010962, 'MV Merlion 11', 'MV Merlion 11', '2025-10-02 00:00:00', None),
        (1000010400, 'MV Merlion 12', 'MV Merlion 12', '2025-08-01 00:00:00', '2025-09-01 00:00:00'),
        (1000010600, 'MV Merlion 12', 'MV Merlion 12', '2025-09-05 00:00:00', '2025-09-20 00:00:00'),
        (1000010700, 'MV Merlion 15', 'MV Merlion 15', '2025-09-10 00:00:00', '2025-09-25 00:00:00'),
        (1000010963, 'MV Merlion 15', 'MV Merlion 15', '2025-09-25 00:00:00', None)
    ]
    
    cursor.executemany('''
        INSERT INTO vessel_advice (vessel_advice_no, vessel_name, system_vessel_name, effective_start_datetime, effective_end_datetime)
        VALUES (?,?,?,?,?)
    ''', vessel_advice_data)
    
    # Insert berth applications
    berth_applications = [
        (1000010960, None, 'N', 'A'),
        (1000010961, None, 'N', 'A'),  
        (1000010962, None, 'N', 'A'),   
        (1000010963, None, 'N', 'A')
    ]
    
    cursor.executemany('''
        INSERT INTO berth_application (vessel_advice_no, vessel_close_datetime, deleted, berthing_status)
        VALUES (?,?,?,?)
    ''', berth_applications)
    
    # Create views
    cursor.execute('''
        CREATE VIEW vw_tranship_pipeline AS
        SELECT
            c.cntr_no,
            c.size_type,
            c.status,
            c.origin_port,
            c.tranship_port,
            c.destination_port,
            v.vessel_name,
            v.imo_no,
            c.eta_ts,
            c.etd_ts,
            c.last_free_day
        FROM container c
        LEFT JOIN vessel v ON v.vessel_id = c.vessel_id
    ''')
    
    cursor.execute('''
        CREATE VIEW vw_edi_last AS
        SELECT
            c.cntr_no,
            MAX(e.sent_at) AS last_edi_time,
            (SELECT e2.message_type FROM edi_message e2 WHERE e2.container_id = c.container_id ORDER BY e2.sent_at DESC LIMIT 1) AS last_edi_type,
            (SELECT e2.status FROM edi_message e2 WHERE e2.container_id = c.container_id ORDER BY e2.sent_at DESC LIMIT 1) AS last_edi_status
        FROM edi_message e
        JOIN container c ON c.container_id = e.container_id
        GROUP BY c.cntr_no
    ''')
    
    conn.commit()
    
    print(f"✅ SQLite database created successfully at: {DB_PATH}")
    print(f"   - {len(vessels)} vessels")
    print(f"   - {len(containers)} containers") 
    print(f"   - {len(edi_messages)} EDI messages (including error scenarios)")
    print(f"   - {len(api_events)} API events")
    print(f"   - {len(vessel_advice_data)} vessel advice records")
    print(f"   - {len(berth_applications)} berth applications")
    print("   - 2 views created")
    
    conn.close()

if __name__ == "__main__":
    setup_database()
