import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Eye, AlertTriangle, Info, HelpCircle } from 'lucide-react';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";

interface Observation {
    label: string;
    confidence: 'LOW' | 'MEDIUM' | 'HIGH';
    details: string;
    category: string;
    evidence_id?: number;
    evidence_index?: number;
}

interface EvidenceCardProps {
    imageUrl: string; // In real app, this would be the backend URL
    observations: Observation[];
    imageCount?: number; // Total number of images analyzed
}

const confidenceDescriptions = {
    HIGH: "Strong visual evidence clearly supports this observation with high certainty",
    MEDIUM: "Visual evidence provides moderate support; some ambiguity exists",
    LOW: "Limited visual evidence; requires additional verification or context"
};

function ConfidenceLegend() {
    return (
        <div className="bg-gray-50 rounded-lg p-3 mb-4 border border-gray-200">
            <div className="flex items-center gap-2 mb-2">
                <Info className="w-4 h-4 text-gray-500" />
                <span className="text-xs font-semibold text-gray-600">Confidence Levels</span>
            </div>
            <div className="space-y-1.5">
                <div className="flex items-start gap-2">
                    <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50 text-xs shrink-0">
                        HIGH
                    </Badge>
                    <span className="text-xs text-gray-500">{confidenceDescriptions.HIGH}</span>
                </div>
                <div className="flex items-start gap-2">
                    <Badge variant="outline" className="text-yellow-600 border-yellow-200 bg-yellow-50 text-xs shrink-0">
                        MEDIUM
                    </Badge>
                    <span className="text-xs text-gray-500">{confidenceDescriptions.MEDIUM}</span>
                </div>
                <div className="flex items-start gap-2">
                    <Badge variant="outline" className="text-red-500 border-red-200 bg-red-50 text-xs shrink-0">
                        LOW
                    </Badge>
                    <span className="text-xs text-gray-500">{confidenceDescriptions.LOW}</span>
                </div>
            </div>
        </div>
    );
}

export function EvidenceCard({ imageUrl, observations, imageCount }: EvidenceCardProps) {
    return (
        <div className="grid grid-cols-1 gap-4">
            {/* Confidence Legend */}
            <ConfidenceLegend />

            {/* Image Count Indicator */}
            {imageCount && imageCount > 1 && (
                <div className="flex items-center gap-2 text-sm text-purple-700 bg-purple-50 px-3 py-2 rounded-lg border border-purple-200">
                    <Eye className="w-4 h-4" />
                    <span>Analyzing <strong>{imageCount}</strong> images - observations grouped by source</span>
                </div>
            )}

            {/* AI Analysis List */}
            <Card>
                <CardContent className="p-4">
                    <h3 className="text-sm font-semibold text-gray-500 mb-3 flex items-center gap-2">
                        <Eye className="w-4 h-4" /> Visual Discovery
                    </h3>
                    <ScrollArea className="h-[300px] pr-4">
                        <div className="space-y-3">
                            {observations.map((obs, idx) => (
                                <div key={idx} className="flex flex-col gap-1 pb-3 border-b last:border-0 border-gray-100">
                                    <div className="flex justify-between items-center">
                                        <div className="flex items-center gap-2">
                                            <span className="font-medium text-sm">{obs.label}</span>
                                            {obs.evidence_index && (
                                                <Badge variant="secondary" className="text-xs px-1.5 py-0">
                                                    Image {obs.evidence_index}
                                                </Badge>
                                            )}
                                        </div>
                                        <TooltipProvider>
                                            <Tooltip>
                                                <TooltipTrigger asChild>
                                                    <Badge
                                                        variant="outline"
                                                        className={`cursor-help ${obs.confidence === 'HIGH' ? 'text-green-600 border-green-200 bg-green-50' :
                                                                obs.confidence === 'MEDIUM' ? 'text-yellow-600 border-yellow-200 bg-yellow-50' :
                                                                    'text-red-500 border-red-200 bg-red-50'
                                                            }`}
                                                    >
                                                        {obs.confidence}
                                                    </Badge>
                                                </TooltipTrigger>
                                                <TooltipContent side="left" className="max-w-xs">
                                                    <p className="text-xs">{confidenceDescriptions[obs.confidence]}</p>
                                                </TooltipContent>
                                            </Tooltip>
                                        </TooltipProvider>
                                    </div>
                                    <p className="text-xs text-gray-500 leading-snug">{obs.details}</p>
                                </div>
                            ))}
                            {observations.length === 0 && (
                                <p className="text-sm text-gray-400 italic">No observations yet.</p>
                            )}
                        </div>
                    </ScrollArea>
                </CardContent>
            </Card>
        </div>
    );
}

