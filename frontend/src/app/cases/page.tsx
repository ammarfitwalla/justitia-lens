'use client';

import { useEffect, useState } from 'react';
import { endpoints, CaseListItem } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Loader2, Plus, Trash2, Eye, RefreshCw, FileText, Image, Scale } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function CasesPage() {
    const [cases, setCases] = useState<CaseListItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [deletingId, setDeletingId] = useState<number | null>(null);
    const router = useRouter();

    const fetchCases = async () => {
        setIsLoading(true);
        try {
            const res = await endpoints.getCases();
            setCases(res.data);
        } catch (err) {
            console.error("Failed to load cases", err);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchCases();
    }, []);

    const handleDelete = async (caseId: number) => {
        if (!confirm("Are you sure you want to delete this case? This action cannot be undone.")) {
            return;
        }

        setDeletingId(caseId);
        try {
            await endpoints.deleteCase(caseId);
            setCases(prev => prev.filter(c => c.id !== caseId));
        } catch (err) {
            console.error("Failed to delete case", err);
            alert("Failed to delete case. Please try again.");
        } finally {
            setDeletingId(null);
        }
    };

    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'COMPLETED':
                return <Badge className="bg-accent hover:bg-accent/90">Completed</Badge>;
            case 'IN_PROGRESS':
                return <Badge className="bg-chart-3 hover:bg-chart-3/90">In Progress</Badge>;
            default:
                return <Badge variant="outline" className="border-muted-foreground/30">Pending</Badge>;
        }
    };

    const formatDate = (dateStr: string) => {
        return new Date(dateStr).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-background">
                <div className="text-center">
                    <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
                    <p className="text-muted-foreground">Loading cases...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-background text-foreground">
            {/* Header */}
            <header className="glass border-b border-border/50 sticky top-0 z-10 backdrop-blur-xl">
                <div className="max-w-6xl mx-auto px-6 py-5">
                    <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-primary/10">
                                <Scale className="h-5 w-5 text-primary" />
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold">Case Library</h1>
                                <p className="text-sm text-muted-foreground">Manage your forensic investigations</p>
                            </div>
                        </div>
                        <div className="flex gap-3">
                            <Button variant="outline" onClick={fetchCases} className="glass glass-hover border-border/50">
                                <RefreshCw className="mr-2 h-4 w-4" /> Refresh
                            </Button>
                            <Link href="/upload">
                                <Button className="bg-primary hover:bg-primary/90">
                                    <Plus className="mr-2 h-4 w-4" /> New Case
                                </Button>
                            </Link>
                        </div>
                    </div>
                </div>
            </header>

            {/* Content */}
            <main className="max-w-6xl mx-auto p-6">
                {cases.length === 0 ? (
                    <Card className="glass glass-hover border-border/50 mt-8">
                        <CardContent className="flex flex-col items-center justify-center py-20">
                            <div className="p-4 rounded-full bg-primary/10 mb-6">
                                <FileText className="h-12 w-12 text-primary" />
                            </div>
                            <h3 className="text-xl font-semibold mb-2">No cases yet</h3>
                            <p className="text-muted-foreground mb-8 text-center max-w-md">
                                Start your first forensic investigation to see it appear here.
                            </p>
                            <Link href="/upload">
                                <Button className="bg-primary hover:bg-primary/90">
                                    <Plus className="mr-2 h-4 w-4" /> Create First Case
                                </Button>
                            </Link>
                        </CardContent>
                    </Card>
                ) : (
                    <div className="grid gap-4">
                        {cases.map((caseItem) => (
                            <Card
                                key={caseItem.id}
                                className="glass glass-hover border-border/50 group"
                            >
                                <CardContent className="p-6">
                                    <div className="flex items-start justify-between gap-4">
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-3 mb-3 flex-wrap">
                                                <h3 className="text-lg font-semibold">
                                                    {caseItem.title}
                                                </h3>
                                                {getStatusBadge(caseItem.analysis_status)}
                                            </div>

                                            {caseItem.description && (
                                                <p className="text-muted-foreground text-sm mb-4 line-clamp-2">
                                                    {caseItem.description}
                                                </p>
                                            )}

                                            <div className="flex items-center gap-4 text-sm text-muted-foreground flex-wrap">
                                                <span className="flex items-center gap-1.5">
                                                    <FileText className="h-4 w-4" />
                                                    <span className="font-medium text-foreground/80">{caseItem.report_count}</span>
                                                    {caseItem.report_count !== 1 ? 'reports' : 'report'}
                                                </span>
                                                <span className="flex items-center gap-1.5">
                                                    <Image className="h-4 w-4" />
                                                    <span className="font-medium text-foreground/80">{caseItem.evidence_count}</span>
                                                    evidence
                                                </span>
                                                <span className="hidden sm:inline">•</span>
                                                <span className="hidden sm:inline">Created {formatDate(caseItem.created_at)}</span>
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-2 flex-shrink-0">
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                className="glass glass-hover border-primary/30 hover:border-primary/50 text-primary"
                                                onClick={() => router.push(`/analysis/${caseItem.id}`)}
                                            >
                                                <Eye className="mr-2 h-4 w-4" />
                                                {caseItem.analysis_status === 'COMPLETED' ? 'View Results' : 'Continue'}
                                            </Button>
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                className="glass glass-hover border-destructive/30 hover:border-destructive/50 text-destructive hover:text-destructive"
                                                onClick={() => handleDelete(caseItem.id)}
                                                disabled={deletingId === caseItem.id}
                                            >
                                                {deletingId === caseItem.id ? (
                                                    <Loader2 className="h-4 w-4 animate-spin" />
                                                ) : (
                                                    <Trash2 className="h-4 w-4" />
                                                )}
                                            </Button>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
}
