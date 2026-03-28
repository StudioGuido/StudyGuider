import { fakeApi } from "../../services/fakeApi";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { supabase } from '../../services/supabaseClient';
import BookCard from "../../components/BookCard";
import BookModal from "../../components/BookModal";

export default function Books() {
  const [books, setBooks] = useState(null);
  const [selectedBook, setSelectedBook] = useState(null);
  const { user } = useAuth();
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);

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

  const handleUploadTextbook = () => {
    const file = event.target.files[0];
  
    // Check if a file was selected and if it's a PDF
    if (file && file.type === "application/pdf") {
      setSelectedFile(file);
    } else {
      alert("Please select a valid PDF file.");
    }
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
              className="w-full p-5 rounded-xl border border-dashed border-gray-700 text-center text-white bg-transparent hover:bg-white/3 transition"
            >
              <div className="mt-1 font-semibold">
                Import New Textbook
                <input type="file" accept=".pdf" onChange={handleUploadTextbook} />
                {selectedFile && <p>Selected: {selectedFile.name}</p>}
              </div>
              <div className="text-3xl">+</div>
            </button>
          </div>
        </div>
        {selectedBook && (
          <BookModal
            book={selectedBook}
            onClose={() => setSelectedBook(null)}
          />
        )}
      </section>
    </main>
  );
}
