import speech_recognition as sr
from gtts import gTTS
import os
import playsound
import datetime
import random
import webbrowser
import requests
from bs4 import BeautifulSoup
import pywhatkit as kit
from deep_translator import GoogleTranslator
import subprocess
import threading
import time
import re
from textblob import TextBlob

CONVERSATION_FILE = "conversation.txt"

# Check if the conversation file exists. If not, create it.
if not os.path.exists(CONVERSATION_FILE):
    with open(CONVERSATION_FILE, "w", encoding="utf-8") as f:
        pass
# Translation function
def translate_to_telugu(text):
    """Translates given text to Telugu using Google Translate."""
    translator = GoogleTranslator(source='en', target='te')
    return translator.translate(text)

def speak_telugu(text):
    """Convert text to speech in Telugu and play the audio."""
    print("\nస్మార్ట్ అసిస్టెంట్:", text)
    tts = gTTS(text=text, lang="te")
    tts.save("response.mp3")
    playsound.playsound(os.path.abspath("response.mp3"))
    os.remove("response.mp3")

def listen_telugu():
    """Listen for Telugu speech and convert it to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nతెలుగు మాట్లాడండి... (Speak in Telugu)")
        recognizer.adjust_for_ambient_noise(source)

        try:
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio, language="te-IN")
            print("\nమీరు చెప్పింది:", text)
            return text
        except sr.UnknownValueError:
            print("\nక్షమించండి, నేను అర్థం చేసుకోలేకపోయాను.")
            return None
        except sr.RequestError:
            print("\nసర్వర్ సమస్య! దయచేసి మళ్లీ ప్రయత్నించండి.")
            return None
        

def listen_for_wake_word():
    """Listens for a wake word in English and triggers the assistant."""
    recognizer = sr.Recognizer()  # Create a local recognizer
    with sr.Microphone() as source:
        print("వేచి ఉండండి....(Waiting for wake word...)")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio, language='en-US').lower()  # Listen in English
            print("వినినది: (Heard):", text)
            return text
        except sr.UnknownValueError:
            print("నేను ఏమి వినలేదు...(I didn't hear anything)")
            return None
        except sr.RequestError:
            print("క్షమించండి, సర్వర్ అందుబాటులో లేదు.(Sorry, the server is unavailable.)")
            return None

def activate_assistant():
    """Activates the assistant when the wake word "panda" is heard."""
    while True:
        wake_word = listen_for_wake_word()
        if wake_word and "panda" in wake_word:  # Wake word to activate assistant
            speak_telugu("హలో! నేను మీ స్మార్ట్ అసిస్టెంట్ పాండాను.") #Hello! I am panda,your smart assistant
            detect_mood()  # Detect user's mood after wake word
            break
        else:
            print("వేచి ఉండండి....(Waiting for wake word...)")

def detect_mood():
    """Detects the user's mood from their response."""
    speak_telugu("ఈ రోజు మీకు ఎలా ఉంది?")  # Translate: "How are you feeling today?"
    recognizer = sr.Recognizer() #Create recognizer instance.
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("భావన కోసం వినండి...") #Listening for mood...
        audio = recognizer.listen(source)
        mood_text = recognizer.recognize_google(audio, language="te-IN").lower() #Recognize in Telugu
        print(f"వినినది: {mood_text}") #Heard: {mood_text}
        blob = TextBlob(mood_text)
        sentiment = blob.sentiment.polarity

        if sentiment > 0:
            speak_telugu("మీరు సంతోషంగా ఉన్నారు! వినడానికి చాలా సంతోషంగా ఉంది.") #"You sound happy! That's great to hear."
        elif sentiment < 0:
            speak_telugu("మీరు బాధగా ఉన్నారు. అన్నీ బాగానే ఉన్నాయని నేను ఆశిస్తున్నాను.") #"You sound upset. I hope everything is okay."
        else:
            speak_telugu("మీరు సాధారణంగా ఉన్నారు. నేను ఈరోజు మీకు ఎలా సహాయం చేయగలను?") #"You sound neutral. How can I assist you today?"


#----------------- Features from main.py, adapted for Telugu---------------------

# Time function
def get_time(timezone='local'):
    """Gets the current time in the specified timezone (defaults to local)."""
    now = datetime.datetime.now()
    time_text = f"ప్రస్తుతం సమయం {now.strftime('%I:%M %p')}"
    return time_text  # Return the Telugu time string

# Dictionary Meaning function
def get_word_meaning(word):
    """Retrieve the meaning of a word from an online dictionary and speak in Telugu."""
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"  # Free Dictionary API
    try:
        response = requests.get(url)
        data = response.json()
        if "title" in data and data["title"] == "No Definitions Found":
            meaning_text = f"క్షమించండి, {word} అనే పదానికి అర్థం కనుగొనలేకపోయాను."
        else:
            meaning = data[0]["meanings"][0]["definitions"][0]["definition"]
            meaning_text = f"{word} అంటే: {meaning}"

        # Translate and speak the meaning
        speak_telugu(meaning_text)
    except Exception as e:
        speak_telugu(f"క్షమించండి, {word} అర్థాన్ని తెచ్చలేకపోయాను. దోషం: {str(e)}")

