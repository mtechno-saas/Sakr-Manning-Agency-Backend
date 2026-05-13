import { createRoot } from "react-dom/client";
import "./styles/globals.css";

import App from "./App.jsx";
import { AuthProvider } from "./context/AuthContext";
import { NotificationProvider } from "./components/dashboard/context/NotificationContext";

createRoot(document.getElementById("root")).render(
  <AuthProvider>
    <NotificationProvider>
      <App />
    </NotificationProvider>
  </AuthProvider>
);
