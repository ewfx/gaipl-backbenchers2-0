import { useState, useEffect } from 'react';
import APIService from "../apicall/APIService";
import {
  Box,
  Button,
  Card,
  FormHelperText,
  Grid,
  IconButton,
  InputAdornment,
  InputLabel,
  OutlinedInput,
  Stack,
  DialogTitle, Select, MenuItem,
  Dialog, Backdrop, CircularProgress, Divider,DialogContent
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import './chat.css'




export default function Chatbot() {
  const [chatHistory, setChatHistory] = useState([]);
  const [chattext, setChattext] = useState();
  const [open, setOpen] = useState(false);


  const beforeApiCall = () => {
   
    if (chattext != "") {
      setOpen(true)
      let input = { type: "input", text: chattext }
      callChatbot(input);
      setChattext("")
    
    }
  }

  const callChatbot = (input) => {
    let req = { query: chattext }
    let l = [...chatHistory]
    l.push(input)
    APIService.postRequest("/search", req).then(res => {
      let resp = res.data;
      if (resp) {
        let input1 = {
          type: "output", text: resp.result.summary.replace(/\n/g, "<br/>")
        }

        l.push(input1)
        setChatHistory(l);
        setOpen(false)
      }
    })

  }


  const showChatMessg = (chat) => {
    if (chat.type === 'input') {
      return <div class="message sent">
        <div class="bubble" dangerouslySetInnerHTML={{ __html: chat.text }}></div>
      </div>
    } else {
      return <div class="message received">
        <div class="bubble" dangerouslySetInnerHTML={{ __html: chat.text }}></div>
      </div>
    }
  }


  return (<>
    <Box sx={{ padding: "10" }}>
      <div class="chat-container">
        <div class="chat-messages">
          {
            chatHistory.length > 0 && chatHistory.map((chat, index) =>
              showChatMessg(chat)
            )
          }
        </div>
        <div class="chat-input">
          <Stack direction="row" spacing={2}>
            <OutlinedInput
              id="text"
              type="text"
              value={chattext}
              name="Query"
              rows={2}
              onChange={e => setChattext(e.target.value)}
              placeholder="Text"
              fullWidth
            />

            <Button variant="contained" onClick={e => beforeApiCall()} endIcon={<SendIcon />}>
              Send
            </Button>

          </Stack> </div>
      </div>
      <br />
    </Box>
    <Dialog
      open={open}
      aria-labelledby="alert-dialog-title"
      aria-describedby="alert-dialog-description"
    >  <DialogContent>
        <Stack sx={{ color: 'grey.500' }} spacing={2} direction="row">
          <CircularProgress color="secondary" />

        </Stack>
      </DialogContent>
    </Dialog>
  </>
  )

}

