import { Inter } from 'next/font/google';
import { AuthProvider } from '@/context/AuthContext';
import { ChatProvider } from '@/context/ChatContext';
import { Navbar } from '@/components/layout/Navbar';
import { Toaster } from 'sonner';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'LinguaLearn',
  description: 'AI-powered language learning',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          <ChatProvider>
            <Navbar />
            <main className="container mx-auto px-4 py-6">{children}</main>
            <Toaster richColors position="top-right" />
          </ChatProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
