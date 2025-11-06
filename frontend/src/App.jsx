import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Books from "./pages/Books/Books";
import Chapters from "./pages/Chapters/Chapters";
import Understanding from "./pages/Understanding/Understanding";
import Reinforce from "./pages/Reinforce/Reinforce";

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/books" replace />} />
          <Route path="/books" element={<Books />} />
          <Route path="/books/:bookId/chapters" element={<Chapters />} />
          {/* understanding */}
          <Route
            path="/books/:bookId/chapters/:chapterId/understanding"
            element={<Understanding defaultMode="summary" />}
          />
          <Route
            path="/books/:bookId/chapters/:chapterId/understanding/ask-ai"
            element={<Understanding defaultMode="askai" />}
          />
          {/* reinforce */}
          <Route
            path="/books/:bookId/chapters/:chapterId/reinforce/flashcards"
            element={<Reinforce type="flashcards" />}
          />
          <Route
            path="/books/:bookId/chapters/:chapterId/reinforce/flashcards/results"
            element={<Reinforce type="flashcards" showResults />}
          />
          <Route
            path="/books/:bookId/chapters/:chapterId/reinforce/quiz"
            element={<Reinforce type="quiz" />}
          />
          <Route
            path="/books/:bookId/chapters/:chapterId/reinforce/quiz/results"
            element={<Reinforce type="quiz" showResults />}
          />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
