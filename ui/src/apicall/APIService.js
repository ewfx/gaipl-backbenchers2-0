import axios from 'axios';
import APP_URL from "./APIConfig"
import Moment from 'moment';
import dayjs from 'dayjs';

var CryptoJS = require("crypto-js");

const APIService = {
    getRequest,
    postRequest,
    getCurrentDate,
    getOnlyCurrentDate,
    postRequestFile,
    setJSONLocalStorage,
    getJSONLocalStorage,
    setLocalStorage,
    getLocalStorage,
    tokenUpdate,
    lineAndbarChartTotable,
    postRequestWithToken,
    removeLocalStorage,
    stringTodate,
    setValuesToFron,
    dateToString,
    dateToStringOnlyDate,
    sortByDate,
    getRequestFullUrl,
    postRequestFullUrl
};




async function getRequest(url, data) {
    return await axios.get(APP_URL + url, data,{
        headers: {
            "ngrok-skip-browser-warning": true
        }
    }).catch(error=>{
        alert(JSON.stringify(error))
        return {error:"network error"}
    });
}

async function getRequestFullUrl(url, data) {
    return await axios.get(url, data).catch(error=>{
        alert(JSON.stringify(error))
        return {error:"network error"}
    });
}

async function postRequestFullUrl(url, data) {
    return await axios.post(url,  data ).catch(error=>{
     alert(JSON.stringify(error))
     return {error:"network error"}
 });
 }

async function postRequestWithToken(url, data1) {
    let token = getLocalStorage('token');
    if (token && url != '/user/login-check') {
        let data = encrypt(JSON.stringify(data1));
        console.log(url);
        return await axios.post(APP_URL + url, { data }, {
            headers: {
                "Authorization": 'Bearer ' + token
            }
        }).catch(function (error) {
            console.log(JSON.stringify(error));
            if (error.message === 'Request failed with status code 401') {
                generatToken().then(res => {
                    if (res) {
                        setLocalStorage('token', res.data.token);
                        return reloadpage(url, data, res.data.token);
                    }
                })
            }
        });
    }
    else {
        let data = encrypt(JSON.stringify(data1));
        return await axios.post(APP_URL + url, { data }).catch(function (error) {
            alert(JSON.stringify(error));
        });
    }
}

async function postRequest(url, data) {
   return await axios.post(APP_URL + url,  data ).catch(error=>{
    alert(JSON.stringify(error))
    return {error:"network error"}
});
}

function diff_minutes(dt2, dt1) {
    //  console.log("dt2 : " + dt2);
    //  console.log("dt1 : " + dt1);
    var diff = (dt2.getTime() - dt1.getTime()) / 1000;
    diff /= 60;
    return Math.abs(Math.round(diff));
}

function setValuesToFron(form,values)
{
    let temp=[...form];
    temp.map(f=>{
        if(f.type==='multipledropdown')
        {
            f.value=values[f.key].split(',');
        }else if(f.type==='datefield'){
            f.value=stringTodate(values[f.key]);
            f.date=dayjs(stringTodate(values[f.key]));
        }else{
            f.value=values[f.key]; 
        }
    })

    return temp;

}

function dateToStringOnlyDate(vale) {
    Moment.locale('en');
    return Moment(vale).format('DD-MM-yyyy');
}

function dateToString(vale) {
        Moment.locale('en');
        return Moment(vale).format('DD-MM-yyyy HH:mm:ss');
    }

function  stringTodate(vale) {
    Moment.locale('en');
    return Moment(vale).toDate();
}

function tokenUpdate() {
    let tt = getJSONLocalStorage('toke-time');
    let cd = new Date();
    let d = diff_minutes(cd, new Date(tt.tokedate));
    let time = tt.session_time - 5;
    //   console.log("Time : " + time);

    if (d > time) {
        console.log("d : " + d);
        generatToken().then(res => {
            if (res) {
                setLocalStorage('token', res.data.token);
                let toketime = { tokedate: new Date(), session_time: 30 };
                APIService.setJSONLocalStorage('toke-time', toketime);
            }
        });
    }
}

async function reloadpage(url, data, token) {
    return await axios.post(APP_URL + url, { data }, {
        headers: {
            "Authorization": 'Bearer ' + token
        }
    }).then();
}


async function generatToken() {
    let us = getJSONLocalStorage('myData');
    let us1 = { user_name: us.mobileNo, password: us.password }
    let data = encrypt(JSON.stringify(us1));
    return await axios.post(APP_URL + '/user/gen-token', { data }).then();
}

async function postRequestFile(url, data1) {
    let data = encrypt(JSON.stringify(data1));
    return await axios.post(APP_URL + url, { data }, {
        responseType: 'blob',
    }).catch(function (error) {
        alert(error.message);
    });
}

function getCurrentDate() {
    Moment.locale('en');
    return Moment(new Date()).format('DD-MM-yyyy HH:mm:ss')
}

function getOnlyCurrentDate() {
    Moment.locale('en');
    return Moment(new Date()).format('DD-MM-yyyy')
}

function setJSONLocalStorage(key, json) {
    setLocalStorage(key, JSON.stringify(json))
}

function getJSONLocalStorage(key) {
    let json = getLocalStorage(key);
    if (json)
        return JSON.parse(json);
}

function setLocalStorage(key, data) {

    let endata = CryptoJS.AES.encrypt(data + '', 'my-secret-key@123').toString();
    localStorage.setItem(key, endata)
}




function encrypt(data) {
    return CryptoJS.AES.encrypt(data + '', 'my-secret-key@123').toString();
}

function getLocalStorage(key) {
    let ciphertext = localStorage.getItem(key);
    if (ciphertext) {
        var bytes = CryptoJS.AES.decrypt(ciphertext, 'my-secret-key@123');
        return bytes.toString(CryptoJS.enc.Utf8);
    } else
        return null;

}

function removeLocalStorage(key) {
    localStorage.removeItem(key);
}

function lineAndbarChartTotable(chart_date) {
    let result = {};
    let headers = [];
    let data = [];
    let d = chart_date.datasets;

    let l = chart_date.labels;

    let h = { key: "label", name: "" };
    headers.push(h);
    console.log(d.length);
    for (var z = 0; z < d.length; z++) {
        let h = { key: d[z].label, name: d[z].label };
        headers.push(h);
    }
    let total = { label: 'Total' };
    for (var k = 0; k < l.length; k++) {
        let row = { label: l[k] };
        for (var i = 0; i < d.length; i++) {
            row[d[i].label] = d[i].data[k];
            total[d[i].label] = (total[d[i].label] ? total[d[i].label] : 0) + d[i].data[k];
        }
        data.push(row);
    }
    data.push(total);
    result.header = headers;
    result.data = data;

    return result;
}

function sortByDate(data){
    return data.sort((a, b) => b.date - a.date);
}

export default APIService;