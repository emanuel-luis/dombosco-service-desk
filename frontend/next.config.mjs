/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: false,
    images: {
        remotePatterns: [
            {
                hostname: "utfs.io",
            },
        ],
    },
};

export default nextConfig;
