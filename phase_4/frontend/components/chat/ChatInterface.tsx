/**
 * ChatInterface component - AI-powered task management with custom chat UI
 *
 * Features:
 * - Professional chat interface (ChatKit-inspired design)
 * - Conversation persistence across page reloads
 * - Real-time message streaming
 * - Error handling with user-friendly messages
 * - Voice input support (English + Urdu)
 * - Custom backend integration (FastAPI + Google Gemini)
 */

'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { RefreshCw, Send, Bot, User } from 'lucide-react';
import { VoiceInput } from './VoiceInput';
import {
  getConversationId,
  setConversationId,
  clearConversationId,
} from '@/lib/utils/storage';
import { getToken } from '@/lib/auth';
import { sendMessage, loadHistory, getActiveConversation } from '@/lib/api/chat';

interface ChatInterfaceProps {
  className?: string;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export function ChatInterface({ className = '' }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [voiceTranscript, setVoiceTranscript] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  /**
   * Auto-scroll to bottom when new messages arrive
   */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  /**
   * Load conversation history on mount
   * Fetches user's active conversation from backend (restores history after re-login)
   */
  useEffect(() => {
    const loadConversationHistory = async () => {
      const token = getToken();
      if (!token) {
        console.log('No auth token found');
        return;
      }

      setIsLoadingHistory(true);
      try {
        // First check localStorage for conversation_id
        let conversationId = getConversationId();

        if (conversationId) {
          // Load history for existing conversation
          console.log('Loading conversation history for ID:', conversationId);
          const history = await loadHistory(conversationId);
          if (history && history.length > 0) {
            setMessages(history);
          }
        } else {
          // No local conversation_id - fetch user's active conversation from backend
          console.log('Fetching active conversation from backend...');
          const activeConv = await getActiveConversation();

          if (activeConv.conversation_id) {
            // User has an existing conversation - restore it
            console.log('Restored conversation ID:', activeConv.conversation_id);
            setConversationId(activeConv.conversation_id);
            if (activeConv.messages && activeConv.messages.length > 0) {
              setMessages(activeConv.messages);
            }
          } else {
            console.log('No existing conversation found - fresh start');
          }
        }
      } catch (err) {
        console.error('Failed to load history:', err);
      } finally {
        setIsLoadingHistory(false);
      }
    };

    loadConversationHistory();
  }, []);

  /**
   * Handle sending a message
   */
  const handleSend = useCallback(async (messageText: string) => {
    if (!messageText.trim() || isLoading) return;

    setIsLoading(true);
    setError(null);

    const userMessage: Message = { role: 'user', content: messageText };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');

    try {
      const token = getToken();
      if (!token) {
        throw new Error('You are not authenticated. Please log in again.');
      }

      const conversationId = getConversationId();
      const response = await sendMessage(messageText, conversationId, token);

      // Store conversation_id if this is a new conversation
      if (response.conversation_id && !conversationId) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // Dispatch event if task was modified via MCP tools
      if (response.tool_calls && response.tool_calls.length > 0) {
        const taskModified = response.tool_calls.some(
          (call: any) =>
            call.tool === 'add_task' ||
            call.tool === 'update_task' ||
            call.tool === 'delete_task' ||
            call.tool === 'complete_task'
        );

        if (taskModified) {
          // Dispatch custom event to notify task list to refresh
          const event = new CustomEvent('taskModified', {
            detail: { source: 'chatbot', tool_calls: response.tool_calls }
          });
          window.dispatchEvent(event);
        }
      }
    } catch (err: any) {
      console.error('Failed to send message:', err);

      // Handle specific error types
      if (err.response?.status === 401) {
        setError(
          'Your session has expired. Please log in again to continue.'
        );
      } else if (err.response?.status === 500) {
        setError(
          'The AI service is temporarily unavailable. Please try again in a moment.'
        );
      } else {
        setError(
          err.message || 'Failed to send message. Please check your connection and try again.'
        );
      }
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  /**
   * Handle form submission
   */
  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    handleSend(inputValue);
  }, [inputValue, handleSend]);

  /**
   * Handle keyboard shortcuts
   */
  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(inputValue);
    }
  }, [inputValue, handleSend]);

  /**
   * Handle new conversation
   */
  const handleNewConversation = useCallback(() => {
    clearConversationId();
    setMessages([]);
    setError(null);
  }, []);

  /**
   * Handle voice transcript
   */
  const handleVoiceTranscript = useCallback((transcript: string) => {
    setVoiceTranscript(transcript);
  }, []);

  /**
   * Send voice transcript as message
   */
  const handleSendVoiceTranscript = useCallback(async () => {
    if (!voiceTranscript) return;
    await handleSend(voiceTranscript);
    setVoiceTranscript(null);
  }, [voiceTranscript, handleSend]);

  return (
    <div className={`flex flex-col h-full bg-gradient-to-b from-gray-900 to-gray-800 ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-700/50 bg-gray-900/80 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Bot className="w-5 h-5 text-neon-cyan" />
              AI Task Assistant
            </h2>
            <p className="text-xs text-gray-400 mt-0.5">
              Powered by Google Gemini • Professional Chat UI
            </p>
          </div>
          {messages.length > 0 && (
            <button
              onClick={handleNewConversation}
              className="px-3 py-1.5 text-xs text-gray-400 hover:text-white bg-gray-800/50 hover:bg-gray-800 border border-gray-700/50 rounded-md transition-colors flex items-center gap-1.5"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              New Chat
            </button>
          )}
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="px-4 py-3 bg-red-900/50 border-b border-red-700/50">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-2">
              <div className="w-5 h-5 text-red-400 mt-0.5">⚠️</div>
              <div>
                <p className="text-sm font-medium text-red-200">{error}</p>
              </div>
            </div>
            <button
              onClick={() => setError(null)}
              className="text-red-400 hover:text-red-200 transition-colors"
              aria-label="Dismiss error"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* Loading history indicator */}
      {isLoadingHistory && (
        <div className="px-4 py-3 bg-neon-cyan/10 border-b border-neon-cyan/30">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 border-2 border-neon-cyan border-t-transparent rounded-full animate-spin" />
            <p className="text-sm font-medium text-neon-cyan">
              Loading conversation history...
            </p>
          </div>
        </div>
      )}

      {/* Voice transcript preview */}
      {voiceTranscript && (
        <div className="mx-4 mt-2 p-3 bg-purple-900/30 border border-purple-500/50 rounded-lg">
          <p className="text-sm text-purple-200">
            🎤 Voice input: "{voiceTranscript}"
          </p>
          <div className="flex gap-2 mt-2">
            <button
              onClick={handleSendVoiceTranscript}
              className="text-xs bg-purple-500 px-3 py-1 rounded hover:bg-purple-600 transition-colors"
              disabled={isLoading}
            >
              {isLoading ? 'Sending...' : 'Send'}
            </button>
            <button
              onClick={() => setVoiceTranscript(null)}
              className="text-xs bg-gray-600 px-3 py-1 rounded hover:bg-gray-700 transition-colors"
              disabled={isLoading}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Messages container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4
        scrollbar-thin scrollbar-thumb-neon-cyan/40 scrollbar-track-gray-800/50
        hover:scrollbar-thumb-neon-cyan/60">
        {messages.length === 0 && !isLoadingHistory && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <Bot className="w-16 h-16 text-gray-600 mb-4" />
            <h3 className="text-xl font-medium text-gray-300 mb-2">
              Welcome to AI Task Assistant
            </h3>
            <p className="text-gray-500 max-w-md">
              I can help you manage tasks with natural language. Try saying:
              <br />
              <span className="text-neon-cyan">"Add buy groceries with high priority"</span>
              <br />
              <span className="text-neon-cyan">"Show all tasks due this week"</span>
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex gap-3 ${
              message.role === 'assistant' ? 'items-start' : 'items-start justify-end'
            }`}
          >
            {message.role === 'assistant' && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-neon-cyan/20 flex items-center justify-center">
                <Bot className="w-5 h-5 text-neon-cyan" />
              </div>
            )}

            <div
              className={`max-w-[70%] px-4 py-3 rounded-lg ${
                message.role === 'assistant'
                  ? 'bg-gray-800 border border-gray-700'
                  : 'bg-neon-cyan/10 border border-neon-cyan/30'
              }`}
            >
              <p className="text-sm text-gray-200 whitespace-pre-wrap break-words">
                {message.content}
              </p>
            </div>

            {message.role === 'user' && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-neon-cyan flex items-center justify-center">
                <User className="w-5 h-5 text-gray-900" />
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-3 items-start">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-neon-cyan/20 flex items-center justify-center">
              <Bot className="w-5 h-5 text-neon-cyan" />
            </div>
            <div className="bg-gray-800 border border-gray-700 px-4 py-3 rounded-lg">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="p-4 border-t border-gray-700/50 bg-gray-900/80 backdrop-blur-sm">
        <form onSubmit={handleSubmit} className="flex gap-2 items-end">
          <div className="flex-1">
            <textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message... (Shift+Enter for new line)"
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-neon-cyan resize-none
                scrollbar-thin scrollbar-thumb-neon-cyan/40 scrollbar-track-gray-800/50 hover:scrollbar-thumb-neon-cyan/60"
              rows={1}
              style={{ minHeight: '48px', maxHeight: '120px' }}
              disabled={isLoading}
            />
          </div>
          {/* WhatsApp-style: Show Voice when empty, Send when has text */}
          {inputValue.trim() ? (
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-3 bg-neon-cyan hover:bg-neon-cyan/80 disabled:bg-gray-700 disabled:text-gray-500 text-gray-900 font-medium rounded-lg transition-all flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              Send
            </button>
          ) : (
            <VoiceInput onTranscript={handleVoiceTranscript} />
          )}
        </form>
        <p className="text-xs text-gray-500 mt-2 text-center">
          Press Enter to send • Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
