import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17202a",
        mint: "#1f9d72",
        amberline: "#d48b16",
        paper: "#f7f8f5",
      },
    },
  },
  plugins: [],
};

export default config;
