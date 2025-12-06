import ChapterSidebarNav from "../../components/ChapterSidebar";
import PhaseNavbar from "../../components/PhaseNavbar";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fakeApi } from "../../services/fakeApi";
import PdfViewer from "./PdfViewer";
import samplePdf from "../../assets/sample.pdf";


export default function Understanding() {
  const { bookId, chapterId } = useParams();
  const [activePhase, setActivePhase] = useState("understanding");

  const [summary, setSummary] = useState(null);

  useEffect(() => {
    if (activePhase === "summary") {
      fakeApi.getSummary(bookId, chapterId).then(setSummary);
    }
  }, [bookId, chapterId, activePhase]);

  return (

    <section className="h-screen flex overflow-hidden">
      <ChapterSidebarNav />
      <div className="flex-1 px-8 py-6 flex flex-col gap-6 overflow-hidden min-h-0">
        <PhaseNavbar activePhase={activePhase} onSelectPhase={setActivePhase} />

        <section className="flex-1 grid grid-cols-2 gap-4 min-h-0">
          {/* Left: PDF viewer placeholder */}
          <div className="rounded p-4 bg-slate-950 min-h-0 flex flex-col">
            <PdfViewer fileUrl={samplePdf} />
          </div>

          {/* Right: Summary / AskAI */}
          <div className="border border-neutral-800 rounded-xl p-4 flex flex-col min-h-0">
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

            <div className="flex-1 min-h-0">
              {activePhase === "summary" ? (
                <div className="rounded p-4 h-full overflow-auto whitespace-pre-wrap">
                  {summary?.text ?? "No summary yet."}
                </div>
              ) : (
                <div className="rounded p-4 h-full overflow-auto">
                  <p className="mb-2 text-sm text-gray-600">AskAI (mock):</p>
                  <div className="text-gray-800">
                    Q: What’s the gist of this chapter?
                    <br />
                    A: (Pretend AI answer goes here.)
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>
      </div>
    </section>
  );
}
