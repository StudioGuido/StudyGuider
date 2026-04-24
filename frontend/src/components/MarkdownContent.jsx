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
      className="rounded bg-neutral-800 px-1 py-0.5 text-xs text-slate-200 break-all"
      {...props}
    />
  ),
  pre: (props) => (
    <pre
      className="my-2 max-w-full overflow-x-auto rounded bg-neutral-800 p-2 text-xs text-slate-200 whitespace-pre-wrap break-words"
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

export default function MarkdownContent({ children }) {
  return (
    <ReactMarkdown components={markdownComponents}>{children}</ReactMarkdown>
  );
}
