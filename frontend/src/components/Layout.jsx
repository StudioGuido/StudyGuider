import Navbar from "./Navbar";

export default function Layout({ children }) {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="w-full max-w-screen-2xl mx-auto p-4">{children}</main>
    </div>
  );
}
