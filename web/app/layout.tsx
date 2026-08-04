import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "Tactic Fingerprint | Football style intelligence",
  description: "Explore team tactical DNA from event-level football data."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
