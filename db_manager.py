import sqlite3
import datetime
from datetime import date
import secrets
import smtplib
from email.mime.text import MIMEText
import bcrypt

# conn = sqlite3.connect("data.db", check_same_thread=False)
# c = conn.cursor()
# hashed_password = bcrypt.hashpw("adminadmin".encode(), bcrypt.gensalt())
# c.execute("""
#     INSERT INTO users (name, email, password, role, profile_pic) VALUES(?,?,?,?,?)
# """, ("Admin", "admin@gmail.com", hashed_password, 0,"uploads/default-avatar.png"))

# # c.execute("""DELETE FROM users""")
# conn.commit()
# c.execute(
#     '''
#         DROP TABLE IF EXISTS users
#     '''
# )

# c.execute('''
#     CREATE TABLE IF NOT EXISTS users (
#         id INTEGER PRIMARY KEY,
#         name TEXT,
#         email TEXT,
#         password TEXT,
#         sex TEXT,
#         role INTEGER,
#         is_active INTEGER DEFAULT 1,
#         profile_pic,
#         created_at DATE,
#         doctor_id INTEGR,
#         FOREIGN KEY (doctor_id) REFERENCES users(id)
#     )
# ''')
#

# c.execute('''
#     DELETE FROM users WHERE role = 0;
# ''')

# # conn.commit()
# hashed_password = bcrypt.hashpw("adminadmin".encode(), bcrypt.gensalt())
# c.execute('''
#             INSERT INTO users (name, email, password, sex, role, profile_pic, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)
#         ''', ("Admin", "admin@gmail.com", hashed_password, "M", "0", "uploads/default-avatar.png", datetime.date.today()))
# conn.commit()
# c.execute('''
#             INSERT INTO users (name, email, password, sex, created_at) VALUES (?, ?, ?, ?, ?)
#         ''', ("User2", "user2@gmail.com", hashed_password, "F", datetime.date(year=2023, month=2, day=22)))
# c.execute('''
#             INSERT INTO users (name, email, password, sex, created_at) VALUES (?, ?, ?, ?, ?)
#         ''', ("User3", "user3@gmail.com", hashed_password, "F", datetime.date(year=2023, month=3, day=15)))
# c.execute('''
#             INSERT INTO users (name, email, password, sex, created_at) VALUES (?, ?, ?, ?, ?)
#         ''', ("User4", "user4@gmail.com", hashed_password, "M", datetime.date(year=2023, month=1, day=15)))

# # c.execute('''
# #              INSERT INTO users (name, email, password, sex, created_at, is_admin) VALUES (?, ?, ?, ?, ?, ?)
# #          ''', ("Admin", "admin@gmail.com", hashed_password, "M", datetime.date(year=2023, month=1, day=15), 1))
# conn.commit()

# c.execute('''
#     CREATE TABLE IF NOT EXISTS password_resets (
#         token TEXT,
#         email TEXT,
#         expiration_time TIMESTAMP
#     )
# ''')


def check_email_exists(email):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    # Execute a query to check if the email exists in the database
    c.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email,))
    result = c.fetchone()
    count = result[0]
    if count > 0:
        return True
    else:
        return False


def generate_random_passwor():
    import secrets
    import string

    letters = string.ascii_letters
    digits = string.digits
    special_chars = string.punctuation

    alphabet = letters + digits + special_chars
    pwd = ''
    for _ in range(12):
        pwd += ''.join(secrets.choice(alphabet))

    return pwd


