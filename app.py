from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import requests
import datetime
import os

app = Flask(__name__)

# Configure SQLite database
path = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"+os.path.join(path, 'weather_data2.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)
#db.init_app(app)

# Database model to store weather data
class Weather(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Integer, nullable=False)
    wind_speed = db.Column(db.Float, nullable=False)
    date_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)

@app.route('/', methods=['GET', 'POST'])
def weather2():
    weather_data = None
    error_message = None

    if request.method == 'POST':
        city = request.form['city']
        api_key = '87093c1953a45bfb2301b50b3c15faa9'

        # Get latitude and longitude from the Geocoding API
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
        geo_response = requests.get(geo_url)

        if geo_response.status_code == 200:
            geo_data = geo_response.json()

            if geo_data:  # Check if the list is not empty
                lat = geo_data[0]['lat']
                lon = geo_data[0]['lon']

                # Get weather data using latitude and longitude
                weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
                weather_response = requests.get(weather_url)

                if weather_response.status_code == 200:
                    weather_data = weather_response.json()

                    # Save the weather data to the database
                    new_weather = Weather(
                        city=weather_data['name'],
                        description=weather_data['weather'][0]['description'],
                        temperature=weather_data['main']['temp'],
                        humidity=weather_data['main']['humidity'],
                        wind_speed=weather_data['wind']['speed']
                    )
                    db.session.add(new_weather)
                    db.session.commit()

                else:
                    error_message = "Error fetching weather data. Please try again."
            else:
                error_message = "City not found. Please check the name and try again."
        else:
            error_message = "Error with the geocoding request. Please try again."

    return render_template('weather2.html', weather_data=weather_data, error_mess=error_message)

@app.route('/future_weather', methods=['GET'])
def future_weather():
    future_date = datetime.datetime.utcnow() + datetime.timedelta(weeks=1)
    future_weather_data = Weather.query.filter(Weather.date_time >= future_date).all()
    
    return render_template('weather2.html', future_weather_data=future_weather_data, future_date=future_date)

if __name__ == '__main__':
    # Create the database
    with app.app_context():
        db.create_all()

    app.run(debug=True)
