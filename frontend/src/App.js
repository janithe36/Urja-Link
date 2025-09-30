import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
    iconUrl: require('leaflet/dist/images/marker-icon.png'),
    shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// MODIFIED: Paste the accurate coordinates you copied from Google Maps here.
const AIT_PUNE_COORDS = [18.607038213745916, 73.87507577241476]; 

const AnalysisResults = ({ results }) => {
    if (!results || results.error) {
        return <div style={styles.resultsBox}><h3>Error</h3><p>{results?.error || 'Could not load analysis.'}</p></div>;
    }
    return (
        <div style={styles.resultsBox}>
            <h3>Analysis Summary</h3>
            <p><strong>Total Potential:</strong> {results.total_potential_gwh_year} GWh/year</p>
            <ul>
                {results.potential_by_orientation_kwh && Object.entries(results.potential_by_orientation_kwh).map(([key, value]) => (
                    <li key={key}><strong>{key}:</strong> {value.toLocaleString()} kWh</li>
                ))}
            </ul>
        </div>
    );
};

function App() {
    const [analysisData, setAnalysisData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchRooftopData = async () => {
            try {
                const response = await axios.get('http://127.0.0.1:8000/api/analyze-ait-campus/');
                setAnalysisData(response.data);
            } catch (error) {
                setAnalysisData({ error: 'Failed to connect to the backend.' });
            } finally {
                setIsLoading(false);
            }
        };
        fetchRooftopData();
    }, []);

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
            <header style={styles.header}><h1>Urja Link</h1></header>
            <div style={{ flex: 1, position: 'relative' }}>
                <MapContainer center={AIT_PUNE_COORDS} zoom={17} style={{ height: '100%', width: '100%' }}>
                    {/* MODIFIED: This now uses a satellite map layer */}
                    <TileLayer
                        url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                        attribution='Tiles &copy; Esri'
                    />
                    <Marker position={AIT_PUNE_COORDS}><Popup>AIT Pune Campus</Popup></Marker>
                </MapContainer>
                {isLoading ? <div style={styles.resultsBox}><h2>Running AI Analysis...</h2></div> : <AnalysisResults results={analysisData} />}
            </div>
        </div>
    );
}

const styles = {
    header: { padding: '10px', backgroundColor: '#2c3e50', color: 'white', textAlign: 'center' },
    resultsBox: {
        position: 'absolute', top: '10px', right: '10px', zIndex: 1000,
        backgroundColor: 'white', padding: '15px', borderRadius: '5px',
        boxShadow: '0 0 10px rgba(0,0,0,0.5)', maxWidth: '300px',
    }
};

export default App;