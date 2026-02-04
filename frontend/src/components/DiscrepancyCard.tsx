'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, FileText, Eye, Clock } from 'lucide-react';
import { SynthesisDiscrepancy } from '@/lib/api';

interface DiscrepancyCardProps {
    discrepancies: SynthesisDiscrepancy[];
}

export function DiscrepancyCard({ discrepancies }: DiscrepancyCardProps) {
    if (discrepancies.length === 0) {
        return (
            <div className="text-center py-10 text-gray-400 border-2 border-dashed rounded-lg bg-green-50 border-green-200">
                <div className="flex flex-col items-center">
                    <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mb-3">
                        <span className="text-2xl">✓</span>
                    </div>
                    <p className="font-medium text-green-600">No Discrepancies Found</p>
                    <p className="text-sm text-green-500 mt-1">The narrative aligns with the visual evidence</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {/* Alert Banner */}
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                <div>
                    <p className="font-medium text-red-700">
                        {discrepancies.length} Discrepanc{discrepancies.length === 1 ? 'y' : 'ies'} Detected
                    </p>
                    <p className="text-sm text-red-600 mt-1">
                        The following inconsistencies were found between the report narrative and visual evidence.
                    </p>
                </div>
            </div>

            {/* Discrepancy List */}
            {discrepancies.map((disc, idx) => (
                <Card key={idx} className="border-l-4 border-l-red-500 bg-white shadow-sm">
                    <CardContent className="p-4">
                        <div className="flex items-start justify-between mb-3">
                            <Badge variant="outline" className="text-red-600 border-red-200 bg-red-50">
                                <AlertTriangle className="w-3 h-3 mr-1" />
                                {disc.status}
                            </Badge>
                            {disc.timestamp_ref && (
                                <span className="text-xs text-gray-400 flex items-center gap-1">
                                    <Clock className="w-3 h-3" />
                                    {disc.timestamp_ref}
                                </span>
                            )}
                        </div>

                        {/* What Report Says vs What Evidence Shows */}
                        <div className="grid grid-cols-2 gap-4 mb-3">
                            <div className="bg-blue-50 rounded-lg p-3 border border-blue-100">
                                <div className="flex items-center gap-2 text-blue-700 font-medium text-xs mb-2">
                                    <FileText className="w-3 h-3" />
                                    REPORT CLAIMS
                                </div>
                                <p className="text-sm text-blue-800">{disc.clean_claim}</p>
                            </div>

                            <div className="bg-purple-50 rounded-lg p-3 border border-purple-100">
                                <div className="flex items-center gap-2 text-purple-700 font-medium text-xs mb-2">
                                    <Eye className="w-3 h-3" />
                                    EVIDENCE SHOWS
                                </div>
                                <p className="text-sm text-purple-800">{disc.visual_fact}</p>
                            </div>
                        </div>

                        {/* Explanation */}
                        <div className="bg-gray-50 rounded-lg p-3 border">
                            <p className="text-sm text-gray-700">
                                <span className="font-medium">Analysis: </span>
                                {disc.description}
                            </p>
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}
