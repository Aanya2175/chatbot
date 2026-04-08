import { useState, useEffect, useRef } from "react";
import ChatPanel from "./components/ChatPanel";
import Dashboard from "./components/Dashboard";
import ReminderToast from "./components/ReminderToast";
import axios from "axios";
import "./App.css";

const API = "http://localhost:8000";

export default function App() {
  const [sessionId, setSessionId] = useState(null);
  const [activeTab, setActiveTab] = useState("chat");
  const [reminders, setReminders] = useState([]);
  const wsRef = useRef(null);

  useEffect(() => {
  const connectWS = (sid) => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${sid}`);
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === "reminder") {
        setReminders(prev => [...prev, data.message]);
      }
    };
    wsRef.current = ws;
    const ping = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) ws.send("ping");
    }, 30000);
    return () => { clearInterval(ping); ws.close(); };
  };

  const existing = localStorage.getItem("celiac_session_id");
  if (existing) {
    setSessionId(existing);
    connectWS(existing);
  } else {
    axios.get(`${API}/session`).then(res => {
      const sid = res.data.session_id;
      localStorage.setItem("celiac_session_id", sid);
      setSessionId(sid);
      connectWS(sid);
    });
  }
}, []);

  const dismissReminder = (i) => {
    setReminders(prev => prev.filter((_, idx) => idx !== i));
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <div className="logo">🌾</div>
          <div>
            <h1>Celiac Assistant</h1>
            <p>Powered by Llama 3.2 · Local & Private</p>
          </div>
        </div>
        <nav className="tabs">
          <button
            className={activeTab === "chat" ? "tab active" : "tab"}
            onClick={() => setActiveTab("chat")}
          >Chat</button>
          <button
            className={activeTab === "dashboard" ? "tab active" : "tab"}
            onClick={() => setActiveTab("dashboard")}
          >Dashboard</button>
        </nav>
      </header>

      <main className="main">
        {activeTab === "chat" && (
          <ChatPanel sessionId={sessionId} api={API} />
        )}
        {activeTab === "dashboard" && (
          <Dashboard sessionId={sessionId} api={API} />
        )}
      </main>

      {reminders.map((msg, i) => (
        <ReminderToast key={i} message={msg} onDismiss={() => dismissReminder(i)} />
      ))}
    </div>
  );
}