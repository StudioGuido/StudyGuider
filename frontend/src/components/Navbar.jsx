import { Link, NavLink } from "react-router-dom";

export default function Navbar() {
  const link = ({ isActive }) =>
    `px-3 py-2 rounded ${isActive ? "bg-gray-200" : "hover:bg-gray-100"}`;
  return (
    <header className="border-b">
      <div className="max-w-6xl mx-auto flex items-center justify-between p-3">
        <Link to="/books" className="font-bold">StudyGuider</Link>
        <nav className="flex gap-2">
          <NavLink to="/books" className={link}>Books</NavLink>
        </nav>
      </div>
    </header>
  );
}
