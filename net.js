
const extractData = (data) => {
    return data.body.map(entry => {
        const location = entry.place.location;
        const measures = entry.measures;
        let temperature = null;
        let humidity = null;
        let rain_live = null;
        let rain_60min = null;
        let rain_24h = null;

        // Loop through each measure to find temperature and rain data
        Object.keys(measures).forEach(key => {
            const measure = measures[key];
            if (measure.type && measure.type.includes('temperature')) {
                // Assume the temperature and humidity are always in the same measure
                const tempData = Object.values(measure.res)[0]; // Get the latest reading
                temperature = tempData[0];
                humidity = tempData[1];
            }
            if (measure.rain_live !== undefined) {
                rain_live = measure.rain_live;
                rain_60min = measure.rain_60min;
                rain_24h = measure.rain_24h;
            }
        });

        return { location, temperature, humidity, rain_live, rain_60min, rain_24h };
    });
};

const result = extractData(jsonData);
console.log(result);