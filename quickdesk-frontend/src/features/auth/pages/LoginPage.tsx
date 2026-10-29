import LoginForm from "../components/LoginForm";
export default function LoginPage() {
  return (
    <section className="flex flex-col bg-surface border border-border rounded-xl p-12 w-full max-w-md  shadow-sm space-y-8">
      <div className="flex flex-col space-y-2">
        <h1 className="text-lg font-semibold tracking-tight text-foreground">
          Welcome back!
        </h1>
        <p className="text-sm text-muted">
          Sign in to your account to continue using QuickDesk.
        </p>
      </div>
      <LoginForm />
    </section>
  );
}
