import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.API_URL 
          ? `${process.env.API_URL}/api/:path*`
          : 'http://127.0.0.1:7070/api/:path*',
      },
    ]
  }
};

export default nextConfig;
