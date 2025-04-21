from mongo import chat_with_music
from sql_langchain3_0 import housing_queries
from 
def main():
    # Display the welcome message
    print("Welcome to the Database Query Interface!")
    print("You can query either the Housing Database (MySQL) or the Spotify Database (MongoDB).")
    while True:        print("\n--- Select a database to query ---")
        print("1. Housing Database (MySQL)")
        print("2. Spotify Database (MongoDB)")
        print("3. Exit")
        
        choice = input(f"Enter your choice (1-3): ").strip()

        if choice == "1":
            # Call the MySQL query function
            housing_queries()
        elif choice == "2":
            # Call the MongoDB query function
            chat_with_music()
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

    print("Thank you for using the Database Query Interface!")

if __name__ == "__main__":
    main()