def create_user(name, email, sex, role):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    password = generate_random_passwor()
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    print(password)
    try:
        c.execute('''
            INSERT INTO users (name, email, sex, role, profile_pic, password, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, email, sex, role, "uploads/default-avatar.png", hashed_password, date.today()))
        conn.commit()
        send_email_with_password(name, email, password)

        return True
    except Exception as e:
        print(str(e))
        return False
    finally:
        c.close()
        conn.close()


def edit_user(user_id, name, sex):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    try:
        c.execute('''
            UPDATE users SET name = ?, sex = ? WHERE id = ?
            ''', (name, sex, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(str(e))
        return False
    finally:
        c.close()
        conn.close()


def send_email_with_password(name, email, password):
    sender_email = "zakimouzaoui123@gmail.com"
    sender_password = "rvcxcsouyzocyfba"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Construct the email message
    subject = "Login password"
    message = f"Hi {name}, your password is {password}. You can now login with it in our plateform http://localhost:8503"

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = email

    try:
        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


# conn = sqlite3.connect('data.db')
# c = conn.cursor()

# c.execute("""
#     UPDATE users SET created_at = ? WHERE id = ?
# """, (date(year=2023, month=3, day=6), 2))
# conn.commit()

# c.close()
# conn.close()


def authenticate_user(email, password):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    try:
        c.execute(
            "SELECT id, name, password, role, is_active, email, profile_pic FROM users WHERE email = ?", (email,))
        result = c.fetchone()

        if result is None:
            return {"status": "error", "message": "Invalid email"}
        else:
            if result[4] == 0:
                return {"status": "error", "message": "Your account is currently blocked. Please contact the admin to restore it"}

        hashed_password = result[2]

        if not bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return {"status": "error", "message": "Invalid password"}
        return {"status": "success", "result": [result[0], result[3], result[1], result[4], result[5], result[-1]]}

    except Exception as e:
        print(e)
        return {"status": "error", "message": "Something went wrong"}
    finally:
        c.close()
        conn.close()


def is_password_strong(password):
    # Check length
    if len(password) < 8:
        return False

    # Check for uppercase letter, lowercase letter, and digit
    has_uppercase = False
    has_lowercase = False
    has_digit = False
    for char in password:
        if char.isupper():
            has_uppercase = True
        elif char.islower():
            has_lowercase = True
        elif char.isdigit():
            has_digit = True

    # Check if all required criteria are met
    if not (has_uppercase and has_lowercase and has_digit):
        return False

    # Password is strong
    return True


def change_password(user_id, new_password):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    try:
        # user = c.execute(
        #     "SELECT password FROM users WHERE id = ?", (user_id,)).fetchone()

        # hashed_old_password = user[0]
        # if not bcrypt.checkpw(old_password.encode('utf-8'), hashed_old_password):
        #     return {
        #         "status": "error", "message": "Incorrect old password"
        #     }
        # else:
        if is_password_strong(new_password):
            hashed_password = bcrypt.hashpw(
                new_password.encode(), bcrypt.gensalt())
            c.execute("""
                    UPDATE users SET password = ? WHERE id = ?
                """, (hashed_password, user_id))
            conn.commit()

            return {"status": "success", "message": "Password changed successfully"}
        else:
            return {"status": "error", "message": "Password must be atleast 8 characters and contains uppercase and lowercase"}
    except Exception as e:
        print(str(e))
        return {"status": "error", "message": "Something went wrong"}
    finally:
        c.close()
        conn.close()


def change_profile_pic(user_id, url):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute("""
        UPDATE users SET profile_pic = ? WHERE id = ?
    """, (url, user_id))
    conn.commit()
    c.close()
    conn.close()


# def retrieve_users():
#     conn = sqlite3.connect('data.db')
#     c = conn.cursor()

#     try:
#         c.execute("SELECT COUNT(*) FROM users")
#         data = c.fetchone()[0]
#         return data
#     except Exception as e:
#         print(str(e))
#         return []
#     finally:
#         c.close()
#         conn.close()

# def paginate_users(col_order, order_type, limit, offset):
#     c.execute(
#         f"SELECT id, name, sex, email, role, is_active, created_at FROM users WHERE role != 0 ORDER BY {col_order} {order_type} LIMIT {limit} OFFSET {offset}")
#     return c.fetchall()


def retrieve_users():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute(
        f"SELECT id, name, sex, email, role, is_active, created_at FROM users WHERE role != 0 AND role != 3")
    data = c.fetchall()
    c.close()
    conn.close()

    return data


def block_unblock_user(id, val):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute(f"""UPDATE users SET is_active = {val} WHERE id = {id}
                """)
    conn.commit()
    c.close()
    conn.close()


def is_admin(user_id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    try:
        c.execute(f"SELECT id from users WHERE is_admin == 1 LIMIT 1")
        id = c.fetchone()[0]
        return user_id == str(id)
    except:
        return None
    finally:
        c.close()
        conn.close()


def generate_password_reset_token(email):
    token = secrets.token_urlsafe(32)
    expiration_time = datetime.datetime.now() + datetime.timedelta(hours=1)
    conn = sqlite3.connect('data.db')

    c = conn.cursor()
    c.execute('''
        INSERT INTO password_resets (token, email, expiration_time)
        VALUES (?, ?, ?)
    ''', (token, email, expiration_time))
    conn.commit()
    c.close()
    conn.close()
    return token


def send_password_reset_email(email, token):
    # Email configuration
    sender_email = "zakimouzaoui123@gmail.com"
    sender_password = "rvcxcsouyzocyfba"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Construct the email message
    subject = "Password Reset"
    # message = f"Click the link below to reset your password:\n\n" \
    #           f"http://localhost:8501/Reset%20Password?token={token}"
    message = f"Your secret token is {token}. Do not share it with anyone. These token will expire in 1 hour"

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = email

    try:
        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def reset_password(token, new_password):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    try:
        c.execute('''
            SELECT email, expiration_time
            FROM password_resets
            WHERE token = ?
        ''', (token,))
        result = c.fetchone()
        if result is None:
            # Token not found or expired
            return False

        email, expiration_time = result
        if str(datetime.datetime.now()) > expiration_time:
            # Token expired
            return False

        hashed_password = bcrypt.hashpw(
            new_password.encode(), bcrypt.gensalt())
        c.execute('''
            UPDATE users
            SET password = ?
            WHERE email = ?
        ''', (hashed_password, email))
        conn.commit()

        c.execute('''
            DELETE FROM password_resets
            WHERE token = ?
        ''', (token,))
        conn.commit()

        return True
    finally:
        c.close()
        conn.close()


def create_patient_table():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute("DROP TABLE IF EXISTS patients")
    c.execute("""
        CREATE TABLE IF NOT EXISTS patients(
            name TEXT,
            sex TEXT,
            age INTEGER,
            user_id INTEGER,
            doctor_id INTEGER,
            created_at DATE,
            FOREIGN KEY (user_id) REFERENCES users (id)
            FOREIGN KEY (doctor_id) REFERENCES users (id))
    """)
    conn.commit()
    c.close()
    conn.close()


def add_patient(doctor_id, name, email, sex, age):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    try:
        random_pwd = generate_random_passwor()
        hashed_password = bcrypt.hashpw(random_pwd.encode(), bcrypt.gensalt())

        c.execute("""
            INSERT INTO users(name, email, password, sex, role, created_at) VALUES(?,?,?,?,?,?)
        """, (name, email, hashed_password, sex, "3", date.today()))
        user_id = c.lastrowid
        c.execute("""
            INSERT INTO patients(user_id, name, sex, age, doctor_id, created_at) VALUES(?,?,?,?,?,?)
        """, (user_id, name, sex, age, doctor_id, date.today()))

        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        c.close()
        conn.close()


def edit_patient(user_id, name, sex, age):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    try:
        c.execute("""
            UPDATE patients SET name = ?, sex = ?, age = ? WHERE user_id = ?
        """, (name, sex, age, user_id))

        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        c.close()
        conn.close()


def delete_patient(user_id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    try:
        c.execute("""
            DELETE FROM patients WHERE user_id = ?
        """, (user_id,))

        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        c.close()
        conn.close()


def view_patients(doctor_id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute("SELECT patients.user_id, patients.name, patients.sex, patients.age, patients.created_at "
              "FROM patients "
              "JOIN users ON patients.doctor_id = users.id "
              "WHERE users.id = ?", (doctor_id,))
    result = c.fetchall()
    c.close()
    conn.close()
    return result


def view_all_patients():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute(f"""SELECT p.user_id, p.name, u.email, p.sex, p.age, u.id, u.name, p.created_at FROM patients p
                JOIN users u ON p.doctor_id = u.id
                """)

    result = c.fetchall()
    c.close()
    conn.close()

    return result


# def get_pending_requests():

#     c.execute(f"""SELECT p.id, p.name, p.sex, p.age, p.tumor, u.id, u.name, p.created_at FROM patients p
#                 JOIN users u ON p.user_id = u.id WHERE p.req_status == -1
#                 """)
#     result = c.fetchall()
#     return result


# def approve_deny_request(id, val):
#     c.execute(f"""UPDATE patients SET req_status = {val} WHERE id = {id}
#                 """)
#     conn.commit()


def delete_patients():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute("""
        DELETE FROM patients
    """)
    conn.commit()
    c.close()
    conn.close()


def create_message_table():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute("""
        DROP TABLE IF EXISTS  messages
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY, name TEXT, email TEXT, subject TEXT, content TEXT, is_read INTEGER DEFAULT 0, created_at DATE
        )
    """)
    conn.commit()
    c.close()
    conn.close()


def add_message(name, email, subject, content):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute("""
            INSERT INTO messages(name, email, subject, content, created_at) VALUES(?,?,?,?,?)
        """, (name, email, subject, content, datetime.date.today()))

    conn.commit()
    c.close()
    conn.close()


def mark_as_read(id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute(f"""
            UPDATE messages SET is_read = 1 WHERE id = {id}
        """)
    conn.commit()
    c.close()
    conn.close()


def get_messages():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    try:
        c.execute("""
            SELECT * FROM messages ORDER BY created_at DESC
        """)
        return c.fetchall()
    except:
        return []
    finally:
        c.close()
        conn.close()


def delete_single_message(id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute(f"""
            DELETE FROM messages WHERE id = {id}
        """)
    conn.commit()
    c.close()
    conn.close()


def delete_all_messages():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute(f"""
            DELETE FROM messages
        """)
    conn.commit()
    c.close()
    conn.close()


# conn = sqlite3.connect('data.db')
# c = conn.cursor()
# c.execute("DELETE FROM users WHERE id = 16")
# conn.commit()
# c = conn.cursor()
# c.close()


def add_history(activity):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("""
        INSERT INTO history (activity, timestamp) VALUES(?,?)
    """, (activity, datetime.date.today()))
    conn.commit()
    c.close()
    conn.close()


def delete_activities(ids):
    id_list = ', '.join(str(id) for id in ids)
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute(f"""
        DELETE FROM history WHERE id IN ({id_list})
    """)
    conn.commit()
    c.close()
    conn.close()


def get_history():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    try:
        c.execute("""
            SELECT * FROM history
        """)
        return c.fetchall()
    except:
        return []
    finally:
        c.close()
        conn.close()


def create_notifications_table():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("""
        DROP TABLE IF EXISTS notifications
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS notifications(
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            req_id INTEGER,
            title TEXT,
            notification TEXT,
            is_read INTEGER DEFAULT 0,
            timestamp DATE,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (req_id) REFERENCES patients (id))
    """)
    conn.commit()
    c.close()
    conn.close()


def add_notification(user_id, req_id, title, content):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("""
        INSERT INTO notifications(user_id, req_id, title, notification, timestamp) VALUES(?,?,?,?,?)
    """, (user_id, req_id, title, content, datetime.date.today()))
    conn.commit()
    c.close()
    conn.close()


def view_notifications(user_id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    try:
        c.execute("""
            SELECT n.id, n.title, n.notification, n.timestamp, n.is_read, p.name, p.age, p.sex, p.tumor, p.created_at AS patient_name
            FROM notifications n
            INNER JOIN patients p ON p.id = n.req_id
            WHERE n.user_id = ?
        """, (user_id, ))
        # c.execute("SELECT * FROM notifications")
        return c.fetchall()
    except:
        return []
    finally:
        c.close()
        conn.close()


def mark_notification_as_read(id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute(f"""
            UPDATE notifications SET is_read = 1 WHERE id = {id}
        """)
    conn.commit()
    c.close()
    conn.close()


def delete_single_notification(id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute(f"""
            DELETE FROM notifications WHERE id = {id}
        """)
    conn.commit()
    c.close()
    conn.close()


def delete_all_notifications():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute(f"""
            DELETE FROM notifications
        """)
    conn.commit()
    c.close()
    conn.close()


def create_appointments_table():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute(""" DROP TABLE IF EXISTS appointment""")
    c.execute("""
        CREATE TABLE IF NOT EXISTS appointment(
            id INTEGER PRIMARY KEY,
            patient_id INTEGER,
            doctor_id INTEGER,
            date DATE,
            status INTEGER DEFAULT 0,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (doctor_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    c.close()
    conn.close()


def add_appointment(patient_id, doctor_id, date):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute("""
        INSERT INTO appointment (patient_id, doctor_id, date) VALUES(?,?,?)
    """, (patient_id, doctor_id, date))
    conn.commit()
    c.close()
    conn.close()

# c.execute("""
#         INSERT INTO appointment (patient_id, doctor_id, date, status) VALUES(?,?,?,?)
#     """, ("8", "2", date(year=2023, month=3, day=20), 2))
# c.execute("""
#         INSERT INTO appointment (patient_id, doctor_id, date, status) VALUES(?,?,?,?)
#     """, ("8", "2", date(year=2023, month=4, day=10), 1))
# conn.commit()
# c.close()
# conn.close()


def get_appointments():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute("""
        SELECT a.id, p.name, d.name, a.date, a.status
        FROM appointment a
        JOIN patients p ON a.patient_id = p.user_id
        JOIN users d ON a.doctor_id = d.id
    """)

    data = c.fetchall()
    c.close()
    conn.close()

    return data


def get_appointments_for_doctor(doctor_id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute("""
        SELECT a.id, p.name, d.name, a.date, a.status
        FROM appointment a
        JOIN patients p ON a.patient_id = p.user_id
        JOIN users d ON a.doctor_id = d.id
        WHERE d.id = ?
    """, (doctor_id, ))

    data = c.fetchall()
    c.close()
    conn.close()

    return data


def get_appointments_for_patient(patient_id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute("""
        SELECT a.id, d.name, a.date, a.status
        FROM appointment a
        JOIN patients p ON a.patient_id = p.user_id
        JOIN users d ON a.doctor_id = d.id
        WHERE p.user_id = ?
        ORDER BY date ASC
    """, (patient_id,))

    data = c.fetchall()
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    return data


def edit_appointment(id, val):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("""
        UPDATE appointment SET status = ? WHERE id = ?
    """, (val, id))
    conn.commit()
    conn = sqlite3.connect('data.db')
    c = conn.cursor()


def create_medical_record_table():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute("""
        DROP TABLE IF EXISTS medical_records
    """)

    c.execute("""
        CREATE TABLE medical_records(
            id INTEGER PRIMARY KEY,
            patient_id INTEGER UNIQUE,
            doctor_id INTEGER,
            tumor_type TEXT,
            tumor_infos TEXT,
            file_format TEXT,
            created_at DATE,
            FOREIGN KEY (doctor_id) REFERENCES users (id)
            )
    """)
    conn.commit()
    c.close()
    conn.close()


# create_medical_record_table()


def add_medical_record(patient_id, doctor_id, tumor_type, tumor_infos, file_format):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute(""" 
        INSERT OR REPLACE INTO medical_records(patient_id, doctor_id, tumor_type, tumor_infos, file_format, created_at) 
        VALUES(?,?,?,?,?,?) ON CONFLICT(patient_id) DO UPDATE SET doctor_id = excluded.doctor_id, tumor_type = excluded.tumor_type, tumor_infos = excluded.tumor_infos
    """, (patient_id, doctor_id, tumor_type, tumor_infos, file_format, date.today()))

    conn.commit()
    c.close()
    conn.close()


def get_medical_records():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute("""
        SELECT medical_records.*, patients.sex, patients.age
        FROM medical_records
        JOIN patients ON medical_records.patient_id = patients.user_id;
    """)
    data = c.fetchall()

    c.close()
    conn.close()
    return data


def get_medical_records_for_patient(patient_id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute("""
        SELECT medical_records.*, patients.sex, patients.age
        FROM medical_records
        JOIN patients ON medical_records.patient_id = patients.user_id
        WHERE patients.user_id = ?
    """, (patient_id,))
    data = c.fetchone()

    c.close()
    conn.close()
    return data


def get_medical_records_for_doctor(doctor_id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute("""
        SELECT medical_records.*, patients.sex, patients.age
        FROM medical_records
        JOIN patients ON medical_records.doctor_id = patients.doctor_id
        WHERE patients.doctor_id = ?
    """, (doctor_id,))
    data = c.fetchall()

    c.close()
    conn.close()
    return data


def check_if_rated(user_id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute("""
        SELECT id FROM ratings WHERE user_id = ?
    """, (user_id,))

    data = c.fetchone()
    c.close()
    conn.close()

    if not data:
        print("has not rated")
        return False
    return True


def add_rating(user_id, rating, text):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute("""
        INSERT INTO ratings (user_id, rating, text, created_at) VALUES(?,?,?,?)
    """, (user_id, rating, text, date.today()))
    conn.commit()
    c.close()
    conn.close()


def get_ratings():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute("""
        SELECT r.id, u.name, r.rating, r.text, r.created_at FROM ratings r JOIN users u ON u.id = r.user_id
    """)

    data = c.fetchall()
    c.close()
    conn.close()

    return data

# c.execute("""
#     UPDATE users SET profile_pic = ? WHERE role = 3
# """, ("uploads/default-avatar.png",))
# conn.commit()
# c.close()
# conn.close()


# create_medical_record_table()

# create_appointments_table()
# create_patient_table()

# c.execute("""
#     INSERT INTO patients (name, sex, age, tumor, created_at, user_id) VALUES(?,?,?,?,?,?)
# """,("Patient Two", "F", 58, "LGG", datetime.date(year=2023, month=5,day=22), 1))

# conn.commit()

# c.execute(f"""UPDATE patients SET req_status = -1 WHERE name = 'Patient Two'
#                 """)
# conn.commit()

# create_message_table()

# c.execute(f"""
#             UPDATE messages SET is_read = 0 WHERE id = 1
#         """)

# c.execute("""
#     DROP TABLE IF EXISTS history
# """)
# c.execute("""
#     CREATE TABLE IF NOT EXISTS history (
#         id INTEGER PRIMARY KEY, activity TEXT, timestamp DATE
#     )
# """)


# c.execute("""delete from patients """)
# conn.commit()

# create_notifications_table()

# hashed_password = bcrypt.hashpw(
#     "aminaamina".encode(), bcrypt.gensalt())
# conn = sqlite3.connect('data.db')
# c = conn.cursor()
# c.execute("UPDATE users SET email = ? WHERE id = ?", ("amina@test.com", 4))
# conn.commit()
# c.close()
# conn.close()

# conn = sqlite3.connect('data.db')
# c = conn.cursor()
# c.execute("DROP TABLE IF EXISTS ratings")
# conn.commit()

# c.execute("""
#         CREATE TABLE IF NOT EXISTS ratings(
#             id INTEGER PRIMARY KEY,
#             user_id INTEGER,
#             rating INTEGER,
#             text TEXT,
#             created_at DATE,
#             FOREIGN KEY (user_id) REFERENCES users (id)
#         )
#     """)
# conn.commit()
# c.close()
# conn.close()
