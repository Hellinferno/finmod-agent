export default function LoadingScreen({ title = "Computing", subtitle = "Please wait..." }: { title?: string, subtitle?: string }) {
    return (
        <div className="bg-panel rounded-lg border border-border-subtle p-8 flex flex-col items-center justify-center min-h-[300px]">
            <div className="w-8 h-8 rounded-full border-2 border-border-subtle border-t-accent animate-spin mb-4"></div>
            <div className="text-[13px] font-semibold text-txt-primary">{title}</div>
            <div className="text-[12px] text-txt-muted mt-1">{subtitle}</div>

            <div className="w-full max-w-sm mt-8 space-y-3">
                <div className="h-2 bg-border-subtle rounded w-full overflow-hidden">
                    <div className="h-full bg-accent animate-pulse w-2/3"></div>
                </div>
                <div className="h-2 bg-border-subtle rounded w-5/6"></div>
                <div className="h-2 bg-border-subtle rounded w-4/6"></div>
            </div>
        </div>
    );
}
