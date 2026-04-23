import { Outlet, useParams, useNavigate, useLocation } from "react-router-dom";
import ChapterSidebar from "./ChapterSidebar";
import PhaseNavbar from "./PhaseNavbar";
import { supabase } from "../services/supabaseClient";

function getPhaseFromPath(pathname) {
  if (pathname.includes("/mastery")) return "mastery";
  if (pathname.includes("/reinforce/quiz")) return "reinforcing";
  if (pathname.includes("/reinforce/flashcards")) return "reinforcing";
  return "understanding";
}

export default function PhaseLayout() {
  const { bookId, chapterId } = useParams();
  const location = useLocation();
  const activePhase = getPhaseFromPath(location.pathname);
  const navigate = useNavigate();

  const handlePhaseSelect = (phase) => {
    if (phase === "understanding") {
      navigate(`/books/${bookId}/chapters/${chapterId}/understanding`);
      return;
    }

    if (phase === "reinforcing") {
      navigate(`/books/${bookId}/chapters/${chapterId}/reinforce/flashcards`);
      return;
    }

    if (phase === "mastery") {
      navigate(`/books/${bookId}/chapters/${chapterId}/mastery`);
      return;
    }
  };

  const handleSignOut = async () => {
    await supabase.auth.signOut();
  };

  return (
    <section className="h-screen flex overflow-hidden">
      <ChapterSidebar activePhase={activePhase} />
      <div className="flex-1 px-8 py-6 flex flex-col gap-6 overflow-hidden min-h-0">
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigate("/books")}
            className="bg-neutral-800 hover:bg-neutral-700 text-white px-4 py-2 rounded text-sm transition-colors"
          >
            &larr; Books
          </button>
          <button
            onClick={handleSignOut}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded text-sm transition-colors"
          >
            Sign Out
          </button>
        </div>
        <PhaseNavbar
          activePhase={activePhase}
          onSelectPhase={handlePhaseSelect}
        />
        <Outlet />
      </div>
    </section>
  );
}
