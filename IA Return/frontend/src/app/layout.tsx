import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "AI GenPerf & FinOps Intelligence Framework",
  description:
    "Enterprise-grade AI Performance & FinOps Intelligence Platform for CIO-level governance and strategic decision-making.",
  keywords: ["AI", "FinOps", "Engineering Intelligence", "CIO Dashboard", "GenAI ROI"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans bg-surface-950 text-slate-100 antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
