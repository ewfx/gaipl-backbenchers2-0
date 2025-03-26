import React, { useEffect, useState } from 'react';
import ViewPages from './ViewPages';
import CircularProgressWithLabel from './CircularProgressWithLabel';


function StreamPostComponent({incident,streameddata}) {
  const [agent, setAgent] = useState();
  const [status, setStatus] = useState([]);
  const [progress,setProgress]=useState(0)

  useEffect(() => {
    const fetchStream = async () => {
      try {
        const response = await fetch('https://e0f4-49-205-250-118.ngrok-free.app/api/stream', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
             'Accept':'text/event-stream',
           
          },
          body: JSON.stringify({incident_id:incident.incident_id ,description:incident.description ,severity:incident.priority}) // Replace with your request body as needed
        });

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }

        // Get the reader from the response body
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';
        let done = false;
        let allData=[]
        let con=0;
        // Continuously read from the stream
        while (!done) {
          const { value, done: doneReading } = await reader.read();
          done = doneReading;
          buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
          
          // Assuming the server sends newline-delimited JSON (NDJSON)
          const lines = buffer.split('\n');
          // Process all complete lines except the last (which may be incomplete)
          lines.slice(0, -1).forEach(line => {
            if (line.trim()) {
              try {
                const parsed = JSON.parse(line.replaceAll('data:',''));
                allData.push(parsed)
                setAgent(parsed.agent)
                setStatus(parsed.status)
                con=con+10;
                setProgress(con)

              } catch (err) {
                console.error('Error parsing JSON:', err, line);
              }
            }
          });
          // Save the last incomplete line back into the buffer
          buffer = lines[lines.length - 1];
       
        }
        streameddata(allData)
       } catch (error) {
        console.error('Error fetching stream:', error);
      }
    };

    fetchStream();
  }, []);

  return (
    <div>
     {agent && ViewPages.infoView("Agent", agent, 12)} 
    
     <CircularProgressWithLabel key={Math.random()} value={progress} />
    </div>
  );
}

export default StreamPostComponent;
