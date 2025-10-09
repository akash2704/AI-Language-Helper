'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { ChatInterface } from '@/components/chat/ChatInterface';
import { SessionSetup } from '@/components/chat/SessionSetup';

export default function ChatPage() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) return null;

  return (
    <div className="grid gap-6 md:grid-cols-[2fr_1fr]">
      <ChatInterface />
      <SessionSetup />
    </div>
  );
}
