'use client';

import { useEffect, useState } from 'react';
import { endpoints, CaseListItem } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Plus, Trash2, Eye, RefreshCw, FileText, Image } from 'lucide-react';
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
                return <Badge className="bg-green-500 hover:bg-green-600">Completed</Badge>;
            case 'IN_PROGRESS':
                return <Badge className="bg-yellow-500 hover:bg-yellow-600">In Progress</Badge>;
            default:
                return <Badge variant="outline">Pending</Badge>;
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
            <div className="min-h-screen flex items-center justify-center bg-slate-950">
                <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-950 text-white">
            {/* Header */}
            <header className="border-b border-slate-800 px-6 py-4">
                <div className="max-w-6xl mx-auto flex justify-between items-center">
                    <div>
                        <h1 className="text-2xl font-bold">Recent Cases</h1>
                        <p className="text-sm text-slate-400">View and manage your investigations</p>
                    </div>
                    <div className="flex gap-3">
                        <Button variant="outline" onClick={fetchCases} className="border-slate-700">
                            <RefreshCw className="mr-2 h-4 w-4" /> Refresh
                        </Button>
                        <Link href="/upload">
                            <Button className="bg-blue-600 hover:bg-blue-500">
                                <Plus className="mr-2 h-4 w-4" /> New Case
                            </Button>
                        </Link>
                    </div>
                </div>
            </header>

            {/* Content */}
            <main className="max-w-6xl mx-auto p-6">
                {cases.length === 0 ? (
                    <Card className="bg-slate-900/50 border-slate-800">
                        <CardContent className="flex flex-col items-center justify-center py-16">
                            <FileText className="h-16 w-16 text-slate-600 mb-4" />
                            <h3 className="text-xl font-semibold text-slate-300 mb-2">No cases yet</h3>
                            <p className="text-slate-500 mb-6">Start your first investigation to see it here.</p>
                            <Link href="/upload">
                                <Button className="bg-blue-600 hover:bg-blue-500">
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
                                className="bg-slate-900/50 border-slate-800 hover:border-slate-700 transition-colors"
                            >
                                <CardContent className="p-6">
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <div className="flex items-center gap-3 mb-2">
                                                <h3 className="text-lg font-semibold text-white">
                                                    {caseItem.title}
                                                </h3>
                                                {getStatusBadge(caseItem.analysis_status)}
                                            </div>

                                            {caseItem.description && (
                                                <p className="text-slate-400 text-sm mb-3 line-clamp-2">
                                                    {caseItem.description}
                                                </p>
                                            )}

                                            <div className="flex items-center gap-4 text-sm text-slate-500">
                                                <span className="flex items-center gap-1">
                                                    <FileText className="h-4 w-4" />
                                                    {caseItem.report_count} report{caseItem.report_count !== 1 ? 's' : ''}
                                                </span>
                                                <span className="flex items-center gap-1">
                                                    <Image className="h-4 w-4" />
                                                    {caseItem.evidence_count} evidence
                                                </span>
                                                <span>•</span>
                                                <span>Created {formatDate(caseItem.created_at)}</span>
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-2 ml-4">
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                className="border-slate-700 hover:bg-slate-800"
                                                onClick={() => router.push(`/analysis/${caseItem.id}`)}
                                            >
                                                <Eye className="mr-2 h-4 w-4" />
                                                {caseItem.analysis_status === 'COMPLETED' ? 'View Results' : 'Continue'}
                                            </Button>
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                className="border-red-900 text-red-500 hover:bg-red-950"
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