# News Function
def get_latest_news():
    """Retrieve the latest news headlines."""
    try:
        # Replace with your NewsAPI key
        api_key = "4a98bf1fd1cb44af93afbd0083773169"  # Replace with your NewsAPI key
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"  # Consider 'in' for India
        response = requests.get(url)
        news_data = response.json()

        if news_data["status"] == "ok":
            articles = news_data["articles"][:3]  # Get the first 3 articles
            news_list = []
            for article in articles:
                title = article["title"]
                description = article["description"]
                # Translate title and description to Telugu
                translated_title = translate_to_telugu(title)
                translated_description = translate_to_telugu(description)
                news_list.append(f"శీర్షిక: {translated_title}\nవివరణ: {translated_description}")

            news_text = "\n\n".join(news_list)
            return news_text
        else:
            return translate_to_telugu("Sorry, I couldn't fetch the latest news at the moment.")
    except Exception as e:
        return translate_to_telugu(f"Error fetching news: {str(e)}")

# Weather Function
def get_weather(location):
    """Fetches the weather for a given location."""
    try:
        # Replace with your OpenWeatherMap API key
        api_key = "1a3a3a439f9a0696398867f0642c7960"  # Replace with your OpenWeatherMap API key
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
        response = requests.get(url)
        data = response.json()

        if data["cod"] != "404":
            main = data["main"]
            weather_description = data["weather"][0]["description"]
            temperature = main["temp"] - 273.15  # Convert from Kelvin to Celsius

            # Translate weather description to Telugu
            translated_description = translate_to_telugu(weather_description)
            weather_text = f"{location} లో వాతావరణం {translated_description} మరియు ఉష్ణోగ్రత {temperature:.2f} డిగ్రీల సెల్సియస్ ఉంది."
            return weather_text
        else:
            return translate_to_telugu(f"Sorry, I couldn't find the weather for {location}.")
    except Exception as e:
        return translate_to_telugu(f"Error fetching weather: {str(e)}")

# Movie Recommendation function
def recommend_movie():
    """Recommends a random movie using TMDb API."""
    try:
        # Replace with your TMDb API key
        api_key = "006b9feaeefc4ac382ecbb5f85450951"  # Replace with your TMDb API key
        url = f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&page=1"
        response = requests.get(url)
        movie_data = response.json()

        if movie_data["results"]:
            movie = random.choice(movie_data["results"])
            movie_title = movie["title"]
            movie_overview = movie["overview"]
            movie_language = movie["original_language"]

            # Translate movie title and overview to Telugu
            translated_title = translate_to_telugu(movie_title)
            translated_overview = translate_to_telugu(movie_overview)

            recommendation_text = f"నేను {translated_title} ({movie_language} లో) చూడమని సిఫార్సు చేస్తున్నాను. ఇక్కడ ఒక చిన్న వివరణ ఉంది: {translated_overview}"
            return recommendation_text
        else:
            return translate_to_telugu("Sorry, I couldn't fetch any movie recommendations at the moment.")
    except Exception as e:
        return translate_to_telugu(f"Sorry, there was an error fetching movie recommendations: {str(e)}")

# Calculation function
def calculate(operation, num1, num2=None):
    """Performs basic mathematical calculations."""
    try:
        num1 = float(num1)
        if num2 is not None:
            num2 = float(num2)
    except ValueError:
        return translate_to_telugu("Error: Please provide valid numbers for the calculation.")

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
            return translate_to_telugu("Error: Division by zero is not allowed.")
    elif operation == "exponentiation" or operation == "power":
        return num1 ** num2
    elif operation == "square root":
        if num1 >= 0:
            return num1 ** 0.5
        else:
            return translate_to_telugu("Error: Cannot take the square root of a negative number.")
    elif operation == "modulus":
        return num1 % num2
    else:
        return translate_to_telugu("Error: Invalid operation. Please use add, subtract, multiply, divide, power, square root, or modulus.")

# Recipe Assistant with Recipe Description function
def get_recipe(ingredients):
    """Finds a recipe based on ingredients."""
    try:
        # Replace with your Spoonacular API key
        api_key = "361ad4728322472aa9e8efbd7a76d52b"  # Replace with your Spoonacular API key
        url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&number=1&apiKey={api_key}"
        response = requests.get(url)

        if response.status_code != 200:
            return translate_to_telugu("Sorry, there was an issue connecting to the recipe service."), None

        data = response.json()

        if not data:
            return translate_to_telugu("Sorry, I couldn't find any recipes with those ingredients."), None

        recipe = data[0]
        recipe_title = recipe.get("title", "Unknown Recipe")
        recipe_id = recipe.get("id", "")
        recipe_url = f"https://spoonacular.com/recipes/{recipe_title.replace(' ', '-')}-{recipe_id}"

        translated_recipe_title = translate_to_telugu(recipe_title)

        return translate_to_telugu(f"I found a recipe: {translated_recipe_title}. Would you like me to open the recipe in your browser?"), recipe_url

    except Exception as e:
        return translate_to_telugu(f"Error fetching recipe: {str(e)}"), None

# Fetch Story function
def fetch_story():
    """Fetches a short story from an API."""
    try:
        response = requests.get("https://shortstories-api.onrender.com/")
        if response.status_code == 200:
            story_data = response.json()
            story = story_data.get("story", "No story available.")
            translated_story = translate_to_telugu(story)
            return translated_story
        else:
            return translate_to_telugu("Failed to fetch a story. Try again later.")
    except Exception as e:
        return translate_to_telugu(f"Error: {e}")

