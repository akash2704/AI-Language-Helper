'use client';

import { createContext, useContext, useState, ReactNode } from 'react';
import { api } from '@/lib/api/api';
import { toast } from 'sonner';
import { ApiError } from '@/types/api';

interface ChatMessage {
  sender: 'user' | 'bot';
  content: string;
}

interface ChatContextType {
  messages: ChatMessage[];
  corrections: string;
  isSessionActive: boolean;
  sessionId: string | null;
  startSession: (targetLang: string, nativeLang: string, level: string) => Promise<void>;
  sendMessage: (message: string) => Promise<void>;
  endSession: () => Promise<string>;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [corrections, setCorrections] = useState<string>('');
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const startSession = async (targetLang: string, nativeLang: string, level: string) => {
    try {
      const response = await api.post('/api/start_session', {
        target_lang: targetLang,
        source_lang: nativeLang,
        level,
      });
      
      setMessages([{ sender: 'bot', content: response.data.response }]);
      setCorrections(response.data.corrections || 'No corrections yet');
      setSessionId(response.data.session_id);
      setIsSessionActive(true);
      toast.success('Session started');
    } catch (error: unknown) {
      const apiError = error as ApiError;
      console.error('Session start error:', error);
      toast.error(apiError.response?.data?.message || 'Failed to start session');
      throw error;
    }
  };

  const sendMessage = async (message: string) => {
    if (!sessionId) {
      toast.error('No active session');
      return;
    }
    
    try {
      const response = await api.post('/api/chat', { 
        user_input: message,
        session_id: sessionId 
      });
      
      setMessages((prev) => [
        ...prev,
        { sender: 'user', content: message },
        { sender: 'bot', content: response.data.response },
      ]);
      setCorrections(response.data.corrections || 'No corrections needed');
    } catch (error: unknown) {
      const apiError = error as ApiError;
      console.error('Send message error:', error);
      toast.error(apiError.response?.data?.message || 'Failed to send message');
      throw error;
    }
  };

  const endSession = async () => {
    if (!sessionId) {
      toast.error('No active session');
      return '';
    }
    
    try {
      const response = await api.get(`/api/feedback?session_id=${sessionId}`);
      setMessages([]);
      setCorrections('');
      setIsSessionActive(false);
      setSessionId(null);
      toast.success('Session ended');
      return response.data.feedback;
    } catch (error: unknown) {
      const apiError = error as ApiError;
      console.error('End session error:', error);
      toast.error(apiError.response?.data?.message || 'Failed to end session');
      throw error;
    }
  };

  return (
    <ChatContext.Provider value={{ 
      messages, 
      corrections, 
      isSessionActive, 
      sessionId,
      startSession, 
      sendMessage, 
      endSession 
    }}>
      {children}
    </ChatContext.Provider>
  );
}

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};