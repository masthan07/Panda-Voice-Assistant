import pyttsx3 as p
import speech_recognition as sr
import datetime
import requests
import webbrowser
import os
import subprocess
import random
import pywhatkit as kit
from textblob import TextBlob
import datetime
import time
import threading
import re  
import streamlit as st

# Initializing the pyttsx3 engine
engine = p.init()
rate = engine.getProperty('rate')
engine.setProperty('rate', 180)
voices = engine.getProperty('voices')
engine.setProperty('voices', voices[1].id)

CONVERSATION_FILE = "conversation.txt"

def speak(text):
    print(f"Assistant: {text}")  # Print the assistant's spoken command
    engine.say(text)
    engine.runAndWait()

# Speech recognition setup
r = sr.Recognizer()

# Function to listen for a wake word
def listen_for_wake_word():
    with sr.Microphone() as mic:
        r.adjust_for_ambient_noise(mic)
        r.dynamic_energy_threshold = True
        print("Listening...")
        audio = r.listen(mic)
        try:
            text = r.recognize_google(audio, language='en-US').lower()
        except:
            return None
    print("USER -> " + text)
    return text

# Function to check for wake word ("panda")
def activate_assistant():
    while True:
        wake_word = listen_for_wake_word()
        if wake_word and "panda" in wake_word:  # Wake word to activate assistant
            speak("Hello! I am panda,your smart assistant")
            detect_mood()  # Detect user's mood after wake word
            break
        else:
            print("Waiting for wake word...")

# Function to detect user's mood
def detect_mood():
    speak("How are you feeling today?")
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=2)
        print("Listening for mood...")
        audio = r.listen(source)
        try:
            mood_text = r.recognize_google(audio).lower()
            print(f"Heard: {mood_text}")
            blob = TextBlob(mood_text)
            sentiment = blob.sentiment.polarity
            if sentiment > 0:
                speak("You sound happy! That's great to hear.")
            elif sentiment < 0:
                speak("You sound upset. I hope everything is okay.")
            else:
                speak("You sound neutral. How can I assist you today?")
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that. Please repeat.")
        except Exception as e:
            print(f"An error occurred: {e}")
            speak("Sorry, something went wrong. Please try again.")

# Function to listen to user input
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language="en-US")
        print(f"User said: {query}")
        return query.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that. Can you please repeat?")
        return None
    except sr.RequestError:
        speak("Sorry, my speech service is down.")
        return None            

# Function to play song using pywhatkit (direct YouTube play)
def play_spotify_song(song_name):
    speak(f"Playing {song_name} on YouTube.")
    kit.playonyt(song_name)  # Play on YouTube using pywhatkit

# Function to get the current time
def get_time(timezone='local'):
    if timezone == 'local':
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
    else:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")  # Default time
    return f"The current time is {current_time}"

