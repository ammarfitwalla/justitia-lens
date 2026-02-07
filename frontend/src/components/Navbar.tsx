'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Scale, Home, Upload, FolderOpen } from 'lucide-react';
import { cn } from '@/lib/utils';

export function Navbar() {
    const pathname = usePathname();

    const navLinks = [
        { href: '/', label: 'Home', icon: Home },
        { href: '/upload', label: 'Upload', icon: Upload },
        { href: '/cases', label: 'Cases', icon: FolderOpen },
    ];

    return (
        <nav className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
            <div className="max-w-6xl mx-auto px-6">
                <div className="flex h-14 items-center justify-between">
                    {/* Logo/Brand - Links to Home */}
                    <Link
                        href="/"
                        className="flex items-center gap-2 hover:opacity-80 transition-opacity"
                    >
                        <div className="p-1.5 rounded-md bg-primary/10">
                            <Scale className="h-5 w-5 text-primary" />
                        </div>
                        <span className="font-semibold text-lg hidden sm:inline">
                            Justitia Lens
                        </span>
                    </Link>

                    {/* Navigation Links */}
                    <div className="flex items-center gap-1">
                        {navLinks.map((link) => {
                            const Icon = link.icon;
                            const isActive = pathname === link.href ||
                                (link.href !== '/' && pathname.startsWith(link.href));

                            return (
                                <Link
                                    key={link.href}
                                    href={link.href}
                                    className={cn(
                                        "flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                                        isActive
                                            ? "bg-primary/10 text-primary"
                                            : "text-muted-foreground hover:text-foreground hover:bg-muted"
                                    )}
                                >
                                    <Icon className="h-4 w-4" />
                                    <span className="hidden sm:inline">{link.label}</span>
                                </Link>
                            );
                        })}
                    </div>
                </div>
            </div>
        </nav>
    );
}
