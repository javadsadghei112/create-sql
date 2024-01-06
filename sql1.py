import sqlite3
from datetime import datetime

conn = sqlite3.connect('reservation_system.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS person (
    national_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    picture BLOB
)
''')
c.execute('''
CREATE TABLE IF NOT EXISTS recreational_place (
    name TEXT PRIMARY KEY,
    phone_number TEXT NOT NULL,
    reservation_fee REAL NOT NULL
)
''')
c.execute('''
CREATE TABLE IF NOT EXISTS reservation (
    national_id INTEGER,
    recreation_place_name TEXT,
    reservation_date TEXT,
    PRIMARY KEY (national_id, recreation_place_name, reservation_date),
    FOREIGN KEY (national_id) REFERENCES person (national_id),
    FOREIGN KEY (recreation_place_name) REFERENCES recreational_place (name)
)
''')
def add_person(national_id, first_name, last_name, picture=None):
    c.execute('SELECT count(*) FROM person WHERE national_id = ?', (national_id,))
    if c.fetchone()[0] == 0:
        try:
            c.execute('INSERT INTO person (national_id, first_name, last_name, picture) VALUES (?, ?, ?, ?)',
                      (national_id, first_name, last_name, picture))
            conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"An error occurred: {e}")
    else:
        print(f"Person with national ID {national_id} already exists.")

def add_recreational_place(name, phone_number, reservation_fee):
    c.execute('SELECT count(*) FROM recreational_place WHERE name = ?', (name,))
    if c.fetchone()[0] == 0:
        try:
            c.execute('INSERT INTO recreational_place (name, phone_number, reservation_fee) VALUES (?, ?, ?)',
                      (name, phone_number, reservation_fee))
            conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"An error occurred: {e}")
    else:
        print(f"Recreational place {name} already exists.")

def make_reservation(national_id, recreation_place_name, reservation_date):
    c.execute('SELECT count(*) FROM reservation WHERE national_id = ? AND recreation_place_name = ? AND reservation_date = ?',
              (national_id, recreation_place_name, reservation_date))
    if c.fetchone()[0] == 0:
        date_format = "%Y-%m-%d"
        try:
            datetime.strptime(reservation_date, date_format)
            c.execute('INSERT INTO reservation (national_id, recreation_place_name, reservation_date) VALUES (?, ?, ?)',
                      (national_id, recreation_place_name, reservation_date))
            conn.commit()
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
        except sqlite3.IntegrityError as e:
            print(f"An error occurred: {e}")
    else:
        print(f"Reservation for national ID {national_id} at place {recreation_place_name} on date {reservation_date} already exists.")

add_person(123456789, "Ali", "Rezaei")
add_recreational_place("Park Shahr", "021-12345678", 100000)
make_reservation(123456789, "Park Shahr", "2023-04-05")

add_person(136782939,'Mohamamad','Ahmadi')
add_recreational_place('char bagh','021-26724726482',0)
make_reservation(136782939,'char bagh','2023-04-06')


def update_person(national_id, first_name=None, last_name=None, picture=None):
    updates = []
    parameters = []

    if first_name is not None:
        updates.append("first_name = ?")
        parameters.append(first_name)
    if last_name is not None:
        updates.append("last_name = ?")
        parameters.append(last_name)
    if picture is not None:
        updates.append("picture = ?")
        parameters.append(picture)
    parameters.append(national_id)

    if updates:
        c.execute(f"UPDATE person SET {', '.join(updates)} WHERE national_id = ?", parameters)
        conn.commit()
        print(f"Person with national_id {national_id} has been updated.")
    else:
        print("Nothing to update.")


def update_recreational_place(name, phone_number=None, reservation_fee=None):
    updates = []
    parameters = []

    if phone_number is not None:
        updates.append("phone_number = ?")
        parameters.append(phone_number)
    if reservation_fee is not None:
        updates.append("reservation_fee = ?")
        parameters.append(reservation_fee)

    # اضافه کردن نام به پارامترها
    parameters.append(name)

    if updates:
        c.execute(f"UPDATE recreational_place SET {', '.join(updates)} WHERE name = ?", parameters)
        conn.commit()
        print(f"Recreational place named {name} has been updated.")
    else:
        print("Nothing to update.")



def update_reservation(national_id, recreation_place_name, old_reservation_date, new_reservation_date):
    try:
        datetime.strptime(new_reservation_date, "%Y-%m-%d")
        c.execute('''
                UPDATE reservation
                SET reservation_date = ?
                WHERE national_id = ? AND recreation_place_name = ? AND reservation_date = ?
            ''', (new_reservation_date, national_id, recreation_place_name, old_reservation_date))
        conn.commit()
        print(f"Reservation updated to new date {new_reservation_date}.")
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")


#update_person(national_id=123456789, first_name="mohsen ", last_name="sadghei")
#update_recreational_place(name="Park Shahr", phone_number="021-98765432", reservation_fee=150000)
#update_reservation(national_id=136782939, recreation_place_name="char bagh", old_reservation_date="2023-04-06", new_reservation_date="2023-04-10")


from PIL import Image  # Import should be at the top of the file
import io


def show_person_reservations(national_id):

    c.execute('SELECT first_name, last_name, picture FROM person WHERE national_id = ?', (national_id,))
    person_data = c.fetchone()

    if person_data:
        first_name, last_name, picture_blob = person_data
        print(f"Name: {first_name} {last_name}")


        if picture_blob:

            image_stream = io.BytesIO(picture_blob)
            image = Image.open(image_stream)


            image.show()


        c.execute('''
            SELECT recreation_place_name, COUNT(*) as reservation_count 
            FROM reservation 
            WHERE national_id = ? GROUP BY recreation_place_name
        ''', (national_id,))

        reservations = c.fetchall()

        if reservations:
            print("Reservations:")
            for place, count in reservations:
                print(f"{place}: {count} time")
        else:
            print("No reservations found.")
    else:
        print(f"No person found with national ID {national_id}.")





show_person_reservations(123456789)


from datetime import datetime


def show_person_reservations_in_date_range(national_id, start_date, end_date):

    try:

        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    # استخراج تصویر و مشخصات شخص
    c.execute('SELECT first_name, last_name FROM person WHERE national_id = ?', (national_id,))
    person_data = c.fetchone()

    if person_data:
        first_name, last_name = person_data
        print(f"Name: {first_name} {last_name}")


        c.execute('''
            SELECT recreation_place_name, reservation_date
            FROM reservation 
            WHERE national_id = ? AND reservation_date BETWEEN ? AND ?
            ORDER BY reservation_date
        ''', (national_id, start_date, end_date))

        reservations = c.fetchall()

        if reservations:
            print(f"Reservations between {start_date} and {end_date}:")
            for place, date in reservations:
                print(f"{place} on {date}")
        else:
            print(f"No reservations found between {start_date} and {end_date}.")
    else:
        print(f"No person found with national ID {national_id}.")



show_person_reservations_in_date_range('00123456789', '2023-01-01', '2023-01-31')










def show_reservations_and_fees_for_place(place_name):
    c.execute('''
    SELECT p.first_name, p.last_name, COUNT(r.reservation_date) as reservation_amount, 
    (COUNT(r.reservation_date) * rp.reservation_fee) as total_fee
    FROM person p
    JOIN reservation r on p.national_id = r.national_id
    JOIN recreational_place rp on r.recreation_place_name = rp.name
    WHERE r.recreation_place_name = ?
    GROUP BY p.national_id
    ''', (place_name,))

    reservations = c.fetchall()
    if reservations:
        for first_name, last_name, reservation_amount, total_fee in reservations:
            print(f"{first_name} {last_name} has reserved {reservation_amount} times with a total fee of {total_fee}")
    else:
        print(f"No reservations found for place '{place_name}'.")


show_reservations_and_fees_for_place('Park Shahr')
show_reservations_and_fees_for_place('char bagh')
conn.close()