# Function to get the meaning of a word
def get_word_meaning(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"  # Free Dictionary API
    try:
        response = requests.get(url)
        data = response.json()
        if "title" in data and data["title"] == "No Definitions Found":
            return f"Sorry, I couldn't find a definition for the word {word}."
        else:
            meaning = data[0]["meanings"][0]["definitions"][0]["definition"]
            return f"The meaning of {word} is: {meaning}"
    except Exception as e:
        return f"Sorry, I couldn't fetch the meaning of {word}. Error: {str(e)}"

# Function to fetch the latest news
def get_latest_news():
    api_key = "4a98bf1fd1cb44af93afbd0083773169"  # Replace with your NewsAPI key
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    try:
        response = requests.get(url)
        news_data = response.json()
        if news_data["status"] == "ok":
            articles = news_data["articles"][:3]
            news_list = []
            for article in articles:
                title = article["title"]
                description = article["description"]
                news_list.append(f"Title: {title}\nDescription: {description}")
            return "\n\n".join(news_list)
        else:
            return "Sorry, I couldn't fetch the latest news at the moment."
    except Exception as e:
        return f"Error fetching news: {str(e)}"

# Function to get the weather
def get_weather(location):
    api_key = "1a3a3a439f9a0696398867f0642c7960"  # Replace with your OpenWeatherMap API key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        if data["cod"] != "404":
            main = data["main"]
            weather_description = data["weather"][0]["description"]
            temperature = main["temp"]
            return f"The weather in {location} is {weather_description} with a temperature of {temperature - 273.15:.2f}°C."
        else:
            return f"Sorry, I couldn't find the weather for {location}."
    except Exception as e:
        return f"Error fetching weather: {str(e)}"

# Function to recommend a random movie using TMDb API
def recommend_movie():
    api_key = "006b9feaeefc4ac382ecbb5f85450951"  # Replace with your TMDb API key
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&page=1"
    try:
        response = requests.get(url)
        movie_data = response.json()
        if movie_data["results"]:
            # Select a random movie from the results
            movie = random.choice(movie_data["results"])
            movie_title = movie["title"]
            movie_overview = movie["overview"]
            movie_language = movie["original_language"]
            return f"I recommend you watch {movie_title} (in {movie_language}). Here's a brief overview: {movie_overview}"
        else:
            return "Sorry, I couldn't fetch any movie recommendations at the moment."
    except Exception as e:
        return f"Sorry, there was an error fetching movie recommendations: {str(e)}"

# Function to perform basic mathematical calculations
def calculate(operation, num1, num2=None):
    try:
        num1 = float(num1)
        if num2 is not None:
            num2 = float(num2)
    except ValueError:
        return "Error: Please provide valid numbers for the calculation."

    if operation == "addition":
        return num1 + num2
    elif operation == "subtract":
        return num1 - num2
    elif operation == "multiply":
        return num1 * num2
    elif operation == "divide":
        if num2 != 0:
            return num1 / num2
        else:
            return "Error: Division by zero is not allowed."
    elif operation == "exponentiation" or operation == "power":
        return num1 ** num2
    elif operation == "square root":
        if num1 >= 0:
            return num1 ** 0.5
        else:
            return "Error: Cannot take the square root of a negative number."
    elif operation == "modulus":
        return num1 % num2
    else:
        return "Error: Invalid operation. Please use add, subtract, multiply, divide, power, square root, or modulus."

# Recipe Assistant with Recipe Description
def get_recipe(ingredients):
    api_key = "361ad4728322472aa9e8efbd7a76d52b"  # Replace with your Spoonacular API key
    url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&number=1&apiKey={api_key}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return "Sorry, there was an issue connecting to the recipe service.", None
        
        data = response.json()

        if not data:
            return "Sorry, I couldn't find any recipes with those ingredients.", None

        recipe = data[0]
        recipe_title = recipe.get("title", "Unknown Recipe")
        recipe_id = recipe.get("id", "")
        recipe_url = f"https://spoonacular.com/recipes/{recipe_title.replace(' ', '-')}-{recipe_id}"

        return f"I found a recipe: {recipe_title}. Would you like me to open the recipe in your browser?", recipe_url

    except Exception as e:
        return f"Error fetching recipe: {str(e)}", None

def fetch_story():
    try:
        response = requests.get("https://shortstories-api.onrender.com/")
        if response.status_code == 200:
            story_data = response.json()
            return story_data.get("story", "No story available.")
        else:
            return "Failed to fetch a story. Try again later."
    except Exception as e:
        return f"Error: {e}"

def tell_story():
    story = fetch_story()
    speak("Here is a story for you.")
    speak(story) 

# Function to listen to user input
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language="en-US")
        print(f"User said: {query}")
        return query.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that. Can you please repeat?")
        return None
    except sr.RequestError:
        speak("Sorry, my speech service is down.")
        return None

def set_reminder(reminder_text, reminder_time):
    def reminder():
        # Calculate the delay in seconds
        delay = (reminder_time - datetime.datetime.now()).total_seconds()
        if delay > 0:
            print(f"Reminder set for {reminder_time.strftime('%H:%M')}. Waiting for {delay} seconds...")
            time.sleep(delay)
            speak(f"Reminder: {reminder_text}")
        else:
            speak("The reminder time has already passed.")

    # Start the reminder thread
    threading.Thread(target=reminder).start()

def set_alarm(alarm_time):
    def alarm():
        time_to_wait = (alarm_time - datetime.datetime.now()).total_seconds()
        if time_to_wait > 0:
            time.sleep(time_to_wait)
            speak("Wake up! Your alarm is ringing.")
        else:
            speak("The alarm time has already passed.")

    threading.Thread(target=alarm).start()

def convert_to_24h(time_input):
    try:
        # Use regex to extract hours, minutes, and period (AM/PM)
        match = re.match(r"(\d{1,2}):?(\d{2})?\s?(a\.?m\.?|p\.?m\.?)?", time_input, re.IGNORECASE)
        if not match:
            # Handle cases like "949 p.m." or "9 49 p.m."
            match = re.match(r"(\d{1,2})\s?(\d{2})\s?(a\.?m\.?|p\.?m\.?)?", time_input, re.IGNORECASE)
            if not match:
                return None

        hours = int(match.group(1))
        minutes = int(match.group(2)) if match.group(2) else 0
        period = match.group(3).lower() if match.group(3) else None

        # Validate hours and minutes
        if not (0 <= hours <= 12 and 0 <= minutes < 60):
            return None

        # Convert to 24-hour format
        if period and "p" in period and hours != 12:
            hours += 12
        elif period and "a" in period and hours == 12:
            hours = 0

        return hours, minutes
    except (AttributeError, ValueError):
        return None

