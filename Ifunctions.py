import os

import dotenv
import psycopg2
import tabulate

dotenv.load_dotenv()


def connect_to_db():
    conn = psycopg2.connect(
        database=os.getenv("DATABASE"),
        user=os.getenv('USER'),
        password=os.getenv('PASSWORD'),
        host=os.getenv('HOST'),
        port=os.getenv('port')
    )
    return conn


def read_from_users_db():
    conn = connect_to_db()
    cursor = conn.cursor()
    query = "SELECT * FROM users"
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


def signup():
    name = input("What is your name? ")
    surname = input("What is your surname? ")
    username = input("What is your username? ")
    password = input("What is your new password? ")
    conn = connect_to_db()
    cursor = conn.cursor()
    query = "INSERT INTO users (name, surname , username , password, superuser) VALUES (%s, %s, %s, %s, %s)"
    users_data = read_from_users_db()
    values = (name, surname, username, password, True if not users_data else False)
    try:
        cursor.execute(query, values)
        conn.commit()
        print("User {} has been registered".format(username))
        return read_from_users_db()[-1][0]
    except psycopg2.errors.UniqueViolation:
        print("username already in use")
        return None


def login():
    username = input("What is your username? ")
    password = input("What is your password? ")
    conn = connect_to_db()
    cursor = conn.cursor()
    query = "SELECT * FROM users where username = %s and password = %s"
    values = (username, password)
    cursor.execute(query, values)
    results = cursor.fetchone()
    conn.close()
    if results:
        print("Logged in successfully")
        return results[0]
    print("username or password is incorrect")
    return None


