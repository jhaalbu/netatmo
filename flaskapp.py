from flask import Flask, render_template, jsonify
import sqlite3
import folium
from folium.plugins import MarkerCluster

app = Flask(__name__)

def hent_stasjoner():
    """Hent alle værstasjoner fra databasen."""
    conn = sqlite3.connect("weather_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT station_id, latitude, longitude, city, street FROM weather_stations")
    stasjoner = cursor.fetchall()
    conn.close()
    return stasjoner

def hent_nedbor(station_id):
    """Hent nedbørdata for en værstasjon."""
    conn = sqlite3.connect("weather_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT measurement_time, value 
        FROM measurements 
        WHERE station_id = ? AND measurement_type = 'rain_24h' 
        ORDER BY measurement_time DESC
    """, (station_id,))
    nedbor_data = cursor.fetchall()
    conn.close()
    return nedbor_data

@app.route('/')
def index():
    """Generer kart og returner som HTML."""
    stasjoner = hent_stasjoner()
    m = folium.Map(location=[58.5, 8.0], zoom_start=7)
    marker_cluster = MarkerCluster().add_to(m)

    for station_id, lat, lon, city, street in stasjoner:
        popup_content = f"""
            <b>Stasjon:</b> {station_id}<br>
            <b>By:</b> {city}<br>
            <b>Gate:</b> {street}<br>
            <a href='/station/{station_id}'>Se nedbørdata</a>
        """
        folium.Marker(
            location=[lat, lon],
            popup=popup_content,
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(marker_cluster)

    return m._repr_html_()

@app.route('/station/<station_id>')
def station_info(station_id):
    """Side som viser nedbørdata for en stasjon."""
    nedbor_data = hent_nedbor(station_id)
    return jsonify({"station_id": station_id, "rain_data": nedbor_data})

if __name__ == '__main__':
    app.run(debug=True)
