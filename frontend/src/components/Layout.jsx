export default function Layout({ children }) {
  return (
    <div className="min-h-screen flex flex-col">
      <main className="max-w-6xl w-full mx-auto p-4">{children}</main>
    </div>
  );
}
