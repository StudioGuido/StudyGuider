import React from 'react'
import './Summary.css';
import { useEffect, useRef, useState } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faArrowLeft } from '@fortawesome/free-solid-svg-icons'
import { useNavigate, useLocation } from 'react-router-dom';
import { useTypewriter } from '../hooks/useTypewriter';
import Chatbot from '../components/Chatbot';
import ReactMarkdown from 'react-markdown';

function cleanMarkdownText(raw) {
    return raw
      .replace(/\r\n/g, '\n')         // Normalize line endings
      .replace(/\n{3,}/g, '\n')     // No huge gaps
      .replace(/[ \t]+\n/g, '\n')     // Trim whitespace at end of lines
      .trim();
  }
  

function Summary() {

    const [fullSummary, setFullSummary] = useState("");
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();
    const location = useLocation();
    const scrollRef = useRef(null);
    const { selectedTitle, selectedChapter } = location.state || {};

    function makeSummaryKey(title, chapter) {
        return `summary:${title}:${chapter}`;
      }

    // 1. POST Request: Summary Contents
    useEffect(() => {
        if (!selectedTitle || !selectedChapter) return;

        const summaryKey = makeSummaryKey(selectedTitle, selectedChapter);
        const cachedSummary = sessionStorage.getItem(summaryKey);
    
        if (cachedSummary) {
            const cleaned = cleanMarkdownText(cachedSummary);
            setFullSummary(cleaned);
            setLoading(false);
            return; // Skip API call
        }
    
        const fetchSummary = async () => {
            try {
                setLoading(true);
                const response = await fetch('http://localhost:8000/api/generateSummary', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        chapter: selectedChapter,
                        textbook: selectedTitle,
                    })
                });
    
                const data = await response.json();
                console.log("Response from server:", data);
    
                const sum = data.response;
                console.log(sum);
                setFullSummary(sum);
    
                // Save in sessionStorage
                sessionStorage.setItem(summaryKey, sum);
    
            } catch (error) {
                console.error("POST request failed:", error);
            } finally {
                setLoading(false); // stop loading either way
            }
        };
    
        if (selectedTitle && selectedChapter) {
            fetchSummary();
        }
    }, [selectedTitle, selectedChapter]);
    

    const typedText = useTypewriter(fullSummary, 10); // Speed (ms per character)
    const [isUserScrolling, setIsUserScrolling] = useState(false);
    // const [showChatbot, setShowChatbot] = useState(false);

    // useEffect(() => {
    //     if (typedText === fullSummary) {
    //       setShowChatbot(true);
    //     }
    //   }, [typedText, fullSummary]);

    // 1. Handle user scrolling manually
    useEffect(() => {
        const handleScroll = () => {
        if (!scrollRef.current) return;
    
        const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
        const isNearBottom = scrollHeight - scrollTop <= clientHeight + 10;
    
        if (!isNearBottom) {
            setIsUserScrolling(true);
        } else {
            setIsUserScrolling(false); // if they scroll back to bottom
        }
        };
    
        const scrollEl = scrollRef.current;
        scrollEl?.addEventListener('scroll', handleScroll);
        return () => scrollEl?.removeEventListener('scroll', handleScroll);
    }, []);
    
    // 2. Auto-scroll only if user hasn’t manually scrolled up
    useEffect(() => {
        if (!scrollRef.current || isUserScrolling) return;
    
        // Use requestAnimationFrame to ensure DOM is ready
        requestAnimationFrame(() => {
        scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        });
    }, [typedText, isUserScrolling]);

    return (
        <div className="s-container">
            <div className="summary-container">
                <div className="back-title">
                    <button
                    id="sum-btn"
                    onClick={() => navigate(-1)}>
                        <FontAwesomeIcon icon={faArrowLeft} size="2x" />
                    </button>
                    <div>
                        <h2>Summary 📝</h2>
                    </div>
                </div>
                <div className="summary-scroll" ref={scrollRef}>
                    { loading ? (
                        <div className="loading-container">
                            <img className="giffy" src="/spin.gif" alt="loading animation" />
                        </div>
                ) : (
                        <div className="typing-summary">
                        <ReactMarkdown>
                            {typedText}
                        </ReactMarkdown>
                    </div>
                    )}
                </div>
            </div>
            <Chatbot 
            selectedChapter={selectedChapter}
            selectedTitle={selectedTitle}
            />
        </div>
    )
}

export default Summary
