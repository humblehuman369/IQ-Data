import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.flipcycle.app',
  appName: 'FlipCycle',
  webDir: '.next',
  server: {
    androidScheme: 'https',
  },
  plugins: {
    Purchases: {
      apiKey: process.env.NEXT_PUBLIC_REVENUECAT_PUBLIC_KEY,
    },
  },
};

export default config;