# Function to parse time input (always converts to 24-hour format)
def parse_time(time_input):
    # Always try to convert to 24-hour format
    parsed_time = convert_to_24h(time_input)
    if parsed_time:
        return parsed_time
    else:
        return None 

book_recommendations = {
    "digital logic": [
        "Digital Design by M. Morris Mano",
        "Fundamentals of Logic Design by Charles H. Roth",
        "Digital Logic and Computer Design by M. Morris Mano"
    ],
    "computer science": [
        "Introduction to the Theory of Computation by Michael Sipser",
        "Computer Organization and Design by David A. Patterson & John L. Hennessy",
        "The Art of Computer Programming by Donald Knuth"
    ],
    "artificial intelligence": [
        "Artificial Intelligence: A Modern Approach by Stuart Russell & Peter Norvig",
        "Deep Learning by Ian Goodfellow, Yoshua Bengio, and Aaron Courville",
        "Pattern Recognition and Machine Learning by Christopher M. Bishop"
    ],
    "machine learning": [
        "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow by Aurélien Géron",
        "Machine Learning Yearning by Andrew Ng",
        "The Hundred-Page Machine Learning Book by Andriy Burkov"
    ],
    "deep learning": [
        "Deep Learning by Ian Goodfellow, Yoshua Bengio, and Aaron Courville",
        "Neural Networks and Deep Learning by Michael Nielsen",
        "Hands-On Deep Learning with PyTorch and TensorFlow by Eli Stevens"
    ],
    "data science": [
        "Data Science for Business by Foster Provost & Tom Fawcett",
        "Python for Data Analysis by Wes McKinney",
        "The Data Science Handbook by Carl Shan"
    ],
    "c programming": [
        "The C Programming Language by Brian W. Kernighan & Dennis M. Ritchie",
        "C: How to Program by Paul Deitel & Harvey Deitel",
        "Let Us C by Yashavant Kanetkar"
    ],
    "c++ programming": [
        "The C++ Programming Language by Bjarne Stroustrup",
        "Effective C++ by Scott Meyers",
        "C++ Primer by Stanley B. Lippman, Josée Lajoie, and Barbara E. Moo"
    ],
    "java programming": [
        "Effective Java by Joshua Bloch",
        "Java: The Complete Reference by Herbert Schildt",
        "Head First Java by Kathy Sierra & Bert Bates"
    ],
    "operating systems": [
        "Operating System Concepts by Abraham Silberschatz",
        "Modern Operating Systems by Andrew S. Tanenbaum",
        "Operating Systems: Three Easy Pieces by Remzi H. Arpaci-Dusseau"
    ],
    "computer networks": [
        "Computer Networking: A Top-Down Approach by James F. Kurose & Keith W. Ross",
        "Data and Computer Communications by William Stallings",
        "Computer Networks by Andrew S. Tanenbaum"
    ],
    "database management": [
        "Database System Concepts by Abraham Silberschatz",
        "Fundamentals of Database Systems by Ramez Elmasri & Shamkant B. Navathe",
        "SQL for Data Scientists by Renee M. P. Teate"
    ],
    "cybersecurity": [
        "Hacking: The Art of Exploitation by Jon Erickson",
        "Cybersecurity Essentials by Charles J. Brooks",
        "The Web Application Hacker's Handbook by Dafydd Stuttard & Marcus Pinto"
    ],
    "computer architecture": [
        "Computer Architecture: A Quantitative Approach by John L. Hennessy & David A. Patterson",
        "Structured Computer Organization by Andrew S. Tanenbaum",
        "Digital Design and Computer Architecture by David Money Harris & Sarah L. Harris"
    ],
    "software engineering": [
        "Software Engineering: A Practitioner's Approach by Roger S. Pressman",
        "Clean Code: A Handbook of Agile Software Craftsmanship by Robert C. Martin",
        "The Mythical Man-Month by Frederick P. Brooks Jr."
    ],
    "compiler design": [
        "Compilers: Principles, Techniques, and Tools by Alfred V. Aho, Monica S. Lam, Ravi Sethi, Jeffrey D. Ullman (Dragon Book)",
        "Modern Compiler Implementation in C by Andrew W. Appel",
        "Engineering a Compiler by Keith D. Cooper & Linda Torczon"
    ]
}

