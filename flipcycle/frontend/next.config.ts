import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  poweredByHeader: false,
  async redirects() {
    return [
      { source: '/dashboard/analyzer', destination: '/dashboard?section=analyzer', permanent: false },
      { source: '/dashboard/pipeline', destination: '/dashboard?section=pipeline', permanent: false },
      { source: '/dashboard/budgets', destination: '/dashboard?section=budgets', permanent: false },
      { source: '/dashboard/documents', destination: '/dashboard?section=documents', permanent: false },
      { source: '/dashboard/team', destination: '/dashboard?section=team', permanent: false },
    ];
  },
};

export default nextConfig;
