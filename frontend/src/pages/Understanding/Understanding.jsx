import { useState } from "react";
import ChapterSidebarNav from "../../components/ChapterSidebar";
import PhaseNavbar from "../../components/PhaseNavbar";

export default function Understanding() {
  const [activePhase, setActivePhase] = useState("understanding");

  return (
    <section className="grid grid-cols-[20rem_1fr] gap-6">
      <ChapterSidebarNav />
      <div className="flex flex-col gap-6">
        <PhaseNavbar activePhase={activePhase} onSelectPhase={setActivePhase} />

        {activePhase === "understanding" && (
          <div className="w-full rounded-3xl border border-neutral-800 bg-neutral-950 p-6 text-slate-200 shadow-lg">
            <div className="flex min-h-[70vh] items-center justify-center rounded-2xl border border-dashed border-neutral-700 bg-neutral-900">
              <span className="text-sm text-slate-400">PDF viewer placeholder</span>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
