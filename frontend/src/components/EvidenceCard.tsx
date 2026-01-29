import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Eye, AlertTriangle } from 'lucide-react';

interface Observation {
    label: string;
    confidence: 'LOW' | 'MEDIUM' | 'HIGH';
    details: string;
    category: string;
}

interface EvidenceCardProps {
    imageUrl: string; // In real app, this would be the backend URL
    observations: Observation[];
}

export function EvidenceCard({ imageUrl, observations }: EvidenceCardProps) {
    return (
        <div className="grid grid-cols-1 gap-4">
            {/* Image View */}
            <div className="relative rounded-lg overflow-hidden border border-gray-200 bg-black/5 aspect-video flex items-center justify-center">
                {/* Placeholder for actual image loading */}
                <img src={imageUrl} alt="Evidence" className="max-h-full max-w-full object-contain" />
            </div>

            {/* AI Analysis List */}
            <Card>
                <CardContent className="p-4">
                    <h3 className="text-sm font-semibold text-gray-500 mb-3 flex items-center gap-2">
                        <Eye className="w-4 h-4" /> Visual Discovery
                    </h3>
                    <ScrollArea className="h-[200px] pr-4">
                        <div className="space-y-3">
                            {observations.map((obs, idx) => (
                                <div key={idx} className="flex flex-col gap-1 pb-3 border-b last:border-0 border-gray-100">
                                    <div className="flex justify-between items-center">
                                        <span className="font-medium text-sm">{obs.label}</span>
                                        <Badge
                                            variant="outline"
                                            className={
                                                obs.confidence === 'HIGH' ? 'text-green-600 border-green-200 bg-green-50' :
                                                    obs.confidence === 'MEDIUM' ? 'text-yellow-600 border-yellow-200 bg-yellow-50' :
                                                        'text-red-500 border-red-200 bg-red-50'
                                            }
                                        >
                                            {obs.confidence}
                                        </Badge>
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
