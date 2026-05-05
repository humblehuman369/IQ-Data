import type { Metadata } from 'next';
import { Providers } from '@/components/providers';
import './globals.css';

export const metadata: Metadata = {
  title: 'FlipCycle | Real estate flip workspace',
  description:
    'FlipCycle helps real estate investors analyze deals, manage rehab budgets, track pipeline stages, and coordinate documents with teams.',
  applicationName: 'FlipCycle',
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? 'https://flipcycle.vercel.app'),
  openGraph: {
    title: 'FlipCycle',
    description: 'A modern workspace for real estate flip teams.',
    type: 'website',
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
