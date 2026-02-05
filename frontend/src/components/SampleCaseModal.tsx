'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { FileText, Image as ImageIcon, ArrowRight, Scale } from 'lucide-react';
import { CaseListItem } from '@/lib/api';

interface SampleCaseModalProps {
    sampleCase: CaseListItem | null;
    isOpen: boolean;
    onClose: () => void;
}

export function SampleCaseModal({ sampleCase, isOpen, onClose }: SampleCaseModalProps) {
    const router = useRouter();

    if (!sampleCase) return null;

    const handleAnalyzeCase = () => {
        onClose();
        router.push(`/analysis/${sampleCase.id}`);
    };

    return (
        <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
            <DialogContent className="sm:max-w-lg">
                <DialogHeader>
                    <div className="flex items-center gap-2 mb-1">
                        <Scale className="h-5 w-5 text-primary" />
                        <Badge variant="outline" className="text-xs">
                            Sample Case
                        </Badge>
                    </div>
                    <DialogTitle className="text-xl">{sampleCase.title}</DialogTitle>
                    <DialogDescription className="pt-2">
                        {sampleCase.description || 'This sample case demonstrates the forensic analysis capabilities of Justitia Lens.'}
                    </DialogDescription>
                </DialogHeader>

                {/* Case Details */}
                <div className="grid grid-cols-2 gap-4 py-4">
                    <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                        <div className="p-2 rounded-full bg-background">
                            <ImageIcon className="h-4 w-4 text-muted-foreground" />
                        </div>
                        <div>
                            <p className="text-sm font-medium">{sampleCase.evidence_count}</p>
                            <p className="text-xs text-muted-foreground">Evidence Items</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                        <div className="p-2 rounded-full bg-background">
                            <FileText className="h-4 w-4 text-muted-foreground" />
                        </div>
                        <div>
                            <p className="text-sm font-medium">{sampleCase.report_count}</p>
                            <p className="text-xs text-muted-foreground">Reports</p>
                        </div>
                    </div>
                </div>

                {/* Info Box */}
                <div className="rounded-lg bg-primary/5 border border-primary/20 p-4">
                    <p className="text-sm text-muted-foreground">
                        This sample case includes pre-loaded evidence and narrative reports.
                        Click below to explore how Justitia Lens analyzes documents,
                        extracts claims, and identifies potential discrepancies.
                    </p>
                </div>

                <DialogFooter className="gap-2 sm:gap-0">
                    <Button variant="outline" onClick={onClose}>
                        Cancel
                    </Button>
                    <Button onClick={handleAnalyzeCase} className="group">
                        Analyze Case
                        <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
