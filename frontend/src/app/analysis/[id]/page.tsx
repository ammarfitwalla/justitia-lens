'use client';

import { useEffect, useState } from 'react';
import { endpoints, NarrativeClaim, VisionObservation, Case, SynthesisDiscrepancy } from '@/lib/api';
import { ClaimCard } from '@/components/ClaimCard';
import { EvidenceCard } from '@/components/EvidenceCard';
import { DiscrepancyCard } from '@/components/DiscrepancyCard';
import { Navbar } from '@/components/Navbar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Loader2, Play, RefreshCw, CheckCircle, ArrowLeft, FileText, Eye, AlertTriangle, Zap } from 'lucide-react';
import Link from 'next/link';

import { useParams } from 'next/navigation';

export default function AnalysisPage() {
    const params = useParams();
    const idParam = params?.id;
    const idString = Array.isArray(idParam) ? idParam[0] : (idParam || '0');
    const caseId = parseInt(idString);

    const [narrativeClaims, setNarrativeClaims] = useState<NarrativeClaim[]>([]);
    const [observations, setObservations] = useState<VisionObservation[]>([]);
    const [discrepancies, setDiscrepancies] = useState<SynthesisDiscrepancy[]>([]);
    const [evidence, setEvidence] = useState<any[]>([]);
    const [caseData, setCaseData] = useState<Case | null>(null);

    // Separate loading states for each analysis
    const [isNarrativeAnalyzing, setIsNarrativeAnalyzing] = useState(false);
    const [isVisionAnalyzing, setIsVisionAnalyzing] = useState(false);
    const [isSynthesizing, setIsSynthesizing] = useState(false);

    // Track if we have cached results for each
    const [hasNarrativeCache, setHasNarrativeCache] = useState(false);
    const [hasVisionCache, setHasVisionCache] = useState(false);
    const [hasSynthesisCache, setHasSynthesisCache] = useState(false);

    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchCase = async () => {
            try {
                const res = await endpoints.getCase(caseId);
                const data = res.data;
                setCaseData(data);
                setEvidence(data.evidence || []);

                // Check for cached narrative results
                if (data.narrative_analysis_json) {
                    try {
                        const cached = JSON.parse(data.narrative_analysis_json);
                        setNarrativeClaims(cached.timeline || []);
                        setHasNarrativeCache(true);
                    } catch (e) {
                        console.error("Failed to parse cached narrative", e);
                    }
                }

                // Check for cached vision results
                if (data.vision_analysis_json) {
                    try {
                        const cached = JSON.parse(data.vision_analysis_json);
                        setObservations(cached.observations || []);
                        setHasVisionCache(true);
                    } catch (e) {
                        console.error("Failed to parse cached vision", e);
                    }
                }

                // Check for cached synthesis results
                if (data.synthesis_analysis_json) {
                    try {
                        const cached = JSON.parse(data.synthesis_analysis_json);
                        setDiscrepancies(cached.discrepancies || []);
                        setHasSynthesisCache(true);
                    } catch (e) {
                        console.error("Failed to parse cached synthesis", e);
                    }
                }
            } catch (err) {
                console.error("Failed to load case", err);
            } finally {
                setIsLoading(false);
            }
        };
        fetchCase();
    }, [caseId]);

    // Run narrative analysis only
    const runNarrativeAnalysis = async (forceRerun: boolean = false) => {
        setIsNarrativeAnalyzing(true);
        try {
            const narrativeRes = await endpoints.analyzeNarrative(caseId, forceRerun);
            setNarrativeClaims(narrativeRes.data.timeline || []);
            setHasNarrativeCache(true);
            // Clear synthesis cache since inputs changed
            if (forceRerun) {
                setDiscrepancies([]);
                setHasSynthesisCache(false);
            }
        } catch (error) {
            console.error("Narrative Analysis Failed", error);
        } finally {
            setIsNarrativeAnalyzing(false);
        }
    };

    // Run vision analysis only
    const runVisionAnalysis = async (forceRerun: boolean = false) => {
        const imageCount = evidence.filter((e: any) => e.type === 'IMAGE').length;
        if (imageCount === 0) return;

        setIsVisionAnalyzing(true);
        try {
            const visionRes = await endpoints.analyzeAllEvidence(caseId, forceRerun);
            setObservations(visionRes.data.observations || []);
            setHasVisionCache(true);
            // Clear synthesis cache since inputs changed
            if (forceRerun) {
                setDiscrepancies([]);
                setHasSynthesisCache(false);
            }
        } catch (error) {
            console.error("Vision Analysis Failed", error);
        } finally {
            setIsVisionAnalyzing(false);
        }
    };

    // Run synthesis analysis
    const runSynthesis = async (forceRerun: boolean = false) => {
        setIsSynthesizing(true);
        try {
            const synthesisRes = await endpoints.synthesize(caseId, forceRerun);
            setDiscrepancies(synthesisRes.data.discrepancies || []);
            setHasSynthesisCache(true);
        } catch (error) {
            console.error("Synthesis Failed", error);
        } finally {
            setIsSynthesizing(false);
        }
    };

    // Run all analyses sequentially
    const runFullDiscovery = async () => {
        await runNarrativeAnalysis(false);
        await runVisionAnalysis(false);
        // Auto-run synthesis after both are complete
        await runSynthesis(false);
    };

    const isAnyAnalyzing = isNarrativeAnalyzing || isVisionAnalyzing || isSynthesizing;
    const canRunSynthesis = hasNarrativeCache && hasVisionCache;
    const isFullyComplete = hasNarrativeCache && hasVisionCache && hasSynthesisCache;

    if (isLoading) {
        return (
            <div className="h-screen flex flex-col bg-background">
                <Navbar />
                <div className="flex-1 flex items-center justify-center">
                    <div className="flex flex-col items-center gap-4">
                        <Loader2 className="h-12 w-12 animate-spin text-primary" />
                        <h2 className="text-xl font-semibold">Loading Investigation...</h2>
                        <p className="text-muted-foreground">Retrieving case files and evidence.</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="h-screen flex flex-col bg-background">
            {/* Global Navigation */}
            <Navbar />

            {/* Page Header */}
            <header className="bg-background border-b border-border px-6 py-4 flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <Link href="/cases">
                        <Button variant="ghost" size="sm">
                            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Cases
                        </Button>
                    </Link>
                    <div>
                        <div className="flex items-center gap-2">
                            <h1 className="text-xl font-bold text-foreground">
                                {caseData?.title || `Investigation #${caseId}`}
                            </h1>
                            {isFullyComplete && (
                                <Badge variant="outline" className="text-green-600 border-green-600">
                                    <CheckCircle className="mr-1 h-3 w-3" /> Fully Analyzed
                                </Badge>
                            )}
                        </div>
                        <p className="text-sm text-muted-foreground">Discovery Analysis Dashboard</p>
                    </div>
                </div>
                <div className="flex gap-2">
                    <Button onClick={runFullDiscovery} disabled={isAnyAnalyzing}>
                        {isAnyAnalyzing ? (
                            <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Processing...</>
                        ) : isFullyComplete ? (
                            <><CheckCircle className="mr-2 h-4 w-4" /> Results Ready</>
                        ) : (
                            <><Play className="mr-2 h-4 w-4" /> Run Full Discovery</>
                        )}
                    </Button>
                </div>
            </header>

            {/* Three Column Layout */}
            <div className="flex-1 flex overflow-hidden">
                {/* Left: Narrative Agent */}
                <div className="w-1/3 p-4 overflow-y-auto border-r bg-white/50">
                    <div className="mb-4 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <FileText className="h-5 w-5 text-blue-600" />
                            <h2 className="text-lg font-semibold text-blue-900">Narrative</h2>
                            {hasNarrativeCache && (
                                <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50 text-xs">
                                    <CheckCircle className="mr-1 h-3 w-3" />
                                </Badge>
                            )}
                        </div>
                        <div className="flex items-center gap-2">
                            <Badge variant="outline" className="text-xs">{narrativeClaims.length}</Badge>
                            {hasNarrativeCache ? (
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => runNarrativeAnalysis(true)}
                                    disabled={isNarrativeAnalyzing || caseData?.is_sample_case}
                                    className="h-7 px-2"
                                >
                                    {isNarrativeAnalyzing ? (
                                        <Loader2 className="h-3 w-3 animate-spin" />
                                    ) : (
                                        <RefreshCw className="h-3 w-3" />
                                    )}
                                </Button>
                            ) : (
                                <Button
                                    size="sm"
                                    onClick={() => runNarrativeAnalysis(false)}
                                    disabled={isNarrativeAnalyzing || caseData?.is_sample_case}
                                    className="h-7 px-2"
                                >
                                    {isNarrativeAnalyzing ? (
                                        <Loader2 className="h-3 w-3 animate-spin" />
                                    ) : (
                                        <Play className="h-3 w-3" />
                                    )}
                                </Button>
                            )}
                        </div>
                    </div>

                    <div className="space-y-3">
                        {narrativeClaims.length === 0 ? (
                            <div className="text-center py-16 text-gray-400 border-2 border-dashed rounded-lg">
                                {isNarrativeAnalyzing ? (
                                    <div className="flex flex-col items-center">
                                        <Loader2 className="h-8 w-8 animate-spin mb-2" />
                                        <p className="text-sm">Analyzing PDF...</p>
                                    </div>
                                ) : (
                                    <p className="text-sm">Click play to analyze</p>
                                )}
                            </div>
                        ) : (
                            narrativeClaims.map((claim, idx) => (
                                <ClaimCard
                                    key={idx}
                                    timestamp={claim.timestamp_ref || "Unknown"}
                                    entity={claim.entity}
                                    action={claim.action}
                                    object={claim.object}
                                    certainty={claim.certainty as "EXPLICIT" | "IMPLIED"}
                                    description={claim.description}
                                />
                            ))
                        )}
                    </div>
                </div>

                {/* Middle: Vision Agent */}
                <div className="w-1/3 p-4 overflow-y-auto border-r bg-gray-50">
                    <div className="mb-4 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Eye className="h-5 w-5 text-purple-600" />
                            <h2 className="text-lg font-semibold text-purple-900">Evidence</h2>
                            {hasVisionCache && (
                                <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50 text-xs">
                                    <CheckCircle className="mr-1 h-3 w-3" />
                                </Badge>
                            )}
                        </div>
                        <div className="flex items-center gap-2">
                            <Badge variant="outline" className="text-xs">{observations.length}</Badge>
                            {hasVisionCache ? (
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => runVisionAnalysis(true)}
                                    disabled={isVisionAnalyzing || caseData?.is_sample_case}
                                    className="h-7 px-2"
                                >
                                    {isVisionAnalyzing ? (
                                        <Loader2 className="h-3 w-3 animate-spin" />
                                    ) : (
                                        <RefreshCw className="h-3 w-3" />
                                    )}
                                </Button>
                            ) : (
                                <Button
                                    size="sm"
                                    onClick={() => runVisionAnalysis(false)}
                                    disabled={isVisionAnalyzing || caseData?.is_sample_case || evidence.filter(e => e.type === 'IMAGE').length === 0}
                                    className="h-7 px-2"
                                >
                                    {isVisionAnalyzing ? (
                                        <Loader2 className="h-3 w-3 animate-spin" />
                                    ) : (
                                        <Play className="h-3 w-3" />
                                    )}
                                </Button>
                            )}
                        </div>
                    </div>

                    {observations.length === 0 ? (
                        <div className="text-center py-16 text-gray-400 border-2 border-dashed rounded-lg">
                            {isVisionAnalyzing ? (
                                <div className="flex flex-col items-center">
                                    <Loader2 className="h-8 w-8 animate-spin mb-2" />
                                    <p className="text-sm">Analyzing images...</p>
                                </div>
                            ) : (
                                <p className="text-sm">Click play to analyze</p>
                            )}
                        </div>
                    ) : (
                        <EvidenceCard
                            images={evidence}
                            observations={observations.map(o => ({
                                ...o,
                                confidence: o.confidence as "LOW" | "MEDIUM" | "HIGH"
                            }))}
                            imageCount={evidence.filter((e: any) => e.type === 'IMAGE').length}
                        />
                    )}
                </div>

                {/* Right: Synthesis / Discrepancies */}
                <div className="w-1/3 p-4 overflow-y-auto bg-white">
                    <div className="mb-4 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <AlertTriangle className="h-5 w-5 text-red-500" />
                            <h2 className="text-lg font-semibold text-red-900">Discrepancies</h2>
                            {hasSynthesisCache && (
                                <Badge
                                    variant="outline"
                                    className={discrepancies.length > 0
                                        ? "text-red-600 border-red-200 bg-red-50 text-xs"
                                        : "text-green-600 border-green-200 bg-green-50 text-xs"
                                    }
                                >
                                    {discrepancies.length > 0 ? (
                                        <AlertTriangle className="mr-1 h-3 w-3" />
                                    ) : (
                                        <CheckCircle className="mr-1 h-3 w-3" />
                                    )}
                                </Badge>
                            )}
                        </div>
                        <div className="flex items-center gap-2">
                            <Badge variant="outline" className="text-xs">{discrepancies.length}</Badge>
                            {hasSynthesisCache ? (
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => runSynthesis(true)}
                                    disabled={isSynthesizing || !canRunSynthesis}
                                    className="h-7 px-2"
                                >
                                    {isSynthesizing ? (
                                        <Loader2 className="h-3 w-3 animate-spin" />
                                    ) : (
                                        <RefreshCw className="h-3 w-3" />
                                    )}
                                </Button>
                            ) : (
                                <Button
                                    size="sm"
                                    onClick={() => runSynthesis(false)}
                                    disabled={isSynthesizing || !canRunSynthesis || caseData?.is_sample_case}
                                    className="h-7 px-2"
                                    variant={canRunSynthesis ? "default" : "outline"}
                                >
                                    {isSynthesizing ? (
                                        <Loader2 className="h-3 w-3 animate-spin" />
                                    ) : (
                                        <Zap className="h-3 w-3" />
                                    )}
                                </Button>
                            )}
                        </div>
                    </div>

                    {!canRunSynthesis ? (
                        <div className="text-center py-16 text-gray-400 border-2 border-dashed rounded-lg">
                            <div className="flex flex-col items-center">
                                <Zap className="h-8 w-8 mb-2 text-gray-300" />
                                <p className="text-sm font-medium">Cross-Reference Analysis</p>
                                <p className="text-xs mt-1">Complete both analyses first</p>
                            </div>
                        </div>
                    ) : isSynthesizing ? (
                        <div className="text-center py-16 text-gray-400 border-2 border-dashed rounded-lg">
                            <div className="flex flex-col items-center">
                                <Loader2 className="h-8 w-8 animate-spin mb-2" />
                                <p className="text-sm">Cross-referencing...</p>
                            </div>
                        </div>
                    ) : hasSynthesisCache ? (
                        <DiscrepancyCard discrepancies={discrepancies} />
                    ) : (
                        <div className="text-center py-16 text-gray-400 border-2 border-dashed rounded-lg">
                            <div className="flex flex-col items-center">
                                <Zap className="h-8 w-8 mb-2 text-yellow-400" />
                                <p className="text-sm font-medium">Ready to Cross-Reference</p>
                                <p className="text-xs mt-1">Click the button to find discrepancies</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
