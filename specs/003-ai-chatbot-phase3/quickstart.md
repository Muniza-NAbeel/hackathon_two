# Phase 3: AI Chatbot - Quickstart Guide

**Get the AI-powered task chatbot running in 10 minutes!**

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Python 3.11+** installed (`python --version`)
- [ ] **Node.js 18+** installed (`node --version`)
- [ ] **PostgreSQL database** (Neon Serverless recommended)
- [ ] **OpenAI API Key** with credits
- [ ] **Phase 2 Todo App** running (for JWT authentication)

## 🚀 Quick Setup (10 Minutes)

### Step 1: Clone and Navigate (30 seconds)

```bash
cd /path/to/hackathon_two
cd phase_3
```

### Step 2: Environment Configuration (2 minutes)

```bash
# Copy environment template
cp .env.example .env

# Open .env in your editor
nano .env  # or vim, code, etc.
```

**Fill in these required values:**

```bash
# From Phase 2 (MUST match exactly)
DATABASE_URL="postgresql://user:pass@host/db"
JWT_SECRET="your-secret-from-phase-2"

# Get from OpenAI Dashboard
OPENAI_API_KEY="sk-proj-xxxxx"

# Local development URLs (default)
MCP_SERVER_URL="http://localhost:8001"
NEXT_PUBLIC_API_URL="http://localhost:8000"
```

### Step 3: Backend Setup (3 minutes)

```bash
cd backend

# Install with UV (fast!)
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Or with regular pip
pip install -r requirements.txt

# Start backend
uvicorn app.main:app --reload --port 8000
```

✅ **Backend should be running at http://localhost:8000**

### Step 4: MCP Server Setup (2 minutes)

**Open a NEW terminal:**

```bash
cd phase_3/mcp

# Install dependencies
uv pip install -r requirements.txt

# Start MCP server
python server.py
```

✅ **MCP server should be running at http://localhost:8001**

### Step 5: Frontend Setup (3 minutes)

**Open ANOTHER new terminal:**

```bash
cd phase_3/frontend

# Install dependencies
npm install

# Start Next.js
npm run dev
```

✅ **Frontend should be running at http://localhost:3000**

### Step 6: Test It! (1 minute)

1. **Open browser:** http://localhost:3000/chat
2. **Login** with Phase 2 credentials
3. **Type:** "Add task to buy groceries"
4. **See:** Task created confirmation! 🎉

## 🧪 Verify Everything Works

Run these commands in the chat:

```
1. "Add task to buy milk"
   → Should create task and show confirmation

2. "Show my tasks"
   → Should list your tasks

3. "Mark task 1 as done"
   → Should mark task complete

4. "Update task 2 to buy almond milk"
   → Should update task title

5. "Delete task 3"
   → Should remove task
```

If all work, **you're ready to go!** ✅

## 🐛 Troubleshooting

### "Database Connection Error"

**Problem:** Can't connect to PostgreSQL

**Solutions:**
1. Check `DATABASE_URL` in `.env` is correct
2. Test connection: `psql $DATABASE_URL`
3. Ensure database from Phase 2 is running
4. Check network/firewall settings

### "OpenAI API Error"

**Problem:** AI responses failing

**Solutions:**
1. Verify `OPENAI_API_KEY` in `.env`
2. Check API key has credits: https://platform.openai.com/usage
3. Test API key:
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

### "JWT Invalid / Unauthorized"

**Problem:** Authentication failing

**Solutions:**
1. Ensure `JWT_SECRET` matches Phase 2 exactly
2. Login again in Phase 2
3. Check token in browser DevTools → Application → LocalStorage
4. Clear browser cache and cookies

### "MCP Server Not Responding"

**Problem:** Tools not executing

**Solutions:**
1. Check MCP server terminal for errors
2. Verify running on port 8001: `lsof -i :8001`
3. Check `MCP_SERVER_URL` in backend `.env`
4. Restart MCP server

### "Port Already in Use"

