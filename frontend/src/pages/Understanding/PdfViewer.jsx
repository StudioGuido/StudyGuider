import React from "react";
import { useState, useEffect } from "react";
import { Document, Page } from "react-pdf";
import "./pdf-worker-setup";

export default function PdfViewer({ fileUrl, initialScale = 1 }) {
  const [numPages, setNumPages] = useState(0);
  const [page, setPage] = useState(1);
  const [scale, setScale] = useState(initialScale);

  console.log("PdfViewer rendering with fileUrl:", fileUrl);

  const onDocumentLoad = ({ numPages }) => {
    console.log("PDF loaded with", numPages, "pages");
    setNumPages(numPages);
  };

  const zoomIn = () =>
    setScale((s) => Math.min(Math.round(s * 1.1 * 10) / 10, 3));
  const zoomOut = () =>
    setScale((s) => Math.max(Math.round(s * 0.9 * 10) / 10, 0.5));
  const goPrev = () => setPage((p) => Math.max(p - 1, 1));
  const goNext = () => setPage((p) => Math.min(p + 1, numPages || 1));

  useEffect(() => {
    if (numPages && page > numPages) setPage(numPages);
  }, [numPages, page, setPage]);

  return (
    <div className="flex h-screen flex-col bg-slate-950 text-slate-100">
      {/* Top toolbar */}
      <div className="sticky top-0 z-10 flex items-center gap-2 border-b border-slate-800 bg-slate-900/95 px-4 py-2 backdrop-blur">
        {/* Pagination controls */}
        <button
          onClick={goPrev}
          disabled={page <= 1}
          className="rounded-md border border-slate-700 px-3 py-1 text-sm disabled:cursor-not-allowed disabled:opacity-40 hover:bg-slate-800 transition"
        >
          Prev
        </button>

        <span className="text-sm text-slate-200">
          Page <br></br> <span className="font-semibold">{page}</span>{" "}
          <span className="text-slate-400">/ {numPages || "—"}</span>
        </span>

        <button
          onClick={goNext}
          disabled={!numPages || page >= numPages}
          className="rounded-md border border-slate-700 px-3 py-1 text-sm disabled:cursor-not-allowed disabled:opacity-40 hover:bg-slate-800 transition"
        >
          Next
        </button>

        {/* Divider */}
        <div className="mx-3 h-5 w-px bg-slate-700" />

        {/* Zoom controls */}
        <button
          onClick={zoomOut}
          className="flex h-8 w-8 items-center justify-center rounded-md border border-slate-700 text-lg leading-none hover:bg-slate-800 transition"
        >
          –
        </button>
        <span className="w-14 text-center text-sm text-slate-200">
          {Math.round(scale * 100)}%
        </span>
        <button
          onClick={zoomIn}
          className="flex h-8 w-8 items-center justify-center rounded-md border border-slate-700 text-lg leading-none hover:bg-slate-800 transition"
        >
          +
        </button>

        {/* Right-aligned label */}
        <div className="ml-auto text-xs uppercase tracking-wide text-slate-400">
          PDF Viewer
        </div>
      </div>

      {/* Scrollable content area */}
      <div className="flex-1 overflow-auto bg-slate-900 p-4">
        <div className="flex justify-center">
          <Document
            file={fileUrl}
            onLoadSuccess={onDocumentLoad}
            loading={<div className="text-sm text-slate-300">Loading PDF…</div>}
          >
            <Page
              pageNumber={page}
              scale={scale}
              renderAnnotationLayer={false}
              renderTextLayer={false}
              className="shadow-xl shadow-black/40"
            />
          </Document>
        </div>
      </div>
    </div>
  );
}
