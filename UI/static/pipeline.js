var hourly = false
// Function to fetch weather data from the API
async function fetchWeatherData() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/weather');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
        return null;
    }
}

async function fetchHourlyData(date){
    try {
        const response = await fetch(`http://127.0.0.1:5000/api/weather/hourly?date=${date}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
        return null;
    }
}

// Function to create HTML content from the data
function createWeatherHtml(data) {
    let htmlContent = '<table border="1"><tr><th>Date</th><th>Max Temp (F)</th><th>Min Temp (F)</th><th>Precipitation (in)</th><th>Weather</th><th>Hourly Data</th></tr>';
    for (const [date, values] of Object.entries(data)) {
        htmlContent += `<tr>
            <td>${date}</td>
            <td>${values[0]}</td>
            <td>${values[1]}</td>
            <td>${values[2]}</td>
            <td>${values[3]}</td>
            <td><button onclick="handleHourlyData('${date}')">Click for Hourly Data</button></td>
        </tr>`;
    }
    htmlContent += '</table>';
    return htmlContent;
}

// Function to create HTML content for hourly data
function createHourlyHtml(date, data) {
    let htmlContent = `<h3>Hourly Data for ${date}</h3>`
    htmlContent += '<table border="1"><tr><th>Hour</th><th>Temperature (F)</th><th>Real Feel (F)</th> <th>Humidity (%) </th> <th>Dew Point</th> <th>Wind Speed (mph)</th> <th>Precipitation (in)</th> <th>Visibility (mi)</th> <th>Pressure (Pa)</th></tr>';
    for (const [time, values] of Object.entries(data)) {
        htmlContent += `<tr>
            <td>${values['tim']}</td>
            <td>${values['temp']}</td>
            <td>${values['real_feel']}</td>
            <td>${values['humidity']}</td>
            <td>${values['dew_point']}</td>
            <td>${values['wind_speed']}</td>
            <td>${values['precip']}</td>
            <td>${values['visibility']}</td>
            <td>${values['pressure']}</td>
        </tr>`;
    }
    htmlContent += '</table>';
    htmlContent += '<button onclick="showWeatherData()">Back</button>'
    return htmlContent;
}

// Function to handle displaying hourly data
async function handleHourlyData(date) {
    const hourlyWeatherData = await fetchHourlyData(date);
    if (hourlyWeatherData) {
        const weatherDataElement = document.getElementById('weather-data');
        const hourlyDataElement = document.getElementById('hourly-data');
        
        if (weatherDataElement && hourlyDataElement) {
            // Hide weather data
            weatherDataElement.style.display = 'none';
            
            // Show hourly data
            hourlyDataElement.innerHTML = createHourlyHtml(date, hourlyWeatherData);
            hourlyDataElement.style.display = 'block';
        }
    }
}

function showWeatherData() {
    const weatherDataElement = document.getElementById('weather-data');
    const hourlyDataElement = document.getElementById('hourly-data');
    
    if (weatherDataElement && hourlyDataElement) {
        // Show weather data
        weatherDataElement.style.display = 'block';
        
        // Hide hourly data
        hourlyDataElement.style.display = 'none';
    }
}

// Main function to fetch data and update the UI
async function main() {
    const weatherData = await fetchWeatherData();
    if (weatherData) {
        const weatherDataElement = document.getElementById('weather-data');
        if (weatherDataElement) {
            weatherDataElement.innerHTML = createWeatherHtml(weatherData);
        }
    }
}

// Call the main function
main();