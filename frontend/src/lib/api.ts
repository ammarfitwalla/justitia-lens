import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

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
    evidence?: Evidence[];
    reports?: Report[];
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
}

export const endpoints = {
    createCase: (data: { title: string; description: string }) =>
        api.post<Case>('/cases', data),

    getCase: (caseId: number) =>
        api.get<Case>(`/cases/${caseId}`),

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

    analyzeNarrative: (caseId: number) =>
        api.post<{ timeline: NarrativeClaim[] }>(`/analyze/case/${caseId}/narrative`),

    analyzeEvidence: (evidenceId: number) =>
        api.post<{ observations: VisionObservation[] }>(`/analyze/evidence/${evidenceId}`)
};
