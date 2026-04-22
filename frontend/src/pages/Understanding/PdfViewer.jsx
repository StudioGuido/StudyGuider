import React from "react";
import { useState, useRef, useEffect } from "react";
import { Document, Page } from "react-pdf";
import "./pdf-worker-setup";

const RENDER_WIDTH = 800; // fixed rasterisation width — never changes

export default function PdfViewer({ fileUrl, initialScale = 1, error = null }) {
  const [numPages, setNumPages] = useState(0);
  const [scale, setScale] = useState(initialScale);
  const [containerWidth, setContainerWidth] = useState(0);
  const [pageHeight, setPageHeight] = useState(0);
  const [animateTransform, setAnimateTransform] = useState(false);
  const containerRef = useRef(null);
  const animateTimerRef = useRef(null);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    let initialized = false;
    const observer = new ResizeObserver(([entry]) => {
      const w = entry.contentRect.width - 32; // subtract px-4 padding
      setContainerWidth(w);
      // Only animate after the initial measurement, not on zoom
      if (initialized) {
        setAnimateTransform(true);
        clearTimeout(animateTimerRef.current);
        animateTimerRef.current = setTimeout(() => setAnimateTransform(false), 350);
      }
      initialized = true;
    });
    observer.observe(el);
    return () => {
      observer.disconnect();
      clearTimeout(animateTimerRef.current);
    };
  }, []);

  const onDocumentLoad = ({ numPages }) => {
    setNumPages(numPages);
  };

  // CSS scale factor: at 100% zoom the page fits the container width
  const cssScale = containerWidth > 0 ? (containerWidth / RENDER_WIDTH) * scale : 1;

  const MIN_SCALE = 0.5;
  const MAX_SCALE = 3;
  const zoomIn = () =>
    setScale((s) => Math.min(Math.round(s * 1.1 * 10) / 10, MAX_SCALE));
  const zoomOut = () =>
    setScale((s) => Math.max(Math.round(s * 0.9 * 10) / 10, MIN_SCALE));
  const canZoomIn = scale < MAX_SCALE;
  const canZoomOut = scale > MIN_SCALE;

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
          onClick={canZoomOut ? zoomOut : undefined}
          aria-disabled={!canZoomOut}
          title={canZoomOut ? "Zoom out" : "Minimum zoom reached"}
          className={`flex h-7 w-7 items-center justify-center rounded-md border text-sm leading-none transition ${
            canZoomOut
              ? "border-neutral-700 hover:bg-neutral-800"
              : "cursor-not-allowed! border-neutral-800 text-slate-600"
          }`}
        >
          –
        </button>
        <span className="w-12 text-center text-xs text-slate-200">
          {Math.round(scale * 100)}%
        </span>
        <button
          onClick={canZoomIn ? zoomIn : undefined}
          aria-disabled={!canZoomIn}
          title={canZoomIn ? "Zoom in" : "Maximum zoom reached"}
          className={`flex h-7 w-7 items-center justify-center rounded-md border text-sm leading-none transition ${
            canZoomIn
              ? "border-neutral-700 hover:bg-neutral-800"
              : "cursor-not-allowed! border-neutral-800 text-slate-600"
          }`}
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
        {error ? (
          <div className="flex h-full items-center justify-center px-4 text-sm text-slate-400">
            {error}
          </div>
        ) : !fileUrl ? (
          <div className="flex h-full items-center justify-center px-4 text-xs text-slate-300">
            Loading chapter…
          </div>
        ) : (
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
                    height: pageHeight ? pageHeight * cssScale : "auto",
                    overflow: "hidden",
                    transition: animateTransform ? "width 0.3s ease, height 0.3s ease" : "none",
                  }}
                >
                  <div
                    style={{
                      transform: `scale(${cssScale})`,
                      transformOrigin: "top left",
                      transition: animateTransform ? "transform 0.3s ease" : "none",
                    }}
                  >
                    <Page
                      pageNumber={index + 1}
                      width={RENDER_WIDTH}
                      onLoadSuccess={index === 0 ? (page) => setPageHeight(page.height) : undefined}
                      renderAnnotationLayer={false}
                      renderTextLayer={false}
                      className="shadow-2xl shadow-black/70"
                    />
                  </div>
                </div>
              ))}
            </div>
          </Document>
        )}
      </div>
    </div>
  );
}