def recommend_book(subject):
    """Recommend books based on the subject."""
    subject = subject.lower()
    if subject in book_recommendations:
        books = book_recommendations[subject]
        recommendation = f"Here are some recommended books on {subject}: " + ", ".join(books) + "."
    else:
        recommendation = "Sorry, I don't have book recommendations for that subject."
    
    speak(recommendation)

def listen_for_subject():
    recognizer = sr.Recognizer()
    """Listen for a subject input from the user."""
    with sr.Microphone() as source:
        speak("Please tell me a subject to recommend books.")
        print("🎤 Listening for a subject...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            print(f"🗣 You said: {text}\n")
            return text.lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn't understand that.")
            return ""
        except sr.RequestError:
            speak("There was an error with the speech recognition service.")
            return ""

# Run the book recommendation process
def book_recommendation_assistant():
    """Main function to handle book recommendations."""
    subject = listen_for_subject()
    if subject:
        recommend_book(subject)   

def search_google(query):
    try:
        # Replace with your SerpApi API key
        api_key = "88d9aafd04addd441519fb60e9ba5da26a92c8f630945255f850461346da6a80"
        url = f"https://serpapi.com/search?q={query}&api_key={api_key}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            # Ensure we have at least one result
            if 'organic_results' in data and len(data['organic_results']) > 0:
                top_result = data['organic_results'][0]  # Get the first search result
                title = top_result.get('title', 'No title available')
                link = top_result.get('link', 'No link available')
                snippet = top_result.get('snippet', 'No snippet available')
                
                # Return a more descriptive response
                return f" Here's a brief description about {query}: {snippet}."
            else:
                return "Sorry, I couldn't find any results for that search."
        else:
            return "Sorry, I couldn't fetch the Google search results at the moment."
    except Exception as e:
        return f"Sorry, there was an error searching Google: {str(e)}" 

# OpenStreetMap Nominatim API for geocoding
def geocode_location(location):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": location,
        "format": "json",
        "limit": 1,  # Get only the top result
        "addressdetails": 1,  # Get detailed address breakdown
        "countrycodes": "IN"  # Restrict to India (for Hyderabad, India)
    }
    headers = {
        "User-Agent": "MyMapsAssistant/1.0 (bellamkondamasthanbasha@gmail.com)"  # Replace with your email
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)  # Add timeout
        response.raise_for_status()  # Raise error for bad status codes
        data = response.json()
        if data:
            lat, lon = float(data[0]["lat"]), float(data[0]["lon"])
            print(f"Geocoded '{location}' to Coordinates: {lat}, {lon}")
            return lat, lon
        else:
            return None
    except (requests.exceptions.RequestException, ValueError, KeyError) as e:
        print(f"Error fetching geocoding data: {e}")
        return None

# OSRM API for routing
def get_route(start, end):
    url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}"
    try:
        response = requests.get(url, timeout=10)  # Add timeout to avoid hanging
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        if data.get("routes"):
            distance = data["routes"][0]["distance"] / 1000  # Convert meters to kilometers
            duration = data["routes"][0]["duration"] / 60  # Convert seconds to minutes
            return distance, duration
        else:
            return None
    except (requests.exceptions.RequestException, ValueError, KeyError) as e:
        print(f"Error fetching route data: {e}")
        return None

# Function to handle navigation
def navigate_to():
    speak("Where would you like to navigate to?")
    destination = listen()
    if not destination:
        speak("Sorry, I didn't catch that. Please try again.")
        return
    
    destination_coords = geocode_location(destination)
    if not destination_coords:
        speak(f"Sorry, I couldn't find the location '{destination}'. Please try again with a different name.")
        return
    
    speak("Where are you starting from?")
    start = listen()
    if not start:
        speak("Sorry, I didn't catch that. Please try again.")
        return
    
    start_coords = geocode_location(start)
    if not start_coords:
        speak(f"Sorry, I couldn't find the location '{start}'. Please try again with a different name.")
        return
    
    route = get_route(start_coords, destination_coords)
    if route:
        distance, duration = route
        speak(f"The distance to {destination} is {distance:.2f} kilometers, and it will take about {duration:.2f} minutes.")
        
        # Open the route in the browser
        url = f"https://www.openstreetmap.org/directions?route={start_coords[0]}%2C{start_coords[1]}%3B{destination_coords[0]}%2C{destination_coords[1]}"
        webbrowser.open(url)
    else:
        speak("Sorry, I couldn't calculate the route. Please check your locations and try again.")

