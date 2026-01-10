import DeckGL from '@deck.gl/react';
import { Map } from 'react-map-gl/maplibre';
import { PolygonLayer } from '@deck.gl/layers';
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
  zoom: 15,
  pitch: 45,
  bearing: 0
};

const MAP_STYLE = 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json';

// Fetch buildings from OpenStreetMap Overpass API
async function fetchBuildings(bbox) {
  const [south, west, north, east] = bbox;

  const query = `
    [out:json][timeout:25];
    (
      way["building"](${south},${west},${north},${east});
      relation["building"](${south},${west},${north},${east});
    );
    out body;
    >;
    out skel qt;
  `;

  try {
    const response = await fetch('https://overpass-api.de/api/interpreter', {
      method: 'POST',
      body: query
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const text = await response.text();

    // Check if response is JSON
    if (!text.startsWith('{')) {
      console.warn('Overpass API returned non-JSON response, possibly rate limited');
      return [];
    }

    const data = JSON.parse(text);

    // Process OSM data into building polygons
    const nodes = {};
    const buildings = [];

    // First pass: collect all nodes
    data.elements.forEach(element => {
      if (element.type === 'node') {
        nodes[element.id] = [element.lon, element.lat];
      }
    });

    // Second pass: build polygons from ways
    data.elements.forEach(element => {
      if (element.type === 'way' && element.nodes) {
        const polygon = element.nodes
          .map(nodeId => nodes[nodeId])
          .filter(coord => coord !== undefined);

        if (polygon.length >= 3) {
          // Get building height from tags, default to random if not available
          const levels = element.tags?.['building:levels'] || element.tags?.levels;
          const height = element.tags?.height
            ? parseFloat(element.tags.height)
            : levels
              ? parseFloat(levels) * 3.5
              : Math.random() * 50 + 20;

          buildings.push({
            polygon,
            height,
            name: element.tags?.name || 'Building'
          });
        }
      }
    });

    return buildings;
  } catch (error) {
    console.error('Error fetching buildings from Overpass API:', error);
    return [];
  }
}

function MapComponent() {
  const [buildings, setBuildings] = useState([]);

  useEffect(() => {
    // Fetch buildings for downtown LA area
    const bbox = [34.04, -118.26, 34.06, -118.23]; // [south, west, north, east]

    fetchBuildings(bbox)
      .then(data => {
        setBuildings(data);
        console.log(`Loaded ${data.length} buildings from OpenStreetMap`);
      })
      .catch(err => {
        console.error('Error fetching buildings:', err);
      });
  }, []);

  const layers = [
    new PolygonLayer({
      id: 'buildings',
      data: buildings,
      extruded: true,
      wireframe: false,
      getPolygon: d => d.polygon,
      getElevation: d => d.height,
      getFillColor: d => {
        // Color buildings by height
        const heightRatio = Math.min(d.height / 200, 1);
        return [
          74 + heightRatio * 100,
          80 + heightRatio * 120,
          87 + heightRatio * 140
        ];
      },
      material: {
        ambient: 0.35,
        diffuse: 0.6,
        shininess: 32,
        specularColor: [50, 50, 50]
      },
      pickable: true,
      autoHighlight: true,
      highlightColor: [255, 200, 0, 150]
    })
  ];

  return (
    <DeckGL
      initialViewState={INITIAL_VIEW_STATE}
      controller={true}
      style={{ width: '100vw', height: '100vh' }}
      layers={layers}
    >
      <Map
        reuseMaps
        mapStyle={MAP_STYLE}
      />
    </DeckGL>
  );
}

export default MapComponent;
