import { useState, useEffect } from 'react';
import APIService from "../apicall/APIService";
import {
  Card,OutlinedInput
 
} from '@mui/material';
import ViewPages from './ViewPages';




export default function KnowledgeBase({ text }) {
  const [summary, setSummary] = useState();


  useEffect(() => {
    let cm = { text: JSON.stringify(text) }
    APIService.postRequest("/knowledgeArticle/"+text.replace('Found KB: ',''), cm).then(res => {
      let resp = res.data;
      if (resp) {
        setSummary(JSON.stringify(resp,null,2))
      }
    })
  }, []);



  return (<>
    {
      summary && <OutlinedInput
        type="text"
        value={summary}
        name='Comment'
        multiline
        readOnly={true}
        rows={10}
        placeholder='Add comment'
        fullWidth
      />
    }

  </>
  )

}

