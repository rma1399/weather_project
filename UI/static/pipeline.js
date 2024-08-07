
/**
 * Watches for updates on the month and year change when the go button is being pressed
 */
document.addEventListener("DOMContentLoaded", function() {
    const monthSelect = document.getElementById("month-select");
    const yearSelect = document.getElementById("year-select");
    const calendarContainer = document.getElementById("calendar-container");

    const currentYear = new Date().getFullYear();
    for (let i = currentYear; i <= currentYear + 5; i++) {
        const option = document.createElement("option");
        option.value = i;
        option.textContent = i;
        if (i === currentYear) option.selected = true;
        yearSelect.appendChild(option);
    }

    document.getElementById("generate-calendar").addEventListener("click", generateCalendar);

    /**
     * grabs month and year values and creates a calendar based on the month and year chosen. It then
     * populates the calendar with dates and if available, data
     */
    async function generateCalendar() {
        calendarContainer.innerHTML = "";

        const selectedMonth = parseInt(monthSelect.value);
        const selectedYear = parseInt(yearSelect.value);

        const firstDay = new Date(selectedYear, selectedMonth, 1).getDay();
        const daysInMonth = new Date(selectedYear, selectedMonth + 1, 0).getDate();

        for (let i = 0; i < firstDay; i++) {
            const emptyCell = document.createElement("div");
            emptyCell.classList.add("calendar-day", "empty");
            calendarContainer.appendChild(emptyCell);
        }

        for (let day = 1; day <= daysInMonth; day++) {
            const weatherData = await fetchWeatherData(selectedMonth,selectedYear, day);
            const dayCell = document.createElement("div");
            dayCell.classList.add("calendar-day");
            dayCell.innerHTML = `<div class="calendar-date">${day}</div>`
            if (weatherData){
                dateString = formatDate(selectedYear,selectedMonth+1, day);
                const [maxTemp, minTemp, precipitation, weather] = weatherData[dateString];
                dayCell.innerHTML = `
                <div class="calendar-date">${day}</div>
                <div class="weather-details">
                    <div><strong>HI (F):</strong> ${maxTemp}</div>
                    <div><strong>LOW (F):</strong> ${minTemp}</div>
                    <div><strong>Precipitation (in):</strong> ${precipitation}</div>
                    <div><strong>Weather:</strong> ${weather}</div>
                    <button onclick="handleHourlyData('${dateString}')">Click for Hourly Data</button>
                </div>
            `;
            console.log(dateString)
            }
            calendarContainer.appendChild(dayCell);
        }
    }

    generateCalendar();
});


/**
 * this function formats a date from a year month and day in a simple manner
 * @param {*} year 
 * @param {*} month 
 * @param {*} day 
 * @returns a formatted date
 */
function formatDate(year, month, day) {
    // Create a new Date object with the provided year, month, and day
    const date = new Date(year, month - 1, day); // Month is 0-indexed, so subtract 1

    // Get the year, month, and day as strings
    const yyyy = date.getFullYear();
    const mm = String(date.getMonth() + 1).padStart(2, '0'); // Add 1 because months are zero-indexed
    const dd = String(date.getDate()).padStart(2, '0');

    // Combine them into the desired format
    return `${yyyy}-${mm}-${dd}`;
}

/**
 * Pulls the weather data from my API, checks if it exists and catches any erros
 * @param {*} month 
 * @param {*} year 
 * @param {*} day 
 * @returns weather data or nothing
 */
async function fetchWeatherData(month, year, day) {
    try {
        const response = await fetch(`http://127.0.0.1:5000/api/weather?month=${month}&year=${year}&day=${day}`);
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

/**
 * Pulls data from my API with a specific date that pulls direct hourly 
 * @param {*} date 
 * @returns data or nothing
 */
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

/**
 * 
 * @param {*} date 
 * @param {*} data 
 * @returns 
 */
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

/**
 * 
 * @param {*} date 
 */
async function handleHourlyData(date) {
    const hourlyWeatherData = await fetchHourlyData(date);
    if (hourlyWeatherData) {
        const hourlyDataElement = document.getElementById('hourly-data');
        const calendarContainer = document.getElementById('calendar-container'); 
        
        if (hourlyDataElement && calendarContainer) { 
            calendarContainer.style.display = 'none'; 
            hourlyDataElement.innerHTML = createHourlyHtml(date, hourlyWeatherData);
            hourlyDataElement.style.display = 'block';
        }
    }
}

/**
 * 
 */
function showWeatherData() {
    const hourlyDataElement = document.getElementById('hourly-data');
    const calendarContainer = document.getElementById('calendar-container'); 
    
    if (hourlyDataElement && calendarContainer) { 
        calendarContainer.style.display = 'block'; 
        calendarContainer.style.display = '';
        hourlyDataElement.style.display = 'none';
    }
}

/**Main function to fetch data and update the UI*/
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