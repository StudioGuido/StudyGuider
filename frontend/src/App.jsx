import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Books from "./pages/Books/Books";
import Chapters from "./pages/Chapters/Chapters";
import Understanding from "./pages/Understanding/Understanding";
import Reinforce from "./pages/Reinforce/Reinforce";
import PhaseLayout from "./components/PhaseLayout";

// --- NEW IMPORTS FOR AUTH ---
import { useAuth } from "./context/AuthContext"; // Import the hook to access user state
import Login from "./pages/Auth/Login"; // Import your new login page
// ----------------------------

export default function App() {

  // Access user and loading status from our AuthContext
  const { user, loading } = useAuth();

  // PURPOSE: Prevents the app from showing the login page for a split second 
  // while Supabase checks if a session already exists in local storage.
  if (loading) {
    return <div className="loading-screen">Loading StudyGuider...</div>;
  }

  // PURPOSE: If there is no user session, we only render the Login page.
  // Once the user logs in, 'user' becomes true and the full app renders below.
  if (!user) {
    return <Login />;
  }




  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/books" replace />} />
          <Route path="/books" element={<Books />} />
          <Route path="/books/:bookId/chapters" element={<Chapters />} />
          <Route element={<PhaseLayout />}>
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
          </Route>
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
