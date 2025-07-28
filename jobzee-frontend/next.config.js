const withNextIntl = require("next-intl/plugin")("./i18n/request.ts");

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  images: {
    domains: ["localhost"],
  },
  async rewrites() {
    return [
      {
        source: "/auth/login",
        destination: "/en/auth/login",
      },
      {
        source: "/auth/register",
        destination: "/en/auth/register",
      },
    ];
  },
};

module.exports = withNextIntl(nextConfig);
