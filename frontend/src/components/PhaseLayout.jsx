import { useState } from "react";
import { Outlet, useParams, useNavigate } from "react-router-dom";
import ChapterSidebar from "./ChapterSidebar";
import PhaseNavbar from "./PhaseNavbar";
import { supabase } from "../services/supabaseClient";

export default function PhaseLayout() {
  const [activePhase, setActivePhase] = useState("understanding");
  const { bookId, chapterId } = useParams();
  const navigate = useNavigate();

  const handlePhaseSelect = (phase) => {
    if (phase === "understanding") {
      navigate(`/books/${bookId}/chapters/${chapterId}/understanding`);
      setActivePhase(phase);
      return;
    }

    if (phase === "reinforcing") {
      navigate(`/books/${bookId}/chapters/${chapterId}/reinforce/flashcards`);
      setActivePhase(phase);
      return;
    }

    if (phase === "mastery") {
      navigate(`/books/${bookId}/chapters/${chapterId}/mastery`);
      setActivePhase(phase);
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
