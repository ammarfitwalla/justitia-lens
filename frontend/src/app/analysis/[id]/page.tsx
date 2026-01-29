'use client';

import { useEffect, useState } from 'react';
import { endpoints, NarrativeClaim, VisionObservation } from '@/lib/api';
import { ClaimCard } from '@/components/ClaimCard';
import { EvidenceCard } from '@/components/EvidenceCard';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Loader2, Play } from 'lucide-react';

export default function AnalysisPage({ params }: { params: { id: string } }) {
    const caseId = parseInt(params.id);
    const [narrativeClaims, setNarrativeClaims] = useState<NarrativeClaim[]>([]);
    const [observations, setObservations] = useState<VisionObservation[]>([]);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [evidence, setEvidence] = useState<any[]>([]);

    useEffect(() => {
        const fetchCase = async () => {
            try {
                const res = await endpoints.getCase(caseId);
                // @ts-ignore - The API result might have evidence not yet in the Interface type if not updated.
                // But we will update the type next.
                setEvidence(res.data.evidence || []);
            } catch (err) {
                console.error("Failed to load case", err);
            }
        };
        fetchCase();
    }, [caseId]);

    const runDiscovery = async () => {
        setIsAnalyzing(true);
        try {
            // 1. Trigger Narrative Agent
            const narrativeRes = await endpoints.analyzeNarrative(caseId);
            setNarrativeClaims(narrativeRes.data.timeline || []);

            // 2. Trigger Vision Agent
            if (evidence.length > 0) {
                const firstImage = evidence.find((e: any) => e.type === 'IMAGE');
                if (firstImage) {
                    const visionRes = await endpoints.analyzeEvidence(firstImage.id);
                    setObservations(visionRes.data.observations || []);
                }
            }
        } catch (error) {
            console.error("Analysis Failed", error);
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <div className="h-screen flex flex-col bg-gray-50">
            {/* Header */}
            <header className="bg-white border-b px-6 py-4 flex justify-between items-center">
                <div>
                    <h1 className="text-xl font-bold">Investigation #{caseId}</h1>
                    <p className="text-sm text-gray-500">Discovery Analysis Dashboard</p>
                </div>
                <Button onClick={runDiscovery} disabled={isAnalyzing}>
                    {isAnalyzing ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Processing AI Agents...</> : <><Play className="mr-2 h-4 w-4" /> Run Discovery Logic</>}
                </Button>
            </header>

            {/* Split Screen */}
            <div className="flex-1 flex overflow-hidden">
                {/* Left: Narrative Agent */}
                <div className="w-1/2 p-6 overflow-y-auto border-r bg-white/50">
                    <div className="mb-4 flex items-center justify-between">
                        <h2 className="text-lg font-semibold text-blue-900">Agent 1: Narrative Timeline</h2>
                        <Badge variant="outline">{narrativeClaims.length} Claims</Badge>
                    </div>

                    <div className="space-y-4">
                        {narrativeClaims.length === 0 ? (
                            <div className="text-center py-20 text-gray-400 border-2 border-dashed rounded-lg">
                                Pending Analysis...
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
                        <h2 className="text-lg font-semibold text-purple-900">Agent 2: Visual Grounding</h2>
                        <Badge variant="outline">{observations.length} Facts</Badge>
                    </div>

                    {/* Mocking Evidence View for MVP Layout */}
                    <EvidenceCard
                        imageUrl="/placeholder-evidence.jpg"
                        observations={observations.map(o => ({
                            ...o,
                            confidence: o.confidence as "LOW" | "MEDIUM" | "HIGH"
                        }))}
                    />
                </div>
            </div>
        </div>
    );
}
