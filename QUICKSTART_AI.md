# Quick Start: AI Agent

## 🚀 Get Started in 3 Steps

### 1. Your API key is already configured! ✅
The `.env` file has been created with your Anthropic API key.

### 2. Start the application

```bash
./start.sh
```

This will:
- Load your API key from `.env`
- Start the Flask backend (with Claude integration)
- Start the React frontend

### 3. Try the AI agent

1. Open http://localhost:5174 in your browser
2. Click the purple chat button (💬) in the top-right corner
3. Try these example queries:

**Data Questions:**
- "How many airports are there?"
- "Tell me about the ports"
- "What's the average warehouse height?"

**Navigation:**
- "Take me to LAX"
- "Show me Long Beach Port"
- "Fly to downtown LA"

**Filtering:**
- "Show me only airports"
- "Hide the warehouses"
- "Display only ports"

**Combined:**
- "Take me to the largest airport"
- "Show me all helipads and fly to the nearest one"

## 🎯 What Can It Do?

### ✅ Implemented Features

1. **Natural Language Queries** - Ask about infrastructure data
2. **Camera Control** - Navigate to locations automatically
3. **Layer Filtering** - Show/hide infrastructure types
4. **Feature Highlighting** - Focus on specific buildings
5. **Contextual Responses** - Claude knows about your LA infrastructure

### 🛠 Available Actions

| Action | Example |
|--------|---------|
| **fly_to_location** | "Take me to LAX" |
| **filter_infrastructure** | "Show only ports" |
| **highlight_feature** | "Highlight the main terminal" |
| **search_infrastructure** | "Find all international airports" |

## 📋 Architecture Overview

```
User Question
    ↓
ChatSidebar (React Component)
    ↓ HTTP POST
Flask API (/api/chat)
    ↓
Claude API (with tools & context)
    ↓
Response + Actions
    ↓
Map Component (executes actions)
```

## 🔧 Files Modified/Created

### Backend
- ✅ [api_server.py](api_server.py) - Added `/api/chat` endpoint
- ✅ [requirements.txt](requirements.txt) - Added `anthropic==0.40.0`
- ✅ [start.sh](start.sh) - Auto-loads `.env` file

### Frontend
- ✅ [app/src/Map.jsx](app/src/Map.jsx) - Added AI action handlers
- ✅ [app/src/ChatSidebar.jsx](app/src/ChatSidebar.jsx) - New chat UI
- ✅ [app/src/ChatSidebar.css](app/src/ChatSidebar.css) - Chat styling

### Configuration
- ✅ [.env](.env) - Your API key (not committed to git)
- ✅ [.env.example](.env.example) - Template for others
- ✅ [.gitignore](.gitignore) - Protects your API key

### Documentation
- ✅ [AI_AGENT_SETUP.md](AI_AGENT_SETUP.md) - Full setup guide
- ✅ [QUICKSTART_AI.md](QUICKSTART_AI.md) - This file!

## 💡 Tips

1. **Be specific** - "Take me to LAX" works better than "Show me an airport"
2. **Use natural language** - The agent understands conversational queries
3. **Combine actions** - "Show only ports and fly to Long Beach"
4. **Ask for data** - "How many helipads are there?"

## 🐛 Troubleshooting

**Chat button doesn't appear?**
- Make sure you ran `npm install` in the `app/` directory
- Check browser console for errors

**Agent says it can't help?**
- Ensure PostgreSQL is running
- Verify API server started successfully
- Check `logs/api.log` for errors

**"No API key" error?**
- Make sure `.env` file exists in project root
- Verify the file contains `ANTHROPIC_API_KEY=sk-ant-...`
- Restart the server after creating `.env`

## 📊 Cost Estimate

Using Claude 3.5 Sonnet:
- ~$0.003-0.015 per interaction
- ~100-200 interactions for $1
- Very affordable for development/testing

## 🎨 Customization

Want to add more capabilities? See [AI_AGENT_SETUP.md](AI_AGENT_SETUP.md#customization) for:
- Adding new tools/actions
- Modifying the system prompt
- Changing the UI appearance
- Extending conversation capabilities

## 🚀 Next Steps

Consider adding:
- [ ] Conversation history persistence
- [ ] More sophisticated queries (e.g., "Find all airports within 5 miles of downtown")
- [ ] Data visualization requests (e.g., "Show me a chart of warehouse heights")
- [ ] Voice input/output
- [ ] Save favorite queries
- [ ] Export chat transcripts

---

**Ready to explore LA's infrastructure with AI? Start chatting!** 💬
