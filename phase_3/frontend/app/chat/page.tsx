/**
 * Chat Page - Main route for AI-powered task management chat
 *
 * Route: /chat
 *
 * Features:
 * - Protected route (requires authentication)
 * - AI chatbot interface for natural language task management
 * - Conversation persistence
 * - Real-time message sending and receiving
 */

import { ChatInterface } from '@/components/chat/ChatInterface';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

export const metadata = {
  title: 'AI Task Assistant | Phase 3',
  description: 'Manage your tasks with natural language using AI',
};

export default function ChatPage() {
  return (
    <ProtectedRoute>
      <div className="h-screen w-full">
        <ChatInterface className="h-full" />
      </div>
    </ProtectedRoute>
  );
}
