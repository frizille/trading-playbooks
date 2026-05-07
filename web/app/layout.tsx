import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Trading Cockpit",
  description: "Local cockpit for Claude-driven trading research",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-bg text-text">
        {children}
      </body>
    </html>
  );
}