# Tell Story function
def tell_story():
    """Tells a fetched story."""
    story = fetch_story()
    speak_telugu("మీ కోసం ఒక కథ ఉంది.")  # "Here is a story for you."
    speak_telugu(story)

# Reminder function
def set_reminder(reminder_text, reminder_time):
    """Sets a reminder for the specified time."""
    def reminder():
        # Calculate the delay in seconds
        delay = (reminder_time - datetime.datetime.now()).total_seconds()
        if delay > 0:
            print(f"Reminder set for {reminder_time.strftime('%H:%M')}. Waiting for {delay} seconds...")
            time.sleep(delay)
            speak_telugu(f"గుర్తుచేసేది: {reminder_text}")  # Reminder
        else:
            speak_telugu("గుర్తుచేసే సమయం ఇప్పటికే దాటిపోయింది.")  # "The reminder time has already passed."

    # Start the reminder thread
    threading.Thread(target=reminder).start()

# Alarm function
def set_alarm(alarm_time):
    """Sets an alarm for the specified time."""
    def alarm():
        time_to_wait = (alarm_time - datetime.datetime.now()).total_seconds()
        if time_to_wait > 0:
            time.sleep(time_to_wait)
            speak_telugu("మేల్కోండి! మీ అలారం మోగుతోంది.")  # "Wake up! Your alarm is ringing."
        else:
            speak_telugu("అలారం సమయం ఇప్పటికే దాటిపోయింది.")  # "The alarm time has already passed."

    threading.Thread(target=alarm).start()

# Time parsing function
def convert_to_24h(time_input):
    """Converts time input to 24-hour format."""
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
    """Parses time input and converts to 24-hour format."""
    # Always try to convert to 24-hour format
    parsed_time = convert_to_24h(time_input)
    if parsed_time:
        return parsed_time
    else:
        return None

# Book Recommendations function
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
        translated_books = [translate_to_telugu(book) for book in books]
        recommendation = f"{subject} పై కొన్ని సిఫార్సు చేయబడిన పుస్తకాలు ఇక్కడ ఉన్నాయి: " + ", ".join(translated_books) + "." #Translated
    else:
        recommendation = translate_to_telugu("Sorry, I don't have book recommendations for that subject.")

    speak_telugu(recommendation)

def listen_for_subject():
    """Listen for a subject input from the user."""
    speak_telugu("పుస్తకాలు సిఫార్సు చేయడానికి దయచేసి నాకు ఒక విషయం చెప్పండి.")
    with sr.Microphone() as source:
        print("విషయం కోసం వినండి...")
        recognizer = sr.Recognizer()
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio, language="te-IN")
            print(f"మీరు చెప్పింది: {text}")
            return text.lower()
        except sr.UnknownValueError:
            speak_telugu("క్షమించండి, నేను అర్థం చేసుకోలేకపోయాను.")
            return ""
        except sr.RequestError:
            speak_telugu("స్పీచ్ రికగ్నిషన్ సేవలో లోపం ఉంది.")
            return ""

# Run the book recommendation process
def book_recommendation_assistant():
    """Main function to handle book recommendations."""
    subject = listen_for_subject()
    if subject:
        recommend_book(subject)

# Google Search function
def search_google(query):
    """Searches Google using SerpApi."""
    try:
        # Replace with your SerpApi API key
        api_key = "88d9aafd04addd441519fb60e9ba5da26a92c8f630945255f850461346da6a80"  # Replace with your SerpApi API key
        url = f"https://serpapi.com/search?q={query}&api_key={api_key}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            if 'organic_results' in data and len(data['organic_results']) > 0:
                top_result = data['organic_results'][0]
                title = top_result.get('title', 'No title available')
                link = top_result.get('link', 'No link available')
                snippet = top_result.get('snippet', 'No snippet available')

                translated_snippet = translate_to_telugu(snippet)
                return f"{query} గురించి క్లుప్తంగా: {translated_snippet}."
            else:
                return translate_to_telugu("Sorry, I couldn't find any results for that search.")
        else:
            return translate_to_telugu("Sorry, I couldn't fetch the Google search results at the moment.")
    except Exception as e:
        return translate_to_telugu(f"Sorry, there was an error searching Google: {str(e)}")

