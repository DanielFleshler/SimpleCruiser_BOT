# SimpleCruiser_BOT

## Telegram Off-Road Bot

Welcome to the SimpleCruiser_BOT repository! This bot helps users find off-road trails in different regions of Israel based on their location and preferred difficulty level.

Note: The bot is written in Hebrew.
## Features

* **Regional Selection:** Users can choose from Central, Southern, and Northern regions.
* **Location Sharing:** Users can share their current location to find nearby trails.
* **Difficulty Levels:** Trails are categorized into easy, medium, and hard difficulty levels.
* **Trail Links:** Provides direct links to trail details in the Off-Road application.

## Interact with the bot

* Use the /start command to begin.
* Choose a region, location, and difficulty level to find trails.
* Share your location to find trails near you.

## Bot Commands

* **/start:** Start interacting with the bot and display the main menu.

## Code Overview

### Main Components

* **Environment Variables:** Managed using dotenv.
* **Trail Data:** Loaded from a `trails.json` file.
* **Coordinate Conversion:** Uses `pyproj` for converting geographic coordinates.
* **Telegram Bot Integration:** Implemented using `python-telegram-bot`.

### Functions

* `load_trail_data(file_path)`: Loads trail data from a JSON file specified by the `file_path` argument. It parses the JSON data and stores it in a structured format for easy access by other functions.

* `convert_coordinates(latitude, longitude)`: Converts geographic coordinates (`latitude` and `longitude`) to Israel Transverse Mercator (ITM) coordinates. This function utilizes the `pyproj` library to perform the coordinate transformation.

* `get_main_menu_buttons(location_known)`: Generates the buttons for the main menu based on whether the user's location is known. This function checks the `location_known` flag and displays buttons relevant to the user's situation (e.g., "Share Location" if unknown, or "Trails near you" if known).
  
* `get_submenu_buttons(area)`: Generates submenu buttons for a specific chosen area (`area`). This function takes the selected region as input and creates buttons for different locations within that area.

* `get_difficulty_buttons(area)`: Generates difficulty level buttons for a specific selected area (`area`). Similar to `get_submenu_buttons`, this function tailors the buttons to the chosen region, presenting options for easy, medium, and hard trails.

* `get_trail_links_by_difficulty(area, difficulty)`: Generates trail links for a specific difficulty level (`difficulty`) within a chosen area (`area`). This function retrieves trail information based on the user's selections and formats them as clickable links.

* `start()`: Handles the `/start` command. This function is the entry point for user interaction. It welcomes the user, explains the bot's purpose, and presents the initial menu options.

* `send_welcome_message(chat_id)`: Sends a welcome message to the user identified by the `chat_id`. This function personalizes the greeting and introduces the bot's functionalities.

* `handle_button_click(update, context)`: Handles button click events triggered by user interaction with the buttons (`update`). It utilizes the `context` object to determine the specific button pressed and executes the corresponding logic (e.g., navigate to a submenu, display trails).

* `handle_area_selection(update, context)`: Handles area selection events (`update`) where the user chooses a specific region. This function processes the chosen area and updates the context to reflect the selection, potentially leading to difficulty level buttons.

* `handle_path_selection(update, context)`: Handles path selection events (`update`), potentially when a user chooses a specific trail. This function retrieves detailed information about the chosen trail and presents it to the user. (Note: Path selection might be handled differently depending on your implementation)

* `handle_difficulty_selection(update, context)`: Handles difficulty level selection events (`update`) where the user chooses a desired difficulty for the trails. This function processes the chosen difficulty and retrieves relevant trail information based on area and difficulty.

* `handle_back_button(update, context)`: Handles the back button press (`update`), allowing users to navigate back to previous menus.
