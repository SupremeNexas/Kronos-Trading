import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import Header from "@/components/Header";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
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
    <html lang="en" className={`dark ${inter.variable}`}>
      <body className="antialiased bg-slate-950 text-slate-50 min-h-screen flex selection:bg-cyan-500/20 selection:text-cyan-200">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0 min-h-screen bg-slate-950">
          <Header />
          <main className="flex-1 overflow-y-auto">{children}</main>
        </div>
      </body>
    </html>
  );
}
