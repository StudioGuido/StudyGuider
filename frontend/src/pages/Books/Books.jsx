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

  const getJWT = async() => {
    const { data, error } = await supabase.auth.getSession();
    const token = data.session?.access_token;
    // console.log(token);
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

  function handleUpload(file) {
    // 1) get presigned url

    // 2) upload to S3

    // 3) Notify backend that textbook is completed


    // TODO: send file to backend
    console.log("Uploading:", file.name);
    setShowUploadModal(false);
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
