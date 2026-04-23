import React from "react";
import { useState } from "react";

export default function Summary({ chapterTitle }) {
  const [isLoading, setIsLoading] = useState(false);

  const summaryContent = {
    title: chapterTitle || "Chapter 1: Introduction",
    sections: [
      {
        heading: "Overview",
        content:
          "This chapter introduces the fundamental concepts and provides context for the topics covered throughout the book.",
      },
      {
        heading: "Key Concepts",
        content:
          "The main ideas and terminology that form the foundation for understanding subsequent chapters.",
      },
    ],
  };

  const handleRegenerate = () => {
    setIsLoading(true);
    // Simulate API call delay
    setTimeout(() => {
      setIsLoading(false);
    }, 2000);
  };
  const regenerateSummary = handleRegenerate;

  return (
    <div className="flex h-full flex-col text-slate-100">
      {/* Scrollable content area */}
      <div className="flex-1 overflow-auto pr-2">
        {isLoading ? (
          <div className="space-y-3 p-2">
            <div className="h-6 w-3/4 animate-pulse rounded bg-neutral-700" />
            <div className="h-4 w-full animate-pulse rounded bg-neutral-700" />
            <div className="h-4 w-5/6 animate-pulse rounded bg-neutral-700" />
            <div className="h-4 w-4/6 animate-pulse rounded bg-neutral-700" />
            <div className="mt-6 h-5 w-1/2 animate-pulse rounded bg-neutral-700" />
            <div className="h-4 w-full animate-pulse rounded bg-neutral-700" />
            <div className="h-4 w-3/4 animate-pulse rounded bg-neutral-700" />
          </div>
        ) : (
          <div className="space-y-6">
            {/* Chapter title */}
            <h1 className="text-xl font-semibold text-white leading-tight">
              {summaryContent.title}
            </h1>

            {/* Sections */}
            {summaryContent.sections.map((section, index) => (
              <div key={index} className="space-y-3">
                <h2 className="text-base font-semibold text-white">
                  {section.heading}
                </h2>
                <div className="text-sm leading-relaxed text-slate-300 whitespace-pre-line">
                  {section.content}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      <button className="mt-4 w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition" onClick={regenerateSummary}>
        Regenerate Summary
      </button>
    </div>
  );
}
