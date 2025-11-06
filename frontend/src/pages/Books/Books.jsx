import { Link } from "react-router-dom";
import { fakeApi } from "../../services/fakeApi";
import { useEffect, useState } from "react";

export default function Books() {
  const [books, setBooks] = useState(null);
  useEffect(() => { fakeApi.getBooks().then(setBooks); }, []);
  if (!books) return <p>Loading…</p>;

  return (
    <section>
      <h1 className="text-2xl font-semibold mb-4">My Books</h1>
      <ul className="space-y-2">
        {books.map(b => (
          <li key={b.id}>
            <Link to={`/books/${b.id}/chapters`} className="text-blue-600 underline">
              {b.title} — {b.author}
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
