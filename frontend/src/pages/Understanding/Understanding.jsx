import ChapterSidebarNav from "../../components/ChapterSidebar";
import PhaseNavbar from "../../components/PhaseNavbar";
import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { supabase } from "../../services/supabaseClient";
import PdfViewer from "./PdfViewer";
import Summary from "./Summary";
import AskAI from "./AskAI";

const summaryCache = new Map();

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
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryError, setSummaryError] = useState(null);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [pdfError, setPdfError] = useState(null);
  const [bookTitle, setBookTitle] = useState(null);
  // Placeholder until we get chapter titles
  const chapterTitle = `${bookTitle || ""}: Chapter ${chapterId || ""}`;

  useEffect(() => {
    let alive = true;
    async function fetchPdfUrl() {
      const session = await supabase.auth.getSession();
      const token = session.data.session.access_token;

      const res = await fetch(
        `http://localhost:8000/api/textbooks/${bookId}/chapters/${chapterId}/pdf`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (!alive) return;
      if (res.status === 404) {
        setPdfError("Chapter not found");
        return;
      }
      if (!res.ok) {
        setPdfError("Failed to load chapter");
        return;
      }
      const data = await res.json();
      if (alive) setPdfUrl(data.presigned_url);
    }
    setPdfUrl(null);
    setPdfError(null);
    fetchPdfUrl();
    return () => { alive = false; };
  }, [bookId, chapterId]);

  // useEffect to grab textbook title
  useEffect(() => {
    async function fetchTitle() {
      try {
        const session = await supabase.auth.getSession();
        const token = session.data.session.access_token;
        if (!token) throw new Error("Not authenticated");

        const res = await fetch(
          `http://localhost:8000/api/getTextbookTitle?textbook_id=${bookId}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!res.ok) throw new Error("Failed to fetch title");

        const data = await res.json();
        console.log("-------------------------", bookId, "-------------------------")
        console.log("-------------------------", data, "-------------------------")
        setBookTitle(data.title); // assuming backend returns { title: "..." }

      } catch (err) {
        console.error("Error fetching title:", err);
      }
    }

    if (bookId) {
      fetchTitle();
    }
  }, [bookId]);


  const fetchSummary = useCallback(async () => {
    if (!bookId || !chapterId) return;
    const key = `${bookId}:${chapterId}`;
    setSummaryLoading(true);
    setSummaryError(null);
    try {
      const { data: sessionData } = await supabase.auth.getSession();
      const token = sessionData.session?.access_token;
      if (!token) throw new Error("Not authenticated");

      const res = await fetch("http://localhost:8000/api/generateSummary", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          textbook_id: bookId,
          chapter_number: parseInt(chapterId, 10),
        }),
      });

      if (!res.ok) throw new Error("Failed to generate summary");

      const data = await res.json();
      setSummary(data.response);
      summaryCache.set(key, data.response);
    } catch (err) {
      console.error("Error generating summary:", err);
      setSummaryError("Failed to generate summary. Please try again.");
    } finally {
      setSummaryLoading(false);
    }
  }, [bookId, chapterId]);

  useEffect(() => {
    if (mode !== "summary") return;
    if (!bookId || !chapterId) return;
    const cached = summaryCache.get(`${bookId}:${chapterId}`);
    if (cached !== undefined) {
      setSummary(cached);
      setSummaryLoading(false);
      setSummaryError(null);
      return;
    }
    setSummary(null);
    fetchSummary();
  }, [mode, bookId, chapterId, fetchSummary]);

  return (
    <section className="flex-1 grid grid-cols-2 gap-4 min-h-0">
      {/* Left: PDF viewer placeholder */}
      <div className="rounded min-h-0 flex flex-col">
        <PdfViewer fileUrl={pdfUrl} error={pdfError} chapterNumber={chapterId} />
      </div>

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
              summary={summary}
              isLoading={summaryLoading}
              error={summaryError}
              onRegenerate={fetchSummary}
            />
          ) : (
            <AskAI bookId={bookId} chapterId={chapterId} />
          )}
        </div>
      </div>
    </section>
  );
}
