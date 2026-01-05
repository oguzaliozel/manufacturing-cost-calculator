import sqlite3
import os
import json

class Database:
    def __init__(self, db_name="manufacturing.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # 1. Materials Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                unit TEXT NOT NULL,
                unit_price REAL NOT NULL,
                scrap_price REAL DEFAULT 0,
                user_id INTEGER DEFAULT 1
            )
        ''')

        # 2. Processes Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                unit_type TEXT NOT NULL,
                unit_cost REAL NOT NULL,
                waste_rate REAL DEFAULT 0,
                user_id INTEGER DEFAULT 1
            )
        ''')

        # 3. Quotes Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                project_name TEXT NOT NULL,
                quote_date TEXT NOT NULL,
                total_amount REAL NOT NULL,
                net_cost REAL NOT NULL,
                profit REAL NOT NULL,
                scrap_value REAL DEFAULT 0,
                status TEXT DEFAULT 'Bekliyor',
                items_json TEXT,
                user_id INTEGER DEFAULT 1
            )
        ''')

        # 4. Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                security_question TEXT NOT NULL,
                security_answer_hash TEXT NOT NULL
            )
        ''')

        # 5. User Settings Table (NEW)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                theme TEXT DEFAULT 'dark',
                language TEXT DEFAULT 'tr',
                dashboard_layout TEXT DEFAULT 'default',
                notification_settings TEXT DEFAULT '{}',
                chart_preferences TEXT DEFAULT '{}',
                favorite_pages TEXT DEFAULT '[]',
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # 6. Customers Table (NEW)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                company TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                tax_id TEXT,
                notes TEXT,
                status TEXT DEFAULT 'Aktif',
                created_date TEXT,
                user_id INTEGER DEFAULT 1
            )
        ''')

        # 7. Calendar Events Table (NEW)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendar_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                event_date TEXT NOT NULL,
                event_time TEXT DEFAULT '09:00',
                event_type TEXT DEFAULT 'Genel',
                color TEXT DEFAULT '#3b82f6',
                description TEXT,
                user_id INTEGER DEFAULT 1
            )
        ''')

        # Migrations for existing DB files
        for table in ["materials", "processes", "quotes"]:
            try:
                cursor.execute(f'ALTER TABLE {table} ADD COLUMN user_id INTEGER DEFAULT 1')
            except sqlite3.OperationalError:
                pass

        try:
            cursor.execute('ALTER TABLE processes ADD COLUMN waste_rate REAL DEFAULT 0')
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute('ALTER TABLE materials ADD COLUMN scrap_price REAL DEFAULT 0')
        except sqlite3.OperationalError:
            pass

        conn.commit()
        conn.close()

    # --- Materials Methods ---
    def add_material(self, name, unit, price, scrap, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO materials (name, unit, unit_price, scrap_price, user_id) VALUES (?, ?, ?, ?, ?)',
                       (name, unit, price, scrap, user_id))
        conn.commit()
        conn.close()

    def get_materials(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM materials WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def delete_material(self, m_id, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM materials WHERE id = ? AND user_id = ?', (m_id, user_id))
        conn.commit()
        conn.close()

    def update_material(self, m_id, name, unit, price, scrap, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''UPDATE materials SET name=?, unit=?, unit_price=?, scrap_price=? WHERE id=? AND user_id=?''',
                       (name, unit, price, scrap, m_id, user_id))
        conn.commit()
        conn.close()

    # --- Processes Methods ---
    def add_process(self, name, unit_type, cost, waste, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO processes (name, unit_type, unit_cost, waste_rate, user_id) VALUES (?, ?, ?, ?, ?)',
                       (name, unit_type, cost, waste, user_id))
        conn.commit()
        conn.close()

    def get_processes(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM processes WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def delete_process(self, p_id, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM processes WHERE id = ? AND user_id = ?', (p_id, user_id))
        conn.commit()
        conn.close()

    def update_process(self, p_id, name, unit_type, cost, waste, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''UPDATE processes SET name=?, unit_type=?, unit_cost=?, waste_rate=? WHERE id=? AND user_id=?''',
                       (name, unit_type, cost, waste, p_id, user_id))
        conn.commit()
        conn.close()

    # --- Quotes Methods ---
    def add_quote(self, customer, project, date, total, cost, profit, scrap, items_json, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO quotes
                          (customer_name, project_name, quote_date, total_amount, net_cost, profit, scrap_value, status, items_json, user_id)
                          VALUES (?, ?, ?, ?, ?, ?, ?, 'Bekliyor', ?, ?)''',
                       (customer, project, date, total, cost, profit, scrap, items_json, user_id))
        conn.commit()
        conn.close()

    def get_quotes(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM quotes WHERE user_id = ? ORDER BY id DESC', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def update_quote(self, q_id, customer, project, total, cost, profit, scrap, items_json, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''UPDATE quotes SET
                          customer_name=?, project_name=?, total_amount=?, net_cost=?,
                          profit=?, scrap_value=?, items_json=?
                          WHERE id=? AND user_id=?''',
                       (customer, project, total, cost, profit, scrap, items_json, q_id, user_id))
        conn.commit()
        conn.close()

    def update_quote_status(self, q_id, status, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE quotes SET status = ? WHERE id = ? AND user_id = ?', (status, q_id, user_id))
        conn.commit()
        conn.close()

    def delete_quote(self, q_id, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM quotes WHERE id = ? AND user_id = ?', (q_id, user_id))
        conn.commit()
        conn.close()

    def get_dashboard_stats(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*), SUM(total_amount), SUM(profit) FROM quotes WHERE status = 'Onaylandı' AND user_id = ?", (user_id,))
        approved = cursor.fetchone()

        cursor.execute("SELECT COUNT(*), SUM(total_amount) FROM quotes WHERE status = 'Bekliyor' AND user_id = ?", (user_id,))
        pending = cursor.fetchone()

        cursor.execute("SELECT SUM(scrap_value) FROM quotes WHERE status != 'Reddedildi' AND user_id = ?", (user_id,))
        scrap = cursor.fetchone()

        conn.close()
        return {
            "approved_count": approved[0] or 0,
            "approved_total": approved[1] or 0,
            "approved_profit": approved[2] or 0,
            "pending_count": pending[0] or 0,
            "pending_total": pending[1] or 0,
            "total_scrap": scrap[0] or 0
        }

    def get_monthly_data(self, user_id):
        """Returns monthly approved quote totals for the current year."""
        conn = self.get_connection()
        cursor = conn.cursor()
        monthly = {}
        for m in range(1, 13):
            month_str = f".{m:02d}."
            cursor.execute(
                "SELECT SUM(total_amount) FROM quotes WHERE status='Onaylandı' AND user_id=? AND quote_date LIKE ?",
                (user_id, f"%{month_str}%")
            )
            val = cursor.fetchone()[0] or 0
            monthly[m] = val
        conn.close()
        return monthly

    # --- Users Methods ---
    def add_user(self, username, password_hash, question, answer_hash):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password_hash, security_question, security_answer_hash) VALUES (?, ?, ?, ?)',
                           (username, password_hash, question, answer_hash))
            user_id = cursor.lastrowid

            # Init user settings
            cursor.execute('INSERT OR IGNORE INTO user_settings (user_id) VALUES (?)', (user_id,))

            # Seed default materials
            default_materials = [
                ("Alüminyum 6061", "Plaka", 450.0, 15.0),
                ("Paslanmaz Çelik 304", "Plaka", 650.0, 12.0),
                ("Bakır Boru", "Metre", 120.0, 5.0),
                ("PVC Profil", "Metre", 85.0, 8.0),
            ]
            for name, unit, price, scrap in default_materials:
                cursor.execute('INSERT INTO materials (name, unit, unit_price, scrap_price, user_id) VALUES (?, ?, ?, ?, ?)',
                               (name, unit, price, scrap, user_id))

            # Seed default processes
            default_processes = [
                ("CNC Kesim", "Saat", 250.0, 10.0),
                ("TIG Kaynak", "Saat", 180.0, 5.0),
                ("Elektrostatik Boya", "Adet", 35.0, 2.0),
                ("Freze İşlemi", "Saat", 320.0, 8.0),
            ]
            for name, unit_type, cost, waste in default_processes:
                cursor.execute('INSERT INTO processes (name, unit_type, unit_cost, waste_rate, user_id) VALUES (?, ?, ?, ?, ?)',
                               (name, unit_type, cost, waste, user_id))

            conn.commit()
            success = True
        except sqlite3.IntegrityError:
            success = False
        finally:
            conn.close()
        return success

    def get_user(self, username):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        return row

    def update_user_password(self, username, new_password_hash):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', (new_password_hash, username))
        conn.commit()
        conn.close()

    # --- User Settings Methods ---
    def get_user_settings(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_settings WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "id": row[0], "user_id": row[1], "theme": row[2],
                "language": row[3], "dashboard_layout": row[4],
                "notification_settings": json.loads(row[5] or '{}'),
                "chart_preferences": json.loads(row[6] or '{}'),
                "favorite_pages": json.loads(row[7] or '[]')
            }
        return {"theme": "dark", "language": "tr"}

    def save_user_settings(self, user_id, theme=None, language=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO user_settings (user_id) VALUES (?)', (user_id,))
        if theme is not None:
            cursor.execute('UPDATE user_settings SET theme=? WHERE user_id=?', (theme, user_id))
        if language is not None:
            cursor.execute('UPDATE user_settings SET language=? WHERE user_id=?', (language, user_id))
        conn.commit()
        conn.close()

    # --- Customers Methods ---
    def add_customer(self, name, company, email, phone, address, tax_id, notes, user_id):
        from datetime import datetime
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO customers (name, company, email, phone, address, tax_id, notes, created_date, user_id)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (name, company, email, phone, address, tax_id, notes,
                        datetime.now().strftime("%d.%m.%Y"), user_id))
        conn.commit()
        conn.close()

    def get_customers(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customers WHERE user_id = ? ORDER BY id DESC', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def delete_customer(self, c_id, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM customers WHERE id = ? AND user_id = ?', (c_id, user_id))
        conn.commit()
        conn.close()

    def update_customer(self, c_id, name, company, email, phone, address, tax_id, notes, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''UPDATE customers SET name=?, company=?, email=?, phone=?, address=?, tax_id=?, notes=?
                          WHERE id=? AND user_id=?''',
                       (name, company, email, phone, address, tax_id, notes, c_id, user_id))
        conn.commit()
        conn.close()

    # --- Calendar Events Methods ---
    def add_event(self, title, event_date, event_time, event_type, color, description, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO calendar_events (title, event_date, event_time, event_type, color, description, user_id)
                          VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (title, event_date, event_time, event_type, color, description, user_id))
        conn.commit()
        conn.close()

    def get_events(self, user_id, month=None, year=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if month and year:
            month_str = f"{year}-{month:02d}"
            cursor.execute('SELECT * FROM calendar_events WHERE user_id = ? AND event_date LIKE ? ORDER BY event_date',
                           (user_id, f"{month_str}%"))
        else:
            cursor.execute('SELECT * FROM calendar_events WHERE user_id = ? ORDER BY event_date', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def delete_event(self, e_id, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM calendar_events WHERE id = ? AND user_id = ?', (e_id, user_id))
        conn.commit()
        conn.close()
