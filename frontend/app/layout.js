import "./globals.css";
import Shell from "../components/layout/Shell";

export const metadata = { title: "FolioAI — Financial Research", description: "Evidence-backed financial research workspace" };

export default function RootLayout({ children }) {
  return <html lang="en"><body><Shell>{children}</Shell></body></html>;
}
