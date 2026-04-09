import React from "react";
import { useState, useRef, useEffect } from "react";
import { Document, Page } from "react-pdf";
import "./pdf-worker-setup";

const RENDER_WIDTH = 800; // fixed rasterisation width — never changes

export default function PdfViewer({ fileUrl, initialScale = 1 }) {
  const [numPages, setNumPages] = useState(0);
  const [scale, setScale] = useState(initialScale);
  const [containerWidth, setContainerWidth] = useState(0);
  const containerRef = useRef(null);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const observer = new ResizeObserver(([entry]) => {
      setContainerWidth(entry.contentRect.width - 32); // subtract px-4 padding
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  const onDocumentLoad = ({ numPages }) => {
    setNumPages(numPages);
  };

  // CSS scale factor: at 100% zoom the page fits the container width
  const cssScale = containerWidth > 0 ? (containerWidth / RENDER_WIDTH) * scale : 1;

  const zoomIn = () =>
    setScale((s) => Math.min(Math.round(s * 1.1 * 10) / 10, 3));
  const zoomOut = () =>
    setScale((s) => Math.max(Math.round(s * 0.9 * 10) / 10, 0.5));

  return (
    <div className="flex h-[70vh] flex-col rounded-3xl border border-neutral-800 bg-[#050509] text-slate-100 overflow-hidden">
      {/* Top toolbar */}
      <div className="flex items-center gap-2 border-b border-neutral-800 bg-black/40 px-4 py-2">
        {/* Page count */}
        <span className="text-xs text-slate-300">
          {numPages ? `${numPages} pages` : "Loading..."}
        </span>

        {/* Divider */}
        <div className="mx-3 h-5 w-px bg-neutral-800" />

        {/* Zoom controls */}
        <button
          onClick={zoomOut}
          className="flex h-7 w-7 items-center justify-center rounded-md border border-neutral-700 text-sm leading-none hover:bg-neutral-800 transition"
        >
          –
        </button>
        <span className="w-12 text-center text-xs text-slate-200">
          {Math.round(scale * 100)}%
        </span>
        <button
          onClick={zoomIn}
          className="flex h-7 w-7 items-center justify-center rounded-md border border-neutral-700 text-sm leading-none hover:bg-neutral-800 transition"
        >
          +
        </button>

        {/* Right-aligned label */}
        <div className="ml-auto text-[10px] uppercase tracking-wide text-slate-500">
          PDF Viewer
        </div>
      </div>

      {/* Scrollable content area with all pages */}
      <div ref={containerRef} className="flex-1 overflow-auto bg-[#050509] py-3">
        <Document
          file={fileUrl}
          onLoadSuccess={onDocumentLoad}
          loading={
            <div className="px-4 text-xs text-slate-300">Loading textbook…</div>
          }
        >
          <div className="inline-flex min-w-full flex-col items-center gap-4 px-4">
            {Array.from({ length: numPages }, (_, index) => (
              <div
                key={index + 1}
                style={{
                  width: RENDER_WIDTH * cssScale,
                  height: "auto",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    transform: `scale(${cssScale})`,
                    transformOrigin: "top left",
                    transition: "transform 0.3s ease",
                  }}
                >
                  <Page
                    pageNumber={index + 1}
                    width={RENDER_WIDTH}
                    renderAnnotationLayer={false}
                    renderTextLayer={false}
                    className="shadow-2xl shadow-black/70"
                  />
                </div>
              </div>
            ))}
          </div>
        </Document>
      </div>
    </div>
  );
}
