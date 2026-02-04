import { Button } from "@/components/ui/button";
import Link from "next/link";
import { ArrowRight, History, Scale, Eye, FileSearch } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-16">
        {/* Top Badge */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-muted border border-border rounded-full text-sm text-foreground">
            <Scale className="w-4 h-4" />
            Justitia Lens <span className="font-mono text-xs">v0.1.0</span>
          </div>
        </div>

        {/* Hero Section */}
        <div className="text-center max-w-4xl mx-auto mb-16">
          <h1 className="text-5xl md:text-6xl font-bold text-foreground mb-6">
            Discovery Gap. <span className="text-primary">Solved.</span>
          </h1>
          <p className="text-xl text-muted-foreground mb-8">
            The AI-powered forensic intelligence platform that identifies
            discrepancies between legal narratives and objective visual evidence.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" className="gap-2">
              <Link href="/upload">
                Start New Investigation
                <ArrowRight className="w-4 h-4" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="gap-2">
              <Link href="/cases">
                <History className="w-4 h-4" />
                View Cases
              </Link>
            </Button>
          </div>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto mb-16">
          {/* Narrative Agent */}
          <div className="bg-card p-6 rounded-lg shadow-sm border border-border hover:shadow-md transition-shadow">
            <div className="w-12 h-12 bg-muted rounded-lg flex items-center justify-center mb-4">
              <FileSearch className="w-6 h-6 text-foreground" />
            </div>
            <h3 className="text-xl font-semibold text-card-foreground mb-2">
              Narrative Agent
            </h3>
            <p className="text-muted-foreground mb-4">
              Extracts a chronological timeline of factual assertions from PDF
              reports with certainty classification.
            </p>
            <Link
              href="/features/narrative"
              className="text-primary hover:text-primary/80 font-medium inline-flex items-center gap-1"
            >
              Learn more
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {/* Vision Agent */}
          <div className="bg-card p-6 rounded-lg shadow-sm border border-border hover:shadow-md transition-shadow">
            <div className="w-12 h-12 bg-muted rounded-lg flex items-center justify-center mb-4">
              <Eye className="w-6 h-6 text-foreground" />
            </div>
            <h3 className="text-xl font-semibold text-card-foreground mb-2">
              Vision Agent
            </h3>
            <p className="text-muted-foreground mb-4">
              Analyzes BWC footage and images for objective forensic attributes
              with confidence scoring.
            </p>
            <Link
              href="/features/vision"
              className="text-primary hover:text-primary/80 font-medium inline-flex items-center gap-1"
            >
              Learn more
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {/* Adversarial Check */}
          <div className="bg-card p-6 rounded-lg shadow-sm border border-border hover:shadow-md transition-shadow">
            <div className="w-12 h-12 bg-muted rounded-lg flex items-center justify-center mb-4">
              <Scale className="w-6 h-6 text-foreground" />
            </div>
            <h3 className="text-xl font-semibold text-card-foreground mb-2">
              Adversarial Check
            </h3>
            <p className="text-muted-foreground mb-4">
              Cross-references narrative claims against visual evidence to flag
              potential discrepancies.
            </p>
            <Link
              href="/features/adversarial"
              className="text-primary hover:text-primary/80 font-medium inline-flex items-center gap-1"
            >
              Learn more
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>

        {/* Footer Tagline */}
        <div className="text-center text-muted-foreground text-sm">
          Powered by Multi-Modal AI • Forensic-Grade Analysis
        </div>
      </div>
    </div>
  );
}