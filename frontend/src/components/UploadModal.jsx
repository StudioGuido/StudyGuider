import React, { useState, useRef } from "react";
import { X, Upload } from "lucide-react";

export default function UploadModal({ onClose, onUpload, error }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef(null);

  function handleFileChange(e) {
    const file = e.target.files[0];
    if (file && file.type === "application/pdf") {
      setSelectedFile(file);
    } else if (file) {
      alert("Please select a valid PDF file.");
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type === "application/pdf") {
      setSelectedFile(file);
    } else if (file) {
      alert("Please select a valid PDF file.");
    }
  }

  async function handleSubmit() {
    if (!selectedFile) return;
    setIsProcessing(true);
    try {
      await onUpload(selectedFile);
    } finally {
      setIsProcessing(false);
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
            disabled={isProcessing}
            className="absolute right-6 top-6 text-sm text-gray-300 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed"
            aria-label="Close"
          >
            <X size={20} color="white" />
          </button>

          <h2 className="text-3xl md:text-4xl font-extrabold leading-tight mb-6">
            Import New Textbook
          </h2>

          <div
            className={`border-2 border-dashed rounded-xl p-10 text-center transition ${
              isProcessing
                ? "border-gray-800 opacity-60 cursor-not-allowed"
                : dragOver
                ? "border-white bg-white/5 cursor-pointer"
                : "border-gray-700 hover:border-gray-500 cursor-pointer"
            }`}
            onClick={() => !isProcessing && fileInputRef.current?.click()}
            onDragOver={(e) => {
              e.preventDefault();
              if (!isProcessing) setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => !isProcessing && handleDrop(e)}
          >
            <Upload size={40} className="mx-auto mb-4 text-gray-400" />
            {selectedFile ? (
              <p className="text-lg text-gray-200">{selectedFile.name}</p>
            ) : (
              <>
                <p className="text-lg text-gray-200">
                  Drag & drop a PDF here, or click to browse
                </p>
                <p className="text-sm text-gray-500 mt-2">Only PDF files are accepted</p>
              </>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="hidden"
            />
          </div>

          {error && (
            <p className="mt-4 text-center text-red-400 text-sm">{error}</p>
          )}

          <div className="flex flex-col items-center mt-8">
            <button
              onClick={handleSubmit}
              disabled={!selectedFile || isProcessing}
              className="w-64 md:w-80 py-5 rounded-3xl bg-transparent border border-gray-700 hover:border-gray-600 text-white text-2xl md:text-3xl font-extrabold disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {isProcessing ? "Processing…" : "Upload"}
            </button>
            {isProcessing && (
              <p className="mt-4 text-sm text-gray-400">
                Processing your textbook. This may take a minute — please don't close this window.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
