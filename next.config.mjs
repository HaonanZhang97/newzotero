/** @type {import('next').NextConfig} */
const nextConfig = {
  // Docker优化配置
  output: 'standalone',

  // API重写，将/api路由代理到Flask后端
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
