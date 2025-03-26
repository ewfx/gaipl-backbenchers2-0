import React, { useEffect, useState } from 'react';

function StreamComponent() {
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    // Create an EventSource to listen for SSE from the API
    const eventSource = new EventSource('https://e0f4-49-205-250-118.ngrok-free.app/api/summarize_incident?incident_id=INC434389');

    // Listen for incoming messages
    eventSource.onmessage = (e) => {
      setMessages((prevMessages) => [...prevMessages, e.data]);
    };

    // Handle any errors
    eventSource.onerror = (err) => {
      console.error('EventSource failed:', err);
      eventSource.close();
    };

    // Cleanup on unmount
    return () => {
      eventSource.close();
    };
  }, []);

  return (
    <div>
      <h2>Streamed Data</h2>
      <ul>
        {messages.map((msg, index) => (
          <li key={index}>{msg}</li>
        ))}
      </ul>
    </div>
  );
}

export default StreamComponent;
