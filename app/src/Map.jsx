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
  zoom: 11,
  pitch: 50,
  bearing: -20
};

const MAP_STYLE = 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json';

// Fetch airports and ports from OpenStreetMap
async function fetchInfrastructure(bbox) {
  const [south, west, north, east] = bbox;

  const query = `
    [out:json][timeout:30];
    (
      // Airports
      way["aeroway"="aerodrome"](${south},${west},${north},${east});
      relation["aeroway"="aerodrome"](${south},${west},${north},${east});

      // Airport terminals
      way["aeroway"="terminal"](${south},${west},${north},${east});

      // Ports and harbors
      way["harbour"="yes"](${south},${west},${north},${east});
      way["landuse"="port"](${south},${west},${north},${east});
      relation["landuse"="port"](${south},${west},${north},${east});

      // Marinas
      way["leisure"="marina"](${south},${west},${north},${east});
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
          // Determine type and height for infrastructure
          const aeroway = element.tags?.aeroway;
          const landuse = element.tags?.landuse;
          const leisure = element.tags?.leisure;
          const harbour = element.tags?.harbour;

          let height = 15; // Default height for infrastructure
          let name = element.tags?.name || 'Infrastructure';
          let type = 'infrastructure';

          if (aeroway === 'aerodrome') {
            height = 5; // Airports are relatively flat
            name = element.tags?.name || 'Airport';
            type = 'airport';
          } else if (aeroway === 'terminal') {
            height = 20; // Airport terminals
            name = element.tags?.name || 'Terminal';
            type = 'terminal';
          } else if (landuse === 'port' || harbour === 'yes') {
            height = 10; // Ports are relatively flat
            name = element.tags?.name || 'Port';
            type = 'port';
          } else if (leisure === 'marina') {
            height = 8;
            name = element.tags?.name || 'Marina';
            type = 'marina';
          }

          buildings.push({
            polygon,
            height,
            name,
            type
          });
        }
      }
    });

    return buildings;
  } catch (error) {
    console.error('Error fetching infrastructure from Overpass API:', error);
    return [];
  }
}

function MapComponent() {
  const [buildings, setBuildings] = useState([]);

  useEffect(() => {
    // Fetch airports and ports across greater LA area
    const greaterLA = [33.7, -118.7, 34.35, -118.15];

    fetchInfrastructure(greaterLA)
      .then(data => {
        setBuildings(data);
        console.log(`Loaded ${data.length} airports, ports, and marinas from LA area`);
      })
      .catch(err => {
        console.error('Error fetching infrastructure:', err);
      });
  }, []);

  const layers = [
    new PolygonLayer({
      id: 'infrastructure',
      data: buildings,
      extruded: true,
      wireframe: false,
      getPolygon: d => d.polygon,
      getElevation: d => d.height,
      getFillColor: d => {
        // Color by infrastructure type
        switch (d.type) {
          case 'airport':
          case 'terminal':
            return [100, 150, 255]; // Blue for airports
          case 'port':
            return [255, 100, 100]; // Red for ports
          case 'marina':
            return [100, 255, 150]; // Green for marinas
          default:
            return [150, 150, 150]; // Gray for other
        }
      },
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
  ];

  return (
    <DeckGL
      initialViewState={INITIAL_VIEW_STATE}
      controller={true}
      style={{ width: '100vw', height: '100vh' }}
      layers={layers}
      getTooltip={({ object }) =>
        object && {
          html: `<div style="background: rgba(0,0,0,0.8); padding: 8px 12px; border-radius: 4px;">
                  <strong>${object.name}</strong><br/>
                  Type: ${object.type.charAt(0).toUpperCase() + object.type.slice(1)}
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
