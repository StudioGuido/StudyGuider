import { Link } from "react-router-dom";
import { useEffect, useRef, useState } from "react";
import { MoreVertical, Trash2 } from "lucide-react";

export default function BookCard({ book, onSelect, onDelete }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    if (!menuOpen) return;
    function handleClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [menuOpen]);

  const handleDeleteClick = (e) => {
    e.stopPropagation();
    setMenuOpen(false);
    onDelete?.(book);
  };

  const content = (
    <div className="flex items-center justify-between gap-4 p-4 rounded-xl hover:border-gray-600 transition-colors">
      <div className="flex items-center gap-4">
        <div className="text-lg font-semibold">{book.title}</div>
        <div className="text-xl">{book.emoji ?? "📘"}</div>
      </div>
      <div className="text-sm text-gray-400 text-right">
        {Array.isArray(book.author) ? book.author.join(", ") : book.author}
      </div>
    </div>
  );

  return (
    <li className="relative">
      {onSelect ? (
        <button
          onClick={() => onSelect(book)}
          className="block w-full text-left pr-12"
          type="button"
        >
          {content}
        </button>
      ) : (
        <Link to={`/books/${book.id}/chapters`} className="block w-full pr-12">
          {content}
        </Link>
      )}

      {onDelete && (
        <div
          ref={menuRef}
          className="absolute right-3 top-1/2 -translate-y-1/2 z-20"
        >
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              setMenuOpen((open) => !open);
            }}
            className="flex h-9 w-9 items-center justify-center rounded-md border border-neutral-700 bg-neutral-900 text-white hover:bg-neutral-800 transition-colors"
            aria-label="Book options"
          >
            <MoreVertical strokeWidth={2.5} className="h-[22px] w-[22px] shrink-0" />
          </button>

          {menuOpen && (
            <div
              className="absolute right-0 top-10 z-10 w-36 rounded-lg border border-neutral-700 bg-neutral-900 shadow-lg py-1"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                type="button"
                onClick={handleDeleteClick}
                className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-red-400 hover:bg-neutral-800 transition-colors"
              >
                <Trash2 size={16} />
                Delete
              </button>
            </div>
          )}
        </div>
      )}
    </li>
  );
}
