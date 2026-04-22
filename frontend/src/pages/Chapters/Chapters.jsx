import { Link, useParams } from "react-router-dom";
import { supabase } from "../../services/supabaseClient";
import { useEffect, useState } from "react";

export default function Chapters() {
  const { bookId } = useParams();
  const [chapters, setChapters] = useState(null);

  useEffect(() => {
    async function fetchChapters() {
      const session = await supabase.auth.getSession();
      const token = session.data.session.access_token;

      const res = await fetch(
        `http://localhost:8000/api/getChapters?textbook_id=${bookId}`,
        { headers: { Authorization: `Bearer ${token}` } },
      );
      const data = await res.json();
      setChapters(data.response);
    }
    fetchChapters();
  }, [bookId]);
  if (!chapters) return <p>Loading…</p>;

  return (
    <section>
      <h1 className="text-2xl font-semibold mb-4">Chapters</h1>
      <ul className="space-y-2">
        {chapters.map((chapter, index) => (
          <li key={chapter.number} className="flex gap-3">
            <span>{chapter.title}</span>
            <Link
              className="text-blue-600 underline"
              to={`/books/${bookId}/chapters/${chapter.number}/understanding`}
            >
              Understanding
            </Link>
            <Link
              className="text-blue-600 underline"
              to={`/books/${bookId}/chapters/${chapter.number}/reinforce/flashcards`}
            >
              Reinforce
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
