import { Link, useNavigate } from "react-router-dom";
import { fakeApi } from "../../services/fakeApi";
import { useEffect, useState } from "react";

export default function Books() {
  const [books, setBooks] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fakeApi.getBooks().then(setBooks);
  }, []);

  if (!books) return <p>Loading…</p>;

  const goToFirstChapter = async (bookId) => {
    const chapters = await fakeApi.getChapters(bookId);
    const first = chapters[0];
    if (first) {
      navigate(`/books/${bookId}/chapters/${first.id}/understanding`);
    } else {
      navigate(`/books/${bookId}/chapters`);
    }
  };

  return (
    <section>
      <h1 className="text-2xl font-semibold mb-4">My Books</h1>
      <ul className="space-y-2">
        {books.map((book) => (
          <li key={book.id}>
            <Link
              to={`/books/${book.id}/chapters`}
              className="text-blue-600 underline"
              onClick={(event) => {
                event.preventDefault();
                goToFirstChapter(book.id);
              }}
            >
              {book.title} - {book.author}
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
