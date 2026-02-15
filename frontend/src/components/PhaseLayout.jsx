import { useState } from "react";
import { Outlet, useParams, useNavigate } from "react-router-dom";
import ChapterSidebar from "./ChapterSidebar";
import PhaseNavbar from "./PhaseNavbar";

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

    // setActivePhase(phase);
  };

  return (
    <section className="h-screen flex overflow-hidden">
      <ChapterSidebar activePhase={activePhase} />
      <div className="flex-1 px-8 py-6 flex flex-col gap-6 overflow-hidden min-h-0">
        <PhaseNavbar
          activePhase={activePhase}
          onSelectPhase={handlePhaseSelect}
        />
        <Outlet />
      </div>
    </section>
  );
}
