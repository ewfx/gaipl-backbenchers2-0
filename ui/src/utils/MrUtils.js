import Moment from 'react-moment';

export default class MrUtils {

    constructor() {
       
    }

    formJsonToRequestJsin(form,user)
    {
        let req={userId:user.userId,comaponyId:user.comaponyId};
        form.map(f=>{
            if(f.type=='date')
            req[f.key]=dateToString(f.value);
            else
            req[f.key]=f.value;

        })
        return req;
    }

    stringTodate(vale) {
        Moment.locale('en');
        return Moment(vale).toDate();
    }

    dateToString(vale) {
        Moment.locale('en');
        return Moment(vale).format('DD-MM-yyyy HH:mm:ss');
    }
}