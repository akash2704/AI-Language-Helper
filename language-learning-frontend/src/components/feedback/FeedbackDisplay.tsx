'use client';

import { useState } from 'react';
import { useChat } from '@/context/ChatContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function FeedbackDisplay() {
  const { endSession, isSessionActive } = useChat();
  const [feedback, setFeedback] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleEndSession = async () => {
    if (isSessionActive) {
      try {
        setIsLoading(true);
        const feedbackText = await endSession();
        setFeedback(feedbackText);
      } catch (error) {
        console.error('Error ending session:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Session Feedback</CardTitle>
      </CardHeader>
      <CardContent>
        {isSessionActive ? (
          <Button 
            onClick={handleEndSession} 
            variant="destructive"
            disabled={isLoading}
          >
            {isLoading ? 'Getting Feedback...' : 'End Session'}
          </Button>
        ) : feedback ? (
          <div className="whitespace-pre-wrap">{feedback}</div>
        ) : (
          <p>No feedback available. Start a session to get feedback.</p>
        )}
      </CardContent>
    </Card>
  );
}