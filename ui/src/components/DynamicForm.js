import { useState, useEffect } from 'react';
import { strengthColor, strengthIndicator } from '../utils/password-strength';
import { EyeOutlined, EyeInvisibleOutlined, EditOutlined, CheckOutlined, UploadOutlined } from '@ant-design/icons';
import { useNavigate } from "react-router-dom";
import Moment from 'moment';
import {
    Box,
    Button,
    FormControl,
    FormHelperText,
    Grid,
    IconButton,
    InputAdornment,
    InputLabel,
    OutlinedInput,
    Stack,
    Typography, Select, MenuItem,
    Dialog, Backdrop, CircularProgress, Divider
} from '@mui/material';
import APIService from '../apicall/APIService';
import SuccessWindow from '../pages/SuccessWindow';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import ViewPages from '../pages/ViewPages';


export default function DynamicForm({ formFields, onSubmit, md, subBtn, clrBtn, url, getUrl, redirect }) {
    const [openDail, setOpenDail] = useState(false);
    const [formJson, setFormJson] = useState();
    const [open, setOpen] = useState(false);
    const [error, setError] = useState(false);
    const [success, setSuccess] = useState(false);
    let navigate = useNavigate();
    const userData = JSON.parse(APIService.getLocalStorage('myData'));
    useEffect(() => {
        if (getUrl) {
            APIService.postRequest(getUrl, userData).then(res => {
                let resp = res.data;
                if (resp) {
                    const temp = [...formFields]
                    temp.map(f => {
                        f.value = resp[f.key];
                    })
                    setFormJson(temp);
                }
                else {
                    setFormJson(formFields);
                }

            })
        }
        else {
            setFormJson(formFields);
        }
    }, []);




    const onTextFieldChange = (e, field, index) => {
        let temp = [...formJson];
        temp[index].value = e.target.value;
        field.value = e.target.value;
        setFormJson(temp);
    }

    const textField = (field, index) => {
        return <OutlinedInput
            id={index + "tf"}
            type="text"
            value={field.value}
            name={field.name}
            onChange={e => onTextFieldChange(e, field, index)}
            placeholder={field.label}
            fullWidth
        />
    }

    const onNumberFieldChange = (e, field, index) => {
        let temp = [...formJson];
        temp[index].value = e.target.value;
        field.value = e.target.value;
        setFormJson(temp);
    }

    const numberField = (field, index) => {
        return <OutlinedInput
            id={index + "tf"}
            type="number"
            value={field.value}
            name={field.name}
            onChange={e => onNumberFieldChange(e, field, index)}
            placeholder={field.label}
            fullWidth
        />
    }

    const onTextAreaChange = (e, field, index) => {
        let temp = [...formJson];
        temp[index].value = e.target.value;
        field.value = e.target.value;
        setFormJson(temp);
    }

    const textArea = (field, index) => {
        return <>
            <OutlinedInput
                id={index + "tf"}
                type="text"
                value={field.value}
                name={field.name}
                multiline
                rows={2}
                onChange={e => onTextAreaChange(e, field, index)}
                placeholder={field.label}
                fullWidth
            />
            <InputLabel>{field.value && '(' + field.value.length + ')'}</InputLabel>
        </>
    }

    const onPasswordChange = (e, field, index) => {
        const v = strengthIndicator(e.target.value);
        let temp = [...formJson];
        temp[index].value = e.target.value;
        field.value = e.target.value;
        temp[index].level = strengthColor(v);
        setFormJson(temp);
    };

    const handleClickShowPassword = (field, index) => {

        let temp = [...formJson];
        if (temp[index].showPassword)
            temp[index].showPassword = false;
        else
            temp[index].showPassword = true;
        setFormJson(temp);

    };

    const passwordField = (field, index) => {
        return <Box>
            <OutlinedInput
                fullWidth
                id={index + "pf"}
                type={field.showPassword ? 'text' : 'password'}
                value={field.value}
                name={field.name}
                onChange={(e) => {
                    onPasswordChange(e, field, index);
                }}
                endAdornment={
                    <InputAdornment position="end">
                        <IconButton
                            aria-label="toggle password visibility"
                            onClick={handleClickShowPassword(field, index)}
                            edge="end"
                            size="large"
                        >
                            {field.showPassword ? <EyeOutlined /> : <EyeInvisibleOutlined />}
                        </IconButton>
                    </InputAdornment>
                }
                placeholder="******"
                inputProps={{}}
            />
            <FormControl fullWidth sx={{ mt: 2 }}>
                <Grid container spacing={2} alignItems="center">
                    <Grid item>
                        <Box sx={{ bgcolor: field.level?.color, width: 85, height: 8, borderRadius: '7px' }} />
                    </Grid>
                    <Grid item>
                        <Typography variant="subtitle1" fontSize="0.75rem">
                            {field.level?.label}
                        </Typography>
                    </Grid>
                </Grid>
            </FormControl>
        </Box>
    }
    const onDropDownChange = (e, field, index) => {
        let temp = [...formJson];
        temp[index].value = e.target.value;
        field.value = e.target.value;
        setFormJson(temp);
    }

    const dropDownField = (field, index) => {
        return <Select fullWidth
            id={index + "dd"}
            value={field.value ? field.value : "NAdefault"}
            onChange={(e) => onDropDownChange(e, field, index)}
        >
            {(field.required && field.required == 'true') ? <MenuItem key='select' value="NAdefault">--Select--</MenuItem> : <MenuItem key='all' value="NAdefault">--All--</MenuItem>}
            {

                field.options.map((m, index) =>
                    <MenuItem key={index} value={m.value}>{m.key}</MenuItem>
                )
            }
        </Select>

    }

    const onOtherDropDownChange = (e, field, index) => {
        let temp = [...formJson];
        temp[index].value = e.target.value;
        field.value = e.target.value;
        if (field.value === temp[index].otherValue) {
            temp.map(f => {
                if (f.key === temp[index].otherKey) {
                    f.type = "textfield";
                    if (temp[index].required) {
                        f.required = "true";
                    }
                }
            }
            )
        } else {
            temp.map(f => {
                if (f.key === temp[index].otherKey) {
                    f.type = "hidden";
                    if (temp[index].required) {
                        f.required = null;
                    }
                }
            }
            )
        }


        setFormJson(temp);
    }

    const otherDropDownField = (field, index) => {
        return <Select fullWidth
            id={index + "dd"}
            value={field.value ? field.value : "NAdefault"}
            onChange={(e) => onOtherDropDownChange(e, field, index)}
        >
            {(field.required && field.required == 'true') ? <MenuItem key='select' value="NAdefault">--Select--</MenuItem> : <MenuItem key='all' value="NAdefault">--All--</MenuItem>}
            {

                field.options.map((m, index) =>
                    <MenuItem key={index} value={m.value}>{m.key}</MenuItem>
                )
            }
        </Select>

    }



    const onMultipleDropDownChange = (e, field, index) => {
        let temp = [...formJson];
        temp[index].value = e.target.value;
        field.value = e.target.value;
        setFormJson(temp);
    }

    const multipleDropDownField = (field, index) => {
        return <Select fullWidth
            id={index + "dd"}
            value={field.value}
            multiple
            onChange={(e) => onMultipleDropDownChange(e, field, index)}
        >{
                field.options.map((m, index) =>
                    <MenuItem key={index} value={m.key}>{m.value}</MenuItem>
                )
            }
        </Select>

    }

    const ondateFieldChange = (e, field, index) => {

        console.log(e + '')
        let temp = [...formJson];
        temp[index].value = e + '';
        temp[index].date = e;
        setFormJson(temp);
    }



    const dateField = (field, index) => {
        return <LocalizationProvider id={index + 'd1'} dateAdapter={AdapterDayjs}><DatePicker
            value={field.date}
            onChange={(e) => ondateFieldChange(e, field, index)} formatDate={(date) => Moment(date).format('DD-MM-YYYY')}
        /></LocalizationProvider>


    }

    const onUploadClick = (event, index) => {
        let temp = [...formJson];
        var file = event.target.files[0];
        const reader = new FileReader();
        var url = reader.readAsDataURL(file);

        reader.onload = (e) => {
            console.log(e)
            temp[index].value = (reader.result);
            var image = new Image();
            image.src = e.target.result;
            image.onload = function () {
                var height = this.height;
                var width = this.width;
                var w = temp[index].width;
                var h = temp[index].height;
                if (w && h && ((h + 5) >= 200 || height <= (h - 5)) && (width >= (w + 5) || width <= (w - 5))) {
                    temp[index].error = "Height and Width must be 135 X 195";
                    temp[index].fileName = null
                    temp[index].value = null
                    setFormJson(temp);
                } else {
                    console.log(url)
                    temp[index].valueSize = (event.target.files[0]);
                    let fsize = parseInt(temp[index].valueSize.size) / 1024;
                    if (fsize < parseInt(temp[index].size)) {
                        temp[index].fileName = temp[index].valueSize.name;
                        temp[index].error = null;
                        console.log(temp[index].valueSize.size);
                    } else {
                        temp[index].error = "File should be less than " + temp[index].size + "KB";
                    }
                    setFormJson(temp);
                }

            };


        };

    }



    const uploadField = (field, index) => {
        return <Box>
            <input
                accept={field.media}
                style={{ display: "none" }}
                id={field.key}
                type="file"
                onChange={e => onUploadClick(e, index)}
            />
            <label htmlFor={field.key}>
                <Button fullWidth startIcon={<UploadOutlined />} variant="contained" color="secondary" component="span">
                    {field.fileName ? field.fileName : 'Upload'}
                </Button>
            </label>

        </Box>
    }

    const textLabel = (field, index) => {
        return <Typography key={index + ''} variant="h5" >
            {field.value}
        </Typography>
    }



    const currencylabel = (field, index) => {
        return <Typography key={index + ''} color="red" variant="h3" >
            {ViewPages.formatMoney(field.value)}
        </Typography>
    }



    const divider = () => {
        return <Divider component="li" />
    }

    const getField = (field, index) => {
        if (field.type === 'textfield')
            return textField(field, index);
        if (field.type === 'numberfield')
            return numberField(field, index);
        else if (field.type === 'textarea')
            return textArea(field, index);
        else if (field.type === 'password')
            return passwordField(field, index);
        else if (field.type === 'singledropdown')
            return dropDownField(field, index);
        else if (field.type === 'otherdropdown')
            return otherDropDownField(field, index);
        else if (field.type === 'multipledropdown')
            return multipleDropDownField(field, index);
        else if (field.type === 'datefield')
            return dateField(field, index);
        else if (field.type === 'fileupload')
            return uploadField(field, index);
        else if (field.type === 'textlabel')
            return textLabel(field, index);
        else if (field.type === 'divider')
            return divider();
        else if (field.type === 'currencylabel')
            return currencylabel(field, index);


    }

    const getFields = (field, index) => {
        return <><Grid item xs={12} md={(field.md ? field.md : md)}>
            <Stack spacing={1} >
                {field.label && <InputLabel htmlFor={index}>{field.label}{(field.required && field.required == 'true') ? '*' : ''}</InputLabel>}
                {
                    getField(field, index)

                }
                {field.error && (
                    <FormHelperText error id="helper-text-firstname-signup">
                        {field.error}
                    </FormHelperText>
                )}
            </Stack>

        </Grid>

        </>
    }


    const formSubmit = () => {
        setOpen(true);
        let check = true;
        let temp = [...formJson];
        temp.map(f => {
            if (f.type == 'singledropdown')
                f.value = f.value == 'NAdefault' ? '' : f.value;
            if (f.required && (!f.value || f.value === undefined || f.value === '' || f.value.length === 0)) {
                f.error = f.label + ' is required';
                check = false;
            }
            else if (f.minValue && (parseInt(f.minValue) > parseInt(f.value))) {
                f.error = f.label + ' should be greater than or equal ' + f.minValue;
                check = false;
            }
            else
                f.error = null;
        })
        if (check) {
            let from = formJsonToRequestJsin(formJson);
            if (url) {
                console.log(JSON.stringify(from));
                APIService.postRequest(url, from).then(res => {
                    let resp = res.data;
                    if (resp && resp.code === 'success') {
                        setOpenDail(true);
                        setOpen(false);
                        setSuccess(resp.message);

                    }
                    else {
                        setError(resp.message);
                        setOpen(false);
                    }
                })
            }
            else {
                onSubmit('submit', from);
                setOpen(false);
            }
        }
        else {
            setFormJson(temp);
            setOpen(false);
        }

    }

    const dateToString = (vale) => {
        if (vale != '') {
            let v = parseInt(vale) + 19800;
            var d = APIService.dateToStringOnlyDate(new Date(v))
            return d;
        } else {
            return '';
        }
    }




    const formJsonToRequestJsin = (form) => {
        let req = {};
        form.map(f => {
            if (f.type == 'datefield')
                req[f.key] = dateToString(f.value);
            else if (f.type == 'multipledropdown')
                req[f.key] = f.value.toString();
            else if (f.type == 'singledropdown')
                req[f.key] = f.value == 'NAdefault' ? '' : f.value;
            else
                req[f.key] = f.value;

        })
        if (userData) {
            req.userId = userData.userId;
            req.mobileNumber = userData.mobileNumber;
            req.userName = userData.fullName;
            req.companyType = userData.userType;
            if (userData.company)
                req.companyId = userData.company.companyId;
        }
        return req;
    }

    const formClear = () => {

        let temp = [...formJson];
        temp.map(fi => {
            if (fi.type === 'multipledropdown')
                fi.value = [];
            else
                fi.value = "";
            fi.error = null;
        })
        setFormJson(temp);
    }

    const redirectTopage = () => {
        if (redirect) {
            setOpenDail(false);
            navigate(redirect);
        }
        else {
            setOpenDail(false);
            if (onSubmit)
                onSubmit("refresf", {})
        }
    }



    return (
        <>


            <Grid container spacing={2} >
                {formJson && formJson.map((field, index) =>
                    field.type != 'hidden' && getFields(field, index)
                )
                }


            </Grid><br />
            {
                error && <center> <Typography variant="h5" color="red" >
                    {error}
                </Typography><br /></center>
            }
            {(subBtn && clrBtn) ?
                <Grid container spacing={2} md={12}>
                    <Grid item xs={12} md={3}>

                    </Grid>
                    <Grid item xs={12} md={3}>

                        <Button disableElevation startIcon={<EditOutlined />} fullWidth size="large" onClick={formClear()} variant="contained" color="primary">
                            {clrBtn}
                        </Button>

                    </Grid>
                    <Grid item xs={12} md={3}>

                        <Button disableElevation startIcon={<CheckOutlined />} fullWidth size="large" onClick={e => formSubmit()} variant="contained" color="info">
                            {subBtn}
                        </Button>

                    </Grid>
                    <Grid item xs={12} md={3}>

                    </Grid>
                </Grid> : <Grid container spacing={2} md={12}>
                    <Grid item xs={12} md={12}>

                        <center>   <Button disableElevation startIcon={<CheckOutlined />} size="large" onClick={e => formSubmit()} variant="contained" color="info">
                            {subBtn}
                        </Button></center>

                    </Grid>
                </Grid>
            }


            <Dialog
                open={openDail}

            >
                <SuccessWindow message={success} redirect={redirect} btnlable="Ok" onClose={e => redirectTopage()} />
            </Dialog>

            <Backdrop
                sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}
                open={open}

            >
                <CircularProgress color="inherit" />
            </Backdrop>

        </>

    )
}