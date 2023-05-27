import kp_functions

if __name__ == '__main__':

    choice = input("What do you want? ")
    if choice == 'wishlist':
        kp_functions.load_wishlist()
    elif choice == 'ratings':
        kp_functions.load_ratings()
    
    

