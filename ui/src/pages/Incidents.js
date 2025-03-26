
import APIService from "../apicall/APIService";
import DynamicTable from "../components/DynamicTable"
import { useNavigate } from "react-router-dom";

export default function Incidents() {
  const navigate = useNavigate();
  const priority = [
    { key: "Low ", value: "Low" },
    { key: "Medium", value: "Medium" },
    { key: "High", value: "High" }
  ]


  const status = [
    { key: "Open", value: "Open" },
    { key: "In Progress", value: "In Progress" },
    { key: "Resolved", value: "Resolved" }
  ];
  const headers = [
    { id: "affected_app", label: "View", key: "affected_app", type: "button", align: "right" },
    { id: "incident_id", label: "incident_id", key: "incident_id", type: "text", align: "left" },
    { id: "title", label: "title", key: "title", type: "text", align: "left" },
    { id: "description", label: "description", key: "description", type: "text", align: "left" },
    { id: "priority", label: "priority", key: "priority", type: "text", align: "left" },
    { id: "reported_by", label: "reported_by", key: "reported_by", type: "text", align: "left" },
    { id: "reported_date", label: "reported_date", key: "reported_date", type: "date", align: "right" },
    { id: "status", label: "Status", key: "status", type: "text", align: "left" },
    { id: "resolved_date", label: "resolved_date", key: "resolved_date", type: "text", align: "right" },
    { id: "resolved_by", label: "resolved_by", key: "resolved_by", type: "text", align: "right" },
    { id: "resolution_notes", label: "resolution_notes", key: "resolution_notes", type: "text", align: "right" },
    { id: "affected_app", label: "affected_app", key: "affected_app", type: "text", align: "right" },
    { id: "affected_microservice", label: "affected_microservice", key: "affected_microservice", type: "text", align: "right" }



  ];

  const filter = [
    { label: "incident id", key: "incident_id", type: "textfield", value: "" },
    { label: "Priority", key: "priority", type: "singledropdown", value: "", options: priority },
    { label: "Status", key: "status", type: "singledropdown", value: "", options: status },
    { label: "From Date", key: "fromDate", type: "datefield", value: "" },
    { label: "To date", key: "toDate", type: "datefield", value: "" }

  ];



  const onButtonClick = (type, row) => {
    APIService.setJSONLocalStorage("selected-incident",row)
    navigate("/incidentview")
  }




  return (
    <>
    <h2>Incidents</h2>
    <DynamicTable headers={headers} url="/incident-post" onButtonClick={(type, row) => onButtonClick(type, row)} filters={filter} /> </>
  )
}

