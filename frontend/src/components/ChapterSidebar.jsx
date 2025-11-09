import { useEffect, useState } from "react";
import { NavLink, Link, useParams } from "react-router-dom";
import { fakeApi } from "../services/fakeApi";

export default function ChapterSidebarNav({ className = "", target = "understanding" }) {
  const { bookId } = useParams();
  const [book, setBook] = useState(null);
  const [chapters, setChapters] = useState([]);

  useEffect(() => {
    let alive = true;
    fakeApi.getBooks().then((books) => {
      if (!alive) return;
      setBook(books.find((b) => b.id === bookId) ?? null);
    });
    fakeApi.getChapters(bookId).then((chs) => alive && setChapters(chs));
    return () => { alive = false; };
  }, [bookId]);

  const title = book?.title ?? "Loading…";
  const authors = Array.isArray(book?.authors)
    ? book.authors.join(", ")
    : (book?.author ?? "");

  return (
    <aside
      className={[
        "w-80 shrink-0 h-screen sticky top-0",
        "bg-neutral-950 text-slate-50 border-r border-neutral-800",
        className,
      ].join(" ")}
      aria-label="Chapter navigation"
    >
      <header className="px-4 pb-3 pt-5 border-b border-neutral-800">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          {title} <span aria-hidden>🧠</span>
        </h2>
        {authors && <p className="text-sm text-slate-300">{authors}</p>}
      </header>

      <nav className="p-3 overflow-y-auto h-[calc(100%-4.25rem)]">
        <ul className="space-y-2">
          {chapters.map((c, idx) => (
            <li key={c.id}>
              <NavLink
                to={`/books/${bookId}/chapters/${c.id}/${target}`}
                className={({ isActive }) =>
                  [
                    "block rounded-lg px-4 py-3",
                    "bg-neutral-900 ring-1 ring-neutral-800",
                    "hover:bg-neutral-800 hover:ring-neutral-700",
                    isActive && "bg-neutral-800 ring-neutral-600",
                  ]
                    .filter(Boolean)
                    .join(" ")
                }
                end={false}
              >
                <span className="font-medium">
                  {`Chapter ${idx + 1}: ${c.title}`}
                </span>
              </NavLink>
            </li>
          ))}

          <li className="pt-1">
            <Link
              to={`/books/${bookId}/chapters`}
              className="block rounded-lg px-4 py-3 bg-neutral-900 ring-1 ring-neutral-800 hover:bg-neutral-800 hover:ring-neutral-700"
            >
              Select New Chapter <span className="text-slate-300" aria-hidden>＋</span>
            </Link>
          </li>
        </ul>
      </nav>
    </aside>
  );
}
