function(data) {
    const measures = data.measures;
    for (const key in measures) {
        const device = measures[key];
        if (device.type && device.type.includes("temperature")) {
            // Reknar med temperatur alltid er først
            const resKeys = Object.keys(device.res);
            if (resKeys.length > 0) {
                // Satser på første valg i "res" er riktig
                const firstResKey = resKeys[0];
                return device.res[firstResKey][0]; // [0] for å finne først valg, satser på det er temperatur
    }
    // Returnerer null hvis ikkje temperatur er funne
    return null;
}
    }
}