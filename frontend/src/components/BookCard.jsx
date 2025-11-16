import { Link } from "react-router-dom";

export default function BookCard({ book }) {
  return (
    <li>
      <Link to={`/books/${book.id}/chapters`} className="block w-full">
        <div className="flex items-center justify-between gap-4 p-4 rounded-xl border border-gray-700 hover:border-gray-600 transition-colors">
          <div className="flex items-center gap-4">
            <div className="text-lg font-semibold">{book.title}</div>
            <div className="text-xl">{book.emoji ?? "📘"}</div>
          </div>
          <div className="text-sm text-gray-400">
            {Array.isArray(book.author) ? book.author.join(", ") : book.author}
          </div>
        </div>
      </Link>
    </li>
  );
}
