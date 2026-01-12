/**
 * Voice Input Component - Advanced Feature from Phase 1
 *
 * Allows users to speak their task commands instead of typing.
 * Supports multiple languages including English and Urdu.
 */

'use client';

import { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Globe } from 'lucide-react';

interface VoiceInputProps {
  onTranscript: (text: string) => void;
  className?: string;
}

export function VoiceInput({ onTranscript, className = '' }: VoiceInputProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [language, setLanguage] = useState<'en-US' | 'ur-PK'>('en-US');
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // Check if browser supports Web Speech API
    if (typeof window !== 'undefined') {
      const SpeechRecognition =
        (window as any).SpeechRecognition ||
        (window as any).webkitSpeechRecognition;

      if (SpeechRecognition) {
        setIsSupported(true);
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = false;
        recognitionRef.current.interimResults = false;
      }
    }
  }, []);

  const startRecording = () => {
    if (!recognitionRef.current) return;

    recognitionRef.current.lang = language;

    recognitionRef.current.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      onTranscript(transcript);
      setIsRecording(false);
    };

    recognitionRef.current.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setIsRecording(false);
    };

    recognitionRef.current.onend = () => {
      setIsRecording(false);
    };

    try {
      recognitionRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
      setIsRecording(false);
    }
  };

  const stopRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsRecording(false);
    }
  };

  if (!isSupported) {
    return null; // Don't show button if not supported
  }

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {/* Language Selector */}
      <button
        onClick={() => setLanguage(language === 'en-US' ? 'ur-PK' : 'en-US')}
        className="p-2 text-gray-400 hover:text-white transition-colors"
        title={language === 'en-US' ? 'Switch to Urdu' : 'Switch to English'}
        disabled={isRecording}
      >
        <Globe className="w-4 h-4" />
        <span className="text-xs ml-1">
          {language === 'en-US' ? '🇺🇸' : '🇵🇰'}
        </span>
      </button>

      {/* Voice Input Button */}
      <button
        onClick={isRecording ? stopRecording : startRecording}
        className={`p-3 rounded-lg transition-all ${
          isRecording
            ? 'bg-red-500 hover:bg-red-600 animate-pulse shadow-lg shadow-red-500/50'
            : 'bg-neon-cyan hover:bg-neon-cyan/80'
        }`}
        aria-label={isRecording ? 'Stop recording' : 'Start recording'}
        title={isRecording ? 'Click to stop' : 'Click to speak'}
      >
        {isRecording ? (
          <MicOff className="w-5 h-5 text-white" />
        ) : (
          <Mic className="w-5 h-5 text-gray-900" />
        )}
      </button>

      {/* Recording Indicator */}
      {isRecording && (
        <div className="flex items-center gap-1">
          <div className="flex items-center gap-1">
            <div
              className="w-1 h-4 bg-red-400 rounded animate-pulse"
              style={{ animationDelay: '0s' }}
            />
            <div
              className="w-1 h-6 bg-red-400 rounded animate-pulse"
              style={{ animationDelay: '0.1s' }}
            />
            <div
              className="w-1 h-8 bg-red-400 rounded animate-pulse"
              style={{ animationDelay: '0.2s' }}
            />
            <div
              className="w-1 h-6 bg-red-400 rounded animate-pulse"
              style={{ animationDelay: '0.3s' }}
            />
            <div
              className="w-1 h-4 bg-red-400 rounded animate-pulse"
              style={{ animationDelay: '0.4s' }}
            />
          </div>
          <span className="ml-2 text-red-400 text-sm font-medium animate-pulse">
            Listening...
          </span>
        </div>
      )}
    </div>
  );
}
