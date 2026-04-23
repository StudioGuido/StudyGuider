import React from "react";
import ReactMarkdown from "react-markdown";

const markdownComponents = {
  h1: (props) => (
    <h1
      className="mt-6 text-xl font-semibold text-white leading-tight first:mt-0"
      {...props}
    />
  ),
  h2: (props) => (
    <h2
      className="mt-6 text-base font-semibold text-white first:mt-0"
      {...props}
    />
  ),
  h3: (props) => (
    <h3
      className="mt-4 text-sm font-semibold text-white first:mt-0"
      {...props}
    />
  ),
  p: (props) => (
    <p className="text-sm leading-relaxed text-slate-300" {...props} />
  ),
  ul: (props) => (
    <ul
      className="list-disc space-y-1 pl-5 text-sm text-slate-300"
      {...props}
    />
  ),
  ol: (props) => (
    <ol
      className="list-decimal space-y-1 pl-5 text-sm text-slate-300"
      {...props}
    />
  ),
  li: (props) => <li className="leading-relaxed" {...props} />,
  strong: (props) => <strong className="font-semibold text-white" {...props} />,
  em: (props) => <em className="italic text-slate-200" {...props} />,
  code: (props) => (
    <code
      className="rounded bg-neutral-800 px-1 py-0.5 text-xs text-slate-200"
      {...props}
    />
  ),
  a: (props) => (
    <a
      className="text-blue-400 underline hover:text-blue-300"
      target="_blank"
      rel="noreferrer"
      {...props}
    />
  ),
};

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
            <ReactMarkdown components={markdownComponents}>
              {summary}
            </ReactMarkdown>
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
