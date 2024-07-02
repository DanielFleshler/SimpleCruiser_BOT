import os
from dotenv import load_dotenv
import json
from math import sqrt, trunc

from pyproj import Transformer
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Application,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

# Load environment variables
load_dotenv()

# Function to load trail data from a JSON file
def load_trail_data(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            return data['areas']
    except (FileNotFoundError, json.JSONDecodeError) as error:
        print(f"Error loading trail data: {error}")
        return {}

# Function to convert geographic coordinates to Israel Transverse Mercator (ITM) coordinates
def convert_coordinates(latitude,longitude):
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:2039")
    northing, easting = transformer.transform(latitude, longitude)
    return easting, northing

# Generate the main menu buttons
def get_main_menu_buttons(isUserLocation):
    if isUserLocation:
        return [
            [InlineKeyboardButton("🌟 מרכז", callback_data="area:1"), InlineKeyboardButton("🌞 דרום", callback_data="area:2")],
            [InlineKeyboardButton("🌲 צפון", callback_data="area:3")],
            [InlineKeyboardButton("🔍 הצג מסלולים לידך", callback_data="showTrails")]
        ]
    else:
        return [
            [InlineKeyboardButton("🌟 מרכז", callback_data="area:1"), InlineKeyboardButton("🌞 דרום", callback_data="area:2")],
            [InlineKeyboardButton("🌲 צפון", callback_data="area:3")],
            [InlineKeyboardButton("📍 שתף מיקום", callback_data="userLocation")]
        ]

# Generate submenu buttons for a specific area
def get_submenu_buttons(area, trail_data):
    area_trail_data = (
        trail_data['center'] if area == "1"
        else trail_data['south'] if area == "2"
        else trail_data['north']
    )
    location_buttons = []
    locations = area_trail_data["locations"]
    for location_name in locations:
        button_row = [InlineKeyboardButton(location_name, callback_data=f"path:{area}:{location_name}")]
        location_buttons.append(button_row)
    location_buttons.append([InlineKeyboardButton("🔙 חזור", callback_data="back")])
    return location_buttons

# Generate difficulty level buttons for a specific location
def get_difficulty_buttons(area, location, trail_data):
    area_trail_data = (
        trail_data['center'] if area == "1"
        else trail_data['south'] if area == "2"
        else trail_data['north']
    )
    difficulty_buttons = []
    difficulty_levels = {
        'easy': '✊ קל',
        'medium': '💪 בינוני',
        'hard': '👊 קשה'
    }
    for level, label in difficulty_levels.items():
        if area_trail_data['locations'][location][level]:
            button_row = [InlineKeyboardButton(label, callback_data=f"difficulty:{area}:{location}:{label}")]
            difficulty_buttons.append(button_row)
    difficulty_buttons.append([InlineKeyboardButton("🔙 חזור", callback_data="back")])
    return difficulty_buttons

# Generate trail links for a specific difficulty level
def get_trail_links_by_difficulty(area, location, difficulty, trail_data):
    area_trail_data = (
        trail_data['center'] if area == "1"
        else trail_data['south'] if area == "2"
        else trail_data['north']
    )
    difficulty_map = {
        '✊ קל': 'easy',
        '💪 בינוני': 'medium',
        '👊 קשה': 'hard'
    }
    trails = area_trail_data['locations'][location][difficulty_map[difficulty]]
    return [[InlineKeyboardButton(trail['trail_name'], url=trail['location_link'])] for trail in trails]

# Handle the /start command
async def start(update: Update, context: CallbackContext):
    context.user_data["menu"] = "main"
    context.user_data['area'] = None
    context.user_data['location'] = None
    isUserLocation = context.user_data.get("isUserLocation", False)  # Fetch the isUserLocation state

    buttons = get_main_menu_buttons(isUserLocation)
    await send_welocme_message(update, context)
    await update.message.reply_text(
        "🏞️ <b>בחר אפשרות:</b>", 
        parse_mode='HTML', 
        reply_markup=InlineKeyboardMarkup(buttons)
    )
async def send_welocme_message(update: Update, context: CallbackContext):
    welcome_message = (
        "👊 **ברוך הבא לבוט הטיולים שלנו!** 🏞️\n\n"
        "בבוט הזה תוכל לבחור מיקום בארץ ולמצוא את המעלה הבא שלך לפי רמת קושי.\n\n"
        "🌍 <b>איך זה עובד?</b>\n\n"
        "1. **בחר אזור בארץ** 🇮🇱\n"
        "2. **בחר מיקום באותו אזור** 📍\n"
        "3. **בחר את רמת הקושי של המעלה** 🧗‍♂️\n\n"
        "הבוט יציג לך את כל המעלות ברמת הקושי שבחרת. לחץ על המעלה שתרצה ותעבור לאפליקציית Off-Road עם כל הפרטים הדרושים. 🚗💨\n\n"
        "🔔 **שימו לב:**\n"
        "אם רמות הקושי **קל, בינוני, קשה** אינן מופיעות, אין לנו מעלה ברמת קושי זו במאגר.\n\n"
        "🌄 <b>אפשרות נוספת:</b>\n"
        "שלח לבוט את המיקום שלך, והוא ימצא עבורך את המעלות הקרובים ביותר. 📲\n\n"
        "- תוכל לשתף את המיקום שלך באמצעות כפתור **שתף מיקום** 📍\n"
        "- או להשתמש בכפתור **מהדק** כדי לשתף את מיקומך בצ'אט 📎\n\n"
        "🔔 **שימו לב:**\n"
        "אם אינך רואה את אפשרות שיתוף המיקום, ייתכן שאין לך הרשאות לשלוח מיקום בצ'אט.\n\n"
        "💪 **בהצלחה!** 🚶‍♂️🌄"
    )
    await update.message.reply_text(
        welcome_message,
        parse_mode='HTML',
    )    

# Define the callback handler
async def handle_button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    trail_data = context.bot_data["trail_data"]

    if data == "userLocationMenu":
        context.user_data["menu"] = "userLocationMenu"
        isUserLocation = context.user_data.get("isUserLocation", True)
        buttons = get_main_menu_buttons(isUserLocation)
        await query.edit_message_text(
            "🏞️ <b>בחר אפשרות:</b>", 
            parse_mode='HTML', 
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data == "showTrails":
        # Show trails near the user using the new function
        user_location = context.user_data.get("userLocation")
        if user_location:
            buttons = show_trails_near_user(update, context)
            if buttons:
                await query.edit_message_text(
                    "**מסלולים בקרבת מקום:**\n\n",
                    parse_mode='HTML',
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            else:
                await query.edit_message_text(
                    "<b>❌ לא נמצאו מסלולים בקרבתך!</b>\n\n",
                    parse_mode='HTML', 
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 חזור", callback_data="back")]])
                )
        else:
            await query.edit_message_text(
                "<b>❌ לא נמצא המיקום שלך! נא שתף את מיקום כדי להמשיך.</b>\n\n",
                parse_mode='HTML', 
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 חזור", callback_data="back")]])
            )
    elif data == "mainMenu":
        context.user_data["menu"] = "main"
        isUserLocation = context.user_data.get("isUserLocation", True)
        buttons = get_main_menu_buttons(isUserLocation)
        await query.edit_message_text(
            "🏞️ <b>בחר אפשרות:</b>", 
            parse_mode='HTML', 
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data.startswith("area:"):
        await handle_area_selection(update, context, data, trail_data)
    elif data.startswith("path:"):
        await handle_path_selection(update, context, data, trail_data)
    elif data.startswith("difficulty:"):
        await handle_difficulty_selection(update, context, data, trail_data)
    elif data == "userLocation":
        # Create a button to share the user's location
        shareLocation_button = KeyboardButton("📍 שתף את מיקומך", request_location=True)
        keyboard = ReplyKeyboardMarkup([[shareLocation_button]], resize_keyboard=True, one_time_keyboard=True)
        await query.message.reply_text(
            "בחר את מיקומך באמצעות כפתור השיתוף של מיקום",
            reply_markup=keyboard
        )
    elif data == "back":
        await handle_back_button(update, context, trail_data)


# Handle area selection
async def handle_area_selection(update: Update, context: CallbackContext, data: str, trail_data: dict):
    area = data.split(":")[1]
    context.user_data["menu"] = "submenu"
    context.user_data["area"] = area
    buttons = get_submenu_buttons(area, trail_data)
    await update.callback_query.edit_message_text(
        "🏞️ <b>בחר מיקום:</b>", 
        parse_mode='HTML', 
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Handle path selection
async def handle_path_selection(update: Update, context: CallbackContext, data: str, trail_data: dict):
    _, area, location = data.split(":")
    context.user_data["menu"] = "difficulty"
    context.user_data["location"] = location
    buttons = get_difficulty_buttons(area, location, trail_data)
    difficulty_message = (
        "<b>🏞️ בחר רמת קושי:</b>\n\n"
        "<b>לא בכל האיזורים יש מסלולים בכל רמות הקושי.</b>\n"
        "<b>❗ <i>אם רמת קושי מסוימת אינה מופיעה, זה אומר שאין מסלולים באותה רמת קושי באיזור שנבחר.</i></b>"
    )
    await update.callback_query.edit_message_text(
        difficulty_message,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Handle difficulty level selection
async def handle_difficulty_selection(update: Update, context: CallbackContext, data: str, trail_data: dict):
    data = update.callback_query.data
    _, area, location, difficulty = data.split(":")

    buttons = get_trail_links_by_difficulty(area, location, difficulty, context.bot_data["trail_data"])
    message = f"🏞️ <b>בחרת ברמת קושי: {difficulty}!</b>"

    await update.callback_query.answer()

    await update.callback_query.message.reply_text(
        message,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Handle the back button
async def handle_back_button(update: Update, context: CallbackContext, trail_data: dict):
    current_menu = context.user_data.get("menu", "main")
    isUserLocation = context.user_data.get("isUserLocation", False)  # Fetch the isUserLocation state

    if current_menu == "submenu":
        context.user_data["menu"] = "main"
        buttons = get_main_menu_buttons(isUserLocation)
        await update.callback_query.edit_message_text(
            "🏞️ <b>בחר את האיזור:</b>", 
            parse_mode='HTML', 
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif current_menu == "difficulty":
        context.user_data["menu"] = "submenu"
        area = context.user_data["area"]
        buttons = get_submenu_buttons(area, trail_data)
        await update.callback_query.edit_message_text(
            "🏞️ <b>בחר מיקום:</b>", 
            parse_mode='HTML', 
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif current_menu == "showTrailsMenu":
        context.user_data["menu"] = "userLocationMenu"
        message, buttons = await handle_location_message(update, context, flag=True)
        await update.callback_query.edit_message_text(
            message,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(buttons)
        )

# Handle location messages
async def handle_location_message(update: Update, context: CallbackContext, flag=False):
    if not flag:
        location = update.message.location
        context.user_data["userLocation"] = location
    else:
        location = context.user_data.get("userLocation")

    easting, northing = convert_coordinates(location.latitude,location.longitude)
    print(f"Received location: {location.latitude}, {location.longitude}")
    print(f"Converted location: {easting}, {northing}")

    context.user_data["isUserLocation"] = True
    context.user_data["menu"] = "userLocationMenu"

    message = (
        f"המסלולים שיוצגו יהיו במרחק של עד 10 ק״מ ממיקומך🌲\n\n"
        f"📍 **מיקום שלך:**\n"
        f"מז: {easting:.2f}\n"
        f"צפ: {northing:.2f}\n"
    )

    buttons = [
        [InlineKeyboardButton("🔍 הצג מסלולים לידך", callback_data="showTrails")],
        [InlineKeyboardButton("🏠 בחר מהתפריט הראשי", callback_data="mainMenu")]
    ]

    if not flag:
        await update.message.reply_text(
            f"✅ **המיקום שלך נקלט בהצלחה!**",
            reply_markup=ReplyKeyboardRemove()
        )
        await update.message.reply_text(
            message,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        return message, buttons

# Define function to show trails near the user within a radius of 10 km
def show_trails_near_user(update: Update, context: CallbackContext, radius_km: int = 20):

    # Update User state
    context.user_data["menu"] = "showTrailsMenu"
    # Retrieve the user's location from user_data
    location = context.user_data.get("userLocation")
    
    # Convert the user's location from latitude and longitude to easting and northing
    easting, northing = convert_coordinates(location.latitude,location.longitude)

    easting = trunc(easting)
    northing = trunc(northing)

    print(f"Received location: {location.latitude}, {location.longitude}")
    print(f"Converted location: {easting}, {northing}")

    # Define the radius in meters
    radius_m = radius_km * 1000
        
    # List to store trails within the radius
    trails_within_radius = []

    #Acess trail data from the bot_data
    trail_data = context.bot_data["trail_data"]
    
    # Loop through the trail data to find trails within the specified radius
    for area in trail_data:
        for location in trail_data[area]['locations']:
            for difficulty in trail_data[area]['locations'][location]:
                for trail in trail_data[area]['locations'][location][difficulty]:
                    if trail['location_easting'] and trail['location_northing']:
                        trail_easting = int(trail['location_easting'])
                        trail_northing = int(trail['location_northing'])
                        distance = sqrt((trail_easting - easting)**2 + (trail_northing - northing)**2)
                        if distance <= radius_m:
                            trails_within_radius.append(trail)                     
    
    # Check if there are any trails within the radius
    if trails_within_radius:
        buttons = [[InlineKeyboardButton(trail['trail_name'], url=trail['location_link'])] for trail in trails_within_radius]
        buttons.append([InlineKeyboardButton("🔙 חזור", callback_data="back")])
        return buttons
    else:
        return None



# Main function to start the bot
def main():
    # Load bot token
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    trail_data_file = 'trails.json'  
    trail_data = load_trail_data(trail_data_file)

    application = Application.builder().token(BOT_TOKEN).build()  
    application.bot_data["trail_data"] = trail_data  

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_button_click))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location_message))

    # Start polling
    application.run_polling()

if __name__ == '__main__':
    main()
