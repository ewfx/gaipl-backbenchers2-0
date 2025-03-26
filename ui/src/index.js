import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./layout/Layout";
import Incidents from "./pages/Incidents";
import IncidentView from "./pages/IncidentView";
import Chatbot from "./pages/Chatbot";
import NoPage from "./pages/NoPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Incidents />} />
          <Route path="incidentview" element={<IncidentView />} />
          <Route path="chatbot" element={<Chatbot />} />
          <Route path="*" element={<NoPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);