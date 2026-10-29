import { Routes, Route } from "react-router";

import AuthLayout from "../components/layout/AuthLayout";
import EmployeeLayout from "../components/layout/EmployeeLayout";
import AgentLayout from "../components/layout/AgentLayout";

import LoginPage from "../features/auth/pages/LoginPage";
import RegisterPage from "../features/auth/pages/RegisterPage";

import EmployeeHomePage from "../features/employe/pages/EmployeeHomePage";
import AgentDashboardPage from "../features/agents/pages/AgentDashboardPage";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<AuthLayout />}>
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
      </Route>

      <Route path="/employee" element={<EmployeeLayout />}>
        <Route index element={<EmployeeHomePage />} />
      </Route>

      <Route path="/agent" element={<AgentLayout />}>
        <Route index element={<AgentDashboardPage />} />
      </Route>
    </Routes>
  );
}
