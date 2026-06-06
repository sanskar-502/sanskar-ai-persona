import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  weight: ["300", "400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: "Sanskar Dubey — AI Persona",
  description: "Chat with the autonomous AI persona of Sanskar Dubey. RAG-grounded over real resume and GitHub projects. Built for the SCALER AI Engineer Intern assignment.",
  keywords: ["AI", "Persona", "Sanskar Dubey", "SCALER", "Voice Agent", "RAG"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} font-sans antialiased`}>
        {children}
      </body>
    </html>
  );
}
