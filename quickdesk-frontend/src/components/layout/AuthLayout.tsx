import { Outlet } from "react-router";
export default function AuthLayout() {
  return (
    <main className="min-h-screen bg-canvas flex items-center justify-center p-6">
      <Outlet />
    </main>
  );
}
