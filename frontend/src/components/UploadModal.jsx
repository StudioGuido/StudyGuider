import React, { useState, useRef } from "react";
import { X, Upload } from "lucide-react";

export default function UploadModal({ onClose, onUpload }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
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

  function handleSubmit() {
    if (selectedFile) {
      onUpload(selectedFile);
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

          <h2 className="text-3xl md:text-4xl font-extrabold leading-tight mb-6">
            Import New Textbook
          </h2>

          <div
            className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition ${
              dragOver
                ? "border-white bg-white/5"
                : "border-gray-700 hover:border-gray-500"
            }`}
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
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

          <div className="flex justify-center mt-8">
            <button
              onClick={handleSubmit}
              disabled={!selectedFile}
              className="w-64 md:w-80 py-5 rounded-3xl bg-transparent border border-gray-700 hover:border-gray-600 text-white text-2xl md:text-3xl font-extrabold disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Upload
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
