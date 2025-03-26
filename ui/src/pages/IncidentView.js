import { useState, useEffect } from 'react';
import APIService from "../apicall/APIService";
import TabContext from '@mui/lab/TabContext';
import TabList from '@mui/lab/TabList';
import TabPanel from '@mui/lab/TabPanel';
import ViewPages from './ViewPages';
import {
  Button, Grid, Select, MenuItem, Stack, Typography, OutlinedInput, DialogTitle, Container, Card, Box, Tab, Dialog, DialogContent, DialogContentText, IconButton
} from '@mui/material';
import DynamicForm from '../components/DynamicForm';
import DoneOutlineOutlinedIcon from '@mui/icons-material/DoneOutlineOutlined';
import StreamPostComponent from './StreamPostComponent';
import { Outlet, Link } from "react-router-dom";
import Summary from './Summary';
import SimpleLineChart from './SimpleLineChart';
import KnowledgeBase from './KnowledgeBase';
import PDFIframeViewer from './PDFIframeViewer';



export default function IncidentView() {
  const [incident, setIncident] = useState(APIService.getJSONLocalStorage("selected-incident"));
  const [commentHistory, setCommentHistory] = useState([]);
  const [value, setValue] = useState('1');
  const [comment, setComment] = useState();
  const [status, setStatus] = useState(incident.status);
  const [summery, setSummery] = useState();
  const [open, setOpen] = useState(false);
  const [agentData, setAgentData] = useState();
  const [closeBtn, setCloseBtn] = useState(false);

  const filter = [
    { label: "Comments", key: "comment", type: "textarea", value: "", rows: 2 }
  ]


  useEffect(() => {
    if (incident.status === 'Open') {
      getSummery()
      setOpen(true)
      setCloseBtn(false)
    }
    else {
      setSummery(incident.summary)
      setAgentData(incident.agent_data)
    }

    getComments()


  }, []);

  const getComments = () => {
    let req = { incident_id: incident.incident_id }
    APIService.postRequest("/get-comments", req).then(res => {
      let resp = res.data;
      if (resp) {
        setCommentHistory(resp)
      }
    })
  }

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  const addComments = () => {
    let cm = { date: APIService.getCurrentDate(), comment: comment, incident_id: incident.incident_id, user: 'Satish' }
    APIService.postRequest("/save-comment", cm).then(res => {
      getComments()
    })


  }

  const drawComment = (comment) => {
    return <>

      <Card sx={{
        maxWidth: "100%",
        margin: "0px",
        padding: "20px",
      }}>

        {ViewPages.infoView('Satish - ' + comment.date, comment.comment, 12)}
      </Card><br /></>
  }

  const showIncidents = (key, value) => {
    if (key != '_id') {
      if (key === 'reported_date') {
        return <h3> {key}: {' ' + APIService.dateToString(value)}<br /></h3>
      }
      else {
        return <h3> {key}: {' ' + value}<br /></h3>
      }
    }
  }

  const downloadRCA = () => {
    APIService.getRequest("/download/" + incident.incident_id, {}).then(res => {
      let resp = res.data;
      if (resp) {
        const url = window.URL.createObjectURL(new Blob([resp]));

        // Create a temporary link element
        const link = document.createElement('a');
        link.href = url;
        // Set the desired file name for the download
        link.setAttribute('download', incident.incident_id + '.pdf');
        // Append to the document body to make it clickable
        document.body.appendChild(link);
        // Programmatically click the link to trigger the download
        link.click();

        // Cleanup: remove the link and revoke the object URL
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }
    })
  }

  const getSummery = () => {
    let cm = { text: incident.title }
    APIService.postRequestFullUrl("https://e0f4-49-205-250-118.ngrok-free.app/api/summarize", cm).then(res => {
      let resp = res.data;
      if (resp) {
        setSummery(resp)
      }
    })
  }

  const streameddata = (agent) => {
    let temp = {}

    if (agent) {
      console.log(JSON.stringify(agent))
      agent.map((a, index) => {
        temp[a.agent.replaceAll(' ', '_')] = a;
      })
      setAgentData(temp);
    }

    setOpen(false)
  }

  const updateStatus = () => {
    let temp = { ...incident }
    temp._id = null;
    temp.status = status;
    temp.summary = summery;
    temp.agent_data = agentData;
    APIService.postRequest("/update-incident/" + temp.incident_id, temp).then(res => {
      let resp = res.data;
      if (resp) {
        setIncident(temp)
        APIService.setJSONLocalStorage("selected-incident", temp)
      }
    })

  }
  return (
    <>{incident && <Grid container >
      <Grid item xs={12} md={3}>
        <Card sx={{
          maxWidth: "80%",
          margin: "0px",
          padding: "20px",
        }}>
          {ViewPages.infoView("Incident Id", incident.incident_id, 12)}
          {ViewPages.infoView("Priority Id", incident.priority, 12)}
          <Grid container md={12}>
            <Grid item xs={12} sm={6} md={6}>
              <Stack>
                <Typography color="primary.darker" variant="subtitle1">Status</Typography>
                <Select fullWidth
                  value={status} disabled={incident.status === 'Resolved'}
                  onChange={(e) => setStatus(e.target.value)}
                >
                  <MenuItem key='Open' value="Open" >Open</MenuItem>
                  <MenuItem key='In Progress' value="In Progress" >In Progress</MenuItem>
                  <MenuItem key='Resolved' value="Resolved" >Resolved</MenuItem>
                </Select>
              </Stack>
            </Grid>

            <Grid item xs={12} sm={6} md={6}>
              <br /> <br />
              {(incident.status != status) &&
                <Button color="success" onClick={e => updateStatus()} ><DoneOutlineOutlinedIcon /></Button>
              }</Grid></Grid>
          {ViewPages.infoView("affected_app", incident.affected_app, 12)}
          {
            <Button variant="contained" color="info" onClick={e => downloadRCA()} disabled={incident.status != 'Resolved'}>Generate RCA</Button>
          }
        </Card>
      </Grid>
      <Grid item xs={12} md={9}>
        <Box sx={{ width: '100%', typography: 'body1' }}>
          <TabContext value={value}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <TabList onChange={handleChange} aria-label="lab API tabs example">
                <Tab sx={{ color: "info.main" }} label="Incident" value="1" />
                <Tab sx={{ color: "info.main" }} label="Metrics" value="2" />
                <Tab sx={{ color: "info.main" }} label="Work Flow" value="3" />
                <Tab sx={{ color: "info.main" }} label="Knowledge Base" value="4" />
                <Tab sx={{ color: "info.main" }} label="Summary" value="5" />
              </TabList>
            </Box>
            <TabPanel value="1" sx={{ padding: "5px" }}>

              {
                summery && <Card sx={{
                  maxWidth: "100%",
                  margin: "0px",
                  padding: "20px",
                }}> {ViewPages.infoView("Incident Summary", summery.summary, 12)}</Card>
              }
              {
                (agentData && agentData.Classifier) && <Card sx={{
                  maxWidth: "100%",
                  margin: "0px",
                  padding: "20px",
                }}>
                  {ViewPages.infoView('Classifier', agentData.Classifier.output, 12)}

                </Card>
              }

              <br />

              {(incident.status == 'Open' || incident.status == 'In Progress') &&
                <>
                  <OutlinedInput
                    type="text"
                    value={comment}
                    name='Comment'
                    multiline
                    rows={2}
                    onChange={e => setComment(e.target.value)}
                    placeholder='Add comment'
                    fullWidth
                  /><br />
                  <Button sx={{ float: "right" }} color="success" onClick={e => addComments()} >Submit</Button>
                </>
              }


              <br />
              {(commentHistory && commentHistory.length > 0) && commentHistory.map((com, index) =>
                drawComment(com)
              )
              }
              <br />
              <Card sx={{
                maxWidth: "100%",
                margin: "0px",
                padding: "20px",
              }}>
                {incident && Object.entries(incident).map(([key, value]) => (
                  showIncidents(key, value)
                ))}
              </Card>

            </TabPanel>
            <TabPanel value="2" sx={{ padding: "5px" }}>
            {(agentData && agentData.Telemetry_API_Handler) ? <>
                <SimpleLineChart telemetry={agentData.Telemetry_API_Handler.output}/></>:<>NA</>
            }
            </TabPanel>
            <TabPanel value="3" sx={{ padding: "5px" }}>

              {(agentData && agentData.Workflow_Decision_Agent) && <Card sx={{
                maxWidth: "100%",
                margin: "0px",
                padding: "20px",
              }}>
                <Typography variant="subtitle1">'Workflow Decision Agent</Typography>

                {agentData.Workflow_Decision_Agent.output && Object.entries(agentData.Workflow_Decision_Agent.output).map(([key, value]) => (
                  ViewPages.infoView(key, JSON.stringify(value), 12)
                ))}

              </Card>
              }
              <br />
              {(agentData && agentData.API_Handler) && <Card sx={{
                maxWidth: "100%",
                margin: "0px",
                padding: "20px",
              }}>
                <Typography variant="subtitle1">API Handler</Typography>
                {ViewPages.infoView('Status', agentData.API_Handler.output.status, 12)}
                <Grid item xs={12} sm={6} md={12}>
                  <Stack>
                    <Typography color="primary.darker" variant="subtitle1">Content</Typography>
                    <Link target="_blank"  to={agentData.API_Handler.output.content}>{agentData.API_Handler.output.content}</Link>
                  </Stack>
                </Grid>


              </Card>
              }

            </TabPanel>
            <TabPanel value="4" sx={{ padding: "5px" }}>
              {
                (agentData && agentData.KB_Article_Retriever) && <Card sx={{
                  maxWidth: "100%",
                  margin: "0px",
                  padding: "20px",
                }}>
                  {ViewPages.infoView('KB Article Retriever', agentData.KB_Article_Retriever.output, 12)}
                  <KnowledgeBase text={agentData.KB_Article_Retriever.output}/>

                </Card>
              }


              {
                (agentData && agentData.PDF_Reader && agentData.PDF_Reader.output) &&  <Card sx={{
                  maxWidth: "100%",
                  margin: "0px",
                  padding: "20px",
                }}>
                  <Stack>
                    <Typography variant="subtitle1">Access KB here</Typography>
                    <Link target="_blank"  to={agentData.PDF_Reader.output}>{agentData.PDF_Reader.output}</Link>
                  </Stack>

                  </Card>
              }
            </TabPanel>
            <TabPanel value="5" sx={{ padding: "5px" }}>
            {(agentData && agentData.Summary_Generator) && 
               <Summary text={agentData.Summary_Generator.output}/>
              }
            </TabPanel>
            <TabPanel value="6" sx={{ padding: "5px" }}>
              {agentData && Object.entries(agentData).map(([key, value]) => (
                ViewPages.infoView(key, JSON.stringify(value), 12)
              ))}
            </TabPanel>
          </TabContext>
        </Box>
      </Grid>
    </Grid>

    }
      <Dialog
        open={open}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          Analyzing Incident {incident.incident_id}
        </DialogTitle>
        <DialogContent>
          <StreamPostComponent incident={incident} streameddata={(agent) => streameddata(agent)} />
          {closeBtn && <>
            <h3>Analyses Completed</h3>
            <Button sx={{ float: "right" }} color="success" onClick={e => setOpen(false)} >Close</Button> </>
          }
        </DialogContent>

      </Dialog>

    </>
  )

}

