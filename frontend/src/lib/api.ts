import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://justitia-backend-594957503553.us-central1.run.app/api/v1';


export const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export interface Case {
    id: number;
    title: string;
    description: string;
    status: string;
    analysis_status: string;
    narrative_analysis_json?: string;
    vision_analysis_json?: string;
    synthesis_analysis_json?: string;
    evidence?: Evidence[];
    reports?: Report[];
    is_sample_case?: boolean;
}

export interface CaseListItem {
    id: number;
    title: string;
    description?: string;
    status: string;
    analysis_status: string;
    created_at: string;
    updated_at?: string;
    evidence_count: number;
    report_count: number;
    is_sample_case?: boolean;
    thumbnail_path?: string;
}

export interface Report {
    id: number;
    case_id: number;
    file_path: string;
}

export interface Evidence {
    id: number;
    case_id: number;
    file_path: string;
    type: string;
}

export interface NarrativeClaim {
    timestamp_ref: string | null;
    entity: string;
    action: string;
    object: string | null;
    certainty: string;
    description: string;
}

export interface VisionObservation {
    timestamp_ref: string;
    category: string;
    entity: string;
    label: string;
    confidence: string;
    details: string;
    evidence_id?: number;  // Which evidence this observation came from
    evidence_index?: number;  // 1-based index for display
}

// Synthesis/Discrepancy interfaces
export interface SynthesisDiscrepancy {
    timestamp_ref?: string;
    clean_claim: string;   // What the report says
    visual_fact: string;   // What the evidence shows
    description: string;   // Explanation of the discrepancy
    status: string;        // FLAGGED, REVIEWED, DISMISSED
}

export const endpoints = {
    // Case management
    getCases: () =>
        api.get<CaseListItem[]>('/cases'),

    getSampleCases: () =>
        api.get<CaseListItem[]>('/sample-cases'),

    createCase: (data: { title: string; description: string }) =>
        api.post<Case>('/cases', data),

    getCase: (caseId: number) =>
        api.get<Case>(`/cases/${caseId}`),

    deleteCase: (caseId: number) =>
        api.delete(`/cases/${caseId}`),

    // File uploads
    uploadReport: (caseId: number, file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post<Report>(`/upload/report/${caseId}`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
    },

    uploadEvidence: (caseId: number, file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post<Evidence>(`/upload/evidence/${caseId}`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
    },

    // Analysis
    analyzeNarrative: (caseId: number, forceRerun: boolean = false) =>
        api.post<{ timeline: NarrativeClaim[] }>(`/analyze/case/${caseId}/narrative?force_rerun=${forceRerun}`),

    // Analyze single evidence item (kept for backwards compatibility)
    analyzeEvidence: (evidenceId: number, forceRerun: boolean = false) =>
        api.post<{ observations: VisionObservation[] }>(`/analyze/evidence/${evidenceId}?force_rerun=${forceRerun}`),

    // Analyze ALL evidence for a case (aggregated results)
    analyzeAllEvidence: (caseId: number, forceRerun: boolean = false) =>
        api.post<{ observations: VisionObservation[] }>(`/analyze/case/${caseId}/evidence?force_rerun=${forceRerun}`),

    // Synthesis - cross-reference narrative with visual evidence to find discrepancies
    synthesize: (caseId: number, forceRerun: boolean = false) =>
        api.post<{ discrepancies: SynthesisDiscrepancy[] }>(`/analyze/case/${caseId}/synthesize?force_rerun=${forceRerun}`),

    rerunAnalysis: (caseId: number) =>
        api.post<{ message: string; narrative_analysis: any; vision_analysis: any }>(`/analyze/case/${caseId}/rerun`),
};
