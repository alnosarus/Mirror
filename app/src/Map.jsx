import DeckGL from '@deck.gl/react';
import { Map } from 'react-map-gl/maplibre';
import { GeoJsonLayer, PathLayer } from '@deck.gl/layers';
import { useState, useEffect, useRef, useCallback } from 'react';
import { FlyToInterpolator } from '@deck.gl/core';
import 'maplibre-gl/dist/maplibre-gl.css';
import ChatSidebar from './ChatSidebar';

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
  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);
  const [chatOpen, setChatOpen] = useState(false);
  const [visibleLayers, setVisibleLayers] = useState({
    airports: true,
    ports: true,
    warehouses: true
  });
  const [highlightedFeature, setHighlightedFeature] = useState(null);
  const [routeData, setRouteData] = useState(null);
  const [routeInfo, setRouteInfo] = useState(null);
  const deckRef = useRef(null);

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

  // Handle actions from Claude AI
  const handleChatAction = useCallback((action) => {
    console.log('Executing action:', action);

    switch (action.tool) {
      case 'fly_to_location':
        const { longitude, latitude, zoom = 14, pitch = 50, bearing = 0, duration = 2000 } = action.input;
        setViewState({
          longitude,
          latitude,
          zoom,
          pitch,
          bearing,
          transitionDuration: duration,
          transitionInterpolator: new FlyToInterpolator()
        });
        break;

      case 'filter_infrastructure':
        const newVisibility = {
          airports: action.input.types.includes('airports'),
          ports: action.input.types.includes('ports'),
          warehouses: action.input.types.includes('warehouses')
        };
        setVisibleLayers(newVisibility);
        console.log('Updated layer visibility:', newVisibility);
        break;

      case 'highlight_feature':
        // Find and highlight the feature
        const { name, type } = action.input;
        let data = null;
        if (type === 'airport') data = airportData;
        else if (type === 'port') data = portData;
        else if (type === 'warehouse') data = warehouseData;

        if (data) {
          const feature = data.features.find(f =>
            f.properties.name && f.properties.name.toLowerCase().includes(name.toLowerCase())
          );
          if (feature) {
            setHighlightedFeature(feature.properties.id);
            // Also fly to the feature
            const coords = feature.geometry.coordinates[0][0]; // Get first coordinate of polygon
            setViewState({
              longitude: coords[0],
              latitude: coords[1],
              zoom: 15,
              pitch: 50,
              bearing: 0,
              transitionDuration: 2000,
              transitionInterpolator: new FlyToInterpolator()
            });
          }
        }
        break;

      case 'calculate_route':
        // Calculate route between two points
        const { start, end } = action.input;
        fetch('http://localhost:5001/api/route', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ start, end })
        })
          .then(res => res.json())
          .then(data => {
            if (data.success) {
              setRouteData(data.route.coordinates);
              setRouteInfo({
                distance: data.route.distance_km,
                duration: data.route.duration_minutes,
                trafficDelay: data.route.traffic_delay
              });
              // Fly to show the whole route
              const allCoords = data.route.coordinates;
              const avgLon = allCoords.reduce((sum, c) => sum + c[0], 0) / allCoords.length;
              const avgLat = allCoords.reduce((sum, c) => sum + c[1], 0) / allCoords.length;
              setViewState({
                longitude: avgLon,
                latitude: avgLat,
                zoom: 12,
                pitch: 45,
                bearing: 0,
                transitionDuration: 2000,
                transitionInterpolator: new FlyToInterpolator()
              });
            }
          })
          .catch(err => console.error('Route calculation error:', err));
        break;

      case 'find_nearest':
        // Find nearest infrastructure to a location
        const findLocation = action.input.location;
        const infraType = action.input.infrastructure_type;
        fetch('http://localhost:5001/api/find-nearest', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ location: findLocation, infrastructure_type: infraType })
        })
          .then(res => res.json())
          .then(data => {
            if (data.success) {
              const feature = data.feature;
              // Fly to the nearest feature
              setViewState({
                longitude: feature.coordinates.lon,
                latitude: feature.coordinates.lat,
                zoom: 15,
                pitch: 50,
                bearing: 0,
                transitionDuration: 2000,
                transitionInterpolator: new FlyToInterpolator()
              });
              // Highlight it
              setHighlightedFeature(feature.id);
              console.log(`Found nearest ${infraType}: ${feature.name} (${feature.distance_km} km away)`);
            }
          })
          .catch(err => console.error('Find nearest error:', err));
        break;

      default:
        console.log('Unknown action:', action.tool);
    }
  }, [airportData, portData, warehouseData]);

  const layers = [
    // Airport infrastructure layer
    airportData && visibleLayers.airports && new GeoJsonLayer({
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
      getFillColor: f => {
        // Highlight if this feature is selected
        if (highlightedFeature && f.properties.id === highlightedFeature) {
          return [255, 200, 0, 255];
        }
        return [99, 145, 214, 200]; // Light blue-grey for airports
      },
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
    portData && visibleLayers.ports && new GeoJsonLayer({
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
        // Highlight if this feature is selected
        if (highlightedFeature && f.properties.id === highlightedFeature) {
          return [255, 200, 0, 255];
        }
        const subtype = f.properties.subtype;
        if (subtype === 'quay') return [48, 99, 56, 200]; // Dark red-grey for quays
        if (subtype === 'pier') return [48, 99, 56, 200]; // Dark grey-green for piers
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
    warehouseData && visibleLayers.warehouses && new GeoJsonLayer({
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
      getFillColor: f => {
        // Highlight if this feature is selected
        if (highlightedFeature && f.properties.id === highlightedFeature) {
          return [255, 200, 0, 255];
        }
        return [140, 120, 90, 200]; // Brown/tan for warehouses
      },
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
    }),

    // Route visualization layer
    routeData && new PathLayer({
      id: 'route-layer',
      data: [{ path: routeData }],
      getPath: d => d.path,
      getColor: [255, 100, 50, 255],
      getWidth: 8,
      widthMinPixels: 3,
      widthMaxPixels: 10,
      billboard: false,
      capRounded: true,
      jointRounded: true,
      pickable: false
    })
  ].filter(Boolean);

  return (
    <>
      <DeckGL
        ref={deckRef}
        viewState={viewState}
        onViewStateChange={({ viewState }) => setViewState(viewState)}
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

      <ChatSidebar
        isOpen={chatOpen}
        onToggle={() => setChatOpen(!chatOpen)}
        onAction={handleChatAction}
      />

      {/* Route Info Display */}
      {routeInfo && (
        <div style={{
          position: 'absolute',
          top: '20px',
          left: '20px',
          background: 'rgba(20, 20, 30, 0.95)',
          backdropFilter: 'blur(10px)',
          padding: '16px 20px',
          borderRadius: '8px',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.5)',
          minWidth: '250px',
          zIndex: 100
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '8px'
          }}>
            <h3 style={{
              margin: 0,
              color: 'white',
              fontSize: '16px',
              fontWeight: '600'
            }}>Route Details</h3>
            <button
              onClick={() => { setRouteData(null); setRouteInfo(null); }}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'rgba(255, 255, 255, 0.6)',
                fontSize: '20px',
                cursor: 'pointer',
                padding: '0 4px',
                lineHeight: 1
              }}
            >×</button>
          </div>
          <div style={{
            color: 'rgba(255, 255, 255, 0.9)',
            fontSize: '14px',
            lineHeight: '1.6'
          }}>
            <div style={{ marginBottom: '8px' }}>
              <span style={{ color: 'rgba(255, 255, 255, 0.6)' }}>Distance:</span>{' '}
              <strong>{routeInfo.distance} km</strong> ({(routeInfo.distance * 0.621371).toFixed(2)} mi)
            </div>
            <div style={{ marginBottom: '8px' }}>
              <span style={{ color: 'rgba(255, 255, 255, 0.6)' }}>Duration:</span>{' '}
              <strong>{routeInfo.duration} min</strong>
            </div>
            {routeInfo.trafficDelay > 0 && (
              <div style={{
                color: '#ff6b6b',
                fontSize: '13px'
              }}>
                ⚠️ +{Math.round(routeInfo.trafficDelay / 60)} min traffic delay
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}

export default MapComponent;
