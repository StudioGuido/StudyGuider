import { Link, useParams } from "react-router-dom";
import { fakeApi } from "../../services/fakeApi";
import { useEffect, useState } from "react";

export default function Chapters() {
  const { bookId } = useParams();
  const [chapters, setChapters] = useState(null);
  useEffect(() => { fakeApi.getChapters(bookId).then(setChapters); }, [bookId]);
  if (!chapters) return <p>Loading…</p>;

  return (
    <section>
      <h1 className="text-2xl font-semibold mb-4">Chapters</h1>
      <ul className="space-y-2">
        {chapters.map(c => (
          <li key={c.id} className="flex gap-3">
            <span>{c.title}</span>
            <Link
              className="text-blue-600 underline"
              to={`/books/${bookId}/chapters/${c.id}/understanding`}
            >
              Understanding
            </Link>
            <Link
              className="text-blue-600 underline"
              to={`/books/${bookId}/chapters/${c.id}/reinforce/flashcards`}
            >
              Reinforce
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
