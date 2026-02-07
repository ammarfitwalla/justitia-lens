'use client';

import { useState, useEffect } from 'react';
import { CreateCaseForm } from '@/components/CreateCaseForm';
import { UploadZone } from '@/components/UploadZone';
import { SampleCaseCard } from '@/components/SampleCaseCard';
import { SampleCaseModal } from '@/components/SampleCaseModal';
import { Navbar } from '@/components/Navbar';
import { endpoints, CaseListItem } from '@/lib/api';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowRight, FileText, Image, Scale, CheckCircle2, Sparkles } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function UploadPage() {
    const [caseId, setCaseId] = useState<number | null>(null);
    const [reportId, setReportId] = useState<number | null>(null);
    const [evidenceCount, setEvidenceCount] = useState(0);
    const router = useRouter();

    // Sample cases state
    const [sampleCases, setSampleCases] = useState<CaseListItem[]>([]);
    const [selectedSampleCase, setSelectedSampleCase] = useState<CaseListItem | null>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);

    // Fetch sample cases on mount
    useEffect(() => {
        const fetchSampleCases = async () => {
            try {
                const res = await endpoints.getSampleCases();
                setSampleCases(res.data);
            } catch (error) {
                console.error('Failed to fetch sample cases:', error);
            }
        };
        fetchSampleCases();
    }, []);

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

    const handleSampleCaseClick = (sampleCase: CaseListItem) => {
        setSelectedSampleCase(sampleCase);
        setIsModalOpen(true);
    };

    return (
        <div className="min-h-screen bg-background">
            {/* Global Navigation */}
            <Navbar />

            {/* Page Header */}
            <header className="border-b border-border bg-background/80">
                <div className="max-w-5xl mx-auto px-6 py-5">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-muted">
                            <Scale className="h-5 w-5 text-foreground" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-foreground">New Investigation</h1>
                            <p className="text-sm text-muted-foreground">Upload evidence for forensic analysis</p>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="container mx-auto py-10 max-w-5xl px-6">
                {/* Progress Steps */}
                <div className="flex items-center justify-center gap-4 mb-12">
                    <div className={`flex items-center gap-2 ${!caseId ? 'text-foreground' : 'text-muted-foreground'}`}>
                        <div className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${!caseId ? 'border-primary bg-primary/10' : 'border-border bg-muted'}`}>
                            {caseId ? <CheckCircle2 className="h-5 w-5" /> : <span className="font-semibold">1</span>}
                        </div>
                        <span className="font-medium hidden sm:inline">Case Details</span>
                    </div>
                    <div className="w-12 sm:w-20 h-0.5 bg-border"></div>
                    <div className={`flex items-center gap-2 ${caseId && !reportId ? 'text-foreground' : caseId && reportId ? 'text-muted-foreground' : 'text-muted-foreground'}`}>
                        <div className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${caseId && reportId ? 'border-primary bg-primary/10' : caseId ? 'border-primary bg-primary/10' : 'border-border bg-muted'}`}>
                            {reportId ? <CheckCircle2 className="h-5 w-5" /> : <span className="font-semibold">2</span>}
                        </div>
                        <span className="font-medium hidden sm:inline">Upload Files</span>
                    </div>
                    <div className="w-12 sm:w-20 h-0.5 bg-border"></div>
                    <div className={`flex items-center gap-2 ${reportId && evidenceCount > 0 ? 'text-foreground' : 'text-muted-foreground'}`}>
                        <div className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${reportId && evidenceCount > 0 ? 'border-primary bg-primary/10' : 'border-border bg-muted'}`}>
                            <span className="font-semibold">3</span>
                        </div>
                        <span className="font-medium hidden sm:inline">Analyze</span>
                    </div>
                </div>

                {/* Step 1: Case Meta + Sample Cases */}
                {!caseId && (
                    <div className="animate-fade-in space-y-8">
                        <CreateCaseForm onSuccess={setCaseId} />

                        {/* Sample Cases Section */}
                        {sampleCases.length > 0 && (
                            <div className="pt-8">
                                <div className="relative">
                                    <div className="absolute inset-0 flex items-center">
                                        <div className="w-full border-t border-border"></div>
                                    </div>
                                    <div className="relative flex justify-center">
                                        <span className="bg-background px-4 text-sm text-muted-foreground">
                                            or explore a sample case
                                        </span>
                                    </div>
                                </div>

                                <div className="mt-8">
                                    <div className="flex items-center gap-2 mb-4">
                                        <Sparkles className="h-5 w-5 text-primary" />
                                        <h2 className="text-lg font-semibold">Sample Cases</h2>
                                    </div>
                                    <p className="text-sm text-muted-foreground mb-6">
                                        Try one of our pre-loaded cases to see how Justitia Lens analyzes evidence and identifies discrepancies.
                                    </p>

                                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                                        {sampleCases.map((sampleCase) => (
                                            <SampleCaseCard
                                                key={sampleCase.id}
                                                sampleCase={sampleCase}
                                                onClick={() => handleSampleCaseClick(sampleCase)}
                                            />
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Step 2: Files */}
                {caseId && (
                    <div className="space-y-6 animate-fade-in">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {/* Narrative Upload */}
                            <Card className="border-border p-6 hover:shadow-md transition-shadow">
                                <div className="flex items-center gap-3 mb-4">
                                    <div className="p-2 rounded-lg bg-muted">
                                        <FileText className="h-5 w-5 text-foreground" />
                                    </div>
                                    <div>
                                        <h2 className="text-lg font-semibold text-card-foreground">Legal Narrative</h2>
                                        <p className="text-sm text-muted-foreground">Police report or affidavit</p>
                                    </div>
                                    {reportId && (
                                        <CheckCircle2 className="h-5 w-5 text-foreground ml-auto" />
                                    )}
                                </div>
                                <UploadZone
                                    label={reportId ? "Report uploaded" : "Upload PDF"}
                                    type="report"
                                    accept={{ 'application/pdf': ['.pdf'] }}
                                    onUpload={handleReportUpload}
                                />
                            </Card>

                            {/* Evidence Upload */}
                            <Card className="border-border p-6 hover:shadow-md transition-shadow">
                                <div className="flex items-center gap-3 mb-4">
                                    <div className="p-2 rounded-lg bg-muted">
                                        <Image className="h-5 w-5 text-foreground" />
                                    </div>
                                    <div>
                                        <h2 className="text-lg font-semibold text-card-foreground">Visual Evidence</h2>
                                        <p className="text-sm text-muted-foreground">BWC footage or CCTV images</p>
                                    </div>
                                    {evidenceCount > 0 && (
                                        <div className="ml-auto flex items-center gap-1.5 text-sm">
                                            <CheckCircle2 className="h-4 w-4 text-foreground" />
                                            <span className="text-foreground font-medium">{evidenceCount}</span>
                                        </div>
                                    )}
                                </div>
                                <UploadZone
                                    label={evidenceCount > 0 ? `${evidenceCount} items uploaded` : "Upload images"}
                                    type="evidence"
                                    accept={{ 'image/*': ['.png', '.jpg', '.jpeg', '.webp'] }}
                                    onUpload={handleEvidenceUpload}
                                    multiple={true}
                                />
                            </Card>
                        </div>

                        {/* Begin Analysis Button */}
                        {reportId && evidenceCount > 0 && (
                            <div className="flex justify-center pt-8 animate-fade-in">
                                <Button
                                    size="lg"
                                    className="w-full md:w-auto px-12 group"
                                    onClick={() => router.push(`/analysis/${caseId}`)}
                                >
                                    Begin Forensic Analysis
                                    <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                                </Button>
                            </div>
                        )}
                    </div>
                )}
            </main>

            {/* Sample Case Modal */}
            <SampleCaseModal
                sampleCase={selectedSampleCase}
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
            />
        </div>
    );
}
