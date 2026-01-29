'use client';

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Image as ImageIcon, Loader2, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';

interface UploadZoneProps {
    onUpload: (file: File) => Promise<void>;
    type: 'report' | 'evidence';
    label: string;
    accept: Record<string, string[]>;
}

export function UploadZone({ onUpload, type, label, accept }: UploadZoneProps) {
    const [isUploading, setIsUploading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [isComplete, setIsComplete] = useState(false);
    const [fileName, setFileName] = useState<string>('');

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        const file = acceptedFiles[0];
        if (!file) return;

        setFileName(file.name);
        setIsUploading(true);
        setProgress(30);

        try {
            await onUpload(file);
            setProgress(100);
            setIsComplete(true);
        } catch (error) {
            console.error(error);
            setIsComplete(false);
            setProgress(0);
        } finally {
            setIsUploading(false);
        }
    }, [onUpload]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept,
        maxFiles: 1,
        disabled: isUploading || isComplete
    });

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
                            {!isComplete && !isUploading && (
                                <p className="text-sm text-gray-500">Drag & drop or click to upload</p>
                            )}
                        </div>

                        {isUploading && (
                            <div className="w-full space-y-2">
                                <Progress value={progress} className="w-full" />
                                <p className="text-xs text-gray-400">Uploading...</p>
                            </div>
                        )}

                        {isComplete && (
                            <div className="flex items-center gap-2 text-green-600">
                                <CheckCircle className="w-5 h-5" />
                                <span className="text-sm font-medium">{fileName}</span>
                            </div>
                        )}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
