
import {
    Grid, Typography, Stack, Avatar
} from '@mui/material';
import API_URL from '../apicall/APIConfig';
const ViewPages = {
    infoView,
    techTypeView,
    currebcyFormatter,
    statusFormatter,
    formatMoney
}

function infoView(title, value, md) {
    return <Grid item xs={12} sm={6} md={md}>
        <Stack>
            <Typography color="primary.darker" variant="subtitle1">{title}</Typography>
            <Typography variant="h5" display="block" gutterBottom> {value}</Typography>
        </Stack>
    </Grid>
}

function techTypeView(tech, index) {
    return <Grid item xs={12} sm={6} md={6}><Stack key={index + "tec"} direction="row" spacing={2} alignItems="center" sx={{ p: 0.5 }}>
        <Avatar alt="profile user" src={API_URL + "/media/image?path=" + tech.photoPath} sx={{ width: 80, height: 80 }} />
        <Stack>
            <Typography variant="h4">{tech.name}</Typography>
            {tech.characterName && <Typography variant="h5" display="block" gutterBottom> {tech.characterName}</Typography>}
        </Stack>
    </Stack></Grid>


}

function formatMoney(amount, decimalCount = 0, decimal = ".", thousands = ",") {
    try {
      decimalCount = Math.abs(decimalCount);
      decimalCount = isNaN(decimalCount) ? 2 : decimalCount;
  
      const negativeSign = amount < 0 ? "-" : "";
  
      let i = parseInt(amount = Math.abs(Number(amount) || 0).toFixed(decimalCount)).toString();
      let j = (i.length > 3) ? i.length % 3 : 0;
  
      return negativeSign +
        (j ? i.substr(0, j) + thousands : '') +
        i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + thousands) +
        (decimalCount ? decimal + Math.abs(amount - i).toFixed(decimalCount).slice(2) : "");
    } catch (e) {
      console.log(e)
    }
  }

function formatNumber(val) {
    if (parseInt(val) > 999) {

        return formatMoney(val)
    }
    else
        return val;
}

function currebcyFormatter(title, value, md) {
    return <Grid item xs={12} sm={6} md={md}>
        <Stack>
            <Typography  variant="subtitle1">{title}</Typography>
            <Typography variant="h4" display="block" color="red" gutterBottom> {formatNumber(value)}</Typography>
        </Stack>
    </Grid>


}

function statusColor(status) {
    if (status === 'closed')
        return 'error';
    if (status === 'accepted' || status === 'completed')
        return 'green';
    else
        return 'secondary';
}

function statusFormatter(title, value, md) {
    return <Grid item xs={12} sm={6} md={md}>
        <Stack>
            <Typography variant="subtitle1">{title}</Typography>
            <Typography variant="h4" display="block" color={statusColor(value)} gutterBottom> {formatNumber(value)}</Typography>
        </Stack>
    </Grid>



}

export default ViewPages;