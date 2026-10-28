import type { Metadata } from "next";
import { Montserrat, Nunito_Sans } from "next/font/google";
import "./globals.css";

import { Footer } from "./_components/footer";
import { AuthProviderJWT } from "./context/authContext";
import RequireAuth from "./context/requireAuth";

// Open replacements for the site's proprietary Museo and Trueno, see docs/BRAND.md
const heading = Montserrat({
  subsets: ["latin"],
  variable: "--font-heading",
  display: "swap",
});
const body = Nunito_Sans({
  subsets: ["latin"],
  variable: "--font-body",
  display: "swap",
  // next/font has no fallback metrics for Nunito Sans; skip the adjustment instead of warning.
  adjustFontFallback: false,
});

export const metadata: Metadata = {
  title: "Dom Bosco Service Desk",
  description:
    "Atendimento para pais e responsáveis. Projeto acadêmico não oficial, sem vínculo com o Colégio Dom Bosco.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className={`${heading.variable} ${body.variable}`}>
      <body className="flex min-h-screen flex-col">
        <AuthProviderJWT>
          <main className="flex-1">
            <RequireAuth>{children}</RequireAuth>
          </main>
        </AuthProviderJWT>
        <Footer />
      </body>
    </html>
  );
}
