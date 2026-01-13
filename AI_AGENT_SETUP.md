# AI Agent Setup Guide

This guide will help you set up the Claude AI agent for the Mirror Project.

## Overview

The AI agent allows users to interact with the infrastructure visualization using natural language. Users can ask questions about the data and request actions like navigating to specific locations or filtering infrastructure types.

## Features

### Supported Actions

1. **Camera Controls** - Navigate the map
   - "Take me to LAX"
   - "Fly to Long Beach Port"
   - "Show me Downtown LA"

2. **Data Queries** - Get information about infrastructure
   - "How many airports are in LA?"
   - "What types of ports do we have?"
   - "Tell me about the warehouses"

3. **Filter Infrastructure** - Show/hide layers
   - "Show me only airports"
   - "Hide the warehouses"
   - "Display only ports and airports"

4. **Highlight Features** - Focus on specific buildings
   - "Highlight LAX terminal"
   - "Show me the main pier at Long Beach"

## Setup Instructions

### 1. Get an Anthropic API Key

1. Go to [https://console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Navigate to Settings → API Keys
4. Create a new API key
5. Copy the key (it will only be shown once!)

### 2. Configure Environment Variables

1. Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```bash
   ANTHROPIC_API_KEY=your_actual_api_key_here
   ```

3. **Important**: Never commit `.env` to version control!

### 3. Install Dependencies

Python dependencies are already installed. If you need to reinstall:

```bash
python3 -m pip install --user -r requirements.txt
```

### 4. Start the Application

Make sure to export your environment variable before starting the API server:

```bash
# Export the API key
export ANTHROPIC_API_KEY=your_api_key_here

# Start the servers
./start.sh
```

Or start manually in two terminals:

**Terminal 1 - Backend:**
```bash
export ANTHROPIC_API_KEY=your_api_key_here
python3 api_server.py
```

**Terminal 2 - Frontend:**
```bash
cd app
npm run dev
```

### 5. Using the AI Agent

1. Open the application in your browser (usually http://localhost:5174)
2. Click the chat button (💬) in the top-right corner
3. Start asking questions or making requests!

## Example Conversations

### Data Questions
```
User: How many airports are there?
Agent: There are 1,657 airport infrastructure features in the Los Angeles area, including airports, helipads, and terminals.
```

### Navigation
```
User: Take me to LAX
Agent: Flying to Los Angeles International Airport (LAX)
[Map automatically flies to LAX coordinates]
```

### Filtering
```
User: Show me only ports
Agent: Filtering to show only port infrastructure
[Map hides airports and warehouses, showing only ports]
```

### Combined Actions
```
User: Show me the largest port and fly there
Agent: The largest port facility is the Port of Los Angeles. Flying there now.
[Map flies to the port and highlights it]
```

## Architecture

### Backend (Flask)

**New Endpoint:** `POST /api/chat`

The chat endpoint:
1. Receives user messages
2. Gathers infrastructure statistics from PostgreSQL
3. Calls Claude API with:
   - System prompt (context about the data)
   - Tool definitions (available actions)
   - Conversation history
   - User's message
4. Returns Claude's response and any action requests

**Tool Definitions:**

- `fly_to_location` - Move camera to coordinates
- `filter_infrastructure` - Show/hide infrastructure types
- `highlight_feature` - Highlight specific buildings
- `search_infrastructure` - Query the database

### Frontend (React)

**New Components:**

- `ChatSidebar.jsx` - Chat UI component
- `ChatSidebar.css` - Styling for chat interface

**Enhanced Map Component:**

The Map component now includes:
- State management for view, filters, and highlights
- Action handler to execute Claude's tool calls
- Layer visibility controls
- Feature highlighting system

## Customization

### Adding New Actions

To add a new action:

1. **Define the tool in `api_server.py`:**

```python
{
    "name": "your_action_name",
    "description": "What this action does",
    "input_schema": {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Parameter description"}
        },
        "required": ["param1"]
    }
}
```

2. **Handle the action in `Map.jsx`:**

```javascript
case 'your_action_name':
    // Implement the action
    console.log('Executing your action', action.input);
    break;
```

### Modifying the System Prompt

Edit the `system_prompt` in [api_server.py](api_server.py:252-276) to change how Claude understands and responds to queries.

### Adjusting the UI

Modify [ChatSidebar.css](app/src/ChatSidebar.css) to change colors, positioning, or styling.

## Troubleshooting

### "No API key found" error

Make sure you've exported the environment variable:
```bash
export ANTHROPIC_API_KEY=your_key_here
```

### Chat button doesn't appear

Check the browser console for errors. Make sure the frontend build succeeded.

### Agent gives generic responses

The agent needs infrastructure data to be loaded. Ensure:
- PostgreSQL is running
- Database is populated (`python3 setup_postgres.py`)
- API server is returning data from `/api/airports`, `/api/ports`, `/api/warehouses`

### Actions don't work

Check the browser console for action execution logs. Ensure the action handler in `Map.jsx` is receiving the correct action format.

## Cost Considerations

Claude API usage is billed per token. Each chat interaction uses:
- ~500-1000 tokens for system prompt and context
- ~50-200 tokens per user message
- ~100-300 tokens per Claude response

Approximate cost: $0.003-0.015 per interaction (using Claude 3.5 Sonnet)

To minimize costs:
- Keep conversations concise
- Use specific questions rather than open-ended exploration
- Consider caching frequently used context (future enhancement)

## Security Notes

⚠️ **Important Security Considerations:**

1. **Never commit API keys** - Always use environment variables
2. **API key protection** - Don't expose the backend publicly without authentication
3. **Rate limiting** - Consider adding rate limits in production
4. **Input validation** - The backend validates tool inputs, but additional checks may be needed for production

## Future Enhancements

Potential improvements:
- [ ] Conversation persistence (save chat history)
- [ ] Voice input/output
- [ ] Multi-turn tool use (agent can chain multiple actions)
- [ ] Custom saved queries/shortcuts
- [ ] Data visualization requests (charts, statistics)
- [ ] Export chat transcripts
- [ ] Integration with additional data sources

## Support

For issues or questions:
- Check the main [README.md](README.md)
- Review the [Dependencies documentation](DEPENDENCIES.md)
- Report issues on GitHub

---

Built with Claude 3.5 Sonnet via the Anthropic API
