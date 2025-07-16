// Weather Widget para Scriptable iOS
// Basado en Universal Weather Bot
// Actualización automática cada hora

// Configuración de APIs - REEMPLAZA CON TUS CLAVES
const API_KEYS = {
    weatherapi: "YOUR_WEATHERAPI_KEY_HERE", // Obtén gratis en weatherapi.com
    tomorrow: "YOUR_TOMORROW_KEY_HERE", // Opcional - tomorrow.io
    visualcrossing: "YOUR_VISUALCROSSING_KEY_HERE" // Obtén gratis en visualcrossing.com
};

const DEFAULT_CITY = "Montevideo"; // Ciudad por defecto

// Configuración del widget
const WIDGET_CONFIG = {
    backgroundColor: new Color("#1a1a2e"),
    titleColor: new Color("#ffffff"),
    textColor: new Color("#e0e0e0"),
    accentColor: new Color("#4fc3f7"),
    warningColor: new Color("#ff9800"),
    dangerColor: new Color("#f44336")
};

// Función principal
async function createWidget() {
    const widget = new ListWidget();

    try {
        // Obtener datos del clima
        const weatherData = await getWeatherData();

        if (!weatherData) {
            return createErrorWidget("No se pudieron obtener datos del clima");
        }

        // Configurar el widget
        setupWidget(widget, weatherData);

    } catch (error) {
        console.error("Error:", error);
        return createErrorWidget("Error al obtener datos: " + error.message);
    }

    return widget;
}

// Obtener datos del clima de múltiples fuentes
async function getWeatherData() {
    const sources = [];

    // Intentar obtener datos de múltiples fuentes
    try {
        const weatherApiData = await fetchWeatherAPI();
        if (weatherApiData) sources.push(weatherApiData);
    } catch (e) {
        console.log("WeatherAPI falló:", e.message);
    }

    try {
        const metNoData = await fetchMETNorway();
        if (metNoData) sources.push(metNoData);
    } catch (e) {
        console.log("MET Norway falló:", e.message);
    }

    try {
        const visualCrossingData = await fetchVisualCrossing();
        if (visualCrossingData) sources.push(visualCrossingData);
    } catch (e) {
        console.log("Visual Crossing falló:", e.message);
    }

    if (sources.length === 0) {
        throw new Error("No se pudieron obtener datos de ninguna fuente");
    }

    // Agregar datos de múltiples fuentes
    return aggregateWeatherData(sources);
}

// WeatherAPI
async function fetchWeatherAPI() {
    const url = `https://api.weatherapi.com/v1/forecast.json?key=${API_KEYS.weatherapi}&q=${DEFAULT_CITY}&days=1&aqi=no&alerts=no`;

    const request = new Request(url);
    const response = await request.loadJSON();

    if (!response || !response.current) {
        throw new Error("Respuesta inválida de WeatherAPI");
    }

    const current = response.current;
    const forecast = response.forecast.forecastday[0];
    const hourly = forecast.hour;

    // Obtener próximas 12 horas
    const now = new Date();
    const currentHour = now.getHours();
    const nextHours = hourly.slice(currentHour, currentHour + 12);

    return {
        source: "WeatherAPI",
        city: response.location.name,
        country: response.location.country,
        current: {
            temp: current.temp_c,
            condition: current.condition.text,
            humidity: current.humidity,
            windKph: current.wind_kph,
            feelsLike: current.feelslike_c
        },
        hourly: nextHours.map(h => ({
            time: h.time,
            temp: h.temp_c,
            precip: h.precip_mm,
            windKph: h.wind_kph
        }))
    };
}

// MET Norway (gratuito, no requiere clave)
async function fetchMETNorway() {
    // Primero obtener coordenadas de la ciudad
    const coords = await getCityCoordinates(DEFAULT_CITY);
    if (!coords) throw new Error("No se pudieron obtener coordenadas");

    const url = `https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=${coords.lat}&lon=${coords.lon}`;

    const request = new Request(url);
    request.headers = {
        'User-Agent': 'WeatherWidget/1.0 iOS'
    };

    const response = await request.loadJSON();

    if (!response || !response.properties) {
        throw new Error("Respuesta inválida de MET Norway");
    }

    const timeseries = response.properties.timeseries;
    const current = timeseries[0].data.instant.details;

    return {
        source: "MET Norway",
        city: DEFAULT_CITY,
        country: "Unknown",
        current: {
            temp: current.air_temperature,
            condition: "Unknown",
            humidity: current.relative_humidity,
            windKph: (current.wind_speed || 0) * 3.6,
            feelsLike: current.air_temperature
        },
        hourly: timeseries.slice(0, 12).map(t => ({
            time: t.time,
            temp: t.data.instant.details.air_temperature,
            precip: t.data.next_1_hours?.details?.precipitation_amount || 0,
            windKph: (t.data.instant.details.wind_speed || 0) * 3.6
        }))
    };
}

