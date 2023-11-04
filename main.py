import kp_functions

choices = {
    '1': kp_functions.load_wishlist,
    '2': kp_functions.load_ratings
}

if __name__ == '__main__':

    choice = input("What do you want?\n\t1. KP wishlist\n\t2. KP ratings\n ")
    choices[choice]()
