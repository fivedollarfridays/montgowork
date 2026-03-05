export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="max-w-2xl text-center space-y-6">
        <h1 className="text-4xl font-bold tracking-tight text-primary sm:text-5xl">
          MontGoWork
        </h1>
        <p className="text-xl text-muted-foreground">
          Workforce Navigator for Montgomery, Alabama
        </p>
        <div className="flex gap-4 justify-center pt-4">
          <a
            href="/assess"
            className="rounded-lg bg-primary px-6 py-3 text-primary-foreground font-medium hover:opacity-90 transition-opacity"
          >
            Start Assessment
          </a>
          <a
            href="/credit"
            className="rounded-lg bg-secondary px-6 py-3 text-secondary-foreground font-medium hover:opacity-90 transition-opacity"
          >
            Check Credit
          </a>
        </div>
      </div>
    </main>
  );
}
