'use client';

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Image as ImageIcon, Loader2, CheckCircle, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';

interface UploadZoneProps {
    onUpload: (file: File) => Promise<void>;
    type: 'report' | 'evidence';
    label: string;
    accept: Record<string, string[]>;
    multiple?: boolean; // Allow multiple files for evidence
}

interface UploadedFile {
    name: string;
    status: 'uploading' | 'complete' | 'error';
    message?: string;
}

export function UploadZone({ onUpload, type, label, accept, multiple = false }: UploadZoneProps) {
    const [isUploading, setIsUploading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
    const [currentFile, setCurrentFile] = useState<string>('');

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        if (acceptedFiles.length === 0) return;

        setIsUploading(true);

        // For single file mode (reports), just upload the first file
        if (!multiple) {
            const file = acceptedFiles[0];
            setCurrentFile(file.name);
            setProgress(30);

            try {
                await onUpload(file);
                setProgress(100);
                setUploadedFiles([{ name: file.name, status: 'complete' }]);
            } catch (error: any) {
                console.error(error);
                const msg = error.response?.data?.detail || error.message || "Upload failed";
                setUploadedFiles([{ name: file.name, status: 'error', message: msg }]);
            } finally {
                setIsUploading(false);
            }
            return;
        }

        // For multiple files mode (evidence), upload each sequentially
        const totalFiles = acceptedFiles.length;

        for (let i = 0; i < acceptedFiles.length; i++) {
            const file = acceptedFiles[i];
            setCurrentFile(file.name);
            setProgress(Math.round(((i) / totalFiles) * 100));

            try {
                await onUpload(file);
                setUploadedFiles(prev => [...prev, { name: file.name, status: 'complete' }]);
            } catch (error: any) {
                console.error(`Failed to upload ${file.name}:`, error);
                const msg = error.response?.data?.detail || error.message || "Upload failed";
                setUploadedFiles(prev => [...prev, { name: file.name, status: 'error', message: msg }]);
            }
        }

        setProgress(100);
        setIsUploading(false);
        setCurrentFile('');
    }, [onUpload, multiple]);

    const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
        onDrop,
        accept,
        maxFiles: multiple ? 3 : 1, // Match backend limit of 3
        maxSize: 20 * 1024 * 1024, // 20MB limit
        disabled: isUploading,
        onDropRejected: (rejections) => {
            rejections.forEach(rejection => {
                rejection.errors.forEach(error => {
                    let message = error.message;
                    if (error.code === 'file-too-large') {
                        message = `File is larger than 20MB`;
                    } else if (error.code === 'too-many-files') {
                        message = `Maximum 3 files allowed`;
                    }
                    setUploadedFiles(prev => [...prev, {
                        name: rejection.file.name,
                        status: 'error',
                        message: message
                    }]);
                });
            });
        }
    });

    const hasUploads = uploadedFiles.length > 0;
    const successCount = uploadedFiles.filter(f => f.status === 'complete').length;

    return (
        <Card className={`border-dashed border-2 ${isDragActive ? 'border-primary bg-primary/5' : 'border-gray-200'}`}>
            <CardContent className="p-6">
                <div {...getRootProps()} className="cursor-pointer text-center">
                    <input {...getInputProps()} />
                    <div className="flex flex-col items-center gap-4">
                        <div className="p-4 bg-gray-100 rounded-full">
                            {type === 'report' ? <FileText className="w-8 h-8 text-gray-500" /> : <ImageIcon className="w-8 h-8 text-gray-500" />}
                        </div>

                        <div className="space-y-1">
                            <h3 className="font-semibold text-lg">{label}</h3>
                            {!isUploading && (
                                <p className="text-sm text-gray-500">
                                    {multiple
                                        ? 'Drag & drop or click to upload (multiple files supported)'
                                        : 'Drag & drop or click to upload'}
                                </p>
                            )}
                        </div>

                        {isUploading && (
                            <div className="w-full space-y-2">
                                <Progress value={progress} className="w-full" />
                                <p className="text-xs text-gray-400">Uploading {currentFile}...</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Uploaded Files List */}
                {hasUploads && (
                    <div className="mt-4 pt-4 border-t">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-gray-700">
                                Uploaded Files
                            </span>
                            <Badge variant="outline" className="text-green-600 border-green-200">
                                {successCount} file{successCount !== 1 ? 's' : ''}
                            </Badge>
                        </div>
                        <div className="space-y-2 max-h-40 overflow-y-auto">
                            {uploadedFiles.map((file, idx) => (
                                <div key={idx} className="flex items-center gap-2 text-sm">
                                    {file.status === 'complete' ? (
                                        <CheckCircle className="w-4 h-4 text-green-600 shrink-0" />
                                    ) : file.status === 'error' ? (
                                        <X className="w-4 h-4 text-red-500 shrink-0" />
                                    ) : (
                                        <Loader2 className="w-4 h-4 animate-spin text-blue-500 shrink-0" />
                                    )}
                                    <span className={`truncate ${file.status === 'error' ? 'text-red-500' : 'text-gray-600'}`}>
                                        {file.name}
                                        {file.message && <span className="text-xs text-red-400 ml-1">({file.message})</span>}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}

