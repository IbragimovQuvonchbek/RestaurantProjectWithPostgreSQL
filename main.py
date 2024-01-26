from Ifunctions import signup, login, is_superuser, show_meals_table, add_meal, delete_meal, update_meal, search_meal, \
    show_cart, remove_from_cart, register_meal, cancel_reservation

while True:
    print("Exit[0] Log in[1] Sign up[2]")
    choice = int(input("choice: "))
    current_user = None
    if choice == 0:
        break
    elif choice == 1:
        print("==========Log in============")
        current_user = login()
    elif choice == 2:
        print("==========Sign up===========")
        current_user = signup()

    while current_user:
        superuser = is_superuser(current_user)
        if superuser:
            print("Log out[0] See meals[1] Meal functions[2]")
        else:
            print("Log out[0] See meals[1] My order[2]")
        choice = int(input("choice: "))
        if choice == 0:
            break
        elif choice == 1:
            # see meals
            print(show_meals_table())
            while True:
                if superuser:
                    print("Back[0] Search[1]")
                else:
                    print("Back[0] Search[1] Add to Cart[2]")
                choice = int(input("choice: "))
                if choice == 0:
                    break
                elif choice == 1:
                    print(search_meal())
                elif choice == 2 and not superuser:
                    register_meal(current_user)
        elif choice == 2 and superuser:
            while True:
                print("Back[0] Edit[1] Delete[2] Add[3]")
                choice = int(input("choice: "))
                print(show_meals_table())
                if choice == 0:
                    break
                elif choice == 1:
                    update_meal()
                elif choice == 2:
                    delete_meal()
                elif choice == 3:
                    add_meal()
        elif choice == 2 and not superuser:
            cart = show_cart(current_user)
            if cart:
                print(cart[0])
                print(f"Total price: {cart[1]}")
                while True:
                    print("Back[0] Remove from Cart[1] Cancel reservation[2]")
                    choice = int(input("choice: "))
                    if choice == 0:
                        break
                    elif choice == 1:
                        remove_from_cart(current_user)
                    elif choice == 2:
                        cancel_reservation(current_user)
            else:
                print("No cart found")
