
import { useNavigate } from "react-router-dom";
import {
    Button, Typography
} from '@mui/material';

export default function SuccessWindow({ message, btnlable, redirect, onClose }) {
    let navigate = useNavigate();
    const onButtocClick = () => {
        if (redirect) {
            navigate(redirect);
        }
        else {
            onClose();
        }
    }

    return (
       
            <center>
                <Typography variant="h4" color="green">
                    {message}
                </Typography><br/>
                <Button variant="contained" color="success" onClick={e => onButtocClick()}>{btnlable}</Button>
            </center>
     
    )
}