// Visual Crossing
async function fetchVisualCrossing() {
    const url = `https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/${DEFAULT_CITY}?unitGroup=metric&key=${API_KEYS.visualcrossing}&contentType=json&include=hours`;

    const request = new Request(url);
    const response = await request.loadJSON();

    if (!response || !response.currentConditions) {
        throw new Error("Respuesta inválida de Visual Crossing");
    }

    const current = response.currentConditions;
    const today = response.days[0];

    return {
        source: "Visual Crossing",
        city: response.resolvedAddress.split(',')[0],
        country: "Unknown",
        current: {
            temp: current.temp,
            condition: current.conditions,
            humidity: current.humidity,
            windKph: current.windspeed,
            feelsLike: current.feelslike
        },
        hourly: today.hours.slice(0, 12).map(h => ({
            time: `${today.datetime}T${h.datetime}`,
            temp: h.temp,
            precip: h.precip || 0,
            windKph: h.windspeed
        }))
    };
}

// Obtener coordenadas de una ciudad (para MET Norway)
async function getCityCoordinates(city) {
    try {
        // Usar un servicio gratuito de geocodificación
        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(city)}&limit=1`;

        const request = new Request(url);
        request.headers = {
            'User-Agent': 'WeatherWidget/1.0 iOS'
        };

        const response = await request.loadJSON();

        if (response && response.length > 0) {
            return {
                lat: parseFloat(response[0].lat),
                lon: parseFloat(response[0].lon)
            };
        }

        return null;
    } catch (e) {
        console.log("Error obteniendo coordenadas:", e.message);
        return null;
    }
}

// Agregar datos de múltiples fuentes
function aggregateWeatherData(sources) {
    if (sources.length === 0) return null;

    // Usar la primera fuente como base
    const base = sources[0];

    // Pesos para cada fuente (igual que el bot)
    const weights = {
        "WeatherAPI": 0.4,
        "MET Norway": 0.3,
        "Visual Crossing": 0.3
    };

    // Agregar datos actuales
    let tempSum = 0, windSum = 0, humiditySum = 0, weightSum = 0;

    sources.forEach(source => {
        const weight = weights[source.source] || 0.2;
        tempSum += source.current.temp * weight;
        windSum += source.current.windKph * weight;
        humiditySum += source.current.humidity * weight;
        weightSum += weight;
    });

    const avgTemp = tempSum / weightSum;
    const avgWind = windSum / weightSum;
    const avgHumidity = humiditySum / weightSum;

    // Agregar datos horarios
    const hourlyData = [];
    const maxHours = Math.min(...sources.map(s => s.hourly.length));

    for (let i = 0; i < maxHours; i++) {
        let hourTempSum = 0, hourPrecipSum = 0, hourWindSum = 0, hourWeightSum = 0;

        sources.forEach(source => {
            if (source.hourly[i]) {
                const weight = weights[source.source] || 0.2;
                hourTempSum += source.hourly[i].temp * weight;
                hourPrecipSum += source.hourly[i].precip * weight;
                hourWindSum += source.hourly[i].windKph * weight;
                hourWeightSum += weight;
            }
        });

        if (hourWeightSum > 0) {
            hourlyData.push({
                time: sources[0].hourly[i].time,
                temp_c: hourTempSum / hourWeightSum,
                precip_mm: hourPrecipSum / hourWeightSum,
                wind_kph: hourWindSum / hourWeightSum
            });
        }
    }

    // Calcular estadísticas del día
    const temps = hourlyData.map(h => h.temp_c);
    const precips = hourlyData.map(h => h.precip_mm);
    const winds = hourlyData.map(h => h.wind_kph);

    const minTemp = Math.min(...temps);
    const maxTemp = Math.max(...temps);
    const totalPrecip = precips.reduce((a, b) => a + b, 0);
    const avgWindDay = winds.reduce((a, b) => a + b, 0) / winds.length;
    const maxPrecip = Math.max(...precips);

    return {
        city: base.city,
        country: base.country,
        sources: sources.map(s => s.source).join(", "),
        current: {
            temp: avgTemp,
            condition: base.current.condition,
            humidity: avgHumidity,
            windKph: avgWind,
            feelsLike: avgTemp // Simplificado
        },
        today: {
            minTemp: minTemp,
            maxTemp: maxTemp,
            totalPrecip: totalPrecip,
            avgWind: avgWindDay,
            maxPrecip: maxPrecip
        },
        nextHours: hourlyData.slice(0, 6)
    };
}



// Configurar el widget con diseño horizontal en 2 columnas
function setupWidget(widget, data) {
    widget.backgroundColor = WIDGET_CONFIG.backgroundColor;
    widget.setPadding(10, 10, 10, 10);

    // Header compacto con temperatura y ciudad
    const headerStack = widget.addStack();
    headerStack.layoutHorizontally();
    headerStack.centerAlignContent();

    // Emoji + Temperatura grande
    const weatherEmoji = getWeatherEmoji(data.current.temp, data.today.maxPrecip, data.current.windKph / 3.6);
    const mainTempText = headerStack.addText(`${weatherEmoji} ${Math.round(data.current.temp)}°C`);
    mainTempText.font = Font.boldSystemFont(21);
    mainTempText.textColor = WIDGET_CONFIG.titleColor;

    headerStack.addSpacer();

    // Ciudad y hora
    const locationStack = headerStack.addStack();
    locationStack.layoutVertically();

    const cityText = locationStack.addText(data.city);
    cityText.font = Font.systemFont(11);
    cityText.textColor = WIDGET_CONFIG.textColor;
    cityText.textOpacity = 0.8;

    const updateTime = new Date().toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit'
    });
    const timeText = locationStack.addText(`🔄 ${updateTime}`);
    timeText.font = Font.systemFont(9);
    timeText.textColor = WIDGET_CONFIG.textColor;
    timeText.textOpacity = 0.6;

    widget.addSpacer(8);

    // Layout principal en 2 columnas
    const mainStack = widget.addStack();
    mainStack.layoutHorizontally();

    // COLUMNA IZQUIERDA - Resumen del día
    const leftColumn = mainStack.addStack();
    leftColumn.layoutVertically();
    leftColumn.size = new Size(160, 0);

    const summaryTitle = leftColumn.addText("📊 Resumen del día:");
    summaryTitle.font = Font.boldSystemFont(13);
    summaryTitle.textColor = WIDGET_CONFIG.accentColor;

    leftColumn.addSpacer(2);

    // Temperatura min/max
    const tempEmoji = getTempColorEmoji(data.today.maxTemp);
    const tempSummary = leftColumn.addText(`${tempEmoji} ${Math.round(data.today.minTemp)}°C - ${Math.round(data.today.maxTemp)}°C`);
    tempSummary.font = Font.systemFont(12);
    tempSummary.textColor = WIDGET_CONFIG.textColor;

    // Precipitación
    let precipText;
    if (data.today.totalPrecip > 0) {
        const rainProb = getRainProbability(data.today.maxPrecip);
        precipText = `🌧️ ${data.today.totalPrecip.toFixed(1)}mm (${rainProb}%)`;
    } else {
        precipText = "☀️ Sin lluvia";
    }

    const precipSummary = leftColumn.addText(precipText);
    precipSummary.font = Font.systemFont(12);
    precipSummary.textColor = WIDGET_CONFIG.textColor;

    // Viento
    const windDesc = getWindDescription(data.today.avgWind);
    const windSummary = leftColumn.addText(`💨 ${Math.round(data.today.avgWind)}km/h (${windDesc})`);
    windSummary.font = Font.systemFont(12);
    windSummary.textColor = WIDGET_CONFIG.textColor;

    // Humedad (nueva información)
    const humidityText = leftColumn.addText(`💧 ${Math.round(data.current.humidity)}% humedad`);
    humidityText.font = Font.systemFont(12);
    humidityText.textColor = WIDGET_CONFIG.textColor;

    // Sensación térmica (nueva información)
    const feelsLikeText = leftColumn.addText(`🌡️ Sensación ${Math.round(data.current.feelsLike)}°C`);
    feelsLikeText.font = Font.systemFont(12);
    feelsLikeText.textColor = WIDGET_CONFIG.textColor;

    // Separador vertical
    mainStack.addSpacer(10);

    // COLUMNA DERECHA - Próximas horas
    const rightColumn = mainStack.addStack();
    rightColumn.layoutVertically();

    const hoursTitle = rightColumn.addText("⏰ Próximas horas:");
    hoursTitle.font = Font.boldSystemFont(13);
    hoursTitle.textColor = WIDGET_CONFIG.accentColor;

    rightColumn.addSpacer(2);

    // Mostrar próximas 4 horas (solo futuras)
    const now = new Date();
    const currentHour = now.getHours();
    let futureHours = 0;

    for (let i = 0; i < data.nextHours.length && futureHours < 4; i++) {
        const hour = data.nextHours[i];
        const hourTime = new Date(hour.time).getHours();

        // Solo mostrar horas futuras
        if (hourTime > currentHour) {
            const hourEmoji = getWeatherEmoji(hour.temp_c, hour.precip_mm, hour.wind_kph / 3.6);
            const hourText = rightColumn.addText(`${hourTime}:00 ${hourEmoji} ${Math.round(hour.temp_c)}°C`);
            hourText.font = Font.systemFont(11);
            hourText.textColor = WIDGET_CONFIG.textColor;
            hourText.textOpacity = 0.9;
            futureHours++;
        }
    }

    widget.addSpacer(6);

    // Recomendación en la parte inferior (una sola línea)
    const recommendations = getRecommendations(data);
    if (recommendations.length > 0) {
        const recStack = widget.addStack();
        recStack.layoutHorizontally();
        recStack.centerAlignContent();

        const recText = recStack.addText(`💡 ${recommendations[0]}`);
        recText.font = Font.systemFont(10);
        recText.textColor = WIDGET_CONFIG.accentColor;
        recText.textOpacity = 0.9;
    }
}

// Funciones auxiliares (copiadas del bot de Python)
function getWeatherEmoji(temp, precipitation, windSpeed) {
    if (precipitation > 5.0) {
        if (temp < 2) return "🌨️";
        else if (precipitation > 10) return "⛈️";
        else return "🌧️";
    } else if (precipitation > 0.5) {
        return "🌦️";
    } else if (windSpeed > 8) {
        return "💨";
    } else if (temp > 25) {
        return "☀️";
    } else if (temp > 15) {
        return "🌤️";
    } else if (temp > 5) {
        return "⛅";
    } else {
        return "🌫️";
    }
}

function getTempColorEmoji(temp) {
    if (temp >= 30) return "🔴";
    else if (temp >= 25) return "🟠";
    else if (temp >= 20) return "🟡";
    else if (temp >= 15) return "🟢";
    else if (temp >= 10) return "🔵";
    else if (temp >= 5) return "🟣";
    else return "⚪";
}

function getRainProbability(precipitation) {
    if (precipitation === 0) return 0;
    else if (precipitation < 0.1) return 10;
    else if (precipitation < 0.5) return 30;
    else if (precipitation < 2.0) return 60;
    else if (precipitation < 5.0) return 80;
    else return 95;
}

function getWindDescription(windKph) {
    if (windKph < 7) return "Calma";
    else if (windKph < 18) return "Brisa ligera";
    else if (windKph < 29) return "Brisa moderada";
    else if (windKph < 43) return "Viento fuerte";
    else return "Viento muy fuerte";
}

function getRecommendations(data) {
    const recommendations = [];

    if (data.today.maxTemp > 25) {
        recommendations.push("☀️ Usa protector solar");
    }
    if (data.today.totalPrecip > 2) {
        recommendations.push("☔ Lleva paraguas");
    }
    if (data.today.avgWind > 29) {
        recommendations.push("💨 Cuidado con el viento");
    }
    if (data.today.minTemp < 10) {
        recommendations.push("🧥 Abrígate bien");
    }

    if (recommendations.length === 0) {
        recommendations.push("😊 ¡Día perfecto!");
    }

    return recommendations;
}

// Widget de error
function createErrorWidget(message) {
    const widget = new ListWidget();
    widget.backgroundColor = WIDGET_CONFIG.backgroundColor;
    widget.setPadding(16, 16, 16, 16);

    const errorText = widget.addText("❌ Error");
    errorText.font = Font.boldSystemFont(16);
    errorText.textColor = WIDGET_CONFIG.dangerColor;

    widget.addSpacer(8);

    const messageText = widget.addText(message);
    messageText.font = Font.systemFont(12);
    messageText.textColor = WIDGET_CONFIG.textColor;

    return widget;
}

// Ejecutar el widget
if (config.runsInWidget) {
    // Ejecutándose como widget
    const widget = await createWidget();
    Script.setWidget(widget);
} else {
    // Ejecutándose en la app (preview)
    const widget = await createWidget();
    widget.presentMedium();
}

Script.complete();