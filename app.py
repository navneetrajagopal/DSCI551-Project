import warnings
warnings.simplefilter("ignore")


#from mongo import chat_with_music
from sql import housing_queries


def main():
    print("Welcome to the Database Query Interface!")
    print("You can query either the Housing Database (MySQL) or the Spotify Database (MongoDB).")

    while True:
        print("\n--- Select a database to query ---")
        print("1. Housing Database (MySQL)")
        print("2. Spotify Database (MongoDB)")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ").strip()

        if choice == "1":
            housing_queries()
        elif choice == "2":
            #chat_with_music()
            break
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

    print("Thank you for using the Database Query Interface!")

if __name__ == "__main__":
    main()
