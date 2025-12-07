export default function Layout({ children }) {
  return (
    <div className="min-h-screen flex flex-col bg-[#050505] text-white">
      <main className="flex-1 w-full">{children}</main>
    </div>
  );
}
