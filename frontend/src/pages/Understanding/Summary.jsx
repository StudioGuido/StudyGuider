import React from "react";
import MarkdownContent from "../../components/MarkdownContent";

export default function Summary({
  summary,
  isLoading,
  error,
  onRegenerate,
}) {
  const showSkeleton = isLoading || (!summary && !error);

  return (
    <div className="flex h-full flex-col text-slate-100">
      <div className="flex-1 overflow-auto pr-2">
        {showSkeleton ? (
          <div className="space-y-3 p-2">
            <div className="h-6 w-3/4 animate-pulse rounded bg-neutral-700" />
            <div className="h-4 w-full animate-pulse rounded bg-neutral-700" />
            <div className="h-4 w-5/6 animate-pulse rounded bg-neutral-700" />
            <div className="h-4 w-4/6 animate-pulse rounded bg-neutral-700" />
            <div className="mt-6 h-5 w-1/2 animate-pulse rounded bg-neutral-700" />
            <div className="h-4 w-full animate-pulse rounded bg-neutral-700" />
            <div className="h-4 w-3/4 animate-pulse rounded bg-neutral-700" />
          </div>
        ) : error ? (
          <div className="space-y-3 p-2">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        ) : (
          <div className="space-y-4">
            <MarkdownContent>{summary}</MarkdownContent>
          </div>
        )}
      </div>

      <button
        className="mt-4 w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        onClick={onRegenerate}
        disabled={isLoading}
      >
        {isLoading ? "Generating..." : "Regenerate Summary"}
      </button>
    </div>
  );
}
