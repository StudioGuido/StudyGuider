
async function getToken() {
    const res = await fetch("http://localhost:8000/session");
    const data = await res.json();
    return data.client_secret.value;
}

async function startSession() {
    const token = await getToken();

    const pc = new RTCPeerConnection();
    const dc = pc.createDataChannel("oai-events");

    // mic audio
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    stream.getTracks().forEach(track => pc.addTrack(track, stream));

    // playback
    pc.ontrack = (e) => {
        const audio = document.getElementById("remoteAudio");
        audio.srcObject = e.streams[0];
    }

    dc.onopen = () => {
        dc.send(JSON.stringify({
            type: "session.update",
            session: {
                turn_detection: {
                    type: "server_vad",
                    interrupt_response: false,
                    create_response: false
                }
            }
        }));
    };

    dc.onmessage = async (e) => {
        const event = JSON.parse(e.data);
        console.log("FULL EVENT:", JSON.stringify(event, null, 2));

        const userText = event.item?.content?.[0]?.transcript;
        console.log("userText:", userText);

        console.log(event.type, event);

        if (event.type === "conversation.item.created") {
            const chunks = [
                "john is 67 years old and lives alone in Blacksburg, VA",
                "John's favorite food is pizza, and he does not like tacos",
                "John likes to play the flute and chase ducks"
            ]

            dc.send(JSON.stringify({
                type: "response.create",
                response: {
                    modalities: ["audio", "text"],
                    instructions: "Answer the user's question using the provided context.",
                    input: [{
                        type: "message",
                        role: "user",
                        content: [
                            {
                                type: "input_text",
                                text: `Relevant Context: ${chunks.join(" ")}`
                            },
                            {
                                type: "input_text",
                                text: `User question: ${userText}`
                            }
                        ]
                    }]
                }
            }))
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
}

document.getElementById("connectBtn").addEventListener("click", () => {
    console.log("button clicked");          // ← is the click even registering?
    document.getElementById("connectBtn").disabled = true;
    startSession().catch(err => {
        console.error("startSession failed:", err);  // ← catch silent async errors
    });
});