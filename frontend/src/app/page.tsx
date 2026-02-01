import { Button } from "@/components/ui/button";
import Link from "next/link";
import { ArrowRight, History } from "lucide-react";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-slate-950 text-white selection:bg-blue-500/30">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex">
        <p className="fixed left-0 top-0 flex w-full justify-center border-b border-slate-800 bg-slate-950/50 pb-6 pt-8 backdrop-blur-2xl lg:static lg:w-auto lg:rounded-xl lg:border lg:bg-slate-900/50 lg:p-4">
          Justitia Lens&nbsp;
          <code className="font-mono font-bold">v0.1.0</code>
        </p>
      </div>

      <div className="relative flex place-items-center before:absolute before:h-[300px] before:w-[480px] before:-translate-x-1/2 before:rounded-full before:bg-gradient-to-br before:from-blue-500 before:to-transparent before:opacity-10 before:blur-3xl after:absolute after:-z-20 after:h-[180px] after:w-[240px] after:translate-x-1/3 after:bg-gradient-to-tr after:from-cyan-400 after:to-transparent after:opacity-10 after:blur-3xl z-[-1]">
        <h1 className="text-6xl font-bold tracking-tighter text-center bg-clip-text text-transparent bg-gradient-to-b from-white to-slate-400">
          Discovery Gap.<br />Solved.
        </h1>
      </div>

      <div className="mt-12 text-center max-w-2xl text-slate-400">
        <p className="mb-8 text-lg">
          The AI-powered forensic intelligence platform that identifies discrepancies between
          legal narratives and objective visual evidence.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/upload">
            <Button size="lg" className="bg-blue-600 hover:bg-blue-500 text-white border-0 w-full sm:w-auto">
              Start New Investigation <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
          <Link href="/cases">
            <Button size="lg" variant="outline" className="border-slate-600 hover:bg-slate-800 text-white w-full sm:w-auto">
              <History className="mr-2 h-4 w-4" /> View Recent Cases
            </Button>
          </Link>
        </div>
      </div>

      <div className="mb-32 grid text-center lg:max-w-5xl lg:w-full lg:mb-0 lg:grid-cols-3 lg:text-left mt-24 gap-8">
        <div className="group rounded-lg border border-slate-800 px-5 py-4 transition-colors hover:border-slate-600 hover:bg-slate-900/50">
          <h2 className={`mb-3 text-2xl font-semibold`}>
            Narrative Agent{' '}
            <span className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
              -&gt;
            </span>
          </h2>
          <p className={`m-0 max-w-[30ch] text-sm opacity-50`}>
            Parses PDF reports to extract a timeline of factual assertions.
          </p>
        </div>

        <div className="group rounded-lg border border-slate-800 px-5 py-4 transition-colors hover:border-slate-600 hover:bg-slate-900/50">
          <h2 className={`mb-3 text-2xl font-semibold`}>
            Vision Agent{' '}
            <span className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
              -&gt;
            </span>
          </h2>
          <p className={`m-0 max-w-[30ch] text-sm opacity-50`}>
            Analyzes BWC footage/images for distinct forensic attributes.
          </p>
        </div>

        <div className="group rounded-lg border border-slate-800 px-5 py-4 transition-colors hover:border-slate-600 hover:bg-slate-900/50">
          <h2 className={`mb-3 text-2xl font-semibold`}>
            Adversarial Check{' '}
            <span className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
              -&gt;
            </span>
          </h2>
          <p className={`m-0 max-w-[30ch] text-sm opacity-50`}>
            Cross-references claims against evidence to flag discrepancies.
          </p>
        </div>
      </div>
    </main>
  );
}
