import kp_functions
import imdb_functions
import parsing_functions

choices = {
    '1': kp_functions.load_watchlist,
    '2': kp_functions.load_ratings,
    '3': imdb_functions.run_watchlist_adding,
    '4': imdb_functions.run_rating,
    '5': parsing_functions.parse_ratings,
    '6': parsing_functions.parse_watchlist
}

if __name__ == '__main__':

    choice = input("What do you want?\n\t1. Export KP watchlist\n\t2. Export KP ratings\n\t" 
                   "3. Add movies/shows to IMDB watchlist\n\t4. Rate movies/shows on IMDB\n\t"
                   "5. Parse ratings HTML content\n6. Parse watchlist HTML content\n")
    choices[choice]()
