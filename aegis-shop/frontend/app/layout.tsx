import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/lib/store";

export const metadata: Metadata = {
  title: "Aegis Shop",
  description: "Enterprise security & observability products",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
