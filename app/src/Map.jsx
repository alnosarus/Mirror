import DeckGL from '@deck.gl/react';
import { Map } from 'react-map-gl/maplibre';
import { GeoJsonLayer } from '@deck.gl/layers';
import { useState, useEffect } from 'react';
import 'maplibre-gl/dist/maplibre-gl.css';

// Suppress WebGL context errors in console (known DeckGL + React 19 issue)
const originalError = console.error;
console.error = (...args) => {
  if (typeof args[0] === 'string' && args[0].includes('maxTextureDimension2D')) {
    return;
  }
  originalError.apply(console, args);
};

const INITIAL_VIEW_STATE = {
  longitude: -118.2437,
  latitude: 34.0522,
  zoom: 11,
  pitch: 50,
  bearing: -20
};

const MAP_STYLE = 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json';

function MapComponent() {
  const [airportData, setAirportData] = useState(null);
  const [portData, setPortData] = useState(null);
  const [warehouseData, setWarehouseData] = useState(null);

  useEffect(() => {
    // Load airport infrastructure from PostgreSQL API
    fetch('http://localhost:5001/api/airports')
      .then(res => res.json())
      .then(data => {
        setAirportData(data);
        console.log(`Loaded ${data.features.length} airport infrastructure features from PostgreSQL`);
      })
      .catch(err => console.error('Error loading airport data:', err));

    // Load port infrastructure from PostgreSQL API
    fetch('http://localhost:5001/api/ports')
      .then(res => res.json())
      .then(data => {
        setPortData(data);
        console.log(`Loaded ${data.features.length} port infrastructure features from PostgreSQL`);
      })
      .catch(err => console.error('Error loading port data:', err));

    // Load warehouses from PostgreSQL API
    fetch('http://localhost:5001/api/warehouses')
      .then(res => res.json())
      .then(data => {
        setWarehouseData(data);
        console.log(`Loaded ${data.features.length} warehouse buildings from PostgreSQL`);
      })
      .catch(err => console.error('Error loading warehouse data:', err));
  }, []);

  const layers = [
    // Airport infrastructure layer
    airportData && new GeoJsonLayer({
      id: 'airports',
      data: airportData,
      filled: true,
      extruded: true,
      wireframe: false,
      getElevation: f => {
        // Different heights for different airport classes
        const cls = f.properties.class;
        if (cls === 'airport' || cls === 'international_airport') return 8;
        if (cls === 'terminal') return 15;
        if (cls === 'helipad' || cls === 'heliport') return 3;
        return 5;
      },
      getFillColor: [90, 100, 120, 200], // Dark blue-grey for airports
      getLineColor: [60, 70, 90],
      lineWidthMinPixels: 1,
      material: {
        ambient: 0.4,
        diffuse: 0.7,
        shininess: 32,
        specularColor: [60, 60, 60]
      },
      pickable: true,
      autoHighlight: true,
      highlightColor: [255, 200, 0, 200]
    }),

    // Port infrastructure layer
    portData && new GeoJsonLayer({
      id: 'ports',
      data: portData,
      filled: true,
      extruded: true,
      wireframe: false,
      getElevation: f => {
        // Ports and piers are relatively flat
        const subtype = f.properties.subtype;
        if (subtype === 'quay') return 8;
        if (subtype === 'pier') return 5;
        return 3;
      },
      getFillColor: f => {
        const subtype = f.properties.subtype;
        if (subtype === 'quay') return [120, 90, 90, 200]; // Dark red-grey for quays
        if (subtype === 'pier') return [100, 110, 100, 200]; // Dark grey-green for piers
        return [100, 100, 100, 200];
      },
      getLineColor: [70, 70, 70],
      lineWidthMinPixels: 1,
      material: {
        ambient: 0.4,
        diffuse: 0.7,
        shininess: 32,
        specularColor: [60, 60, 60]
      },
      pickable: true,
      autoHighlight: true,
      highlightColor: [255, 200, 0, 200]
    }),

    // Warehouse buildings layer
    warehouseData && new GeoJsonLayer({
      id: 'warehouses',
      data: warehouseData,
      filled: true,
      extruded: true,
      wireframe: false,
      getElevation: f => {
        // Use height from data, or default based on floors
        if (f.properties.height && f.properties.height > 0) {
          return f.properties.height;
        }
        if (f.properties.num_floors && f.properties.num_floors > 0) {
          return f.properties.num_floors * 4; // Assume 4m per floor
        }
        return 8; // Default warehouse height
      },
      getFillColor: [140, 120, 90, 200], // Brown/tan for warehouses
      getLineColor: [100, 85, 65],
      lineWidthMinPixels: 1,
      material: {
        ambient: 0.4,
        diffuse: 0.7,
        shininess: 32,
        specularColor: [60, 60, 60]
      },
      pickable: true,
      autoHighlight: true,
      highlightColor: [255, 200, 0, 200]
    })
  ].filter(Boolean);

  return (
    <DeckGL
      initialViewState={INITIAL_VIEW_STATE}
      controller={true}
      style={{ width: '100vw', height: '100vh' }}
      layers={layers}
      getTooltip={({ object }) =>
        object && object.properties && {
          html: `<div style="background: rgba(0,0,0,0.8); padding: 8px 12px; border-radius: 4px;">
                  <strong>${object.properties.name || 'Unnamed'}</strong><br/>
                  ${object.properties.subtype ? `Type: ${object.properties.subtype}` : ''}
                  ${object.properties.class ? `<br/>Class: ${object.properties.class}` : ''}
                </div>`,
          style: {
            fontSize: '0.8em',
            color: 'white'
          }
        }
      }
    >
      <Map
        reuseMaps
        mapStyle={MAP_STYLE}
      />
    </DeckGL>
  );
}

export default MapComponent;
