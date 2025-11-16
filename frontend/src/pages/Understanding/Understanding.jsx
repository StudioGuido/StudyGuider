import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fakeApi } from "../../services/fakeApi";
import PdfViewer from "./PdfViewer";
import samplePdf from "../../assets/sample.pdf";

export default function Understanding({ defaultMode = "summary" }) {
  const { bookId, chapterId } = useParams();
  const [mode, setMode] = useState(defaultMode); // "summary" | "askai"
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    if (mode === "summary") {
      fakeApi.getSummary(bookId, chapterId).then(setSummary);
    }
  }, [bookId, chapterId, mode]);

  return (
    <section className="grid grid-cols-2 gap-4">
      {/* Left: PDF viewer placeholder */}
      <div className="border rounded p-4">
        <PdfViewer fileUrl={samplePdf} />
      </div>

      {/* Right: Summary / AskAI */}
      <div>
        <div className="mb-3 flex gap-2">
          <button
            className={`px-3 py-2 rounded ${mode === "summary" ? "bg-gray-200" : ""}`}
            onClick={() => setMode("summary")}
          >
            Summary
          </button>
          <button
            className={`px-3 py-2 rounded ${mode === "askai" ? "bg-gray-200" : ""}`}
            onClick={() => setMode("askai")}
          >
            AskAI
          </button>
        </div>

        {mode === "summary" ? (
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
  );
}
