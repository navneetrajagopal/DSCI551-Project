def main():
    while True:
        print("\n--- Select a database to query ---")
        print("1. Housing Database (MySQL)")
        print("2. Spotify Database (MongoDB)")
        print("3. Exit")
        
        choice = input(f"Enter your choice (1-3): ").strip()

        if choice == "1":
            # Call the MySQL query function
            print("stub")
        elif choice == "2":
            # Call the MongoDB query function
            print("stub")
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()