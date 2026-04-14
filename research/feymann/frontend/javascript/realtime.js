
async function getToken() {
    const res = await fetch("/session");
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
        const audio = document.getElementById("audio-output");
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

        const userText = event.transcript
        console.log("userText:", userText);

        console.log(event.type, event);

        if (event.type === "conversation.item.done") {
            const chunks = [
                "The mitochondria is the powerhouse of the cell.",
                "Cells are the basic unit of life.",
                "DNA carries genetic information."
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