# Function to calculate distance between two places
def calculate_distance():
    speak("What is the origin location?")
    origin = listen()
    if not origin:
        speak("Sorry, I didn't catch that. Please try again.")
        return
    
    speak("What is the destination location?")
    destination = listen()
    if not destination:
        speak("Sorry, I didn't catch that. Please try again.")
        return
    
    origin_coords = geocode_location(origin)
    if not origin_coords:
        speak(f"Sorry, I couldn't find the location '{origin}'. Please try again with a different name.")
        return
    
    destination_coords = geocode_location(destination)
    if not destination_coords:
        speak(f"Sorry, I couldn't find the location '{destination}'. Please try again with a different name.")
        return
    
    route = get_route(origin_coords, destination_coords)
    if route:
        distance, duration = route
        speak(f"The distance between {origin} and {destination} is {distance:.2f} kilometers, and it will take about {duration:.2f} minutes.")
    else:
        speak("Sorry, I couldn't calculate the distance. Please check your locations and try again.") 


def should_stop():
    return os.path.exists("stop_flag.txt") 

def send_whatsapp_message():
    """
    Sends a WhatsApp message to a specified contact with voice input for the message content.
    """

    # 1. Get the contact number
    print("Please provide the recipient's phone number with country code (e.g., +1234567890):")
    #Speak and input number
    number = input("Enter number:")

    # 2. Get the message content using speech recognition
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak the message you want to send:")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=10) # 10 sec timeout
            message = recognizer.recognize_google(audio, language="en-US")  # Recognize in English
            print(f"Recognized Message: {message}")
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand the message. Please type it:")
            message = input("Enter message:")
        except sr.RequestError:
            print("Sorry, the speech recognition service is down. Please type your message:")
            message = input("Enter message:")
        except sr.WaitTimeoutError:
            print("No speech detected. Please type your message:")
            message = input("Enter message:")

    # 3. Get the time to send the message
    now = datetime.datetime.now()
    send_hour = now.hour
    send_minute = now.minute + 1 # Send message after two minutes. You can replace number.

    if send_minute >= 60:
        send_hour = (send_hour + 1) % 24
        send_minute %= 60
    print(f"Sending message at {send_hour}:{send_minute}")
    try:
        # 4. Send the WhatsApp message using pywhatkit
        kit.sendwhatmsg(number, message, send_hour, send_minute)
        print("WhatsApp message sent successfully!")

    except Exception as e:
        print(f"An error occurred while sending the WhatsApp message: {e}")       

