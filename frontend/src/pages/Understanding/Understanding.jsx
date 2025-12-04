import ChapterSidebarNav from "../../components/ChapterSidebar";
import PhaseNavbar from "../../components/PhaseNavbar";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fakeApi } from "../../services/fakeApi";
import PdfViewer from "./PdfViewer";
import samplePdf from "../../assets/sample.pdf";


export default function Understanding() {
  const [activePhase, setActivePhase] = useState("understanding");
  // const [mode, setMode] = useState(defaultMode); // "summary" | "askai"

  return (

    <section className="grid grid-cols-[20rem_1fr] gap-6">
      <ChapterSidebarNav />
      <div className="flex flex-col gap-6">
        
        <PhaseNavbar activePhase={activePhase} onSelectPhase={setActivePhase} />
      </div>
      
        {/* {activePhase === "understanding" && (
          <div className="w-full rounded-3xl border border-neutral-800 bg-neutral-950 p-6 text-slate-200 shadow-lg">
            <div className="flex min-h-[70vh] items-center justify-center rounded-2xl border border-dashed border-neutral-700 bg-neutral-900">
              <span className="text-sm text-slate-400">PDF viewer placeholder</span> */}

    <section className="grid grid-cols-2 gap-4">
      {/* Left: PDF viewer placeholder */}
      <div className="border rounded p-4">
        <PdfViewer fileUrl={samplePdf} />
      </div>

      {/* Right: Summary / AskAI */}
      <div>
        <div className="mb-3 flex gap-2">
          <button
            className={`px-3 py-2 rounded ${activePhase === "summary" ? "bg-gray-200" : ""}`}
            onClick={() => setActivePhase("summary")}
          >
            Summary
          </button>
          <button
            className={`px-3 py-2 rounded ${activePhase === "askai" ? "bg-gray-200" : ""}`}
            onClick={() => setActivePhase("askai")}
          >
            AskAI
          </button>
        </div>

        {activePhase === "summary" ? (
          <div className="border rounded p-4 h-[60vh] overflow-auto whitespace-pre-wrap">
            {summary?.text ?? "No summary yet."}
          </div>
        ) : (
          <div className="border rounded p-4 h-[60vh]">
            <p className="mb-2 text-sm text-gray-600">AskAI (mock):</p>
            <div className="text-gray-800">
              Q: What’s the gist of this chapter?
              <br />
              A: (Pretend AI answer goes here.)
            </div>
          </div>
        )}
      </div>
    </section>
    </section>
  );
}
