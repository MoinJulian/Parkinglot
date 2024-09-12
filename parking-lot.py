import json
import os  # To check if the file exists

# Initialize data structures: 14 days and 20 parking spaces per day
# Each space stores: (visitor_name, car_license, is_accessible)
parking_spaces = [[None for _ in range(20)] for _ in range(14)]

def reset_parking_system():
    """Reset the parking system for the next two-week period."""
    global parking_spaces
    parking_spaces = [[None for _ in range(20)] for _ in range(14)]
    print("Parking system reset complete.")
    save_parking_data()

def save_parking_data():
    """Save parking space data to a JSON file compatible with MongoDB."""
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
    
    # Save to JSON file
    with open('parking_spaces.json', 'w') as file:
        json.dump(parking_data, file, indent=4)
    
    print("Parking data saved to 'parking_spaces.json'.")

def load_parking_data():
    """Load parking space data from the JSON file when the program starts."""
    global parking_spaces
    if not os.path.exists('parking_spaces.json'):
        # If the file doesn't exist, initialize the system as empty
        print("No existing parking data found. Starting with an empty system.")
        save_parking_data()  # Create the file for the first time
    else:
        try:
            with open('parking_spaces.json', 'r') as file:
                data = json.load(file)
                # Convert back from JSON to the parking_spaces list format
                parking_spaces = [
                    [
                        (item["name"], item["car_license"], item["is_accessible"]) if item else None 
                        for item in day
                    ]
                    for day in data["parking_spaces"]
                ]
            print("Parking data loaded from 'parking_spaces.json'.")
        except json.JSONDecodeError:
            print("Error decoding JSON data. Starting with an empty system.")

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
            
            # Save the updated parking space data to the file
            save_parking_data()
            
            # Ask if visitor wants to book another space
            another_booking = input("Do you want to book another parking space? (yes/no): ").lower()
            if another_booking == 'no':
                exit()
        
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def main():
    """Main function to run the parking booking system."""
    load_parking_data()  # Load existing parking data when the program starts
    while True:
        book_parking_space()
        # End of the two-week period: reset the parking system
        reset_input = input("Reset parking system for the next two-week period? (yes/no): ").lower()
        if reset_input == 'yes':
            reset_parking_system()
        else:
            print(parking_spaces)

# Run the main program
main()
