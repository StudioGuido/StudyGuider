import React from "react";
import { useNavigate } from "react-router-dom";
import { fakeApi } from "../services/fakeApi";
import { X } from 'lucide-react';

export default function BookModal({ book, onClose }) {
  const navigate = useNavigate();
  if (!book) return null;

  const goToFirstChapter = async () => {
    const chapters = await fakeApi.getChapters(book.id);
    const first = chapters[0];
    if (first) {
      navigate(`/books/${book.id}/chapters/${first.id}/understanding`);
      return true;
    }
    return false;
  };

  async function handleStart() {
    onClose();
    const navigated = await goToFirstChapter();
    if (!navigated) {
      navigate(`/books/${book.id}/chapters`);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4 py-8">
      <div
        className="absolute inset-0 bg-black/60"
        onClick={onClose}
        aria-hidden
      />

      <div className="relative w-full max-w-3xl text-white pointer-events-auto">
        <div className="bg-[#121212] border border-[#3D3D3D] rounded-2xl p-8 shadow-xl max-h-[75vh] overflow-auto">
          <button
            onClick={onClose}
            className="absolute right-6 top-6 text-sm text-gray-300 hover:text-white"
            aria-label="Close"
          >
            <X size={20} color="white" />
          </button>

          <h2 className="text-3xl md:text-4xl font-extrabold leading-tight mb-2">
            {book.title}
          </h2>

          <div className="text-lg text-gray-300 mb-6">
            {Array.isArray(book.author) ? book.author.join(", ") : book.author}
          </div>

          <p className="text-base md:text-lg text-gray-200 mb-10 leading-relaxed">
            "{book.description}"
          </p>

          <div className="flex justify-center">
            <button
              onClick={handleStart}
              className="w-64 md:w-80 py-5 rounded-3xl bg-transparent border border-gray-700 hover:border-gray-600 text-white text-2xl md:text-3xl font-extrabold"
            >
              Get Started
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
