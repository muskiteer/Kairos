import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  webpack: (config) => {
    // Handle node modules that need to be external
    config.externals = config.externals || [];
    
    // Handle optional dependencies
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      net: false,
      tls: false,
    };
    
    return config;
  },
  transpilePackages: ['@lit-protocol/lit-node-client', '@lit-protocol/constants'],
};

export default nextConfig;
