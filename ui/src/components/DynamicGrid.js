import * as React from 'react';
import { useState, useEffect } from 'react';
import APIService from 'apicall/APIService';
import MovieGrid from './MovieGrid';
import TenderCard from './TenderCard';
import BiddingCard from './BiddingCard';
import SellerTenderCard from './SellerTenderCard';
import {
    Button,Typography,
    Grid,
    Accordion, AccordionSummary, AccordionDetails, Box
} from '@mui/material';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import DynamicForm from 'components/DynamicForm';
import { BackwardOutlined, ForwardOutlined, PlusOutlined } from '@ant-design/icons';

export default function DynamicGrid({ data, filters, btns, url, onButtonClick, filtermd, cardType }) {
    const userData = JSON.parse(APIService.getLocalStorage('myData'));
    const [tbData, setTbData] = useState();
    const [page, setPage] = React.useState(0);
    const rowsPerPage = 12;
    useEffect(() => {
        if (data) {
            setTbData(data);
        }
        else {
            searchData(formJsonToRequestJsin(filters, 0));
        }
    }, []);

    const searchData = (req) => {
        APIService.postRequest(url, req).then(res => {
            let resp = res.data;
            if (resp) {

                setTbData(resp)
            }
        })
    }

    const formJsonToRequestJsin = (form, pageNo) => {
        let req = {};
        form.map(f => {
            if (f.type == 'date')
                req[f.key] = dateToString(f.value);
            else
                req[f.key] = f.value;

        })
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










    const filterSubmit = (type, form) => {

        setPage(0);
        if (userData) {
            form.userId = userData.userId;
            form.userName = userData.fullName;
            form.companyType = userData.userType;
            if (userData.company)
                form.companyId = userData.company.companyId;
        }
        if (rowsPerPage > 0) {
            form.pageSize = rowsPerPage;
            form.page = 0;
        }
        searchData(form, 0);
    }

    const pageDown = () => {
        if (page > 0) {
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

    const viewCard = (card) => {
        if (cardType === 'bidding') {
            return <BiddingCard key={card.tenderRightId} data={card} onButtonClik={(type, data) => { onTableBtnClick(type, data); }} />
        } else if (cardType === 'tenders') {
            return <TenderCard key={card.tenderRightId} data={card} onButtonClik={(type, data) => { onTableBtnClick(type, data); }} />
        }
        else if (cardType === 'tender') {
            return <SellerTenderCard key={card.tenderRightId} data={card} onButtonClik={(type, data) => { onTableBtnClick(type, data); }} />
        }
        else
            return <MovieGrid key={card.id} data={card} onButtonClik={(type, data) => { onTableBtnClick(type, data); }} />
    }

    return (
        <>
            <Accordion >
                <AccordionSummary sx={{':hover': {boxShadow: 5,backgroundColor: "info.lighter",}}}
                    expandIcon={<ArrowDropDownIcon />}
                    aria-controls="panel1-content"
                    id="panel1-header"
                ><Typography color="secondary" gutterBottom variant="h4" component="h4">
                    Search
                    </Typography>
                </AccordionSummary>
                <AccordionDetails>
                    <DynamicForm formFields={filters} md={filtermd ? filtermd : 6} onSubmit={(type, form) => filterSubmit(type, form)} subBtn="Search" />

                </AccordionDetails>
            </Accordion>
            <br />
            <Grid container spacing={2}>
                <Grid sx={{ float: "right" }} item xs={12} md={1}>
                    {
                        btns && btns.map((btn, index) =>
                            btn.type == 'header' && <Button startIcon={<PlusOutlined />} key={index + '1'} variant="contained" color="success" onClick={e => { onHeaderBtnClick(btn.action); e }} >{btn.name}</Button>
                        )
                    }
                </Grid>
            </Grid><br />
            <Grid container spacing={2}>

                {tbData && tbData.map((card) => (
                    viewCard(card)
                ))}

                <Grid item xs={12} md={12}>
                    {tbData && <center>
                        <Box>
                            <Button disabled={page == 0 ? true : false} startIcon={<BackwardOutlined />} onClick={e => { pageDown(); e }} />
                            {page + 1}
                            <Button disabled={tbData.length < rowsPerPage ? true : false} startIcon={<ForwardOutlined />} onClick={e => { pageUp(); e }} />
                        </Box>
                    </center>
                    }
                </Grid>
            </Grid>
        </>
    )
}