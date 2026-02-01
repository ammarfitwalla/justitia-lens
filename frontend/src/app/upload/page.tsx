'use client';

import { useState } from 'react';
import { CreateCaseForm } from '@/components/CreateCaseForm';
import { UploadZone } from '@/components/UploadZone';
import { endpoints } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function UploadPage() {
    const [caseId, setCaseId] = useState<number | null>(null);
    const [reportId, setReportId] = useState<number | null>(null);
    const [evidenceCount, setEvidenceCount] = useState(0);
    const router = useRouter();

    const handleReportUpload = async (file: File) => {
        if (!caseId) return;
        const res = await endpoints.uploadReport(caseId, file);
        setReportId(res.data.id);
    };

    const handleEvidenceUpload = async (file: File) => {
        if (!caseId) return;
        await endpoints.uploadEvidence(caseId, file);
        setEvidenceCount(prev => prev + 1);
    };

    return (
        <div className="container mx-auto py-10 max-w-4xl space-y-8">
            <h1 className="text-3xl font-bold tracking-tight text-center mb-10">
                Discovery Ingestion
            </h1>

            {/* Step 1: Case Meta */}
            {!caseId && (
                <CreateCaseForm onSuccess={setCaseId} />
            )}

            {/* Step 2: Files */}
            {caseId && (
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-4">
                            <h2 className="text-xl font-semibold">1. Legal Context</h2>
                            <UploadZone
                                label="Upload Narrative (PDF)"
                                type="report"
                                accept={{ 'application/pdf': ['.pdf'] }}
                                onUpload={handleReportUpload}
                            />
                        </div>

                        <div className="space-y-4">
                            <h2 className="text-xl font-semibold">2. Physical Evidence</h2>
                            <UploadZone
                                label="Upload Images (BWC/CCTV)"
                                type="evidence"
                                accept={{ 'image/*': ['.png', '.jpg', '.jpeg'] }}
                                onUpload={handleEvidenceUpload}
                                multiple={true}
                            />
                            <p className="text-sm text-muted-foreground text-center">
                                {evidenceCount} items uploaded
                            </p>
                        </div>
                    </div>

                    {reportId && evidenceCount > 0 && (
                        <div className="flex justify-center pt-8">
                            <Button
                                size="lg"
                                className="w-full md:w-auto px-8"
                                onClick={() => router.push(`/analysis/${caseId}`)}
                            >
                                Begin Discovery Analysis <ArrowRight className="ml-2 w-4 h-4" />
                            </Button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
