'use client';

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { FileText, Image as ImageIcon } from 'lucide-react';
import { CaseListItem } from '@/lib/api';

interface SampleCaseCardProps {
    sampleCase: CaseListItem;
    onClick: () => void;
}

export function SampleCaseCard({ sampleCase, onClick }: SampleCaseCardProps) {
    return (
        <Card
            className="cursor-pointer hover:shadow-lg hover:border-primary/50 transition-all duration-200 overflow-hidden group"
            onClick={onClick}
        >
            {/* Thumbnail Section */}
            <div className="relative h-32 bg-gradient-to-br from-muted to-muted/50 overflow-hidden">
                {sampleCase.thumbnail_path ? (
                    <img
                        src={`http://localhost:8000/api/v1/files/${encodeURIComponent(sampleCase.thumbnail_path)}`}
                        alt={sampleCase.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        onError={(e) => {
                            // Fallback to gradient if image fails to load
                            (e.target as HTMLImageElement).style.display = 'none';
                        }}
                    />
                ) : (
                    <div className="w-full h-full flex items-center justify-center">
                        <div className="p-4 rounded-full bg-background/50">
                            <FileText className="w-8 h-8 text-muted-foreground" />
                        </div>
                    </div>
                )}
                <div className="absolute top-2 right-2">
                    <Badge className="bg-primary/90 text-primary-foreground text-xs">
                        Sample
                    </Badge>
                </div>
            </div>

            <CardContent className="p-4">
                <h3 className="font-semibold text-sm line-clamp-2 mb-2 group-hover:text-primary transition-colors">
                    {sampleCase.title}
                </h3>

                <p className="text-xs text-muted-foreground line-clamp-2 mb-3">
                    {sampleCase.description || 'Click to view case details and analysis'}
                </p>

                {/* Evidence & Report counts */}
                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                        <ImageIcon className="w-3 h-3" />
                        <span>{sampleCase.evidence_count} evidence</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <FileText className="w-3 h-3" />
                        <span>{sampleCase.report_count} report</span>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
