# Routing Feature - TomTom Integration

## Overview

The routing feature allows users to calculate and visualize driving routes between any two points in the Los Angeles area. It uses the TomTom Routing API to provide real-time traffic-aware directions with estimated travel time and distance.

## Features

✅ **Route Calculation** - Get optimal driving routes between two points
✅ **Visual Route Display** - Orange path overlay showing the exact route
✅ **Distance & Time Estimates** - Real-time calculations with traffic data
✅ **Traffic Awareness** - Shows traffic delays when present
✅ **AI Integration** - Natural language routing via Claude agent
✅ **Automatic Camera** - Map automatically frames the entire route

## How It Works

### Backend (Flask API)

**New Endpoint:** `POST /api/route`

**Request Format:**
```json
{
  "start": {
    "lat": 33.9416,
    "lon": -118.4085
  },
  "end": {
    "lat": 33.7545,
    "lon": -118.1933
  }
}
```

**Response Format:**
```json
{
  "success": true,
  "route": {
    "distance": 36230,
    "distance_km": 36.23,
    "distance_miles": 22.51,
    "duration": 1722,
    "duration_minutes": 28.7,
    "traffic_delay": 0,
    "coordinates": [[lon, lat], [lon, lat], ...]
  }
}
```

### Frontend (React)

**New Components:**

1. **Route Layer (PathLayer)**
   - Orange path visualization
   - 8px width (3-10px responsive)
   - Rounded caps and joints
   - Overlays infrastructure layers

2. **Route Info Display**
   - Top-left panel
   - Shows distance (km and miles)
   - Shows duration (minutes)
   - Shows traffic delays
   - Closeable with × button

### AI Agent Integration

**New Tool:** `calculate_route`

Claude can now understand and execute routing requests:

**Example Queries:**
- "Show me the route from LAX to Long Beach Port"
- "How do I get from downtown LA to LAX?"
- "Calculate the route between these two airports"
- "What's the distance from LAX to the Port of LA?"

## Setup Instructions

### 1. Get a TomTom API Key

