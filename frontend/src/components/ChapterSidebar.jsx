import { useEffect, useState } from "react";
import { NavLink, useParams, useLocation } from "react-router-dom";
import { supabase } from "../services/supabaseClient";

function getPhaseSuffixFromPath(pathname) {
  if (pathname.includes("/mastery")) return "mastery";
  if (pathname.includes("/reinforce/quiz")) return "reinforce/quiz";
  if (pathname.includes("/reinforce/flashcards")) return "reinforce/flashcards";
  if (pathname.includes("/understanding/ask-ai")) return "understanding/ask-ai";
  return "understanding";
}

export default function ChapterSidebar({ className = "", activePhase }) {
  const { bookId } = useParams();
  const location = useLocation();
  const [chapters, setChapters] = useState([]);
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    let alive = true;
    async function fetchChapters() {
      const session = await supabase.auth.getSession();
      const token = session.data.session.access_token;

      const res = await fetch(
        `http://localhost:8000/api/getChapters?textbook_id=${bookId}`,
        { headers: { Authorization: `Bearer ${token}` } },
      );
      const data = await res.json();
      if (alive) setChapters(data.response);
    }
    fetchChapters();
    return () => {
      alive = false;
    };
  }, [bookId]);

  const phaseToPath = {
    understanding: "understanding",
    reinforcing: "reinforce/flashcards",
    mastery: "mastery",
  };
  const defaultPhaseSuffix = phaseToPath[activePhase] ?? "understanding";
  const phaseSuffix =
    getPhaseSuffixFromPath(location.pathname) || defaultPhaseSuffix;

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
          "shrink-0 h-screen sticky top-0 overflow-hidden transition-all duration-300 flex flex-col min-h-0",
          "bg-neutral-950 text-slate-50 border-r border-neutral-800",
          collapsed ? "w-14" : "w-80",
          className,
        ].join(" ")}
        aria-label="Chapter navigation"
      >
        <div className="flex items-center justify-between pr-2 pl-2 pt-7 pb-2">
          <button
            type="button"
            onClick={() => setCollapsed((c) => !c)}
            className="flex h-8 w-8 items-center justify-center rounded-md hover:bg-neutral-800 transition-colors"
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            <span className="text-lg leading-none">&#9776;</span>
          </button>
          <div className="flex-1 px-3">
            <h2 className="text-xl font-semibold">Chapters</h2>
          </div>
        </div>

        <div
          className={`flex-1 min-h-0 transition-opacity duration-300 ${collapsed ? "opacity-0 pointer-events-none" : "opacity-100"}`}
        >
          <nav className="p-3 overflow-y-auto h-full">
            <ul className="space-y-2">
              {chapters.map((chapter, idx) => (
                <li key={chapter.number}>
                  <NavLink
                    to={`/books/${bookId}/chapters/${chapter.number}/${phaseSuffix}`}
                    className={({ isActive }) => getChapterClasses(isActive)}
                    style={({ isActive }) =>
                      isActive ? { color: "#000000" } : undefined
                    }
                    end={false}
                  >
                    <span className="font-medium">{chapter.title}</span>
                  </NavLink>
                </li>
              ))}
            </ul>
          </nav>
        </div>
      </aside>
    </>
  );
}
