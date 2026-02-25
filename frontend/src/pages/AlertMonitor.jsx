import { useState, useEffect } from 'react';
import { alertsAPI } from '../api/client';
import { Bell, Filter, ChevronDown, X, CheckCircle, XCircle, Eye, AlertTriangle } from 'lucide-react';

export default function AlertMonitor() {
    const [alerts, setAlerts] = useState([]);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [filterSeverity, setFilterSeverity] = useState('');
    const [filterStatus, setFilterStatus] = useState('');
    const [selectedAlert, setSelectedAlert] = useState(null);

    useEffect(() => {
        loadAlerts();
        const interval = setInterval(loadAlerts, 15000);
        return () => clearInterval(interval);
    }, [filterSeverity, filterStatus]);

    const loadAlerts = async () => {
        try {
            const params = {};
            if (filterSeverity) params.severity = filterSeverity;
            if (filterStatus) params.status = filterStatus;
            params.limit = 100;

            const [alertsRes, statsRes] = await Promise.all([
                alertsAPI.list(params),
                alertsAPI.stats(),
            ]);
            setAlerts(alertsRes.data);
            setStats(statsRes.data);
        } catch (err) {
            console.error('Failed to load alerts:', err);
        } finally {
            setLoading(false);
        }
    };

    const updateAlertStatus = async (id, status, isFP = false) => {
        try {
            await alertsAPI.update(id, {
                status,
                is_false_positive: isFP,
                false_positive_reason: isFP ? 'Marked as false positive by analyst' : undefined,
            });
            loadAlerts();
            setSelectedAlert(null);
        } catch (err) {
            console.error('Failed to update alert:', err);
        }
    };

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold flex items-center gap-3">
                        <Bell className="w-7 h-7 text-amber-400" />
                        Alert Monitor
                    </h1>
                    <p className="text-soc-muted text-sm mt-1">Real-time security alert monitoring and triage</p>
                </div>
            </div>

            {/* Quick Stats */}
            {stats && (
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                    {[
                        { label: 'Total', value: stats.total, color: 'text-white' },
                        { label: 'Open', value: stats.open, color: 'text-red-400' },
                        { label: 'Critical', value: stats.critical, color: 'text-red-500' },
                        { label: 'High', value: stats.high, color: 'text-orange-400' },
                        { label: 'FP Rate', value: `${stats.false_positive_rate}%`, color: 'text-soc-dim' },
                    ].map(({ label, value, color }) => (
                        <div key={label} className="glass-card p-3 text-center">
                            <p className={`text-xl font-bold ${color}`}>{value}</p>
                            <p className="text-xs text-soc-dim">{label}</p>
                        </div>
                    ))}
                </div>
            )}

            {/* Filters */}
            <div className="flex gap-3 flex-wrap">
                <select
                    className="input-field w-auto"
                    value={filterSeverity}
                    onChange={(e) => setFilterSeverity(e.target.value)}
                >
                    <option value="">All Severities</option>
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                </select>
                <select
                    className="input-field w-auto"
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                >
                    <option value="">All Status</option>
                    <option value="open">Open</option>
                    <option value="investigating">Investigating</option>
                    <option value="resolved">Resolved</option>
                    <option value="false_positive">False Positive</option>
                </select>
                {(filterSeverity || filterStatus) && (
                    <button
                        className="btn-ghost text-sm"
                        onClick={() => { setFilterSeverity(''); setFilterStatus(''); }}
                    >
                        <X className="w-4 h-4 mr-1 inline" /> Clear Filters
                    </button>
                )}
            </div>

            {/* Alert Table */}
            <div className="glass-card overflow-hidden">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-soc-border text-left text-xs text-soc-dim uppercase tracking-wider">
                            <th className="p-4">Severity</th>
                            <th className="p-4">Alert</th>
                            <th className="p-4">Source IP</th>
                            <th className="p-4">MITRE</th>
                            <th className="p-4">Status</th>
                            <th className="p-4">Events</th>
                            <th className="p-4">Time</th>
                            <th className="p-4">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr><td colSpan={8} className="p-8 text-center text-soc-dim">Loading alerts...</td></tr>
                        ) : alerts.length === 0 ? (
                            <tr><td colSpan={8} className="p-8 text-center text-soc-dim">
                                No alerts found. Run an attack simulation to generate alerts.
                            </td></tr>
                        ) : (
                            alerts.map((alert) => (
                                <tr key={alert.id} className="table-row">
                                    <td className="p-4">
                                        <span className={`px-2 py-1 rounded text-xs font-bold font-mono severity-${alert.severity}`}>
                                            {alert.severity?.toUpperCase()}
                                        </span>
                                    </td>
                                    <td className="p-4">
                                        <p className="text-sm font-medium truncate max-w-xs">{alert.title}</p>
                                        <p className="text-xs text-soc-dim">{alert.source}</p>
                                    </td>
                                    <td className="p-4 font-mono text-sm text-soc-cyan">{alert.source_ip || '—'}</td>
                                    <td className="p-4">
                                        <span className="text-xs text-purple-400">{alert.mitre_technique || '—'}</span>
                                        {alert.mitre_technique_id && (
                                            <p className="text-xs text-soc-dim font-mono">{alert.mitre_technique_id}</p>
                                        )}
                                    </td>
                                    <td className="p-4">
                                        <span className={`px-2 py-1 rounded text-xs status-${alert.status}`}>
                                            {alert.status}
                                        </span>
                                    </td>
                                    <td className="p-4 font-mono text-sm">{alert.event_count}</td>
                                    <td className="p-4 text-xs text-soc-dim whitespace-nowrap">
                                        {alert.created_at ? new Date(alert.created_at).toLocaleString() : ''}
                                    </td>
                                    <td className="p-4">
                                        <div className="flex gap-1">
                                            <button
                                                onClick={() => updateAlertStatus(alert.id, 'resolved')}
                                                className="p-1.5 rounded hover:bg-green-500/20 text-soc-dim hover:text-green-400 transition-colors"
                                                title="Resolve"
                                            >
                                                <CheckCircle className="w-4 h-4" />
                                            </button>
                                            <button
                                                onClick={() => updateAlertStatus(alert.id, 'false_positive', true)}
                                                className="p-1.5 rounded hover:bg-amber-500/20 text-soc-dim hover:text-amber-400 transition-colors"
                                                title="Mark as False Positive"
                                            >
                                                <XCircle className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
