const defaultPhases = [
  { key: "understanding", title: "Understanding", subtitle: "Phase 1" },
  { key: "reinforcing", title: "Reinforcing", subtitle: "Phase 2" },
  { key: "mastery", title: "Mastery", subtitle: "Phase 3" },
];

function getPhaseButtonStyle(isActive) {
  if (isActive) {
    return {
      className:
        "flex flex-col items-center justify-center rounded-xl px-6 py-4 text-sm font-semibold transition border shadow-lg border-white bg-white text-black",
      style: { backgroundColor: "#ffffff", color: "#000000ff" },
    };
  }

  return {
    className:
      "flex flex-col items-center justify-center rounded-xl px-6 py-4 text-sm font-semibold transition border border-neutral-800 bg-neutral-900 text-slate-100 hover:bg-neutral-800",
    style: { backgroundColor: "#0f0f0f", color: "#ffffffff" },
  };
}

export default function PhaseNavbar({
  phases = defaultPhases,
  activePhase,
  onSelectPhase,
}) {
  return (
    <div className="w-full rounded-2xl border border-neutral-800 bg-black/60 p-5 shadow-lg">
      <div className="grid grid-cols-3 gap-3">
        {phases.map((phase) => {
          const isActive = phase.key === activePhase;
          return (
            <button
              key={phase.key}
              type="button"
              onClick={() => onSelectPhase(phase.key)}
              {...getPhaseButtonStyle(isActive)}
            >
              <span
                className={`text-lg font-semibold ${isActive ? "text-black" : "text-slate-100"}`}
              >
                {phase.title}
              </span>
              <span
                className={`text-xs font-medium ${isActive ? "text-black" : "text-slate-400"}`}
              >
                {phase.subtitle}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
