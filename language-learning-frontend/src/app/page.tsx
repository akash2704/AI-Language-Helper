'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/context/AuthContext';

export default function Home() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-80px)]">
      <h1 className="text-4xl font-bold mb-4">Welcome to LinguaLearn</h1>
      <p className="text-lg mb-6 text-center max-w-md">
        Learn languages with AI-powered assistance, real-time corrections, and personalized feedback.
      </p>
      {isAuthenticated ? (
        <Link href="/chat">
          <Button size="lg">Start Learning</Button>
        </Link>
      ) : (
        <div className="space-x-4">
          <Link href="/login">
            <Button variant="outline" size="lg">Login</Button>
          </Link>
          <Link href="/register">
            <Button size="lg">Register</Button>
          </Link>
        </div>
      )}
    </div>
  );
}