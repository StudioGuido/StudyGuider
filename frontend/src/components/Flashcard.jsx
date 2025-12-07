import { useEffect, useState } from "react";
import "./Flashcard.css";

export default function Flashcard({ front, back, cardId }) {
  const [isFlipped, setIsFlipped] = useState(false);

  useEffect(() => {
    setIsFlipped(false);
  }, [cardId, front, back]);

  return (
    <button
      type="button"
      className="flashcard"
      onClick={() => setIsFlipped(prev => !prev)}
      aria-live="polite"
    >
      <div className={`flashcard-inner ${isFlipped ? "is-flipped" : ""}`}>
        <div className="flashcard-face flashcard-front">
          <div className="flashcard-header">
            <span className="flashcard-hint">Question</span>
          </div>
          <p className="flashcard-text">{front ?? "…"}</p>
          <span className="flashcard-hint">Click to reveal answer</span>
        </div>
        <div className="flashcard-face flashcard-back">
          <div className="flashcard-header">
            <span className="flashcard-hint">Answer</span>
          </div>
          <p className="flashcard-text">{back ?? "…"}</p>
          <span className="flashcard-hint">Tap to go back</span>
        </div>
      </div>
    </button>
  );
}
