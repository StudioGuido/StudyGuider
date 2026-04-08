import { fakeApi } from "../../services/fakeApi";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { supabase } from '../../services/supabaseClient';
import BookCard from "../../components/BookCard";
import BookModal from "../../components/BookModal";
import UploadModal from "../../components/UploadModal";

export default function Books() {
  const [books, setBooks] = useState(null);
  const [selectedBook, setSelectedBook] = useState(null);
  const { user } = useAuth();
  const navigate = useNavigate();
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [status, setStatus] = useState("");

  useEffect(() => {
    fakeApi.getBooks().then(setBooks);
    console.log(user);
  }, []);
  
  if (!books)
    return (
      <p className="min-h-screen flex items-center justify-center text-white">
        Loading…
      </p>
    );

async function handleUpload(file) {
  try {
    // 1) Get a fresh token directly — don't rely on state which may be null
    const { data: sessionData } = await supabase.auth.getSession();
    const currentToken = sessionData.session?.access_token;
    if (!currentToken) throw new Error("Not authenticated");

    // 2) Get presigned URL
    const res = await fetch("http://localhost:8000/api/getPresignedUrl", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${currentToken}`,
      },
    });
    if (!res.ok) throw new Error("Failed to get upload URL");
    const { presigned_url, book_id, file_key } = await res.json();

    console.log(presigned_url)

    // 3) Upload file directly to S3
    const uploadRes = await fetch(presigned_url, {
      method: "PUT",
      body: file,
      headers: { "Content-Type":  "application/pdf" },
    });
    if (!uploadRes.ok) throw new Error("S3 upload failed");

    console.log("Upload good!")
    // 4) Notify backend to start processing
    const processResponse = await fetch("http://localhost:8000/process-pdf", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ book_id, file_key }),
    });
    if (!processResponse.ok) throw new Error("Failed to start processing");
    const processData = await processResponse.json();
    console.log(processData.message);

    // 5) Poll until complete
    await pollStatus(book_id, currentToken);

    setShowUploadModal(false);
  } catch (err) {
    console.error("Upload error:", err);
    const message = err.message === "Failed to fetch"
      ? "Could not connect to the server. Please try again later."
      : err.message;
    setUploadError(message);
  }
}

async function pollStatus(textbookId, currentToken) {
  const MAX_ATTEMPTS = 60; // 3 min at 3s intervals
  for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt++) {
    const res = await fetch(`/api/textbooks/${textbookId}/status`, {
      headers: { Authorization: `Bearer ${currentToken}` },
    });
    if (!res.ok) throw new Error("Failed to fetch status");

    const data = await res.json();
    setStatus(data.status);

    if (data.status === "complete") return;
    if (data.status === "failed") throw new Error("Processing failed");

    await new Promise((r) => setTimeout(r, 3000));
  }
  throw new Error("Processing timed out");
}

  return (
    <main className="min-h-screen text-white flex items-center justify-center px-4">
      <section className="w-full max-w-2xl">
        <header className="text-center mb-6">
          <h1 className="text-4xl font-extrabold">Welcome, {user?.user_metadata?.firstName || user?.email || "User"}!</h1>
          <p className="text-gray-300 mt-2">
            Please select the textbook you want to access
          </p>
        </header>

        <div className="bg-[#0b0b0b] border border-gray-800 rounded-2xl p-6 space-y-4 shadow-xl">
          <ul className="space-y-3">
            {books.map((b) => (
              <BookCard
                key={b.id}
                book={b}
                onSelect={(book) => setSelectedBook(book)}
              />
            ))}
          </ul>

          <div>
            <button
              type="button"
              onClick={() => { setUploadError(null); setShowUploadModal(true); }}
              className="w-full p-5 rounded-xl border border-dashed border-gray-700 text-center text-white bg-transparent hover:bg-white/3 transition"
            >
              <div className="text-3xl">+</div>
              <div className="mt-1 font-semibold">Import New Textbook</div>
            </button>
          </div>
        </div>
        {selectedBook && (
          <BookModal
            book={selectedBook}
            onClose={() => setSelectedBook(null)}
          />
        )}
        {showUploadModal && (
          <UploadModal
            onClose={() => setShowUploadModal(false)}
            onUpload={handleUpload}
            error={uploadError}
          />
        )}
      </section>
    </main>
  );
}