**Problem:** Can't start service

**Solutions:**
```bash
# Find process using port 8000
lsof -i :8000
# Kill it
kill -9 <PID>

# Or use different ports in .env
```

### "Module Not Found"

**Problem:** Import errors

**Solutions:**
```bash
# Backend
cd backend
pip install -r requirements.txt

# MCP
cd mcp
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

## 📝 Development Workflow

### Daily Development

```bash
# Terminal 1: Backend
cd phase_3/backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2: MCP Server
cd phase_3/mcp
python server.py

# Terminal 3: Frontend
cd phase_3/frontend
npm run dev
```

### Running Tests

```bash
# Backend tests
cd phase_3/backend
pytest tests/ -v

# MCP tests
cd phase_3/mcp
pytest tests/ -v

# Frontend tests
cd phase_3/frontend
npm test
```

### Making Changes

1. **Backend/MCP:** Edit code → Tests auto-reload → Verify
2. **Frontend:** Edit code → Hot reload → Verify in browser
3. **Database:** Create migration → Run `alembic upgrade head`

## 🎯 What's Next?

Now that it's running, try:

### Learn the Features

- **Test all CRUD operations** (create, read, update, delete)
- **Try different phrasings** for natural language
- **Test conversation persistence** (reload page, history persists)
- **Try special characters** (emojis, Unicode)

### Explore the Code

```
phase_3/
├── backend/app/services/agent_runner.py  # AI logic
├── mcp/tools/                            # MCP tools
└── frontend/components/chat/             # Chat UI
```

### Read Documentation

- [Architecture](../phase_3/docs/architecture.md) - How it works
- [API Reference](../phase_3/docs/api_reference.md) - REST API
- [MCP Tools](../phase_3/docs/mcp_tools.md) - Tool specs

### Deploy to Production

See [Deployment Guide](../phase_3/docs/deployment.md)

## ⚡ Performance Tips

### Speed up Development

```bash
# Use UV (10x faster than pip)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv pip install ...

# Use parallel testing
pytest -n auto

# Enable hot reload
npm run dev --turbo
```

### Optimize Database

```sql
-- Add indexes for better performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
```

## 🔐 Security Checklist

Before deploying:

- [ ] Change `JWT_SECRET` from default
- [ ] Use environment variables, not hardcoded secrets
- [ ] Enable HTTPS in production
- [ ] Set up CORS properly
- [ ] Enable rate limiting
- [ ] Review user ownership validation
- [ ] Set up monitoring and alerting

## 💡 Pro Tips

1. **Use UV Package Manager** - 10x faster than pip
2. **Keep terminals organized** - Label them (Backend, MCP, Frontend)
3. **Watch logs** - Errors show up immediately
4. **Test incrementally** - Don't wait for full build
5. **Read error messages** - They're usually helpful!
6. **Use hot reload** - Changes reflect instantly
7. **Commit often** - Small, tested changes

## 🆘 Still Stuck?

### Check Logs

```bash
# Backend logs (Terminal 1)
# MCP logs (Terminal 2)
# Frontend logs (Terminal 3)
# Browser console (F12)
```

### Common Issues

1. **Wrong directory** - Ensure `cd phase_3/backend` etc.
2. **Virtual env not activated** - See `(.venv)` in prompt
3. **Port conflicts** - Change ports in .env
4. **Old processes** - Kill and restart
5. **Cache issues** - Clear browser cache

### Get Help

- Check [README.md](../phase_3/README.md)
- Review [tasks.md](./tasks.md) for implementation details
- Check terminal logs for error messages

## ✅ Success Criteria

You're successful when:

- ✅ All 3 services running without errors
- ✅ Chat interface loads at http://localhost:3000/chat
- ✅ Can create tasks via natural language
- ✅ Can view/update/delete tasks
- ✅ Tests pass: `pytest` and `npm test`
- ✅ Conversation persists after page reload

**Happy coding!** 🚀
