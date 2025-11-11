import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { SimpleHeader } from "@/components/simple-header";


const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AIPPA - Intelligent Healthcare Simplified",
  description: "AI-powered booking management and patient insights to transform your practice",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
          <main className="flex-1 flex flex-col min-h-screen ">
            <SimpleHeader />
            {children}
          </main>
      </body>
    </html>
  );
}
