import { Routes, Route } from "react-router";
import AuthLayout from "../components/layout/AuthLayout";
import LoginPage from "../features/auth/pages/LoginPage";
import RegisterPage from "../features/auth/pages/RegisterPage";
import EmployeeLayout from "../components/layout/EmployeeLayout";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<AuthLayout />}>
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
      </Route>
      <Route path="/employee" element={<EmployeeLayout />}>
        <Route index element={<div>Employee Dashboard</div>} />
      </Route>
    </Routes>
  );
}
