import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { incidentsAPI } from '../api/client';
import { Search, Clock, AlertTriangle, Shield, Activity, ChevronRight, MapPin } from 'lucide-react';

const SEVERITY_COLORS = {
    critical: '#ef4444', high: '#f97316', medium: '#f59e0b', low: '#3b82f6', info: '#64748b',
};

export default function Investigation() {
    const { id } = useParams();
    const [incidents, setIncidents] = useState([]);
    const [selected, setSelected] = useState(null);
    const [timeline, setTimeline] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadIncidents();
    }, []);

    useEffect(() => {
        if (id) loadIncident(id);
    }, [id]);

    const loadIncidents = async () => {
        try {
            const res = await incidentsAPI.list({ limit: 50 });
            setIncidents(res.data);
            if (!id && res.data.length > 0) {
                loadIncident(res.data[0].id);
            }
        } catch (err) {
            console.error('Failed to load incidents:', err);
        } finally {
            setLoading(false);
        }
    };

    const loadIncident = async (incidentId) => {
        try {
            const [incRes, tlRes] = await Promise.all([
                incidentsAPI.get(incidentId),
                incidentsAPI.timeline(incidentId).catch(() => ({ data: [] })),
            ]);
            setSelected(incRes.data);
            setTimeline(Array.isArray(tlRes.data) ? tlRes.data : []);
        } catch (err) {
            console.error('Failed to load incident:', err);
        }
    };

    const updateStatus = async (status) => {
        if (!selected) return;
        try {
            await incidentsAPI.update(selected.id, { status });
            loadIncident(selected.id);
            loadIncidents();
        } catch (err) {
            console.error('Failed to update:', err);
        }
    };

    return (
        <div className="space-y-6 animate-fade-in">
            <div>
                <h1 className="text-2xl font-bold flex items-center gap-3">
                    <Search className="w-7 h-7 text-purple-400" />
                    Incident Investigation
                </h1>
                <p className="text-soc-muted text-sm mt-1">Deep dive into correlated security incidents with timeline reconstruction</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Incident List */}
                <div className="lg:col-span-4 space-y-3">
                    <h3 className="text-sm font-semibold text-soc-muted uppercase tracking-wider">Active Incidents</h3>
                    {loading ? (
                        <div className="glass-card p-8 text-center text-soc-dim">Loading...</div>
                    ) : incidents.length === 0 ? (
                        <div className="glass-card p-8 text-center text-soc-dim text-sm">
                            No incidents yet. Run a simulation to generate correlated incidents.
                        </div>
                    ) : (
                        <div className="space-y-2 max-h-[70vh] overflow-y-auto pr-1">
                            {incidents.map((inc) => (
                                <button
                                    key={inc.id}
                                    onClick={() => loadIncident(inc.id)}
                                    className={`w-full text-left glass-card-hover p-4 transition-all ${selected?.id === inc.id ? 'border-purple-500/50 bg-purple-500/5' : ''
                                        }`}
                                >
                                    <div className="flex items-center gap-2 mb-2">
                                        <span className={`px-2 py-0.5 rounded text-xs font-bold severity-${inc.severity}`}>
                                            {inc.severity?.toUpperCase()}
                                        </span>
                                        <span className={`px-2 py-0.5 rounded text-xs status-${inc.status}`}>{inc.status}</span>
                                    </div>
                                    <p className="text-sm font-medium truncate">{inc.title}</p>
                                    <div className="flex items-center gap-3 mt-2 text-xs text-soc-dim">
                                        <span>{inc.alert_count} alerts</span>
                                        <span>•</span>
                                        <span>{inc.kill_chain_phase || 'N/A'}</span>
                                    </div>
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                {/* Investigation Workspace */}
                <div className="lg:col-span-8 space-y-4">
                    {!selected ? (
                        <div className="glass-card p-12 text-center">
                            <Search className="w-12 h-12 mx-auto text-soc-dim mb-4" />
                            <p className="text-soc-dim">Select an incident to begin investigation</p>
                        </div>
                    ) : (
                        <>
                            {/* Incident Header */}
                            <div className="glass-card p-5">
                                <div className="flex items-start justify-between">
                                    <div>
                                        <div className="flex items-center gap-2 mb-2">
                                            <span className={`px-2 py-1 rounded text-xs font-bold severity-${selected.severity}`}>
                                                {selected.severity?.toUpperCase()}
                                            </span>
                                            <span className={`px-2 py-1 rounded text-xs status-${selected.status}`}>{selected.status}</span>
                                            {selected.category && (
                                                <span className="px-2 py-1 rounded text-xs bg-purple-500/20 text-purple-300">
                                                    {selected.category}
                                                </span>
                                            )}
                                        </div>
                                        <h2 className="text-lg font-bold">{selected.title}</h2>
                                        <p className="text-sm text-soc-muted mt-1">{selected.description}</p>
                                    </div>
                                    <div className="flex gap-2">
                                        {selected.status === 'open' && (
                                            <button onClick={() => updateStatus('investigating')} className="btn-primary text-sm py-2">
                                                Investigate
                                            </button>
                                        )}
                                        {selected.status !== 'resolved' && (
                                            <button onClick={() => updateStatus('resolved')} className="btn-ghost text-sm border border-green-500/30 text-green-400">
                                                Resolve
                                            </button>
                                        )}
                                    </div>
                                </div>

                                {/* Quick Info */}
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4">
                                    <div className="p-3 rounded-lg bg-soc-bg">
                                        <p className="text-xs text-soc-dim">Alerts</p>
                                        <p className="font-bold text-soc-cyan">{selected.alert_count}</p>
                                    </div>
                                    <div className="p-3 rounded-lg bg-soc-bg">
                                        <p className="text-xs text-soc-dim">Events</p>
                                        <p className="font-bold">{selected.event_count}</p>
                                    </div>
                                    <div className="p-3 rounded-lg bg-soc-bg">
                                        <p className="text-xs text-soc-dim">Kill Chain</p>
                                        <p className="font-bold text-amber-400 text-sm">{selected.kill_chain_phase || 'N/A'}</p>
                                    </div>
                                    <div className="p-3 rounded-lg bg-soc-bg">
                                        <p className="text-xs text-soc-dim">Priority</p>
                                        <p className="font-bold capitalize">{selected.priority}</p>
                                    </div>
                                </div>
                            </div>

                            {/* MITRE Mapping */}
                            {(selected.mitre_tactics?.length > 0 || selected.mitre_techniques?.length > 0) && (
                                <div className="glass-card p-5">
                                    <h3 className="text-sm font-semibold text-soc-muted mb-3 flex items-center gap-2">
                                        <Shield className="w-4 h-4 text-purple-400" />
                                        MITRE ATT&CK Mapping
                                    </h3>
                                    <div className="flex flex-wrap gap-2">
                                        {selected.mitre_tactics?.map((t) => (
                                            <span key={t} className="px-3 py-1.5 rounded-lg bg-purple-500/15 text-purple-300 text-xs border border-purple-500/30">
                                                {t}
                                            </span>
                                        ))}
                                    </div>
                                    {selected.mitre_techniques?.length > 0 && (
                                        <div className="flex flex-wrap gap-2 mt-2">
                                            {selected.mitre_techniques?.map((t) => (
                                                <span key={t} className="px-2 py-1 rounded bg-blue-500/15 text-blue-300 text-xs">
                                                    {t}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* IOC Summary */}
                            {selected.ioc_summary && (
                                <div className="glass-card p-5">
                                    <h3 className="text-sm font-semibold text-soc-muted mb-3 flex items-center gap-2">
                                        <AlertTriangle className="w-4 h-4 text-red-400" />
                                        Indicators of Compromise
                                    </h3>
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                                        <div>
                                            <p className="text-xs text-soc-dim mb-2">IP Addresses</p>
                                            <div className="space-y-1">
                                                {(selected.ioc_summary.ip_addresses || []).map((ip) => (
                                                    <p key={ip} className="text-sm font-mono text-soc-cyan">{ip}</p>
                                                ))}
                                            </div>
                                        </div>
                                        <div>
                                            <p className="text-xs text-soc-dim mb-2">Ports</p>
                                            <div className="flex flex-wrap gap-1">
                                                {(selected.ioc_summary.ports || []).map((port) => (
                                                    <span key={port} className="px-2 py-0.5 rounded bg-soc-bg text-sm font-mono">{port}</span>
                                                ))}
                                            </div>
                                        </div>
                                        <div>
                                            <p className="text-xs text-soc-dim mb-2">Hostnames</p>
                                            <div className="space-y-1">
                                                {(selected.ioc_summary.hostnames || []).map((h) => (
                                                    <p key={h} className="text-sm font-mono">{h}</p>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Attack Timeline */}
                            <div className="glass-card p-5">
                                <h3 className="text-sm font-semibold text-soc-muted mb-4 flex items-center gap-2">
                                    <Clock className="w-4 h-4 text-soc-cyan" />
                                    Attack Timeline
                                </h3>
                                {timeline.length === 0 ? (
                                    <p className="text-soc-dim text-sm text-center py-4">No timeline data available</p>
                                ) : (
                                    <div className="relative pl-6 space-y-4">
                                        <div className="absolute left-2 top-2 bottom-2 w-0.5 bg-gradient-to-b from-soc-cyan via-amber-500 to-red-500" />
                                        {timeline.slice(0, 30).map((entry, i) => (
                                            <div key={i} className="relative group">
                                                <div
                                                    className="absolute -left-4 top-2 w-3 h-3 rounded-full border-2 border-soc-card"
                                                    style={{ background: SEVERITY_COLORS[entry.severity] || '#64748b' }}
                                                />
                                                <div className="glass-card-hover p-3 ml-2">
                                                    <div className="flex items-center gap-2 mb-1">
                                                        <span className="text-xs font-mono text-soc-dim">
                                                            {new Date(entry.timestamp).toLocaleTimeString()}
                                                        </span>
                                                        <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold severity-${entry.severity}`}>
                                                            {entry.severity?.toUpperCase()}
                                                        </span>
                                                        <span className="text-[10px] text-purple-400 font-mono">{entry.mitre_technique || ''}</span>
                                                    </div>
                                                    <p className="text-sm">{entry.description}</p>
                                                    <div className="flex gap-3 mt-1 text-xs text-soc-dim">
                                                        {entry.source_ip && <span>Src: {entry.source_ip}</span>}
                                                        {entry.dest_ip && <span>Dst: {entry.dest_ip}</span>}
                                                        {entry.dest_port && <span>Port: {entry.dest_port}</span>}
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>

                            {/* Affected Hosts */}
                            {selected.affected_hosts?.length > 0 && (
                                <div className="glass-card p-5">
                                    <h3 className="text-sm font-semibold text-soc-muted mb-3 flex items-center gap-2">
                                        <MapPin className="w-4 h-4 text-green-400" />
                                        Affected Hosts
                                    </h3>
                                    <div className="flex flex-wrap gap-2">
                                        {selected.affected_hosts.map((host) => (
                                            <span key={host} className="px-3 py-1.5 rounded-lg bg-soc-bg border border-soc-border text-sm font-mono">
                                                {host}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
