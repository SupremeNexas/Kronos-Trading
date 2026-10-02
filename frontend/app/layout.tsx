import type { Metadata } from "next";
import { Inter_Tight, PT_Serif, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import Header from "@/components/Header";

const ptSerif = PT_Serif({
  subsets: ["latin"],
  variable: "--font-pt-serif",
  weight: ["400"], // PT Serif google font doesn't have 300, 400 is lightest
  display: "swap",
});

const interTight = Inter_Tight({
  subsets: ["latin"],
  variable: "--font-inter-tight",
  weight: ["400", "500", "600"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  weight: ["400", "500", "600"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Kronos AI | Market Intelligence",
  description:
    "Next-generation AI-powered quantitative market intelligence, autoregressive time-series forecasting, and trading analytics.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${ptSerif.variable} ${interTight.variable} ${jetbrainsMono.variable} antialiased min-h-screen flex flex-col`}
        style={{ backgroundColor: "var(--surface-canvas)", color: "var(--color-chalk)" }}
      >
        <Header />
        <main className="flex-1 flex flex-col pt-16">
          {children}
        </main>
      </body>
    </html>
  );
}
