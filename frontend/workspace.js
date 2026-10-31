// Property Workspace Component (Reference Screenshot 3)
// This will be embedded in index.html

function PropertyWorkspace({ propertyId, onNavigate }) {
    const [property, setProperty] = useState(null);
    const [runs, setRuns] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('overview');

    useEffect(() => {
        loadPropertyData();
    }, [propertyId]);

    const loadPropertyData = async () => {
        try {
            const [propRes, runsRes] = await Promise.all([
                fetch(`${API_BASE}/properties/${propertyId}`),
                fetch(`${API_BASE}/properties/${propertyId}/runs`)
            ]);

            const propData = await propRes.json();
            const runsData = await runsRes.json();

            setProperty(propData);
            setRuns(runsData);
        } catch (error) {
            console.error('Failed to load property:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-text-secondary">Loading property...</div>
            </div>
        );
    }

    if (!property) {
        return (
            <div className="p-8">
                <div className="text-red-600">Property not found</div>
                <button
                    onClick={() => onNavigate('dashboard')}
                    className="mt-4 px-4 py-2 bg-primary text-white rounded-lg"
                >
                    ← Back to Dashboard
                </button>
            </div>
        );
    }

    const latest = property.latest_research;

    return (
        <div className="p-8">
            {/* Header */}
            <div className="flex justify-between items-start mb-6">
                <div>
                    <button
                        onClick={() => onNavigate('dashboard')}
                        className="flex items-center gap-2 text-text-secondary hover:text-text-primary mb-4"
                    >
                        <span className="text-xl">←</span>
                    </button>
                    <h1 className="text-3xl font-bold text-text-primary mb-2">
                        {property.name}
                    </h1>
                    <p className="text-sm text-text-secondary">
                        {property.location} • Ref: GV-2024-{propertyId.slice(0, 4).toUpperCase()}
                    </p>
                </div>
                <div className="flex gap-3">
                    <button className="px-4 py-2 border border-border rounded-lg text-sm font-medium hover:bg-gray-50">
                        ✏️ Edit
                    </button>
                    <button className="px-4 py-2 bg-primary text-white rounded-lg text-sm font-semibold hover:bg-primary-dark">
                        📤 Export
                    </button>
                </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-8 border-b border-border mb-8">
                {['Overview', 'History', 'Export'].map(tab => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab.toLowerCase())}
                        className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
                            activeTab === tab.toLowerCase()
                                ? 'border-primary text-primary'
                                : 'border-transparent text-text-secondary hover:text-text-primary'
                        }`}
                    >
                        {tab}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            {activeTab === 'overview' && (
                <OverviewTab property={property} latest={latest} runs={runs} />
            )}
            {activeTab === 'history' && (
                <HistoryTab runs={runs} />
            )}
            {activeTab === 'export' && (
                <ExportTab property={property} latest={latest} />
            )}
        </div>
    );
}

// Overview Tab Component
function OverviewTab({ property, latest, runs }) {
    return (
        <div>
            {/* Three Metrics Cards */}
            {latest && (
                <div className="grid grid-cols-3 gap-6 mb-8">
                    <MetricCard
                        icon="●"
                        label="Status"
                        value={latest.status.charAt(0).toUpperCase() + latest.status.slice(1)}
                        description="Research completed successfully"
                        iconColor="#10B981"
                    />
                    <MetricCard
                        icon="₹"
                        label="Estimated Value"
                        value={latest.estimate ? latest.estimate.formatted : 'Not estimated'}
                        description={`As on ${latest.started?.slice(0, 10) || ''}`}
                        iconColor="#064E3B"
                    />
                    <MetricCard
                        icon="📋"
                        label="Comps"
                        value={latest.comparisons_count || 0}
                        description="Comparable properties analysed"
                        iconColor="#064E3B"
                    />
                </div>
            )}

            {/* Two Column Layout */}
            <div className="grid grid-cols-[1.4fr,1fr] gap-8">
                {/* Property Details */}
                <div className="bg-white border border-border rounded-xl p-6">
                    <h3 className="text-xl font-semibold mb-6">Property Details</h3>

                    <PropertyDetailRow
                        icon="📍"
                        label="Location"
                        value={property.location}
                        action="View on Map"
                    />
                    <PropertyDetailRow
                        icon="🏢"
                        label="Property Type"
                        value="Apartment"
                    />
                    <PropertyDetailRow
                        icon="📐"
                        label="Built-up Area"
                        value={`${property.details.area} sq ft`}
                    />
                    <PropertyDetailRow
                        icon="📏"
                        label="Basis"
                        value={property.details.area_basis}
                    />
                    {property.details.notes && (
                        <PropertyDetailRow
                            icon="📝"
                            label="Notes"
                            value={property.details.notes}
                        />
                    )}

                    <div className="flex gap-3 mt-6">
                        <button className="flex-1 px-4 py-2 bg-primary text-white rounded-lg text-sm font-semibold hover:bg-primary-dark">
                            + New Research
                        </button>
                        <button className="flex-1 px-4 py-2 border border-border rounded-lg text-sm font-medium hover:bg-gray-50">
                            View Details →
                        </button>
                    </div>
                </div>

                {/* Property Summary */}
                <div className="bg-white border border-border rounded-xl p-6">
                    <h3 className="text-xl font-semibold mb-6">Property Summary</h3>

                    {/* Property Image */}
                    <div className="w-full h-48 bg-gradient-to-br from-primary-light to-surface-bg rounded-lg flex items-center justify-center mb-6">
                        <svg width="100" height="80" viewBox="0 0 100 80" fill="none">
                            <path d="M50 5 L5 25 L5 70 L95 70 L95 25 Z" stroke="#064E3B" strokeWidth="2" fill="#EAF2EF"/>
                            <rect x="38" y="35" width="24" height="35" fill="#064E3B" opacity="0.3"/>
                        </svg>
                    </div>

                    <h4 className="font-semibold mb-2">{property.name}</h4>
                    <p className="text-sm text-text-secondary mb-4">{property.location}</p>

                    <div className="flex gap-4 text-sm text-text-secondary mb-6">
                        <span>🏢 Apartment</span>
                        <span>📐 {property.details.area} sq ft</span>
                        <span>🛏️ {property.details.bedrooms} BHK</span>
                    </div>

                    {/* Source Summary */}
                    <div className="border-t border-border pt-4">
                        <div className="flex justify-between items-center mb-3">
                            <h4 className="font-medium">Source Summary</h4>
                            <a href="#" className="text-primary text-sm hover:underline">View Sources →</a>
                        </div>
                        <div className="grid grid-cols-3 gap-4">
                            <div>
                                <div className="text-2xl font-bold">12</div>
                                <div className="text-xs text-text-muted">Listings</div>
                            </div>
                            <div>
                                <div className="text-2xl font-bold">5</div>
                                <div className="text-xs text-text-muted">Transactions</div>
                            </div>
                            <div>
                                <div className="text-2xl font-bold">3</div>
                                <div className="text-xs text-text-muted">Reports</div>
                            </div>
                        </div>
                    </div>

                    {/* Latest Valuation */}
                    {latest && latest.estimate && (
                        <div className="border-t border-border pt-4 mt-4">
                            <div className="flex justify-between items-center mb-2">
                                <h4 className="font-medium">Latest Valuation Snapshot</h4>
                                <span className="text-xs text-text-muted">{latest.started?.slice(0, 10)}</span>
                            </div>
                            <div className="text-3xl font-bold mb-1">{latest.estimate.formatted}</div>
                            <div className="text-sm text-text-secondary">
                                Value range: {latest.estimate.min_value ? `₹${(latest.estimate.min_value/10000000).toFixed(2)} Cr` : '—'} – {latest.estimate.max_value ? `₹${(latest.estimate.max_value/10000000).toFixed(2)} Cr` : '—'}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Research History Section */}
            <div className="mt-8">
                <h3 className="text-xl font-semibold mb-4">Research History</h3>
                <ResearchHistoryList runs={runs.slice(0, 5)} />
            </div>
        </div>
    );
}

// Metric Card Component
function MetricCard({ icon, label, value, description, iconColor }) {
    return (
        <div className="bg-white border border-border rounded-lg p-6 shadow-sm">
            <div className="flex items-center gap-3 mb-3">
                <span style={{ color: iconColor, fontSize: '20px' }}>{icon}</span>
                <span className="text-sm text-text-secondary">{label}</span>
            </div>
            <div className="text-3xl font-bold text-text-primary mb-1">{value}</div>
            <div className="text-xs text-text-muted">{description}</div>
        </div>
    );
}

// Property Detail Row Component
function PropertyDetailRow({ icon, label, value, action }) {
    return (
        <div className="flex items-start py-4 border-b border-border-light last:border-0">
            <div className="w-10 text-xl flex-shrink-0">{icon}</div>
            <div className="flex-1">
                <div className="text-sm text-text-secondary mb-1">{label}</div>
                <div className="text-base text-text-primary">{value}</div>
            </div>
            {action && (
                <a href="#" className="text-primary text-sm hover:underline">{action}</a>
            )}
        </div>
    );
}

// Research History List Component
function ResearchHistoryList({ runs }) {
    if (!runs || runs.length === 0) {
        return <div className="text-text-secondary">No research runs yet</div>;
    }

    return (
        <div className="space-y-3">
            {runs.map((run, idx) => (
                <div
                    key={run.id}
                    className="bg-white border border-border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                >
                    <div className="flex justify-between items-center">
                        <div>
                            <div className="font-medium mb-1">
                                {run.started} — Market analysis with updated comps
                            </div>
                            <div className="text-sm text-text-secondary">
                                <span className={`inline-block w-2 h-2 rounded-full mr-2 ${
                                    run.status === 'completed' ? 'bg-status-completed' :
                                    run.status === 'running' ? 'bg-status-review' :
                                    'bg-status-draft'
                                }`}></span>
                                {run.status.charAt(0).toUpperCase() + run.status.slice(1)}
                            </div>
                        </div>
                        <span className="text-primary">→</span>
                    </div>
                </div>
            ))}
        </div>
    );
}

// History Tab Component
function HistoryTab({ runs }) {
    return (
        <div>
            <h3 className="text-xl font-semibold mb-6">Research History</h3>

            {runs.length === 0 ? (
                <div className="text-center py-12 text-text-secondary">
                    📋 No research runs yet for this property
                </div>
            ) : (
                <div className="space-y-4">
                    {runs.map((run, idx) => (
                        <details key={run.id} className="bg-white border border-border rounded-lg">
                            <summary className="cursor-pointer p-4 font-medium hover:bg-gray-50">
                                Run #{runs.length - idx} — {run.started?.slice(0, 10)} — {run.status.charAt(0).toUpperCase() + run.status.slice(1)}
                            </summary>
                            <div className="p-4 border-t border-border space-y-3">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <div className="text-sm text-text-secondary">Started</div>
                                        <div className="font-medium">{run.started}</div>
                                    </div>
                                    {run.finished && (
                                        <div>
                                            <div className="text-sm text-text-secondary">Finished</div>
                                            <div className="font-medium">{run.finished}</div>
                                        </div>
                                    )}
                                </div>

                                <div>
                                    <div className="text-sm text-text-secondary">Status</div>
                                    <div className="font-medium">{run.status.charAt(0).toUpperCase() + run.status.slice(1)}</div>
                                </div>

                                {run.sources && run.sources.length > 0 && (
                                    <div>
                                        <div className="text-sm text-text-secondary">Sources</div>
                                        <div className="font-medium">{run.sources.join(', ')}</div>
                                    </div>
                                )}

                                {run.estimate && (
                                    <div className="bg-green-50 border border-green-200 rounded p-3">
                                        <div className="text-sm text-green-800 font-semibold">
                                            Estimated Value: {run.estimate.formatted}
                                        </div>
                                    </div>
                                )}

                                {run.comparisons_count > 0 && (
                                    <div>
                                        <div className="text-sm text-text-secondary">Comparisons Found</div>
                                        <div className="font-medium">{run.comparisons_count} properties</div>
                                    </div>
                                )}
                            </div>
                        </details>
                    ))}
                </div>
            )}
        </div>
    );
}

// Export Tab Component
function ExportTab({ property, latest }) {
    if (!latest || latest.status !== 'completed') {
        return (
            <div className="text-center py-12">
                <div className="text-yellow-600 mb-4">⚠️ Complete a research run to generate export reports</div>
            </div>
        );
    }

    return (
        <div>
            <h3 className="text-xl font-semibold mb-6">Export Reports</h3>
            <p className="text-text-secondary mb-8">Export your property research data in multiple formats:</p>

            <div className="grid grid-cols-3 gap-6">
                <ExportCard
                    title="📊 CSV"
                    description="Spreadsheet format for analysis"
                    format="csv"
                    propertyId={property.id}
                />
                <ExportCard
                    title="📄 HTML"
                    description="Readable web format"
                    format="html"
                    propertyId={property.id}
                />
                <ExportCard
                    title="📗 Excel"
                    description="Full data with multiple sheets"
                    format="xlsx"
                    propertyId={property.id}
                />
            </div>

            {/* Report Preview */}
            {latest.estimate && (
                <div className="mt-8 p-6 bg-white border border-border rounded-lg">
                    <h4 className="font-semibold mb-4">Report Preview</h4>
                    <div className="space-y-2 text-sm">
                        <p><strong>Estimated Asking Price:</strong> {latest.estimate.formatted}</p>
                        <p><strong>Based on:</strong> {latest.comparisons_count} comparable properties</p>
                        {latest.estimate.rate_per_sqft && (
                            <p><strong>Median Rate:</strong> ₹{latest.estimate.rate_per_sqft.toLocaleString()}/sq ft</p>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

// Export Card Component
function ExportCard({ title, description, format, propertyId }) {
    const handleDownload = async () => {
        try {
            const response = await fetch(`${API_BASE}/properties/${propertyId}/export/${format}`);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `groundvalue_property_${propertyId}.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Download failed:', error);
            alert('Failed to download file');
        }
    };

    return (
        <div className="bg-white border border-border rounded-lg p-6">
            <h4 className="text-lg font-semibold mb-2">{title}</h4>
            <p className="text-sm text-text-secondary mb-4">{description}</p>
            <button
                onClick={handleDownload}
                className="w-full px-4 py-2 bg-primary text-white rounded-lg text-sm font-semibold hover:bg-primary-dark"
            >
                ⬇️ Download {format.toUpperCase()}
            </button>
        </div>
    );
}
