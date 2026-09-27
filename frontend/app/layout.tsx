import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Kronos AI | Market Intelligence",
  description: "AI-powered market analysis and forecasting",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-slate-950 text-slate-50">{children}</body>
    </html>
  );
}