import type { NextConfig } from "next";
import path from "path";

// Load .env file from the parent directory
require("dotenv").config({ path: path.resolve(__dirname, "..", ".env") });

const nextConfig: NextConfig = {
  /* config options here */
  // Note: Environment variables loaded by `dotenv` are available during the build process
  // and server-side. For client-side access, they still need to be prefixed with NEXT_PUBLIC_
};

export default nextConfig;
