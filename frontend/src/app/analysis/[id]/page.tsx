'use client';

import { useEffect, useState } from 'react';
import { endpoints, NarrativeClaim, VisionObservation, Case } from '@/lib/api';
import { ClaimCard } from '@/components/ClaimCard';
import { EvidenceCard } from '@/components/EvidenceCard';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Loader2, Play, RefreshCw, CheckCircle, ArrowLeft, FileText, Eye } from 'lucide-react';
import Link from 'next/link';

import { useParams } from 'next/navigation';

export default function AnalysisPage() {
    const params = useParams();
    const idParam = params?.id;
    const idString = Array.isArray(idParam) ? idParam[0] : (idParam || '0');
    const caseId = parseInt(idString);

    const [narrativeClaims, setNarrativeClaims] = useState<NarrativeClaim[]>([]);
    const [observations, setObservations] = useState<VisionObservation[]>([]);
    const [evidence, setEvidence] = useState<any[]>([]);
    const [caseData, setCaseData] = useState<Case | null>(null);

    // Separate loading states for each analysis
    const [isNarrativeAnalyzing, setIsNarrativeAnalyzing] = useState(false);
    const [isVisionAnalyzing, setIsVisionAnalyzing] = useState(false);

    // Track if we have cached results for each
    const [hasNarrativeCache, setHasNarrativeCache] = useState(false);
    const [hasVisionCache, setHasVisionCache] = useState(false);

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
            } catch (err) {
                console.error("Failed to load case", err);
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
        } catch (error) {
            console.error("Vision Analysis Failed", error);
        } finally {
            setIsVisionAnalyzing(false);
        }
    };

    // Run both analyses sequentially
    const runFullDiscovery = async () => {
        await runNarrativeAnalysis(false);
        await runVisionAnalysis(false);
    };

    const isAnyAnalyzing = isNarrativeAnalyzing || isVisionAnalyzing;
    const hasBothResults = hasNarrativeCache && hasVisionCache;

    return (
        <div className="h-screen flex flex-col bg-gray-50">
            {/* Header */}
            <header className="bg-white border-b px-6 py-4 flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <Link href="/cases">
                        <Button variant="ghost" size="sm">
                            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Cases
                        </Button>
                    </Link>
                    <div>
                        <div className="flex items-center gap-2">
                            <h1 className="text-xl font-bold">
                                {caseData?.title || `Investigation #${caseId}`}
                            </h1>
                            {hasBothResults && (
                                <Badge variant="outline" className="text-green-600 border-green-600">
                                    <CheckCircle className="mr-1 h-3 w-3" /> Fully Analyzed
                                </Badge>
                            )}
                        </div>
                        <p className="text-sm text-gray-500">Discovery Analysis Dashboard</p>
                    </div>
                </div>
                <div className="flex gap-2">
                    <Button onClick={runFullDiscovery} disabled={isAnyAnalyzing}>
                        {isAnyAnalyzing ? (
                            <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Processing...</>
                        ) : hasBothResults ? (
                            <><CheckCircle className="mr-2 h-4 w-4" /> Results Ready</>
                        ) : (
                            <><Play className="mr-2 h-4 w-4" /> Run Full Discovery</>
                        )}
                    </Button>
                </div>
            </header>

            {/* Split Screen */}
            <div className="flex-1 flex overflow-hidden">
                {/* Left: Narrative Agent */}
                <div className="w-1/2 p-6 overflow-y-auto border-r bg-white/50">
                    <div className="mb-4 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <FileText className="h-5 w-5 text-blue-600" />
                            <h2 className="text-lg font-semibold text-blue-900">Narrative Timeline</h2>
                            {hasNarrativeCache && (
                                <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50 text-xs">
                                    <CheckCircle className="mr-1 h-3 w-3" /> Done
                                </Badge>
                            )}
                        </div>
                        <div className="flex items-center gap-2">
                            <Badge variant="outline">{narrativeClaims.length} Claims</Badge>
                            {hasNarrativeCache ? (
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => runNarrativeAnalysis(true)}
                                    disabled={isNarrativeAnalyzing}
                                >
                                    {isNarrativeAnalyzing ? (
                                        <Loader2 className="h-4 w-4 animate-spin" />
                                    ) : (
                                        <><RefreshCw className="mr-1 h-3 w-3" /> Rerun</>
                                    )}
                                </Button>
                            ) : (
                                <Button
                                    size="sm"
                                    onClick={() => runNarrativeAnalysis(false)}
                                    disabled={isNarrativeAnalyzing}
                                >
                                    {isNarrativeAnalyzing ? (
                                        <Loader2 className="h-4 w-4 animate-spin" />
                                    ) : (
                                        <><Play className="mr-1 h-3 w-3" /> Analyze</>
                                    )}
                                </Button>
                            )}
                        </div>
                    </div>

                    <div className="space-y-4">
                        {narrativeClaims.length === 0 ? (
                            <div className="text-center py-20 text-gray-400 border-2 border-dashed rounded-lg">
                                {isNarrativeAnalyzing ? (
                                    <div className="flex flex-col items-center">
                                        <Loader2 className="h-8 w-8 animate-spin mb-2" />
                                        <p>Analyzing PDF report...</p>
                                    </div>
                                ) : (
                                    'Click "Analyze" to process the narrative'
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

                {/* Right: Vision Agent */}
                <div className="w-1/2 p-6 overflow-y-auto bg-gray-50">
                    <div className="mb-4 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Eye className="h-5 w-5 text-purple-600" />
                            <h2 className="text-lg font-semibold text-purple-900">Visual Grounding</h2>
                            {hasVisionCache && (
                                <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50 text-xs">
                                    <CheckCircle className="mr-1 h-3 w-3" /> Done
                                </Badge>
                            )}
                        </div>
                        <div className="flex items-center gap-2">
                            <Badge variant="outline">{observations.length} Facts</Badge>
                            {hasVisionCache ? (
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => runVisionAnalysis(true)}
                                    disabled={isVisionAnalyzing}
                                >
                                    {isVisionAnalyzing ? (
                                        <Loader2 className="h-4 w-4 animate-spin" />
                                    ) : (
                                        <><RefreshCw className="mr-1 h-3 w-3" /> Rerun</>
                                    )}
                                </Button>
                            ) : (
                                <Button
                                    size="sm"
                                    onClick={() => runVisionAnalysis(false)}
                                    disabled={isVisionAnalyzing || evidence.filter(e => e.type === 'IMAGE').length === 0}
                                >
                                    {isVisionAnalyzing ? (
                                        <Loader2 className="h-4 w-4 animate-spin" />
                                    ) : (
                                        <><Play className="mr-1 h-3 w-3" /> Analyze</>
                                    )}
                                </Button>
                            )}
                        </div>
                    </div>

                    {observations.length === 0 ? (
                        <div className="text-center py-20 text-gray-400 border-2 border-dashed rounded-lg">
                            {isVisionAnalyzing ? (
                                <div className="flex flex-col items-center">
                                    <Loader2 className="h-8 w-8 animate-spin mb-2" />
                                    <p>Analyzing {evidence.filter(e => e.type === 'IMAGE').length} image(s)...</p>
                                </div>
                            ) : (
                                'Click "Analyze" to process the evidence'
                            )}
                        </div>
                    ) : (
                        <EvidenceCard
                            imageUrl="/placeholder-evidence.jpg"
                            observations={observations.map(o => ({
                                ...o,
                                confidence: o.confidence as "LOW" | "MEDIUM" | "HIGH"
                            }))}
                            imageCount={evidence.filter((e: any) => e.type === 'IMAGE').length}
                        />
                    )}
                </div>
            </div>
        </div>
    );
}
