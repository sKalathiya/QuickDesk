import RegisterForm from "../components/RegisterForm";
export default function RegisterPage() {
  return (
    <section className="flex flex-col bg-surface border border-border rounded-xl p-12 w-full max-w-lg  shadow-sm space-y-8">
      <div className="flex flex-col space-y-2">
        <h1 className="text-lg font-semibold tracking-tight text-foreground">
          Welcome!
        </h1>
        <p className="text-sm text-muted">
          Sign up to get started with QuickDesk.
        </p>
      </div>
      <RegisterForm />
    </section>
  );
}