# Function to process commands
def process_commands():
    speak("What can I do for you?")

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=2)
        r.energy_threshold = 4000
        print("Listening for command...")
        try:
            audio = r.listen(source, timeout=10)
            text2 = r.recognize_google(audio).lower()
            print(f"Heard: {text2}")
            # Append user command to conversation file
            with open(CONVERSATION_FILE, "a") as f:
                f.write(f"User: {text2}\n")

            # If the user asks for a song
            if "play" in text2 and "song" in text2:
                speak("What song would you like to play?")
                with open(CONVERSATION_FILE, "a") as f:
                    f.write("Assistant: What song would you like to play?\n")
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=2)
                    print("Listening for the song name...")
                    audio = r.listen(source)
                    song_name = r.recognize_google(audio).lower()
                    print(f"Heard: {song_name}")
                    with open(CONVERSATION_FILE, "a") as f:
                        f.write(f"User: {song_name}\n")
                play_spotify_song(song_name)
                with open(CONVERSATION_FILE, "a") as f:
                    f.write(f"Assistant: Playing {song_name} on YouTube.\n")

            # If the user asks for the date
            elif "date" in text2 or "today" in text2:
                current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
                speak(f"Today's date is {current_date}")
                with open(CONVERSATION_FILE, "a") as f:
                    f.write(f"Assistant: Today's date is {current_date}\n")

            # If the user asks for time
            elif "time" in text2:
                current_time = get_time()  # Calls the function to get current time
                speak(current_time)
                with open(CONVERSATION_FILE, "a") as f:
                    f.write(f"Assistant: {current_time}\n")

            # If the user asks for information or search
            elif "detilas" in text2:
                speak("You need information related to which topic?")
                with open(CONVERSATION_FILE, "a") as f:
                    f.write("Assistant: You need information related to which topic?\n")
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=2)
                    print("Listening for the topic...")
                    audio = r.listen(source)
                    infor = r.recognize_google(audio)
                    print(f"Searching for: {infor}")
                    with open(CONVERSATION_FILE, "a") as f:
                        f.write(f"User: {infor}\n")

                speak(f"Searching for {infor}")
                url = f"https://en.wikipedia.org/wiki/{infor.replace(' ', '_')}"
                speak(f"Here is the information I found on Wikipedia about {infor}")
                with open(CONVERSATION_FILE, "a") as f:
                    f.write(f"Assistant: Here is the information I found on Wikipedia about {infor}\n")
                print(f"Opening: {url}")
                webbrowser.open(url)

            # If the user asks for the meaning of a word
            elif "meaning" in text2 or "definition" in text2 or "what is the meaning of" in text2 or "tell me the definition of" in text2:
                speak("Which word would you like to know the meaning of?")
                with open(CONVERSATION_FILE, "a") as f:
                    f.write("Assistant: Which word would you like to know the meaning of?\n")
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=2)
                    print("Listening for the word...")
                    audio = r.listen(source)
                    word = r.recognize_google(audio)
                    print(f"Heard: {word}")
                    with open(CONVERSATION_FILE, "a") as f:
                        f.write(f"User: {word}\n")

                meaning = get_word_meaning(word)
                speak(meaning)
                with open(CONVERSATION_FILE, "a") as f:
                    f.write(f"Assistant: {meaning}\n")

            # If the user asks for the news
            elif "news" in text2 or "headlines" in text2:
                speak("Here are the latest news headlines:")
                with open(CONVERSATION_FILE, "a") as f:
                    f.write("Assistant: Here are the latest news headlines:\n")
                news = get_latest_news()
                speak(news)
                with open(CONVERSATION_FILE, "a") as f:
                    f.write(f"Assistant: {news}\n")

            # If the user asks for a joke
            elif "joke" in text2:
                speak("Here's a joke for you!")
                with open(CONVERSATION_FILE, "a") as f:
                    f.write("Assistant: Here's a joke for you!\n")
                def get_joke():
                    try:
                        response = requests.get("https://official-joke-api.appspot.com/random_joke")
                        joke = response.json()
                        return f"{joke['setup']} {joke['punchline']}"
                    except Exception as e:
                        return "Sorry, I couldn't get a joke at the moment."
                joke = get_joke()
                speak(joke)
                with open(CONVERSATION_FILE, "a") as f:
                    f.write(f"Assistant: {joke}\n")

            # If the user wants to open an app
            elif "open" in text2:
                app_name = text2.replace("open", "").strip()
                speak(f"Opening {app_name}...")
                with open(CONVERSATION_FILE, "a") as f:
                    f.write(f"Assistant: Opening {app_name}...\n")
                if os.name == 'nt':  # For Windows
                    if "calculator" in app_name:
                        subprocess.Popen("C:\\Windows\\System32\\calc.exe")
                    elif "chrome" in app_name:
                        subprocess.Popen(["C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"])
                    elif "word" in app_name:
                        subprocess.Popen("C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE")
                    elif "excel" in app_name:
                        subprocess.Popen("C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE")
                    elif "powerpoint" in app_name:
                        subprocess.Popen("C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE")
                    else:
                        speak("Sorry, I don't know how to open that app.")
                        with open(CONVERSATION_FILE, "a") as f:
                            f.write("Assistant: Sorry, I don't know how to open that app.\n")
                else:
                    speak("Sorry, I cannot open applications on this system.")
                    with open(CONVERSATION_FILE, "a") as f:
                        f.write("Assistant: Sorry, I cannot open applications on this system.\n")

            # If the user asks for the weather
            elif "weather" in text2 or "climate" in text2:
                speak("Please tell me the location for the weather.")
                with open(CONVERSATION_FILE, "a") as f:
                    f.write("Assistant: Please tell me the location for the weather.\n")
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=2)
                    print("Listening for location...")
                    audio = r.listen(source)
                    location = r.recognize_google(audio)
                    print(f"Heard: {location}")
                    with open(CONVERSATION_FILE, "a") as f:
                        f.write(f"User: {location}\n")
                weather_report = get_weather(location)
                speak(weather_report)
                with open(CONVERSATION_FILE, "a") as f:
                    f.write(f"Assistant: {weather_report}\n")

            # If the user wants to search YouTube
            elif "play" in text2 and "video" in text2:
                speak("What video would you like to play on YouTube?")
                with open(CONVERSATION_FILE, "a") as f:
                    f.write("Assistant: What video would you like to play on YouTube?\n")
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=2)
                    print("Listening for the video name...")
                    audio = r.listen(source)
                    video_name = r.recognize_google(audio).lower()
                    print(f"Heard: {video_name}")
                    with open(CONVERSATION_FILE, "a") as f:
                        f.write(f"User: {video_name}\n")

                # Use pywhatkit to play the video on YouTube
                speak(f"Playing {video_name} on YouTube.")
                with open(CONVERSATION_FILE, "a") as f:
                    f.write(f"Assistant: Playing {video_name} on YouTube.\n")
                kit.playonyt(video_name)

            # If the user asks for a movie recommendation
            elif "recommend" in text2 and "movie" in text2:
                speak("Let me recommend a movie for you.")
                with open(CONVERSATION_FILE, "a") as f:
                    f.write("Assistant: Let me recommend a movie for you.\n")
                recommendation = recommend_movie()
                speak(recommendation)
                with open(CONVERSATION_FILE, "a") as f:
                    f.write(f"Assistant: {recommendation}\n")

            # If the user asks for a mathematical calculation
            elif "calculation" in text2 or "maths" in text2:
                speak("Sure, let's do some math. What operation would you like to perform? (add, subtract, multiply, divide,power,suare root,modulus)")
                with open(CONVERSATION_FILE, "a") as f:
                    f.write("Assistant: Sure, let's do some math. What operation would you like to perform? (add, subtract, multiply, divide,power,suare root,modulus)\n")
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=2)
                    print("Listening for operation...")
                    audio = r.listen(source)
                    operation = r.recognize_google(audio).lower()
                    print(f"Heard: {operation}")
                    with open(CONVERSATION_FILE, "a") as f:
                        f.write(f"User: {operation}\n")

                if operation not in ["add", "subtract", "multiply", "divide","power","square"]:
                    speak("Sorry, I can only handle add, subtract, multiply, or divide operations.")
                    with open(CONVERSATION_FILE, "a") as f:
                        f.write("Assistant: Sorry, I can only handle add, subtract, multiply, or divide operations.\n")
                    return

                speak("Please say the first number.")
                with open(CONVERSATION_FILE, "a") as f:
                    f.write("Assistant: Please say the first number.\n")
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=2)
                    print("Listening for the first number...")
                    audio = r.listen(source)
                    num1 = r.recognize_google(audio)
                    print(f"Heard: {num1}")
                    with open(CONVERSATION_FILE, "a") as f:
                        f.write(f"User: {num1}\n")

                speak("Please say the second number.")
                with open(CONVERSATION_FILE, "a") as f:
                    f.write("Assistant: Please say the second number.\n")
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=2)
                    print("Listening for the second number...")
                    audio = r.listen(source)
                    num2 = r.recognize_google(audio)
                    print(f"Heard: {num2}")
                    with open(CONVERSATION_FILE, "a") as f:
                        f.write(f"User: {num2}\n")

                # Handle any invalid inputs for numbers
                try:
                    num1 = float(num1)
                    num2 = float(num2)
                except ValueError:
                    speak("Sorry, I didn't catch valid numbers. Please try again with valid numbers.")
                    with open(CONVERSATION_FILE, "a") as f:
                        f.write("Assistant: Sorry, I didn't catch valid numbers. Please try again with valid numbers.\n")
                    return

                result = calculate(operation, num1, num2)
                speak(f"The result is {result}")
                with open(CONVERSATION_FILE, "a") as f:
                    f.write(f"Assistant: The result is {result}\n")

            # If the user asks for recipe assistance
            elif "recipe" in text2 or "cook" in text2:
                speak("Please list the ingredients you have.")
                with open(CONVERSATION_FILE, "a") as f:
                    f.write("Assistant: Please list the ingredients you have.\n")
                ingredients = listen()
                if ingredients:
                    with open(CONVERSATION_FILE, "a") as f:
                        f.write(f"User: {ingredients}\n")
                    recipe_result, recipe_url = get_recipe(ingredients)
                    speak(recipe_result)
                    with open(CONVERSATION_FILE, "a") as f:
                        f.write(f"Assistant: {recipe_result}\n")
                    if recipe_url:
                        speak("Say 'yes' to open the recipe or 'no' to cancel.")
                        with open(CONVERSATION_FILE, "a") as f:
                            f.write("Assistant: Say 'yes' to open the recipe or 'no' to cancel.\n")
                        response = listen()
                        if response and "yes" in response:
                            webbrowser.open(recipe_url)
                            speak("Opening the recipe in your browser.")
                            with open(CONVERSATION_FILE, "a") as f:
                                f.write("Assistant: Opening the recipe in your browser.\n")
                        else:
                            speak("Okay, I won't open the recipe.")
                            with open(CONVERSATION_FILE, "a") as f:
                                f.write("Assistant: Okay, I won't open the recipe.\n")
            elif "story" in text2:
                tell_story()
                with open(CONVERSATION_FILE, "a") as f:
                    f.write("Assistant: Here is a story for you.\n")

            elif "alarm" in text2:
                speak("When should I set the alarm? Please say the time.")
                with open(CONVERSATION_FILE, "a") as f:
                    f.write("Assistant: When should I set the alarm? Please say the time.\n")
                time_input = listen()
                if time_input:
                    with open(CONVERSATION_FILE, "a") as f:
                        f.write(f"User: {time_input}\n")
                    parsed_time = parse_time(time_input)
                    if parsed_time:
                        hours, minutes = parsed_time
                        now = datetime.datetime.now()
                        alarm_time = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
                        if alarm_time < now:
                            alarm_time += datetime.timedelta(days=1)  # Set for the next day if time has passed
                        set_alarm(alarm_time)
                        speak(f"Alarm set for {alarm_time.strftime('%H:%M')}.")
                        with open(CONVERSATION_FILE, "a") as f:
                            f.write(f"Assistant: Alarm set for {alarm_time.strftime('%H:%M')}.\n")

            elif "reminder" in text2:
                speak("What should I remind you about?")
                with open(CONVERSATION_FILE, "a") as f:
                    f.write("Assistant: What should I remind you about?\n")
                reminder_text = listen()
                if reminder_text:
                    with open(CONVERSATION_FILE, "a") as f:
                        f.write(f"User: {reminder_text}\n")
                    speak("When should I remind you?")
                    with open(CONVERSATION_FILE, "a") as f:
                        f.write("Assistant: When should I remind you?\n")
                    time_input = listen()
                    if time_input:
                        with open(CONVERSATION_FILE, "a") as f:
                            f.write(f"User: {time_input}\n")
                        parsed_time = parse_time(time_input)
                        if parsed_time:
                            now = datetime.datetime.now()
                            reminder_time = now.replace(hour=parsed_time[0], minute=parsed_time[1], second=0, microsecond=0)
                            if reminder_time < now:
                                reminder_time += datetime.timedelta(days=1)  # Set reminder for the next day if time has passed
                            set_reminder(reminder_text, reminder_time)
                            speak(f"Reminder set for {reminder_time.strftime('%H:%M')}.")
                            with open(CONVERSATION_FILE, "a") as f:
                                f.write(f"Assistant: Reminder set for {reminder_time.strftime('%H:%M')}.\n")
                        else:
                            speak("Sorry, I couldn't understand the time.")
                            with open(CONVERSATION_FILE, "a") as f:
                                f.write("Assistant: Sorry, I couldn't understand the time.\n")

            elif "book" in text2:
                book_recommendation_assistant()
                with open(CONVERSATION_FILE, "a") as f:
                    f.write("Assistant: Here are some book recommendations.\n")

            elif "search" in text2 or "google" in text2:
                speak("What would you like to search for?")
                with open(CONVERSATION_FILE, "a") as f:
                    f.write("Assistant: What would you like to search for?\n")
                query = listen()
                if query:
                    with open(CONVERSATION_FILE, "a") as f:
                        f.write(f"User: {query}\n")
                    result = search_google(query)
                    speak(result)
                    with open(CONVERSATION_FILE, "a") as f:
                        f.write(f"Assistant: {result}\n")

            elif "navigate" in text2:
                navigate_to()
                with open(CONVERSATION_FILE, "a") as f:
                    f.write("Assistant: Navigating to the specified location.\n")

            elif "distance" in text2:
                calculate_distance()
                with open(CONVERSATION_FILE, "a") as f:
                    f.write("Assistant: Calculating the distance between two locations.\n")

            elif "send" or "whatsapp" in text2:
                send_whatsapp_message()
                with open(CONVERSATION_FILE, "a") as f:
                    f.write(f"Assistant: sent message \n")        

        except sr.WaitTimeoutError:
            print("Timeout: No speech detected.")
            speak("Sorry, I didn't hear anything. Please try again.")
            with open(CONVERSATION_FILE, "a") as f:
                f.write("Assistant: Sorry, I didn't hear anything. Please try again.\n")

        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
            speak("Sorry, I didn't catch that. Please repeat.")
            with open(CONVERSATION_FILE, "a") as f:
                f.write("Assistant: Sorry, I didn't catch that. Please repeat.\n")

        except Exception as e:
            print(f"An error occurred: {e}")
            speak("Sorry, something went wrong. Please try again.")
            with open(CONVERSATION_FILE, "a") as f:
                f.write("Assistant: Sorry, something went wrong. Please try again.\n")

# Main loop
def main():
    activate_assistant()
    process_commands()

# Start the assistant
main()