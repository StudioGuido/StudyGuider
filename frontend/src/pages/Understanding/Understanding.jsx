import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fakeApi } from "../../services/fakeApi";
import PdfViewer from "./PdfViewer";
import Summary from "./Summary";
import AskAI from "./AskAI";
import samplePdf from "../../assets/sample.pdf";

function getTabStyle(isActive) {
  if (isActive) {
    return {
      className: "w-1/2 rounded-full py-2 text-sm font-medium transition",
      style: { backgroundColor: "#ffffff", color: "#000000" },
    };
  }
  return {
    className:
      "w-1/2 rounded-full py-2 text-sm font-medium transition hover:text-white",
    style: { backgroundColor: "transparent", color: "#94a3b8" },
  };
}

export default function Understanding({ defaultMode = "summary" }) {
  const { bookId, chapterId } = useParams();
  const [mode, setMode] = useState(defaultMode);
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    if (mode === "summary") {
      fakeApi
        .getSummary(bookId, chapterId)
        .then((data) => setSummary(data?.text ?? null));
    }
  }, [bookId, chapterId, mode]);

  const bookTitle = "Sample Book Title";
  const chapterTitle = "Chapter 1: Introduction";

  return (
    <section className="grid grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)] gap-6">
      {/* Left: PDF card */}
      <PdfViewer fileUrl={samplePdf} />

      {/* Right: Summary / AskAI */}
      <div className="flex h-[70vh] flex-col rounded-3xl border border-neutral-800 bg-[#0a0a0f] px-5 pt-4 pb-4 text-slate-100">
        <div className="w-full">
          <div className="flex w-full rounded-full bg-neutral-900 p-1">
            <button
              {...getTabStyle(mode === "summary")}
              onClick={() => setMode("summary")}
            >
              Summary
            </button>
            <button
              {...getTabStyle(mode === "askai")}
              onClick={() => setMode("askai")}
            >
              AskAI
            </button>
          </div>
        </div>

        <div className="mt-4 flex-1 overflow-hidden">
          {mode === "summary" ? (
            <Summary
              bookTitle={bookTitle}
              chapterTitle={chapterTitle}
              initialSummary={summary}
            />
          ) : (
            <AskAI bookTitle={bookTitle} chapterTitle={chapterTitle} />
          )}
        </div>
      </div>
    </section>
  );
}
