# Phase 3 AI Chatbot - Frontend

Next.js chat interface for AI-powered task management using Gemini.

## Features

- **Chat Interface**: Clean, responsive chat UI with message history
- **JWT Authentication**: Protected routes with token-based auth
- **Conversation Persistence**: Automatically saves conversation_id in localStorage
- **Real-time Messaging**: Send messages and receive AI responses
- **Error Handling**: User-friendly error messages for 401/500 errors
- **Loading States**: Visual feedback while AI processes requests
- **Mobile Responsive**: Works on all screen sizes

## Tech Stack

- Next.js 14.1 (App Router)
- React 18.2
- TypeScript 5.3
- Tailwind CSS 3.4
- JWT for authentication

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   Create `.env.local` file:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Run development server:**
   ```bash
   npm run dev
   ```

4. **Open browser:**
   Navigate to `http://localhost:3000`

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page (redirects to /chat)
│   ├── globals.css         # Global styles
│   ├── login/
│   │   └── page.tsx        # Login page (JWT entry)
│   └── chat/
│       └── page.tsx        # Main chat page
├── components/
│   ├── auth/
│   │   └── ProtectedRoute.tsx  # Auth guard
│   └── chat/
│       ├── ChatInterface.tsx    # Main chat component
│       ├── MessageList.tsx      # Message display
│       └── ChatErrorBoundary.tsx
├── lib/
│   ├── api/
│   │   └── chat.ts         # API client functions
│   └── utils/
│       └── storage.ts      # localStorage utilities
└── package.json
```

## Usage

### 1. Get JWT Token

Get a JWT token from the backend:

```bash
# Login to backend API
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

Copy the token from the response.

### 2. Login to Frontend

1. Open `http://localhost:3000/login`
2. Paste your JWT token
3. Click "Continue to Chat"

### 3. Start Chatting

- Type your message in the input box
- Press Enter or click Send
- AI will respond using Gemini API
- Conversation is automatically saved

### 4. New Conversation

Click "New Conversation" button to start fresh.

## API Integration

The frontend connects to these backend endpoints:

- `POST /api/chat` - Send message and get AI response
- `GET /api/conversations/{id}/history` - Load conversation history
- `POST /api/conversations` - Create new conversation

## Components

### ChatInterface

Main chat component that handles:
- Message state management
- Sending messages to backend
- Loading conversation history
- Error handling
- New conversation creation

### MessageList

Renders messages with:
- Role-based styling (user vs assistant)
- Timestamps
- Auto-scroll to latest message
- Loading indicator
- Empty state

### ProtectedRoute

Authentication guard that:
- Checks for JWT token
- Redirects to login if not authenticated
- Shows loading state during verification

## Storage

Uses localStorage for:
- `phase3_conversation_id` - Current conversation ID
- `auth_token` - JWT authentication token

## Development

```bash
# Run dev server
npm run dev

# Run tests
npm test

# Run tests in watch mode
npm test:watch

# Build for production
npm run build

# Run production build
npm start
```

## Error Handling

The UI handles common errors:

- **401 Unauthorized**: Session expired, please login again
- **500 Server Error**: AI service temporarily unavailable
- **Network Error**: Connection issues
- **Invalid Token**: Token format validation

## Styling

- Tailwind CSS for utility-first styling
- Custom scrollbar styles
- Responsive breakpoints (mobile-first)
- Blue color scheme (primary: #2563eb)

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Known Limitations

- Token validation is client-side only (check for existence)
- No token refresh mechanism
- Conversation history limited to localStorage capacity
- No message editing or deletion

## Future Enhancements

- [ ] Token auto-refresh
- [ ] Message streaming
- [ ] File upload support
- [ ] Voice input
- [ ] Dark mode
- [ ] Conversation list sidebar
- [ ] Message search
- [ ] Export conversation
