import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve MongoDB connection string from environment variables
mongo_db_connection_string = os.getenv('MONGO_DB_CONNECTION_STRING')

# Initialize data structures: 14 days and 20 parking spaces per day
# Each space stores: (visitor_name, car_license, is_accessible)
parking_spaces = [[None for _ in range(20)] for _ in range(14)]

# MongoDB setup
client = MongoClient(mongo_db_connection_string)
db = client['parking_system']  # Database name
collection = db['parking_spaces']  # Collection name

def reset_parking_system():
    """Reset the parking system for the next two-week period."""
    global parking_spaces
    parking_spaces = [[None for _ in range(20)] for _ in range(14)]
    print("Parking system reset complete.")
    save_parking_data()

def save_parking_data():
    """Save parking space data to MongoDB."""
    # Convert parking spaces into a list of dictionaries for MongoDB compatibility
    parking_data = {
        "parking_spaces": [
            [
                {
                    "name": space[0],
                    "car_license": space[1],
                    "is_accessible": space[2]
                } if space else None for space in day
            ]
            for day in parking_spaces
        ]
    }

    # Upsert the data into MongoDB
    collection.update_one(
        {'_id': 'current_data'},  # Use a fixed ID to always update the same document
        {'$set': parking_data},
        upsert=True
    )
    
    print("Parking data saved to MongoDB.")

def load_parking_data():
    """Load parking space data from MongoDB when the program starts."""
    global parking_spaces
    data = collection.find_one({'_id': 'current_data'})
    if data is None:
        # If no data found in the database, initialize the system as empty
        print("No existing parking data found. Starting with an empty system.")
        save_parking_data()  # Create the initial data in MongoDB
    else:
        try:
            # Convert back from MongoDB document to the parking_spaces list format
            parking_spaces = [
                [
                    (item["name"], item["car_license"], item["is_accessible"]) if item else None 
                    for item in day
                ]
                for day in data["parking_spaces"]
            ]
            print("Parking data loaded from MongoDB.")
        except (KeyError, TypeError):
            print("Error decoding data from MongoDB. Starting with an empty system.")

def book_parking_space():
    """Allow a visitor to book a parking space for a specific day."""
    while True:
        try:
            # Input: Ask visitor to request a day for parking (1-14)
            day_requested = int(input("Enter a day (1-14) for parking: ")) - 1
            
            # Check if the input day is valid
            if day_requested < 0 or day_requested >= 14:
                print("Invalid day! Please enter a number between 1 and 14.")
                continue
            
            # Ask if they need an accessible parking space
            accessible_needed = input("Do you need an accessible parking space? (yes/no): ").lower()
            
            if accessible_needed == 'yes':
                # Search for accessible spaces (1-5, i.e., index 0-4)
                available_space_found = False
                for i in range(5):  # Accessible spaces are from index 0 to 4
                    if parking_spaces[day_requested][i] is None:
                        # Ask for visitor details
                        visitor_name = input("Enter your name: ")
                        car_license = input("Enter your car license number: ")
                        
                        # Store visitor's details with the accessible flag
                        parking_spaces[day_requested][i] = (visitor_name, car_license, True)
                        
                        # Inform the visitor of their parking space number
                        print(f"Your accessible parking space number is {i + 1}.")
                        available_space_found = True
                        break
                
                if not available_space_found:
                    print("Sorry, no accessible spaces are available on this day.")
            else:
                # Try to allocate the visitor to general spaces (6-20, i.e., index 5-19)
                available_space_found = False
                for i in range(5, 20):  # General spaces are from index 5 to 19
                    if parking_spaces[day_requested][i] is None:
                        # Ask for visitor details
                        visitor_name = input("Enter your name: ")
                        car_license = input("Enter your car license number: ")
                        
                        # Store visitor's details without the accessible flag
                        parking_spaces[day_requested][i] = (visitor_name, car_license, False)
                        
                        # Inform the visitor of their parking space number
                        print(f"Your general parking space number is {i + 1}.")
                        available_space_found = True
                        break
                
                # If no general space was found, try to allocate to accessible spaces (1-5)
                if not available_space_found:
                    print("No general spaces available. Trying accessible spaces...")
                    for i in range(5):  # Accessible spaces are from index 0 to 4
                        if parking_spaces[day_requested][i] is None:
                            # Ask for visitor details
                            visitor_name = input("Enter your name: ")
                            car_license = input("Enter your car license number: ")
                            
                            # Store visitor's details (even though it's an accessible spot, they don't need it)
                            parking_spaces[day_requested][i] = (visitor_name, car_license, False)
                            
                            # Inform the visitor of their parking space number
                            print(f"All general spaces are full. You have been assigned accessible parking space number {i + 1}.")
                            available_space_found = True
                            break
                
                if not available_space_found:
                    print("Sorry, no spaces (general or accessible) are available on this day.")
            
            # Save the updated parking space data to the database
            save_parking_data()
            
            # Ask if visitor wants to book another space
            another_booking = input("Do you want to book another parking space? (yes/no): ").lower()
            if another_booking == 'no':
                exit()
        
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def display_statistics():
    """Display parking usage statistics."""
    accessible_used_total = 0
    general_used_total = 0
    
    # Iterate over each day
    for day in parking_spaces:
        accessible_used_day = sum(1 for space in day[:5] if space is not None and space[2])
        general_used_day = sum(1 for space in day[5:] if space is not None and not space[2])
        total_used_day = accessible_used_day + general_used_day
        
        print(f"Day {parking_spaces.index(day) + 1}:")
        print(f"  Accessible spaces used: {accessible_used_day}")
        print(f"  General spaces used: {general_used_day}")
        print(f"  Total spaces used: {total_used_day}")
        
        accessible_used_total += accessible_used_day
        general_used_total += general_used_day

    total_used_total = accessible_used_total + general_used_total

    print("\nOverall 14-day statistics:")
    print(f"  Accessible spaces used in total: {accessible_used_total}")
    print(f"  General spaces used in total: {general_used_total}")
    print(f"  Total spaces used in total: {total_used_total}")

def main():
    """Main function to run the parking booking system."""
    load_parking_data()  # Load existing parking data when the program starts
    while True:
        print("\n1. Book parking space")
        print("2. Display statistics")
        print("3. Reset parking system")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")
        if choice == '1':
            book_parking_space()
        elif choice == '2':
            display_statistics()
        elif choice == '3':
            reset_parking_system()
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

# Run the main program
main()
