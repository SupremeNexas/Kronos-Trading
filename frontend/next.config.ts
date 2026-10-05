import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  async rewrites() {
    const apiUrl = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:7070';
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
    ]
  }
};

export default nextConfig;
