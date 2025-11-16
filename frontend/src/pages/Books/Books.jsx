import { fakeApi } from "../../services/fakeApi";
import { useEffect, useState } from "react";
import BookCard from "../../components/BookCard";

export default function Books() {
  const [books, setBooks] = useState(null);
  useEffect(() => {
    fakeApi.getBooks().then(setBooks);
  }, []);
  if (!books)
    return (
      <p className="min-h-screen flex items-center justify-center text-white">
        Loading…
      </p>
    );

  return (
    <main className="min-h-screen text-white flex items-center justify-center px-4">
      <section className="w-full max-w-2xl">
        <header className="text-center mb-6">
          <h1 className="text-4xl font-extrabold">Welcome Nivar!</h1>
          <p className="text-gray-300 mt-2">
            Please select the textbook you want to access
          </p>
        </header>

        <div className="bg-[#0b0b0b] border border-gray-800 rounded-2xl p-6 space-y-4 shadow-xl">
          <ul className="space-y-3">
            {books.map((b) => (
              <BookCard key={b.id} book={b} />
            ))}
          </ul>

          <div>
            <button
              type="button"
              className="w-full p-5 rounded-xl border border-dashed border-gray-700 text-center text-white bg-transparent hover:bg-white/3 transition"
            >
              <div className="mt-1 font-semibold">Import New Textbook</div>
              <div className="text-3xl">+</div>
            </button>
          </div>
        </div>
      </section>
    </main>
  );
}
