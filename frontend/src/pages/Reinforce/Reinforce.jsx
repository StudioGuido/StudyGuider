import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fakeApi } from "../../services/fakeApi";
import ChapterSidebarNav from "../../components/ChapterSidebar";

export default function Reinforce({ type = "flashcards", showResults = false }) {
  const { bookId, chapterId } = useParams();
  const navigate = useNavigate();

  const [items, setItems] = useState([]);
  const [index, setIndex] = useState(0);
  useEffect(() => {
    if (type === "flashcards") {
      fakeApi.getFlashcards(bookId, chapterId).then(setItems);
    } else {
      // for now reuse flashcards as mock quiz source
      fakeApi.getFlashcards(bookId, chapterId).then(setItems);
    }
  }, [bookId, chapterId, type]);

  const done = index >= items.length;
  const resultsRoute = `/books/${bookId}/chapters/${chapterId}/reinforce/${type}/results`;

  if (showResults) {
    return (
      <section>
        <h1 className="text-2xl font-semibold mb-2">Results</h1>
        <p>Nice! You finished {type} for this chapter.</p>
        <button className="mt-4 px-3 py-2 border rounded" onClick={() => navigate(-1)}>Back</button>
      </section>
    );
  }

  if (done) {
    navigate(resultsRoute, { replace: true });
    return null;
  }

  const card = items[index];

  return (
  <section className="grid grid-cols-[20rem_1fr] gap-4">
    <ChapterSidebarNav />
    <div>
      {/* existing Reinforce content unchanged */}
      {/* results view OR card/quiz flow goes here */}
    </div>
  </section>

    // <section>
    //   <h1 className="text-2xl font-semibold mb-4">Reinforce — {type}</h1>
    //   {type === "flashcards" ? (
    //     <div className="border rounded p-6">
    //       <p className="font-medium mb-2">Q: {card?.front ?? "…"}</p>
    //       <details className="mb-4">
    //         <summary className="cursor-pointer">Show Answer</summary>
    //         <p className="mt-2">A: {card?.back}</p>
    //       </details>
    //       <button className="px-3 py-2 border rounded" onClick={() => setIndex(i => i + 1)}>Next</button>
    //     </div>
    //   ) : (
    //     <div className="border rounded p-6">
    //       <p className="font-medium mb-4">Quiz (mock) — choose an answer</p>
    //       {/* mock options */}
    //       <div className="flex gap-2">
    //         <button className="px-3 py-2 border rounded" onClick={() => setIndex(i => i + 1)}>Option A</button>
    //         <button className="px-3 py-2 border rounded" onClick={() => setIndex(i => i + 1)}>Option B</button>
    //         <button className="px-3 py-2 border rounded" onClick={() => setIndex(i => i + 1)}>Option C</button>
    //       </div>
    //     </div>
    //   )}
    // </section>
  );
}
