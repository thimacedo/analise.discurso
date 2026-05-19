import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sentinela Democrática",
  description: "War Room de Análise Forense",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body className="antialiased">
        <div className="scanline" />
        {children}
      </body>
    </html>
  );
}
