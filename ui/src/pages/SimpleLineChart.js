import { useState, useEffect } from 'react';
import { LineChart } from '@mui/x-charts/LineChart';
import {
  Button, Grid, Select, MenuItem, Stack, Typography, OutlinedInput, DialogTitle, Container, Card, Box, Tab, Dialog, DialogContent, DialogContentText, IconButton
} from '@mui/material';

export default function SimpleLineChart({ telemetry }) {

    const [chartData, setChartData] = useState([]);
    useEffect(() => {
      
        let tempNode = []
        if (telemetry) {
            telemetry.map((t,index)=>{
                if(t.node_name.startsWith('Database')){
                    tempNode.push(databaseData(t.telemetry.database,t.node_id))
                }
                if(t.node_name.startsWith('Application')){
                    tempNode.push(appInfoData(t.telemetry.appInfo,t.node_id))
                }
            })
      
           
        } 
        setChartData(tempNode)

    }, []);

    const appInfoData = (app,appName) => {
        let cpu_usage = []
        let memory_usage = []
        let response_time_ms = []
        let timestamp = []
        app.map((chat, index) => {
            cpu_usage.push(chat.cpu_usage)
            memory_usage.push(chat.memory_usage)
            response_time_ms.push(chat.response_time_ms)
            timestamp.push(chat.timestamp)
        })
        return {
            node: appName, label: timestamp, charts: [{ name: 'CPU USAGE', data: cpu_usage },
            { name: 'Memory Usage', data: memory_usage }, { name: 'Response Time', data: response_time_ms }]
        }
    }

    const databaseData = (app,appName) => {
        let connections = []
        let queries_per_second = []
        let latency_ms = []
        let timestamp = []
        app.map((chat, index) => {
            connections.push(chat.connections)
            queries_per_second.push(chat.queries_per_second)
            latency_ms.push(chat.latency_ms)
            timestamp.push(chat.timestamp)
        })
        return {
            node: appName, label: timestamp, charts: [{ name: 'Connections', data: connections },
            { name: 'Queries per second', data: queries_per_second }, { name: 'latency ms', data: latency_ms }]
        }
    }

    const getchart = (chartName, pData, xLabels) => {
        return  <Grid item xs={12} md={6}><Card sx={{
                  maxWidth: "80%",
                  margin: "0px",
                  padding: "20px",
                }}>
            <LineChart
                width={500}
                height={300}
                series={[
                    { data: pData, label: chartName }
                ]}
                xAxis={[{ scaleType: 'point', data: xLabels }]}
            />
        </Card><br/></Grid>
    }

    const getchartCard = (chart) => {
        return <>
            <Typography color="primary.darker" variant="subtitle1">{chart.node}</Typography>
            <Grid container >
            {
                chart.charts && chart.charts.map((c, index) => 
                    getchart(c.name, c.data, chart.label)
                )
            }</Grid>
        </>
    }

    return (
        <>
            {chartData.length>0 && chartData.map((chart, index) =>
                getchartCard(chart)
            )}


        </>

    );
}
