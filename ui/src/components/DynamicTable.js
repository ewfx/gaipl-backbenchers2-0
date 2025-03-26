import * as React from 'react';
import { useState, useEffect } from 'react';
import APIService from '../apicall/APIService';
import {
    Paper,
    Button,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow, Accordion, AccordionSummary, AccordionDetails, Box
} from '@mui/material';
import Grid from '@mui/material/Grid';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import DynamicForm from '../components/DynamicForm';
import APP_URL from '../apicall/APIConfig'
import { Avatar } from '../../node_modules/@mui/material/index';
import { BackwardOutlined, ForwardOutlined, PlusOutlined } from '@ant-design/icons';
import './component.css'

export default function DynamicTable({ data, headers, filters, btns, url, onButtonClick, filtermd }) {
    const userData = JSON.parse(APIService.getLocalStorage('myData'));
    const [tbData, setTbData] = useState();
    const [tbHeaders, setHeaders] = useState();
    const [page, setPage] = React.useState(1);
    const rowsPerPage = 50;


    useEffect(() => {
        if (data) {
            setHeaders(headers);
            setTbData(data);

        }
        else {
            searchData(formJsonToRequestJsin(filters, 1));
        }
    }, []);

    const searchData = (req) => {
        
        APIService.postRequest(url, req).then(res => {
            let resp = res.data;
            if (resp) {
                setHeaders(headers);
                setTbData(resp)
            }
        })
    }

    const formJsonToRequestJsin = (form, pageNo) => {
        let req = {};
        if (form) {
            form.map(f => {
                if (f.type == 'date')
                    req[f.key] = APIService.dateToString(f.value);
                else
                    req[f.key] = f.value;

            })
        }
        if (userData) {
            req.userId = userData.userId;
            req.userName = userData.fullName;
            req.companyType = userData.userType;
            if (userData.company)
                req.companyId = userData.company.companyId;
        }
        if (rowsPerPage > 0) {
            req.pageSize = rowsPerPage;
            req.page = pageNo;
        }
        return req;
    }

    const onHeaderBtnClick = (action) => {
        onButtonClick(action, {})
    }

    const onTableBtnClick = (action, row) => {
        onButtonClick(action, row)
    }

    const showButton = (row, header) => {
        if (header.disableKey === undefined) {
            return false;

        } else {
            return header.disableValu.includes(row[header.disableKey]) ? true : false;
        }
    }


    const tableRowData = (row, header) => {
        if (header.type == 'avatar') {
            return <Avatar
                alt="Remy Sharp"
                src={APP_URL + "/media/image?path=" + row[header.key]}
                sx={{ width: 56, height: 56 }}
            />
        } else if (header.type == 'image') {
            return <img
                src={APP_URL + "/media/image?path=" + row[header.key]}
                alt={header.name}
                style={{ width: 70, height: 100 }}
                loading="lazy"
            />
        } else if (header.type == 'button') {
            return <Button disabled={showButton(row, header)} sx={{ width: "100" }} onClick={e =>onTableBtnClick(header.key, row)} >{header.label}</Button>

        }else if (header.type == 'date') {
            return APIService.dateToString(row[header.key])
        }
        else {
            return row[header.key]
        }
    }
    

    const getHeader = (value, index, align) => {
        return <TableCell style={{background:"gray",color:"white",fontSize:"18px"}} align={align}
            key={index}
        >
            {value}
        </TableCell>
    }

    const getTableRow = (row, header, index) => {
        return <TableCell align={header.align}
            key={index}
        >
            {tableRowData(row, header)}
        </TableCell>
    }

    const getRow = (row, rowIndex) => {
        return <TableRow hover tabIndex={rowIndex} key={rowIndex + "1"}>
            {tbHeaders && tbHeaders.map((header, index) =>
                getTableRow(row, header, index)

            )}
        </TableRow>
    }

    const filterSubmit = (type, form) => {
                setPage(1);
        if (userData) {
            form.userId = userData.userId;
            form.userName = userData.fullName;
            form.companyType = userData.userType;
            if (userData.company)
                form.companyId = userData.company.companyId;
        }
        if (rowsPerPage > 0) {
            form.pageSize = rowsPerPage;
            form.page = 1;
        }
        searchData(form,1);
    }

    const pageDown = () => {
        if (page > 1) {
            let tmp = page - 1;
            setPage(tmp);
            searchData(formJsonToRequestJsin(filters, tmp));
        }
    }

    const pageUp = () => {
        let tmp = page + 1;
        setPage(tmp);
        searchData(formJsonToRequestJsin(filters, tmp));
    }

    return (
        <> {filters &&
            <Accordion>
                <AccordionSummary
                    expandIcon={<ArrowDropDownIcon />}
                    aria-controls="panel1-content"
                    id="panel1-header"
                >
                    Search
                </AccordionSummary>
                <AccordionDetails>
                    <DynamicForm formFields={filters} md={filtermd ? filtermd : 4} onSubmit={(type, form) => filterSubmit(type, form)} subBtn="Search" />

                </AccordionDetails>
            </Accordion>
        }
            <br />
            <Grid container spacing={2}>
                <Grid sx={{ float: "right" }} item xs={12} md={1}>
                    {
                        btns && btns.map((btn, index) =>
                            btn.type == 'header' && <Button key={index + '1'} startIcon={<PlusOutlined />} variant="contained" color="success" onClick={e =>  onHeaderBtnClick(btn.action)} >{btn.name}</Button>
                        )
                    }
                </Grid>
            </Grid><br />
            <Grid container spacing={2}>
                <Grid item xs={12} md={12}>

                    <Paper sx={{ width: '100%' }}>
                        <TableContainer>
                            <Table stickyHeader aria-label="sticky table">
                                <TableHead >
                                    <TableRow >                                        {
                                            tbHeaders && tbHeaders.map((header, index) =>
                                                getHeader(header.label, index, header.align)
                                            )
                                        }
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {
                                        tbData && tbData.map((row, rowIndex) =>
                                            getRow(row, rowIndex)
                                        )
                                    }
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Paper>
                </Grid>
                <Grid item xs={12} md={12}>
                    {tbData && <center>
                        <Box>
                            <Button disabled={page ==1 ? true : false} startIcon={<BackwardOutlined />} onClick={e => pageDown()} />
                            {page + 1}
                            <Button disabled={tbData.length < rowsPerPage ? true : false} startIcon={<ForwardOutlined />} onClick={e => pageUp()} />
                        </Box>
                    </center>
                    }
                </Grid>
            </Grid>
        </>
    )
}