# Geocoding function
def geocode_location(location):
    """Geocodes a location using OpenStreetMap Nominatim."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": location,
        "format": "json",
        "limit": 1,
        "addressdetails": 1,
        "countrycodes": "IN"
    }
    headers = {
        "User-Agent": "MyMapsAssistant/1.0 (bellamkondamasthanbasha@gmail.com)"  # Replace with your email
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
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

# Routing function
def get_route(start, end):
    """Gets the route between two coordinates using OSRM."""
    url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("routes"):
            distance = data["routes"][0]["distance"] / 1000
            duration = data["routes"][0]["duration"] / 60
            return distance, duration
        else:
            return None
    except (requests.exceptions.RequestException, ValueError, KeyError) as e:
        print(f"Error fetching route data: {e}")
        return None

# Navigation function
def navigate_to():
    """Navigates to a specified location."""
    speak_telugu("మీరు ఎక్కడికి వెళ్లాలనుకుంటున్నారు?")
    destination = listen_telugu()
    if not destination:
        speak_telugu("క్షమించండి, నేను అర్థం చేసుకోలేకపోయాను. దయచేసి మళ్లీ ప్రయత్నించండి.")
        return

    destination_coords = geocode_location(destination)
    if not destination_coords:
        speak_telugu(f"క్షమించండి, నేను '{destination}' అనే స్థానాన్ని కనుగొనలేకపోయాను. దయచేసి వేరే పేరుతో మళ్లీ ప్రయత్నించండి.")
        return

    speak_telugu("మీరు ఎక్కడ నుండి బయలుదేరుతున్నారు?")
    start = listen_telugu()
    if not start:
        speak_telugu("క్షమించండి, నేను అర్థం చేసుకోలేకపోయాను. దయచేసి మళ్లీ ప్రయత్నించండి.")
        return

    start_coords = geocode_location(start)
    if not start_coords:
        speak_telugu(f"క్షమించండి, నేను '{start}' అనే స్థానాన్ని కనుగొనలేకపోయాను. దయచేసి వేరే పేరుతో మళ్లీ ప్రయత్నించండి.")
        return

    route = get_route(start_coords, destination_coords)
    if route:
        distance, duration = route
        translated_destination = translate_to_telugu(destination)
        speak_telugu(f"{translated_destination} కు దూరం {distance:.2f} కిలోమీటర్లు, మరియు ఇది సుమారుగా {duration:.2f} నిమిషాలు పడుతుంది.")

        url = f"https://www.openstreetmap.org/directions?route={start_coords[0]}%2C{start_coords[1]}%3B{destination_coords[0]}%2C{destination_coords[1]}"
        webbrowser.open(url)
    else:
        speak_telugu("క్షమించండి, నేను మార్గాన్ని లెక్కించలేకపోయాను. దయచేసి మీ స్థానాలను తనిఖీ చేసి మళ్లీ ప్రయత్నించండి.")

# Distance calculation function
def calculate_distance():
    """Calculates the distance between two locations."""
    speak_telugu("మూలం స్థానం ఏమిటి?")
    origin = listen_telugu()
    if not origin:
        speak_telugu("క్షమించండి, నేను అర్థం చేసుకోలేకపోయాను. దయచేసి మళ్లీ ప్రయత్నించండి.")
        return

    speak_telugu("గమ్యస్థానం ఏమిటి?")
    destination = listen_telugu()
    if not destination:
        speak_telugu("క్షమించండి, నేను అర్థం చేసుకోలేకపోయాను. దయచేసి మళ్లీ ప్రయత్నించండి.")
        return

    origin_coords = geocode_location(origin)
    if not origin_coords:
        speak_telugu(f"క్షమించండి, నేను '{origin}' అనే స్థానాన్ని కనుగొనలేకపోయాను. దయచేసి వేరే పేరుతో మళ్లీ ప్రయత్నించండి.")
        return

    destination_coords = geocode_location(destination)
    if not destination_coords:
        speak_telugu(f"క్షమించండి, నేను '{destination}' అనే స్థానాన్ని కనుగొనలేకపోయాను. దయచేసి వేరే పేరుతో మళ్లీ ప్రయత్నించండి.")
        return

    route = get_route(origin_coords, destination_coords)
    if route:
        distance, duration = route
        translated_origin = translate_to_telugu(origin)
        translated_destination = translate_to_telugu(destination)

        speak_telugu(f"{translated_origin} మరియు {translated_destination} మధ్య దూరం {distance:.2f} కిలోమీటర్లు, మరియు ఇది సుమారుగా {duration:.2f} నిమిషాలు పడుతుంది.")
    else:
        speak_telugu("క్షమించండి, నేను దూరాన్ని లెక్కించలేకపోయాను. దయచేసి మీ స్థానాలను తనిఖీ చేసి మళ్లీ ప్రయత్నించండి.")

def should_stop():
    return os.path.exists("stop_flag.txt") 

#----------------- Main Loop ---------------------

# Smart Assistant Main Loop
def process_commands():
    """Processes user commands after the assistant is activated, looping until the user says 'stop'."""
    speak_telugu("నేను మీ కోసం ఏమి చేయగలను?")  # "What can I do for you?"

    recognizer = sr.Recognizer()  # Create a new recognizer instance

    while True:  # Loop indefinitely until the user says stop

        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=2)

            print("ఆదేశం కోసం వినండి...")  # "Listening for command..."
            try:
                audio = recognizer.listen(source, timeout=10)
                text2 = recognizer.recognize_google(audio, language="te-IN").lower()
                print(f"వినినది: {text2}")

                # Append user command to conversation file
                with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                    f.write(f"User: {text2}\n")

                # Check for the stop word (ensure it's translated and flexible)
                if "ఆపు" in text2 or "నిలిపివేయి" in text2 or "చాలు" in text2:  # "stop," "halt," "enough" (flexible stopping)
                    speak_telugu("సరే, నేను విడిచిపెడుతున్నాను. ధన్యవాదాలు!")  #"Okay, I'm stopping. Thank you!"
                    break  # Exit the loop

                # --- Command processing logic (rest of the code) ---
                # Song
                if "పాట" in text2 or "సాంగ్" in text2:
                    speak_telugu("మీరు ఏ పాటను ప్లే చేయాలనుకుంటున్నారు?")
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write("Assistant: మీరు ఏ పాటను ప్లే చేయాలనుకుంటున్నారు?\n")

                    with sr.Microphone() as source:
                        recognizer.adjust_for_ambient_noise(source, duration=2)
                        print("పాట పేరు కోసం వినండి...")
                        audio = recognizer.listen(source)
                        song_name = recognizer.recognize_google(audio, language="te-IN").lower()
                        print(f"వినినది: {song_name}")
                        with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                            f.write(f"User: {song_name}\n")
                    speak_telugu(f"నేను {song_name} ప్లే చేస్తున్నాను")
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write(f"Assistant: నేను {song_name} ప్లే చేస్తున్నాను\n")
                    kit.playonyt(song_name)

                # Date
                elif "తేదీ" in text2 or "ఈరోజు" in text2:
                    current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
                    translated_date = translate_to_telugu(current_date)
                    speak_telugu(f"ఈరోజు తేదీ {translated_date}")
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write(f"Assistant: ఈరోజు తేదీ {translated_date}\n")

                # Time
                elif "సమయం" in text2:
                    current_time = get_time()
                    speak_telugu(current_time)
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write(f"Assistant: {current_time}\n")

                 # Details/Info
                elif "సమాచారం" in text2 or "గురించి చెప్పు" in text2 or "వివరణ" in text2:
                    speak_telugu("మీకు ఏ అంశం గురించి సమాచారం కావాలో చెప్పండి?")
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write("Assistant: మీకు ఏ అంశం గురించి సమాచారం కావాలో చెప్పండి?\n")

                    with sr.Microphone() as source:
                        recognizer.adjust_for_ambient_noise(source, duration=2)
                        print("అంశం కోసం వినండి...")
                        audio = recognizer.listen(source)
                        infor = recognizer.recognize_google(audio, language="te-IN").lower()
                        print(f"శోధిస్తున్నది: {infor}")
                        with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                            f.write(f"User: {infor}\n")

                    speak_telugu(f"{infor} కోసం శోధిస్తున్నాను")
                    url = f"https://te.wikipedia.org/wiki/{infor.replace(' ', '_')}"

                    speak_telugu(f"{infor} గురించి వికీపీడియాలో సమాచారం దొరికింది.")

                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write(f"Assistant: {infor} గురించి వికీపీడియాలో సమాచారం దొరికింది.\n")

                    print(f"తెరుచుకుంటుంది: {url}")
                    webbrowser.open(url)

                # Meaning
                elif "అర్థం" in text2 or "వివరణ" in text2 or "అంటే ఏమిటి" in text2:
                    speak_telugu("మీకు ఏ పదం యొక్క అర్ధం కావాలో చెప్పండి?")
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write("Assistant: మీకు ఏ పదం యొక్క అర్ధం కావాలో చెప్పండి?\n")

                    with sr.Microphone() as source:
                        recognizer.adjust_for_ambient_noise(source, duration=2)
                        print("పదం కోసం వినండి...")
                        audio = recognizer.listen(source)
                        word = recognizer.recognize_google(audio, language="te-IN").lower()
                        print(f"వినినది: {word}")
                        with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                            f.write(f"User: {word}\n")

                    get_word_meaning(word)  # This now speaks in Telugu

                # News
                elif "వార్తలు" in text2 or "హెడ్లైన్స్" in text2:
                    speak_telugu("తాజా వార్తలు ఇక్కడ ఉన్నాయి:")
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write("Assistant: తాజా వార్తలు ఇక్కడ ఉన్నాయి:\n")
                    news = get_latest_news()
                    speak_telugu(news)
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write(f"Assistant: {news}\n")

                # Joke
                elif "జోక్" in text2 or "హాస్యం" in text2:
                    speak_telugu("మీ కోసం ఒక జోక్ ఇక్కడ ఉంది!")
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write("Assistant: మీ కోసం ఒక జోక్ ఇక్కడ ఉంది!\n")

                    def get_joke():
                        try:
                            response = requests.get("https://official-joke-api.appspot.com/random_joke")
                            joke = response.json()
                            setup = joke['setup']
                            punchline = joke['punchline']

                            # Translate joke text to Telugu
                            setup_te = translate_to_telugu(setup)
                            punchline_te = translate_to_telugu(punchline)

                            return f"{setup_te} {punchline_te}"

                        except Exception as e:
                             return "క్షమించండి, నేను జోక్ తీసుకురాలేకపోతున్నాను."# Translate "Sorry, I couldn't get a joke at the moment."
                    joke = get_joke()
                    speak_telugu(joke)
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write(f"Assistant: {joke}\n")

                #Open Application
                elif "తెరువు" in text2 or "ఓపెన్" in text2:
                   app_name = text2.replace("తెరువు", "").replace("ఓపెన్", "").strip()
                   translated_app_name = translate_to_telugu(app_name)
                   speak_telugu(f"{translated_app_name} తెరుస్తున్నాను...") # Opening
                   with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                      f.write(f"Assistant: {translated_app_name} తెరుస్తున్నాను...\n")
                   if os.name == 'nt':
                       if "కాలిక్యులేటర్" in app_name or "గణితయంత్రి" in app_name:  # Calculator
                           subprocess.Popen("C:\\Windows\\System32\\calc.exe")
                       elif "క్రోమ్" in app_name or "chrome" in app_name: # Chrome
                           subprocess.Popen(["C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"])
                       elif "వర్డ్" in app_name or "word" in app_name:  # MS Word
                           subprocess.Popen("C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE")
                       elif "ఎక్సెల్" in app_name or "excel" in app_name:  # MS Excel
                           subprocess.Popen("C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE")
                       elif "పవర్ పాయింట్" in app_name or "powerpoint" in app_name:  # MS Powerpoint
                           subprocess.Popen("C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE")
                       else:
                           speak_telugu("క్షమించండి, ఆ అప్లికేషన్‌ను ఎలా తెరవాలో నాకు తెలియదు.") #"Sorry, I don't know how to open that app."
                           with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                              f.write("Assistant: క్షమించండి, ఆ అప్లికేషన్‌ను ఎలా తెరవాలో నాకు తెలియదు.\n") #"Assistant: Sorry, I don't know how to open that app.\n"
                   else:
                       speak_telugu("క్షమించండి, ఈ సిస్టమ్‍పై అప్లికేషన్‌లను తెరవలేను.") #"Sorry, I cannot open applications on this system."
                       with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                            f.write("Assistant: క్షమించండి, ఈ సిస్టమ్‍పై అప్లికేషన్‌లను తెరవలేను.\n") #"Assistant: Sorry, I cannot open applications on this system.\n"

                # Weather
                elif "వాతావరణం" in text2 or "క్లైమేట్" in text2 or "వెదర్" in text2:
                    speak_telugu("మీరు ఏ ప్రదేశం కోసం వాతావరణాన్ని తెలుసుకోవాలనుకుంటున్నారు?") # "Please tell me the location for the weather."
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write("Assistant: మీరు ఏ ప్రదేశం కోసం వాతావరణాన్ని తెలుసుకోవాలనుకుంటున్నారు?\n") #f.write("Assistant: Please tell me the location for the weather.\n")
                    location = listen_telugu()
                    if location:
                        weather_report = get_weather(location)
                        speak_telugu(weather_report)
                        with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                            f.write(f"Assistant: {weather_report}\n")

                # YouTube
                elif "ప్లే" in text2 and "వీడియో" in text2:  # "Play" and "video"
                    speak_telugu("మీరు యూట్యూబ్‌లో ఏ వీడియోను ప్లే చేయాలనుకుంటున్నారు?") #"What video would you like to play on YouTube?"
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write("Assistant: మీరు యూట్యూబ్‌లో ఏ వీడియోను ప్లే చేయాలనుకుంటున్నారు?\n") #"Assistant: What video would you like to play on YouTube?\n"

                    with sr.Microphone() as source:
                        recognizer.adjust_for_ambient_noise(source, duration=2)
                        print("వీడియో పేరు కోసం వినండి...")# Listening for the video name..."
                        audio = recognizer.listen(source)
                        video_name = recognizer.recognize_google(audio, language="te-IN").lower()
                        print(f"వినినది: {video_name}")#Heard: {video_name}
                        with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                            f.write(f"User: {video_name}\n")

                    speak_telugu(f"నేను {video_name} యూట్యూబ్‌లో ప్లే చేస్తున్నాను.") #f"Playing {video_name} on YouTube."
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write(f"Assistant: నేను {video_name} యూట్యూబ్‌లో ప్లే చేస్తున్నాను.\n")#f"Assistant: Playing {video_name} on YouTube.\n"

                    kit.playonyt(video_name)

                # Movie
                elif "సినిమా" in text2 or "మూవీ" in text2 or "సిఫార్సు" in text2: # Corrected and added "recommendation"
                    speak_telugu("నేను ఒక సినిమా సిఫార్సు చేస్తాను.") #"Let me recommend a movie for you."
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write("Assistant: నేను ఒక సినిమా సిఫార్సు చేస్తాను.\n") #"Assistant: Let me recommend a movie for you.\n"
                    recommendation = recommend_movie()
                    speak_telugu(recommendation)
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write(f"Assistant: {recommendation}\n")

                # Calculation
                elif "లెక్కింపు" in text2 or "లెక్కలు" in text2 or "గణితం" in text2: # "calculation" or "maths"

                    speak_telugu("ఖచ్చితంగా, మనం కొన్ని లెక్కలు చేద్దాం. మీరు ఏ ఆపరేషన్ చేయాలనుకుంటున్నారు? (కలపడం, తీసివేయడం, గుణించడం, భాగించడం, పవర్, స్క్వేర్ రూట్, మాడ్యులస్)") #Translated

                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write("Assistant: ఖచ్చితంగా, మనం కొన్ని లెక్కలు చేద్దాం. మీరు ఏ ఆపరేషన్ చేయాలనుకుంటున్నారు? (కలపడం, తీసివేయడం, గుణించడం, భాగించడం, పవర్, స్క్వేర్ రూట్, మాడ్యులస్)\n")

                    with sr.Microphone() as source:
                        recognizer.adjust_for_ambient_noise(source, duration=2)
                        print("ఆపరేషన్ కోసం వినండి...") #Listening for operation..."
                        audio = recognizer.listen(source)
                        operation = recognizer.recognize_google(audio, language="te-IN").lower() #Recongnize operation in telugu
                        print(f"వినినది: {operation}")#Heard: {operation}
                        with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                            f.write(f"User: {operation}\n")
                     #Translate operation to english
                    operation_english = None
                    if "కలపడం" in operation:
                        operation_english = "addition"
                    elif "తీసివేయడం" in operation:
                        operation_english = "subtract"
                    elif "గుణించడం" in operation:
                        operation_english = "multiply"
                    elif "భాగించడం" in operation:
                        operation_english = "divide"
                    elif "పవర్" in operation:
                        operation_english = "power"
                    elif "రూట్" in operation:
                        operation_english = "square root"
                    elif "మాడ్యులస్" in operation:
                        operation_english = "modulus"

                    if operation_english not in ["addition", "subtract", "multiply", "divide","power","square root","modulus"]:
                         speak_telugu("క్షమించండి, నేను కలపడం, తీసివేయడం, గుణించడం లేదా భాగించడం వంటి కార్యకలాపాలను మాత్రమే నిర్వహించగలను.")
                         with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                            f.write("క్షమించండి, నేను కలపడం, తీసివేయడం, గుణించడం లేదా భాగించడం వంటి కార్యకలాపాలను మాత్రమే నిర్వహించగలను.\n")
                         continue

                    speak_telugu("మొదటి సంఖ్యను చెప్పండి.")
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write("సహాయకుడు: దయచేసి మొదటి సంఖ్యను చెప్పండి.\n")
                    with sr.Microphone() as source:
                         recognizer.adjust_for_ambient_noise(source, duration=2)
                         print("మొదటి సంఖ్య కోసం వినండి...")
                         audio = recognizer.listen(source)
                         num1 = recognizer.recognize_google(audio, language="te-IN")
                         print(f"వినినది: {num1}")
                         with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                            f.write(f"వినియోగదారుడు: {num1}\n")
                    speak_telugu("దయచేసి రెండవ సంఖ్యను చెప్పండి.")
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write("సహాయకుడు: దయచేసి రెండవ సంఖ్యను చెప్పండి.\n")
                    with sr.Microphone() as source:
                         recognizer.adjust_for_ambient_noise(source, duration=2)
                         print("రెండవ సంఖ్య కోసం వినండి...")
                         audio = recognizer.listen(source)
                         num2 = recognizer.recognize_google(audio, language="te-IN")
                         print(f"వినినది: {num2}")
                         with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                            f.write(f"వినియోగదారుడు: {num2}\n")
                     # Handle any invalid inputs for numbers
                    try:
                        num1 = float(num1)
                        num2 = float(num2)
                    except ValueError:
                        speak_telugu("క్షమించండి, నేను చెల్లుబాటు అయ్యే సంఖ్యలను గ్రహించలేదు. దయచేసి చెల్లుబాటు అయ్యే సంఖ్యలతో మళ్ళీ ప్రయత్నించండి.")
                        with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                            f.write("సహాయకుడు: క్షమించండి, నేను చెల్లుబాటు అయ్యే సంఖ్యలను గ్రహించలేదు. దయచేసి చెల్లుబాటు అయ్యే సంఖ్యలతో మళ్ళీ ప్రయత్నించండి.\n")
                        continue

                    result = calculate(operation_english, num1, num2)
                    speak_telugu(f"ఫలితం {result}")
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write(f"సహాయకుడు: ఫలితం {result}\n")

                # Recipe
                elif "రెసిపీ" in text2 or "వంట" in text2:
                    speak_telugu("మీ దగ్గర ఉన్న పదార్థాలను చెప్పండి.")
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write("Assistant: మీ దగ్గర ఉన్న పదార్థాలను చెప్పండి.\n")

                    ingredients = listen_telugu()
                    if ingredients:
                        with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                            f.write(f"User: {ingredients}\n")

                        recipe_result, recipe_url = get_recipe(ingredients)
                        speak_telugu(recipe_result)
                        with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                            f.write(f"Assistant: {recipe_result}\n")
                        if recipe_url:
                            speak_telugu("వంటకం తెరవడానికి 'అవును' అని చెప్పండి లేదా రద్దు చేయడానికి 'వద్దు' అని చెప్పండి.")
                            with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                                f.write("Assistant: వంటకం తెరవడానికి 'అవును' అని చెప్పండి లేదా రద్దు చేయడానికి 'వద్దు' అని చెప్పండి.\n")
                            response = listen_telugu()
                            if response and ("అవును" in response or "yes" in response):
                                webbrowser.open(recipe_url)
                                speak_telugu("మీ బ్రౌజర్‌లో వంటకం తెరువబడుతోంది.")
                                with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                                    f.write("Assistant: మీ బ్రౌజర్‌లో వంటకం తెరువబడుతోంది.\n")
                            else:
                                speak_telugu("సరే, నేను వంటకం తెరవను.")
                                with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                                    f.write("Assistant: సరే, నేను వంటకం తెరవను.\n")

                #Story
                elif "కథ" in text2:
                    tell_story()
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                       f.write("Assistant: మీ కోసం ఒక కథ ఉంది.\n")

                #Alaram
                elif "అలారం" in text2:
                    speak_telugu("నేను ఎప్పుడు అలారం సెట్ చేయాలి? దయచేసి సమయం చెప్పండి.")
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write("Assistant: నేను ఎప్పుడు అలారం సెట్ చేయాలి? దయచేసి సమయం చెప్పండి.\n")
                    time_input = listen_telugu()
                    if time_input:
                        with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                            f.write(f"User: {time_input}\n")
                        parsed_time = parse_time(time_input)
                        if parsed_time:
                            hours, minutes = parsed_time
                            now = datetime.datetime.now()
                            alarm_time = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
                            if alarm_time < now:
                                alarm_time += datetime.timedelta(days=1)
                            set_alarm(alarm_time)
                            speak_telugu(f"{alarm_time.strftime('%H:%M')} గంటలకు అలారం సెట్ చేయబడింది.")
                            with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                                f.write(f"Assistant: {alarm_time.strftime('%H:%M')} గంటలకు అలారం సెట్ చేయబడింది.\n")
                        else:
                            speak_telugu("క్షమించండి, సమయం నాకు అర్థం కాలేదు.")
                            with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                                f.write("Assistant: క్షమించండి, సమయం నాకు అర్థం కాలేదు.\n")

                #reminder
                elif "గుర్తుచేయి" in text2 or "reminder" in text2:  # Added English
                    speak_telugu("నేను మీకు ఏమి గుర్తుచేయాలి?")
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write("Assistant: నేను మీకు ఏమి గుర్తుచేయాలి?\n")

                    reminder_text = listen_telugu()

                    if reminder_text:
                        with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                            f.write(f"User: {reminder_text}\n")
                        speak_telugu("నేను మీకు ఎప్పుడు గుర్తుచేయాలి?")
                        with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                            f.write("Assistant: నేను మీకు ఎప్పుడు గుర్తుచేయాలి?\n")
                        time_input = listen_telugu()

                        if time_input:
                            with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                                f.write(f"User: {time_input}\n")

                            parsed_time = parse_time(time_input)
                            if parsed_time:
                                now = datetime.datetime.now()
                                reminder_time = now.replace(hour=parsed_time[0], minute=parsed_time[1], second=0, microsecond=0)
                                if reminder_time < now:
                                    reminder_time += datetime.timedelta(days=1)

                                set_reminder(reminder_text, reminder_time)
                                speak_telugu(f"{reminder_time.strftime('%H:%M')} గంటలకు మీకు గుర్తుచేయబడుతుంది.")
                                with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                                    f.write(f"Assistant: {reminder_time.strftime('%H:%M')} గంటలకు మీకు గుర్తుచేయబడుతుంది.\n")
                            else:
                                speak_telugu("క్షమించండి, నాకు సమయం అర్థం కాలేదు.")
                                with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                                    f.write("Assistant: క్షమించండి, నాకు సమయం అర్థం కాలేదు.\n")
                #book recomendation
                elif "పుస్తకం" in text2:
                    book_recommendation_assistant()
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write("Assistant: కొన్ని పుస్తక సిఫార్సులు ఇక్కడ ఉన్నాయి.\n")

                #search
                elif "శోధించు" in text2 or "వెతుకు" in text2 or "గూగుల్" in text2:
                    speak_telugu("మీరు ఏమి శోధించాలనుకుంటున్నారు?")
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write("Assistant: మీరు ఏమి శోధించాలనుకుంటున్నారు?\n")

                    query = listen_telugu()
                    if query:
                        with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                            f.write(f"User: {query}\n")

                        result = search_google(query)
                        speak_telugu(result)
                        with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                            f.write(f"Assistant: {result}\n")

                #Navigation
                elif "మార్గం" in text2 or "దారి" in text2 or "navigate" in text2:
                    navigate_to()
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write("Assistant: నిర్దేశించిన స్థానానికి మార్గనిర్దేశం చేస్తోంది.\n")
                #Distance calculation
                elif "దూరం" in text2:
                    calculate_distance()
                    with open(CONVERSATION_FILE, "a", encoding="utf-8") as f:
                        f.write("సహాయకుడు: రెండు ప్రదేశాల మధ్య దూరాన్ని లెక్కిస్తోంది.\n")

                # Default
                else:
                   speak_telugu("క్షమించండి, నేను అర్థం చేసుకోలేకపోయాను.")

            except sr.WaitTimeoutError:
                print("గడువు ముగిసింది: ఏమీ వినబడలేదు.(Timeout: No speech detected.)")
                speak_telugu("క్షమించండి, ఏమీ వినబడలేదు. దయచేసి మళ్లీ ప్రయత్నించండి.")

            except sr.UnknownValueError:
                print("క్షమించండి, నాకు అది వినబడలేదు.(Sorry, I didn't catch that.)")
                speak_telugu("క్షమించండి, నాకు అది వినబడలేదు. దయచేసి మళ్లీ చెప్పండి.")

            except Exception as e:
                print(f"ఒక లోపం సంభవించింది: {e}")
                speak_telugu("క్షమించండి, ఏదో తప్పు జరిగింది. దయచేసి మళ్లీ ప్రయత్నించండి.")

def main():
    #activate_assistant()
    process_commands()

# Start the assistant
main()