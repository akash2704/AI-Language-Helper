'use client';

import { useState } from 'react';
import { useChat } from '@/context/ChatContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { toast } from 'sonner';

export function ChatInterface() {
  const { messages, sendMessage, isSessionActive, corrections } = useChat();
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !isSessionActive) return;
    
    try {
      setIsLoading(true);
      await sendMessage(input);
      setInput('');
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isSessionActive) {
    return <p className="text-center">Start a session to begin chatting</p>;
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Chat</CardTitle>
      </CardHeader>
      <CardContent className="h-[400px] overflow-y-auto space-y-4">
        {messages.length === 0 ? (
          <Skeleton className="h-20 w-full" />
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[70%] p-2 rounded-lg ${
                  msg.sender === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200'
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))
        )}
      </CardContent>
      <CardFooter>
        <form onSubmit={handleSubmit} className="flex w-full space-x-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={!isSessionActive || isLoading}
          />
          <Button type="submit" disabled={!isSessionActive || isLoading}>
            {isLoading ? 'Sending...' : 'Send'}
          </Button>
        </form>
      </CardFooter>
      <CardContent>
        <p className="text-sm text-muted-foreground">Corrections: {corrections}</p>
      </CardContent>
    </Card>
  );
}