import React, { useState, useRef, useEffect } from 'react';
import { useParams } from 'react-router-dom'

export default function Mastery() {
  const {bookId, chapterId } = useParams(); 
  const [status, setStatus] = useState('Not connected');
  const [isConnecting, setIsConnecting] = useState(false);
  const [transcripts, setTranscripts] = useState([]);
  const [events, setEvents] = useState([]);
  
  const audioRef = useRef(null);
  const pcRef = useRef(null);
  const dcRef = useRef(null);

  const logEvent = (type, data) => {
    setEvents((prev) => [
      ...prev,
      { time: new Date().toLocaleTimeString(), type, data }
    ]);
  };

  useEffect(() => {
    return () => {
      if (pcRef.current) pcRef.current.close();
      if (dcRef.current) dcRef.current.close();
    };
  }, []);

  const getToken = async () => {
    const res = await fetch("http://localhost:8000/api/session");
    const data = await res.json();
    return data.client_secret.value;
  };

  const startSession = async () => {
    try {
      setIsConnecting(true);
      setStatus('Connecting...');
      
      const token = await getToken();
      const pc = new RTCPeerConnection();
      pcRef.current = pc;
      
      const dc = pc.createDataChannel("oai-events");
      dcRef.current = dc;

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => pc.addTrack(track, stream));

      // Handle incoming audio playback
      pc.ontrack = (e) => {
        if (audioRef.current) {
          audioRef.current.srcObject = e.streams[0];
        }
      };

      dc.onopen = () => {
        setStatus('Connected');
        logEvent('session', 'Data channel opened');
        
        dc.send(JSON.stringify({
          type: "session.update",
          session: {
            input_audio_transcription: {
              model: "whisper-1"
            },
            turn_detection: {
              type: "server_vad",
              threshold: 0.95,
              interrupt_response: false,
              create_response: false
            }
          }
        }));
      };

      dc.onmessage = async (e) => {
        const event = JSON.parse(e.data);
        console.log("FULL EVENT:", event);
        logEvent(event.type, event);

        // Handle user transcription completed
        if (event.type === "conversation.item.input_audio_transcription.completed") {
          const userText = event.transcript;
          if (!userText) return;

          // Update UI with user's speech
          setTranscripts((prev) => [...prev, { role: 'user', text: userText }]);
          
          console.log("TEXTBOOK ID:" + bookId)

          let chunks = [];
          try {
            const res = await fetch("http://localhost:8000/api/context", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                transcript: userText,
                chapter: chapterId,
                textbook: bookId,
              })
            });

            if (!res.ok) {
            // This will print the exact Pydantic validation error to your browser console
            const errorDetails = await res.json();
            console.error("FastAPI 422 Error:", JSON.stringify(errorDetails, null, 2));
}
            const data = await res.json();
            chunks = data.response;
            console.log("Context fetched:", chunks);
          } catch (err) {
            console.error("Context fetch failed:", err);
            logEvent('error', 'Context fetch failed');
          }

          // Send injected context back to OpenAI
          dc.send(JSON.stringify({
            type: "response.create",
            response: {
              modalities: ["audio", "text"],
              input: [{
                type: "message",
                role: "user",
                content: [
                  {
                    type: "input_text",
                    text: `Relevant Context: ${chunks}`
                  },
                  {
                    type: "input_text",
                    text: `User query: ${userText}`
                  }
                ]
              }]
            }
          }));
        }
        
        // Optional: Capture the assistant's transcription to show in the UI
        if (event.type === "response.audio_transcript.done") {
          setTranscripts((prev) => [...prev, { role: 'assistant', text: event.transcript }]);
        }
      };

      // SDP handshake
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      const sdpRes = await fetch("https://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/sdp"
        },
        body: offer.sdp
      });

      await pc.setRemoteDescription({ type: "answer", sdp: await sdpRes.text() });

    } catch (err) {
      console.error("startSession failed:", err);
      setStatus('Error');
      setIsConnecting(false);
      logEvent('error', err.message);
    }
  };

  // Helper to determine status color
  const getStatusColor = () => {
    switch (status) {
      case 'Connected': return 'text-[#4caf50]';
      case 'Error': return 'text-[#f44336]';
      case 'Connecting...': return 'text-[#ff9800]';
      default: return 'text-[#888]';
    }
  };

  // Helper to determine log entry text color based on event prefix
  const getLogColor = (type) => {
    if (type.startsWith('session')) return 'text-[#ce93d8]';
    if (type.startsWith('audio') || type.startsWith('input_audio')) return 'text-[#80cbc4]';
    if (type.startsWith('conversation')) return 'text-[#a5d6a7]';
    if (type.startsWith('response')) return 'text-[#90caf9]';
    if (type === 'error') return 'text-[#ef9a9a]';
    return 'text-[#888]';
  };

  return (
    <div className="min-h-screen bg-[#1a1a1a] text-[#eee] font-sans p-8">
      <h1 className="text-2xl font-medium mb-6">Feynman WebRTC Test</h1>
      
      <div className="flex gap-3 items-center mb-4">
        <button 
          onClick={startSession} 
          disabled={isConnecting || status === 'Connected'}
          className="px-5 py-2 rounded-lg border border-[#444] bg-[#2a2a2a] text-[#eee] text-[0.95rem] transition-colors hover:bg-[#333] disabled:opacity-40 disabled:cursor-not-allowed select-none"
        >
          {status === 'Connected' ? 'Connected' : 'Connect'}
        </button>
        <span className={`text-sm px-2.5 py-1 rounded-md bg-[#2a2a2a] ${getStatusColor()}`}>
          {status}
        </span>
      </div>
      
      <p className="text-sm text-[#555] mb-6">
        Click Connect and just start talking — VAD will detect when you speak.
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Transcript Panel */}
        <div className="bg-[#242424] border border-[#333] rounded-xl p-4 h-[400px] flex flex-col">
          <h2 className="text-sm font-medium text-[#888] uppercase tracking-wide mb-3 border-b border-[#333] pb-2">
            Transcript
          </h2>
          <div className="flex-1 overflow-y-auto text-sm leading-relaxed pr-2">
            {transcripts.map((t, i) => (
              <div 
                key={i} 
                className={`mb-3 px-3 py-2 rounded-md ${
                  t.role === 'user' 
                    ? 'bg-[#1e3a5f] text-[#90caf9]' 
                    : 'bg-[#1e3a2f] text-[#a5d6a7]'
                }`}
              >
                <div className="text-xs font-semibold opacity-70 mb-0.5 uppercase">
                  {t.role}
                </div>
                <div>{t.text}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Event Log Panel */}
        <div className="bg-[#242424] border border-[#333] rounded-xl p-4 h-[400px] flex flex-col">
          <h2 className="text-sm font-medium text-[#888] uppercase tracking-wide mb-3 border-b border-[#333] pb-2">
            Events
          </h2>
          <div className="flex-1 overflow-y-auto pr-2">
            {events.map((ev, i) => (
              <div key={i} className={`font-mono text-xs py-1.5 border-b border-[#2a2a2a] break-words ${getLogColor(ev.type)}`}>
                <span className="text-[#555] mr-2 shrink-0">[{ev.time}]</span>
                <span>{ev.type}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Hidden Audio Element for WebRTC Playback */}
      <audio ref={audioRef} autoPlay className="hidden"></audio>
    </div>
  );
}