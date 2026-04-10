import { useEffect, useState } from "react";
import { NavLink, useParams } from "react-router-dom";
import { fakeApi } from "../services/fakeApi";

export default function ChapterSidebar({ className = "", activePhase }) {
  const { bookId } = useParams();
  const [book, setBook] = useState(null);
  const [chapters, setChapters] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedChapterId, setSelectedChapterId] = useState("");
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    let alive = true;
    fakeApi.getBooks().then((books) => {
      if (!alive) return;
      setBook(books.find((b) => b.id === bookId) ?? null);
    });
    fakeApi.getChapters(bookId).then((chs) => {
      if (!alive) return;
      setChapters(chs);
      if (chs.length) {
        setSelectedChapterId(chs[0].id);
      }
    });
    return () => {
      alive = false;
    };
  }, [bookId]);

  const title = book?.title ?? "Loading...";
  const authors = Array.isArray(book?.authors)
    ? book.authors.join(", ")
    : (book?.author ?? "");

  const getChapterClasses = (isActive) => {
    const base = "block rounded-lg px-4 py-3 ring-1 transition-colors";
    if (isActive) {
      // Active: invert to white background with black text, keep hover consistent.
      return `${base} bg-white text-black visited:text-black ring-neutral-200 hover:bg-white hover:ring-neutral-200`;
    }
    // Inactive: dark background with hover to slightly lighter gray.
    return `${base} bg-neutral-900 text-slate-100 ring-neutral-800 hover:bg-neutral-800 hover:ring-neutral-700`;
  };

  return (
    <>
      <aside
        className={[
          "shrink-0 h-screen sticky top-0 overflow-hidden transition-all duration-300",
          "bg-neutral-950 text-slate-50 border-r border-neutral-800",
          collapsed ? "w-14" : "w-80",
          className,
        ].join(" ")}
        aria-label="Chapter navigation"
      >
        {/* Toggle button */}
        <div className="flex items-center px-3 pt-4 pb-2">
          <button
            type="button"
            onClick={() => setCollapsed((c) => !c)}
            className="flex h-8 w-8 items-center justify-center rounded-md hover:bg-neutral-800 transition-colors"
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            <span className="text-lg leading-none">&#9776;</span>
          </button>
        </div>

        <div className={`w-80 transition-opacity duration-300 ${collapsed ? "opacity-0 pointer-events-none" : "opacity-100"}`}>
          <header className="px-4 pb-3 pt-1 border-b border-neutral-800">
            <h2 className="text-xl font-semibold">{title}</h2>
            {authors && <p className="text-sm text-slate-300">{authors}</p>}
          </header>

          <nav className="p-3 overflow-y-auto h-[calc(100vh-7.5rem)]">
            <ul className="space-y-2">
              {chapters.map((c, idx) => (
                <li key={c.id}>
                  <NavLink
                    to={`/books/${bookId}/chapters/${c.id}/${activePhase === "understanding" ? "understanding" : "reinforce/flashcards"}`}
                    className={({ isActive }) => getChapterClasses(isActive)}
                    style={({ isActive }) =>
                      isActive ? { color: "#000000" } : undefined
                    }
                    end={false}
                  >
                    <span className="font-medium">{`Chapter ${idx + 1}: ${c.title}`}</span>
                  </NavLink>
                </li>
              ))}

              <li className="pt-1">
                <button
                  type="button"
                  onClick={() => setModalOpen(true)}
                  className="w-full rounded-lg px-4 py-3 bg-neutral-900 ring-1 ring-neutral-800 hover:bg-neutral-800 hover:ring-neutral-700 flex items-center justify-between"
                >
                  <span>Select New Chapter</span>
                  <span className="text-slate-300" aria-hidden>
                    ＋
                  </span>
                </button>
              </li>
            </ul>
          </nav>
        </div>
      </aside>

      {modalOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70"
          role="dialog"
          aria-modal="true"
          onClick={() => setModalOpen(false)}
        >
          <div
            className="relative w-[22rem] rounded-3xl bg-[#111] px-8 py-6 text-center text-white shadow-2xl ring-1 ring-[#2a2a2a]"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              type="button"
              className="absolute right-2 top-2 flex h-8 w-8 items-center justify-center rounded-full border border-white/60 text-white text-base font-semibold leading-none hover:bg-white/10"
              onClick={() => setModalOpen(false)}
              aria-label="Close"
            >
              ×
            </button>

            <h3 className="mb-6 text-xl font-semibold">Select New Chapter</h3>

            <div className="rounded-2xl border border-white/20 bg-black/40 px-4 py-3 text-left">
              <select
                value={selectedChapterId}
                onChange={(event) => setSelectedChapterId(event.target.value)}
                className="w-full bg-transparent text-white focus:outline-none"
              >
                {chapters.map((chapter, idx) => (
                  <option
                    key={chapter.id}
                    value={chapter.id}
                    className="bg-[#111] text-white"
                  >
                    {`Chapter ${idx + 1}: ${chapter.title}`}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
