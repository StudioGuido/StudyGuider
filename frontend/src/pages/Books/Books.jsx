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
  const [token, setToken] = useState(null)

  const getJWT = async() => {
    const { data, error } = await supabase.auth.getSession();
    const token = data.session?.access_token;
    setToken(token);
  }
  
  useEffect(() => {
    fakeApi.getBooks().then(setBooks);
    console.log(user);
    getJWT();
  }, []);
  
  if (!books)
    return (
      <p className="min-h-screen flex items-center justify-center text-white">
        Loading…
      </p>
    );

async function handleUpload(file) {
  try {
    // 1) Get presigned url
    const res = await fetch("http://localhost:8000/api/getPresignedUrl", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
    });

    if (!res.ok) throw new Error("Failed to get upload URL");
    const { presigned_url } = await res.json();
    console.log(presigned_url)

    // 2) Upload the file directly to S3/Supabase
    const uploadRes = await fetch(presigned_url, {
      method: "PUT",
      body: file, // Send the raw file object
      headers: {
        "Content-Type": "application/pdf", // Must match the backend 'ContentType'
      },
    });

    if (uploadRes.ok) {
      console.log("Upload successful!");
    }
  } catch (err) {
    console.error("Upload error:", err);
  }


  // 3) notify backend that the textbook is uploaded


  setShowUploadModal(false)
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
              onClick={() => setShowUploadModal(true)}
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
          />
        )}
      </section>
    </main>
  );
}
