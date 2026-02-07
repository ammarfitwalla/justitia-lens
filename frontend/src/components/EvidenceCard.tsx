'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Eye, AlertTriangle, Info, HelpCircle, ChevronLeft, ChevronRight, Image as ImageIcon } from 'lucide-react';
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

interface EvidenceImage {
    id: number;
    file_path: string;
    type: string;
}

interface EvidenceCardProps {
    images: EvidenceImage[]; // Array of evidence items with file paths
    observations: Observation[];
    imageCount?: number;
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

// Convert Windows file path to URL path for static serving
// Also handles full URLs (e.g., from Supabase Storage)
function getImageUrl(filePath: string): string {
    // If already a URL, return as-is
    if (filePath.startsWith('http://') || filePath.startsWith('https://')) {
        return filePath;
    }

    // Extract path after 'cases/' and convert to URL for local development
    const match = filePath.match(/cases[\\\/](.+)/);
    if (match) {
        const cleanPath = match[1].replace(/\\/g, '/');
        return `http://localhost:8000/static/cases/${cleanPath}`;
    }
    return filePath;
}

export function EvidenceCard({ images, observations, imageCount }: EvidenceCardProps) {
    const [currentImageIndex, setCurrentImageIndex] = useState(0);
    const imageEvidence = images?.filter(e => e.type === 'IMAGE') || [];
    const totalImages = imageEvidence.length;

    const goToPrevious = () => {
        setCurrentImageIndex((prev) => (prev > 0 ? prev - 1 : totalImages - 1));
    };

    const goToNext = () => {
        setCurrentImageIndex((prev) => (prev < totalImages - 1 ? prev + 1 : 0));
    };

    // Get observations for current image (1-indexed in data)
    const currentObservations = observations.filter(
        obs => obs.evidence_index === currentImageIndex + 1
    );

    return (
        <div className="grid grid-cols-1 gap-4">
            {/* Confidence Legend */}
            <ConfidenceLegend />

            {/* Image Carousel */}
            {totalImages > 0 && (
                <Card className="overflow-hidden">
                    <div className="relative">
                        {/* Image Display */}
                        <div className="relative h-48 bg-gray-100 flex items-center justify-center overflow-hidden">
                            <img
                                src={getImageUrl(imageEvidence[currentImageIndex].file_path)}
                                alt={`Evidence ${currentImageIndex + 1}`}
                                className="max-h-full max-w-full object-contain"
                                onError={(e) => {
                                    const target = e.target as HTMLImageElement;
                                    target.style.display = 'none';
                                    target.nextElementSibling?.classList.remove('hidden');
                                }}
                            />
                            <div className="hidden flex-col items-center text-gray-400">
                                <ImageIcon className="w-12 h-12 mb-2" />
                                <span className="text-sm">Image not available</span>
                            </div>
                        </div>

                        {/* Navigation Arrows */}
                        {totalImages > 1 && (
                            <>
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    className="absolute left-2 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white shadow-md rounded-full h-8 w-8"
                                    onClick={goToPrevious}
                                >
                                    <ChevronLeft className="h-5 w-5" />
                                </Button>
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    className="absolute right-2 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white shadow-md rounded-full h-8 w-8"
                                    onClick={goToNext}
                                >
                                    <ChevronRight className="h-5 w-5" />
                                </Button>
                            </>
                        )}

                        {/* Image Counter */}
                        <div className="absolute bottom-2 left-1/2 -translate-x-1/2 bg-black/60 text-white px-3 py-1 rounded-full text-xs">
                            {currentImageIndex + 1} / {totalImages}
                        </div>
                    </div>

                    {/* Dot Indicators */}
                    {totalImages > 1 && (
                        <div className="flex justify-center gap-1.5 py-2 bg-gray-50">
                            {imageEvidence.map((_, idx) => (
                                <button
                                    key={idx}
                                    className={`w-2 h-2 rounded-full transition-colors ${idx === currentImageIndex ? 'bg-purple-600' : 'bg-gray-300 hover:bg-gray-400'
                                        }`}
                                    onClick={() => setCurrentImageIndex(idx)}
                                />
                            ))}
                        </div>
                    )}
                </Card>
            )}

            {/* Observations for Current Image */}
            <Card>
                <CardContent className="p-4">
                    <h3 className="text-sm font-semibold text-gray-500 mb-3 flex items-center gap-2">
                        <Eye className="w-4 h-4" />
                        {totalImages > 0
                            ? `Observations for Image ${currentImageIndex + 1}`
                            : 'Visual Discovery'}
                    </h3>
                    <ScrollArea className="h-[200px] pr-4">
                        <div className="space-y-3">
                            {(totalImages > 0 ? currentObservations : observations).map((obs, idx) => (
                                <div key={idx} className="flex flex-col gap-1 pb-3 border-b last:border-0 border-gray-100">
                                    <div className="flex justify-between items-center">
                                        <div className="flex items-center gap-2">
                                            <span className="font-medium text-sm">{obs.label}</span>
                                            <Badge variant="secondary" className="text-xs px-1.5 py-0">
                                                {obs.category}
                                            </Badge>
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
                            {(totalImages > 0 ? currentObservations : observations).length === 0 && (
                                <p className="text-sm text-gray-400 italic">No observations for this image yet.</p>
                            )}
                        </div>
                    </ScrollArea>
                </CardContent>
            </Card>
        </div>
    );
}
