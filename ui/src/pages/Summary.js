import { useState, useEffect } from 'react';
import APIService from "../apicall/APIService";
import {
  Card
 
} from '@mui/material';
import ViewPages from './ViewPages';




export default function Summary({ text }) {
  const [summary, setSummary] = useState();


  useEffect(() => {
    let cm = { text: JSON.stringify(text) }
    APIService.postRequestFullUrl("https://e0f4-49-205-250-118.ngrok-free.app/api/summarize", cm).then(res => {
      let resp = res.data;
      if (resp) {
        setSummary(resp)
      }
    })
  }, []);



  return (<>
    {
      summary && <Card sx={{
        maxWidth: "100%",
        margin: "0px",
        padding: "20px",
      }}> {Object.entries(summary).map(([key, value]) => (
        ViewPages.infoView(key, value, 12)
      ))}</Card>
    }

  </>
  )

}

