import datetime as dt
import requests
import random
import uuid
import json
import time
import logging
import requests
import json
import time
from kafka import KafkaProducer




def create_weather_response_dict(api_key: str='ac7fb3b580d92745f1a5a8c5efcae46a', base_url: str="http://api.openweathermap.org/data/2.5/weather?", cities: list=None) -> dict:
    """
    Creates the results JSON from the OpenWeatherMap API call
    """
    

    if cities is None:
        # If no list of cities is provided, use a default list
        cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville", "San Francisco", "Indianapolis", "Columbus", "Fort Worth", "Charlotte", "Seattle", "Denver", "El Paso", "Detroit", "Boston", "Memphis", "Nashville", "Portland", "Oklahoma City", "Las Vegas", "Baltimore", "Louisville", "Milwaukee", "Albuquerque", "Tucson", "Fresno", "Sacramento", "Kansas City", "Long Beach", "Mesa", "Atlanta", "Colorado Springs", "Raleigh", "Omaha", "Miami", "Oakland", "Minneapolis", "Tulsa", "Wichita", "New Orleans", "Arlington", "Cleveland", "Bakersfield", "Tampa", "Aurora", "Honolulu", "Anaheim", "Santa Ana", "Corpus Christi", "Riverside", "St. Louis", "Lexington", "Stockton", "Pittsburgh", "Anchorage", "Cincinnati", "Henderson", "Greensboro", "Plano", "Newark", "Toledo", "Lincoln", "Orlando", "Chula Vista", "Jersey City", "Chandler", "Fort Wayne", "Buffalo", "Durham", "St. Petersburg", "Irvine", "Laredo", "Lubbock", "Madison", "Gilbert", "Norfolk", "Reno", "Winston-Salem", "Glendale", "Hialeah", "Garland", "Scottsdale", "Irving", "Chesapeake", "North Las Vegas", "Fremont", "Baton Rouge", "Richmond", "Boise", "San Bernardino", "Spokane", "Birmingham", "Modesto", "Des Moines", "Rochester", "Tacoma", "Fontana", "Oxnard", "Moreno Valley", "Fayetteville", "Aurora", "Glendale", "Yonkers", "Huntington Beach", "Montgomery", "Amarillo", "Little Rock", "Akron", "Augusta", "Grand Rapids", "Mobile", "Salt Lake City", "Huntsville", "Tallahassee", "Grand Prairie", "Overland Park", "Knoxville", "Worcester", "Brownsville", "Newport News", "Santa Clarita", "Port St. Lucie", "Providence", "Fort Lauderdale", "Chattanooga", "Tempe", "Oceanside", "Garden Grove", "Rancho Cucamonga", "Cape Coral", "Santa Rosa", "Vancouver", "Sioux Falls", "Peoria", "Ontario", "Jackson", "Elk Grove", "Springfield", "Pembroke Pines", "Salem", "Eugene", "Corona", "Pasadena", "Hayward", "Joliet", "Palmdale", "Salinas", "Springfield", "Hollywood", "Paterson", "Kansas City", "Sunrise", "Pomona", "McAllen", "Escondido", "Naperville", "Bridgeport", "Savannah", "Orange", "Pasadena", "Alexandria", "Mesquite", "Syracuse", "Lancaster", "Dayton", "Hayward", "Salinas", "Frisco", "Yonkers", "Hollywood", "Paterson", "Kansas City", "Sunrise", "Pomona", "McAllen", "Escondido", "Naperville", "Bridgeport", "Savannah", "Orange", "Pasadena", "Alexandria", "Mesquite", "Syracuse", "Lancaster", "Dayton", "Fullerton", "McKinney", "Cary", "Cedar Rapids", "Huntsville", "Visalia", "Killeen", "Fargo", "West Valley City", "Columbia", "Downey", "Costa Mesa", "Inglewood", "Miami Gardens", "Waterbury", "Norwalk", "Carlsbad", "Fairfield", "Cambridge", "Westminster", "Round Rock", "Clearwater", "Beaumont", "Peoria", "Evansville", "Bellevue", "Antioch", "Murrieta", "South Bend", "Richardson", "Daly City", "Centennial", "Palm Bay", "Billings", "Erie", "Green Bay", "West Jordan", "Broken Arrow", "Davenport", "Santa Maria", "El Cajon", "San Mateo", "Lewisville", "Rialto", "Elgin", "Lakeland", "Tyler", "Las Cruces", "South Fulton", "Chula Vista", "Newark", "San Buenaventura", "Norwalk", "San Marcos", "Hesperia", "Allen", "Tyler", "Las Cruces", "South Fulton", "Chula Vista", "Newark", "San Buenaventura", "Norwalk", "San Marcos", "Hesperia", "Allen"]

    city = random.choice(cities)
    url = f"{base_url}q={city}&appid={api_key}"
    
    response = requests.get(url).json()
    
    return response



def kelvin_to_celsius(kelvin):
     celsius = kelvin - 273.15
     return celsius


def dataFormatting(response):
    data={}
    
    data["name"] = response['name']

    data["lon"] = response['coord']['lon']
    data["lat"] = response['coord']['lat']
    data["weather_main"] = response['weather'][0]['main']
    data["weather_description"] = response['weather'][0]['description']
    data["temp_min"] = kelvin_to_celsius(response['main']['temp_min'])
    data["temp_max  "] = kelvin_to_celsius(response['main']['temp_max'])
    data["temp_kelvin"] = response['main']['temp']
    data["temp_celsius"] =kelvin_to_celsius(data["temp_kelvin"])
    data["feels_like_kelvin"] = response['main']['feels_like']
    data["feels_like_celsius"]  = kelvin_to_celsius(data["feels_like_kelvin"])   
    data["pressure"] = response['main']['pressure']
    data["wind_speed"] = response['wind']['speed']
    data["humidity"]= response['main'] ['humidity']
    
    
    return data


weather_data = create_weather_response_dict()
formated_data=dataFormatting(weather_data)

print(formated_data)

def create_kafka_producer():
    """
    Creates the Kafka producer object
    """

    return KafkaProducer(bootstrap_servers=['kafka1:19092'])


def start_streaming():
    """
    Writes the API data every 10 seconds to Kafka topic random_names
    """
    producer = create_kafka_producer()
    results = create_weather_response_dict()
    kafka_data = dataFormatting(results)    

    end_time = time.time() + 120 # the script will run for 2 minutes
    while True:
        if time.time() > end_time:
            break

        producer.send("weather_data", json.dumps(kafka_data).encode('utf-8'))
        time.sleep(10)


if __name__ == "__main__":
    start_streaming()