def is_superuser(user_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    query = "SELECT * FROM users where id = %s"
    values = (user_id,)
    cursor.execute(query, values)
    results = cursor.fetchone()
    conn.close()
    return results[-1] if results else None


def read_from_meals_table():
    conn = connect_to_db()
    cursor = conn.cursor()
    query = "SELECT * FROM meals"
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


def show_meals_table():
    meals_data = read_from_meals_table()
    t = tabulate.tabulate(meals_data, tablefmt="pretty", headers=['ID', 'Name', 'Description', 'Price'])
    return t


def add_meal():
    conn = connect_to_db()
    cursor = conn.cursor()
    name = input("What is meal`s name? ")
    description = input("What is meal`s description? ")
    price = input("What is meal`s price? ")
    query = "INSERT INTO meals(name, description, price) VALUES (%s, %s, %s)"
    values = (name, description, price)
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    print("meal added successfully")


def delete_meal():
    conn = connect_to_db()
    cursor = conn.cursor()
    meal_id = int(input("What is meal`s id:"))
    query1 = "SELECT * FROM meals where id = %s"
    values1 = (meal_id,)
    cursor.execute(query1, values1)
    result = cursor.fetchall()
    if result:
        query = "DELETE FROM meals WHERE id = %s"
        values = (meal_id,)
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        print("meal deleted successfully")
    else:
        print("incorrect meal id")


def update_meal():
    conn = connect_to_db()
    cursor = conn.cursor()
    meal_id = int(input("What is meal`s id? "))
    query1 = "SELECT * FROM meals where id = %s"
    values1 = (meal_id,)
    cursor.execute(query1, values1)
    result = cursor.fetchall()
    if result:
        name = input("What is meal's name? ")
        description = input("What is meal's description? ")
        price = input("What is meal's price? ")
        query2 = "UPDATE meals SET name = %s, description = %s, price = %s WHERE id = %s"
        values2 = (name, description, price, meal_id)
        cursor.execute(query2, values2)
        conn.commit()
        conn.close()
        print("meal updated successfully")
    else:
        print("incorrect meal id")


def search_meal():
    meals_search = input("keyword: ")
    data_meals = read_from_meals_table()
    if meals_search:
        raw_data = []
        for meal in data_meals:
            if meals_search.lower() in meal[1].lower():
                raw_data.append(meal)
        t = tabulate.tabulate(raw_data, tablefmt="pretty", headers=['Id', 'Name', 'Description', 'Price'])
        return t
    t = tabulate.tabulate(data_meals, tablefmt="pretty", headers=['Id', 'Name', 'Description', 'Price'])
    return t


def register_meal(user_id):
    conn = connect_to_db()
    cursor = conn.cursor()

    query3 = '''
        select r.date from orders as o join reservations as r
        on o.id = r.order_id where o.user_id = %s group by r.date;
    '''
    values3 = (user_id,)
    cursor.execute(query3, values3)
    reservations = cursor.fetchall()
    raw_reservations = tuple(map(lambda x: str(x[0]), reservations))
    for index, reservation in enumerate(raw_reservations):
        print(f"{index + 1}. {reservation}")
    if not raw_reservations:
        print("Back[0] Create new reservation[1]")
    elif len(raw_reservations) < 3:
        print("Back[0] Choose reservation[1] Create new reservation[2]")
    else:
        print("Back[0] Choose reservation[1]")
    choice = int(input("Enter your choice: "))
    if choice == 1 and raw_reservations:
        reservation_id = int(input("reservation id: "))
        if 0 <= reservation_id - 1 < len(raw_reservations):
            reservation_time = raw_reservations[reservation_id - 1]
        else:
            print("incorrect reservation id")
            return
    elif choice == 1 and not raw_reservations:
        reservation_time = input("reservation time(example: 2024-01-26): ")
    elif choice == 2 and len(raw_reservations) < 3 and raw_reservations:
        reservation_time = input("reservation time(example: 2024-01-26): ")
    else:
        return
    query = '''
        select count(o.meal_id)
        from orders as o join
        reservations as r on o.id = r.order_id
        where o.user_id = %s and r.date = %s group by user_id;
    '''
    values = (user_id, reservation_time)
    cursor.execute(query, values)
    result = cursor.fetchone()
    if not result or result[0] <= 10:
        meal_id = int(input("What is meal`s id? "))
        query1 = "SELECT * FROM meals where id = %s"
        values1 = (meal_id,)
        cursor.execute(query1, values1)
        result = cursor.fetchall()
        if result:
            query2 = "insert into orders (user_id, meal_id) values (%s, %s)"
            values2 = (user_id, meal_id)
            cursor.execute(query2, values2)
            conn.commit()

            query4 = "SELECT * FROM orders where meal_id = %s and user_id = %s"
            values4 = (meal_id, user_id)
            cursor.execute(query4, values4)
            last_order_id = cursor.fetchall()[-1][0]

            query5 = "insert into reservations (order_id, date) values (%s, %s)"
            values5 = (last_order_id, reservation_time)
            cursor.execute(query5, values5)
            conn.commit()
            conn.close()

            print("meal added to cart successfully")
        else:
            print("incorrect meal id")
    else:
        print("ordering meal limit is reached")


def show_cart(user_id):
    conn = connect_to_db()
    cursor = conn.cursor()

    query3 = '''
            select r.date from orders as o join reservations as r
            on o.id = r.order_id where o.user_id = %s group by r.date;
        '''
    values3 = (user_id,)
    cursor.execute(query3, values3)
    reservations = cursor.fetchall()
    raw_reservations = tuple(map(lambda x: str(x[0]), reservations))
    for index, reservation in enumerate(raw_reservations):
        print(f"{index + 1}. {reservation}")

    if raw_reservations:
        reservation_id = int(input("reservation id: "))
        if 0 <= reservation_id - 1 < len(raw_reservations):
            reservation_time = raw_reservations[reservation_id - 1]
        else:
            print("incorrect reservation id")
            return None

        query1 = '''
                select o.id, m.name, m.price from meals as m
                join (select o1.id, o1.meal_id, o1.user_id
                from orders as o1 join
                reservations as r on o1.id = r.order_id
                where r.date = %s and o1.user_id = %s) as o
                on o.meal_id = m.id and o.user_id = %s;
            '''
        values1 = (reservation_time, user_id, user_id)
        cursor.execute(query1, values1)
        result = cursor.fetchall()
        t = tabulate.tabulate(result, headers=['Id', 'Name', 'Price'], tablefmt='pretty')
        return t, calculate_total_price(user_id)
    return None


def remove_from_cart(user_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    query3 = '''
                        select r.date from orders as o join reservations as r
                        on o.id = r.order_id where o.user_id = %s group by r.date;
                    '''
    values3 = (user_id,)
    cursor.execute(query3, values3)
    reservations = cursor.fetchall()
    raw_reservations = tuple(map(lambda x: str(x[0]), reservations))
    for index, reservation in enumerate(raw_reservations):
        print(f"{index + 1}. {reservation}")

    reservation_id = int(input("reservation id: "))
    if 0 <= reservation_id - 1 < len(raw_reservations):
        reservation_time = raw_reservations[reservation_id - 1]
    else:
        print("incorrect reservation id")
        return None
    query2 = "DELETE FROM orders where id = %s and user_id = %s"
    order_id = int(input("What is order`s id to delete? "))
    values2 = (order_id, user_id)
    cursor.execute(query2, values2)
    conn.commit()

    query1 = '''
        delete from reservations where order_id = %s and date = %s
    '''
    values1 = (order_id, reservation_time)
    cursor.execute(query1, values1)
    conn.commit()

    conn.close()

    print("Order has been removed")


def cancel_reservation(user_id):
    conn = connect_to_db()
    cursor = conn.cursor()

    query1 = '''
                select r.date from orders as o join reservations as r
                on o.id = r.order_id where o.user_id = %s group by r.date;
            '''
    values1 = (user_id,)
    cursor.execute(query1, values1)
    reservations = cursor.fetchall()
    raw_reservations = tuple(map(lambda x: str(x[0]), reservations))
    for index, reservation in enumerate(raw_reservations):
        print(f"{index + 1}. {reservation}")

    reservation_id = int(input("reservation id: "))
    if 0 <= reservation_id - 1 < len(raw_reservations):
        reservation_time = raw_reservations[reservation_id - 1]
    else:
        print("incorrect reservation id")
        return None

    query2 = '''
        delete from orders as o where o.id in
        (select r.order_id from reservations as r where date = %s)
        and o.user_id = %s;
    '''
    values2 = (reservation_time, user_id)
    cursor.execute(query2, values2)
    conn.commit()

    query3 = '''
        delete from reservations where date = %s;
    '''
    values3 = (reservation_time,)
    cursor.execute(query3, values3)
    conn.commit()
    conn.close()
    print("reservation deleted")


def calculate_total_price(user_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    query1 = '''
    select
    sum(m.price) as Total
    from meals as m
    join orders as o on o.meal_id = m.id and o.user_id = %s;
    '''
    values1 = (user_id,)
    cursor.execute(query1, values1)
    result = cursor.fetchone()
    return round(result[0], 2)
