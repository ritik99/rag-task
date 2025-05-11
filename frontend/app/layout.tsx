import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils"; // We'll create this util later

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "RAG Testing Interface",
  description: "Test and evaluate your RAG system",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={cn(inter.className, "bg-background text-foreground")}>
        {children}
      </body>
    </html>
  );
}
