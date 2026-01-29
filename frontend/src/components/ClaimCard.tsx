import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Clock, AlertCircle } from 'lucide-react';

interface ClaimCardProps {
    timestamp: string;
    entity: string;
    action: string;
    object: string | null;
    certainty: 'EXPLICIT' | 'IMPLIED';
    description: string;
}

export function ClaimCard({ timestamp, entity, action, object, certainty, description }: ClaimCardProps) {
    return (
        <Card className="mb-4 border-l-4 border-l-blue-500 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="pt-4">
                <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center gap-2 text-sm text-gray-500 font-mono">
                        <Clock className="w-3 h-3" />
                        {timestamp || "??:??"}
                    </div>
                    <Badge variant={certainty === 'EXPLICIT' ? 'default' : 'secondary'} className="text-xs">
                        {certainty}
                    </Badge>
                </div>

                <h4 className="font-semibold text-lg leading-tight mb-1">
                    <span className="text-blue-700">{entity}</span> {action} {object && <span className="text-red-600 font-medium">{object}</span>}
                </h4>

                <p className="text-sm text-gray-600 italic">
                    "{description}"
                </p>
            </CardContent>
        </Card>
    );
}