1. Visit [TomTom Developer Portal](https://developer.tomtom.com/)
2. Sign up for a free account
3. Create a new API key
4. Copy your API key

### 2. Configure Environment

Add your TomTom API key to the `.env` file:

```bash
TOMTOM_API_KEY=your_tomtom_api_key_here
```

### 3. Install Dependencies

The required `requests` library is already installed:

```bash
python3 -m pip install --user -r requirements.txt
```

### 4. Start the Application

```bash
./start.sh
```

The routing feature is now ready to use!

## Usage Examples

### Via Chat Interface

Open the chat (purple button) and try:

**Basic Route:**
```
"Show me the route from LAX to Long Beach Port"
```
→ Map displays orange route line with distance/time info

**Route with Context:**
```
"How do I get to the Port of LA from downtown?"
```
→ Claude calculates coordinates and shows the route

**Multiple Queries:**
```
User: "Take me to LAX"
[Map flies to LAX]
User: "Now show me how to get to Long Beach Port from here"
[Route appears from LAX to port]
```

### Via API (Direct)

```bash
curl -X POST http://localhost:5001/api/route \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"lat": 33.9416, "lon": -118.4085},
    "end": {"lat": 33.7545, "lon": -118.1933}
  }'
```

## Test Results

### LAX to Long Beach Port

- **Distance:** 36.23 km (22.51 miles)
- **Duration:** 28.7 minutes
- **Route Points:** 646 coordinates
- **Traffic:** No delay (current conditions)

### Claude Agent Response

**Input:** "Show me the route from LAX to Long Beach Port"

**Output:**
```json
{
  "text": "Okay, let's calculate a route from LAX to the Long Beach Port:",
  "actions": [{
    "tool": "calculate_route",
    "input": {
      "start": {"lat": 33.9416, "lon": -118.4085},
      "end": {"lat": 33.7545, "lon": -118.1933}
    }
  }]
}
```

## Technical Details

### TomTom API Specifications

**API Version:** v1
**Endpoint:** `https://api.tomtom.com/routing/1/calculateRoute/{locations}/json`

**Parameters Used:**
- `traffic`: true - Include real-time traffic data
- `travelMode`: car - Driving directions
- `key`: Your API key

**Response Fields:**
- `routes[0].summary` - Distance and time summary
- `routes[0].legs[].points` - Route geometry coordinates
- `routes[0].summary.trafficDelayInSeconds` - Current traffic delay

### Route Visualization

**Technology:** DeckGL PathLayer
**Color:** Orange `rgba(255, 100, 50, 255)`
**Width:** 8px (responsive 3-10px)
**Style:** Rounded caps and joints
**Z-Index:** Above infrastructure layers

### Performance

- **API Response Time:** ~500-1000ms
- **Route Points:** 500-1000 coordinates typical
- **Rendering:** GPU-accelerated via WebGL
- **Memory:** Minimal impact (~1-2MB per route)

## API Costs

TomTom offers a **free tier** with:
- **2,500 requests/day** for routing
- No credit card required
- More than enough for development and testing

### Cost Estimates (Paid Plans)

If you exceed free tier:
- ~$0.0005 per route calculation
- ~2,000 routes for $1
- Very affordable for production use

## Error Handling

### No TomTom API Key

**Error Message:**
```json
{
  "error": "TomTom API key not configured",
  "message": "Please add your TomTom API key to the .env file"
}
```

**Solution:** Add `TOMTOM_API_KEY` to `.env` file

### No Route Found

**Error Message:**
```json
{
  "error": "No route found"
}
```

**Causes:**
- Coordinates are too far apart
- Invalid coordinates
- Location not accessible by car

### API Error

**Error Message:**
```json
{
  "error": "Routing service error: [details]"
}
```

**Solutions:**
- Check API key validity
- Verify coordinates are within service area
- Check network connectivity

## Files Modified/Created

### Backend
- ✅ [api_server.py](api_server.py) - Added `/api/route` endpoint
- ✅ [requirements.txt](requirements.txt) - Added `requests==2.31.0`
- ✅ [.env](.env) - Added `TOMTOM_API_KEY`

### Frontend
- ✅ [app/src/Map.jsx](app/src/Map.jsx) - Added route layer & info display
  - PathLayer for route visualization
  - Route info panel component
  - calculate_route action handler

### Configuration
- ✅ [.env.example](.env.example) - Added TomTom key template

### Documentation
- ✅ [ROUTING_FEATURE.md](ROUTING_FEATURE.md) - This file!

## Future Enhancements

Potential improvements:

- [ ] Multiple route options (fastest, shortest, etc.)
- [ ] Turn-by-turn directions
- [ ] Route waypoints (multi-stop routes)
- [ ] Alternative routes display
- [ ] Traffic layer visualization
- [ ] Save/share routes
- [ ] Export routes to GPS devices
- [ ] Pedestrian/bicycle routing modes
- [ ] EV charging station routing
- [ ] Route history

## Troubleshooting

### Route Not Displaying

1. **Check browser console** for errors
2. **Verify API key** is in `.env` file
3. **Restart backend server** to load new environment variables
4. **Check network tab** for API responses

### Claude Not Generating Routes

1. **System prompt** includes routing examples
2. **Tool definition** is properly configured
3. **Coordinates** are being parsed correctly
4. **Try simpler query**: "Route from LAX to downtown"

### Slow Performance

1. **TomTom API response** can take 500-1000ms
2. **Complex routes** with many points may render slowly
3. **Consider simplifying** route geometry for very long routes

## References

- [TomTom Routing API Documentation](https://developer.tomtom.com/routing-api/documentation/tomtom-maps/calculate-route)
- [TomTom Common Routing Parameters](https://developer.tomtom.com/routing-api/documentation/tomtom-maps/common-routing-parameters)
- [DeckGL PathLayer Documentation](https://deck.gl/docs/api-reference/layers/path-layer)

---

**Routing feature successfully integrated!** 🚗🗺️

Users can now ask Claude for directions and see beautiful route visualizations with accurate time and distance estimates.
