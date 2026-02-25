import { useState, useEffect } from 'react';
import { dashboardAPI } from '../api/client';
import {
    BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart
} from 'recharts';
import {
    AlertTriangle, Shield, Activity, Target, TrendingUp,
    Eye, Zap, AlertCircle, Clock, Crosshair
} from 'lucide-react';

const SEVERITY_COLORS = {
    critical: '#ef4444',
    high: '#f97316',
    medium: '#f59e0b',
    low: '#3b82f6',
    info: '#64748b',
};

export default function Dashboard() {
    const [stats, setStats] = useState(null);
    const [severityDist, setSeverityDist] = useState([]);
    const [alertTrend, setAlertTrend] = useState([]);
    const [recentAlerts, setRecentAlerts] = useState([]);
    const [topAttackers, setTopAttackers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadDashboard();
        const interval = setInterval(loadDashboard, 30000);
        return () => clearInterval(interval);
    }, []);

    const loadDashboard = async () => {
        try {
            const [statsRes, sevRes, trendRes, recentRes, attackersRes] = await Promise.all([
                dashboardAPI.stats(),
                dashboardAPI.severityDistribution(),
                dashboardAPI.alertTrend(),
                dashboardAPI.recentAlerts(8),
                dashboardAPI.topAttackers(),
            ]);
            setStats(statsRes.data);
            setSeverityDist(sevRes.data);
            setAlertTrend(trendRes.data);
            setRecentAlerts(recentRes.data);
            setTopAttackers(attackersRes.data);
        } catch (err) {
            console.error('Dashboard load error:', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return (
        <div className="flex items-center justify-center h-[60vh]">
            <div className="flex flex-col items-center gap-4">
                <div className="w-12 h-12 border-4 border-soc-cyan/30 border-t-soc-cyan rounded-full animate-spin" />
                <p className="text-soc-muted">Loading threat intelligence...</p>
            </div>
        </div>
    );

    const statCards = [
        { label: 'Total Events', value: stats?.total_events || 0, icon: Activity, color: 'from-cyan-500 to-blue-500', accent: '#06b6d4' },
        { label: 'Active Alerts', value: stats?.open_alerts || 0, icon: AlertTriangle, color: 'from-amber-500 to-orange-500', accent: '#f59e0b' },
        { label: 'Critical Alerts', value: stats?.critical_alerts || 0, icon: AlertCircle, color: 'from-red-500 to-rose-600', accent: '#ef4444' },
        { label: 'Active Incidents', value: stats?.active_incidents || 0, icon: Target, color: 'from-purple-500 to-violet-600', accent: '#8b5cf6' },
        { label: 'Detection Rules', value: stats?.detection_rules_active || 0, icon: Shield, color: 'from-green-500 to-emerald-600', accent: '#10b981' },
        { label: 'FP Rate', value: `${stats?.false_positive_rate || 0}%`, icon: Eye, color: 'from-slate-500 to-gray-600', accent: '#64748b' },
    ];

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Threat Operations Dashboard</h1>
                    <p className="text-soc-muted text-sm mt-1">
                        Real-time security monitoring and threat intelligence overview
                    </p>
                </div>
                <div className="flex items-center gap-2 text-xs text-soc-dim">
                    <Clock className="w-3 h-3" />
                    <span>Auto-refresh: 30s</span>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                {statCards.map(({ label, value, icon: Icon, color, accent }) => (
                    <div key={label} className="stat-card" style={{ '--accent-color': accent }}>
                        <div className="flex items-center gap-2 mb-3">
                            <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${color} flex items-center justify-center`}>
                                <Icon className="w-4 h-4 text-white" />
                            </div>
                        </div>
                        <p className="text-2xl font-bold">{typeof value === 'number' ? value.toLocaleString() : value}</p>
                        <p className="text-xs text-soc-muted mt-1">{label}</p>
                    </div>
                ))}
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Alert Trend */}
                <div className="lg:col-span-2 glass-card p-5">
                    <h3 className="text-sm font-semibold text-soc-muted mb-4 flex items-center gap-2">
                        <TrendingUp className="w-4 h-4 text-soc-cyan" />
                        Alert Trend (24h)
                    </h3>
                    <ResponsiveContainer width="100%" height={250}>
                        <AreaChart data={alertTrend}>
                            <defs>
                                <linearGradient id="alertGrad" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                            <XAxis dataKey="hour" stroke="#64748b" fontSize={11} />
                            <YAxis stroke="#64748b" fontSize={11} />
                            <Tooltip
                                contentStyle={{ background: '#1a1f35', border: '1px solid #1e293b', borderRadius: '8px', color: '#e2e8f0' }}
                            />
                            <Area type="monotone" dataKey="count" stroke="#06b6d4" fill="url(#alertGrad)" strokeWidth={2} />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>

                {/* Severity Distribution */}
                <div className="glass-card p-5">
                    <h3 className="text-sm font-semibold text-soc-muted mb-4 flex items-center gap-2">
                        <Zap className="w-4 h-4 text-amber-400" />
                        Severity Distribution
                    </h3>
                    <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                            <Pie
                                data={severityDist}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={90}
                                dataKey="count"
                                nameKey="severity"
                                stroke="none"
                            >
                                {severityDist.map((entry, i) => (
                                    <Cell key={i} fill={SEVERITY_COLORS[entry.severity] || '#64748b'} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{ background: '#1a1f35', border: '1px solid #1e293b', borderRadius: '8px', color: '#e2e8f0' }}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                    <div className="flex flex-wrap gap-3 justify-center mt-2">
                        {severityDist.map((entry) => (
                            <div key={entry.severity} className="flex items-center gap-1.5 text-xs">
                                <div className="w-2.5 h-2.5 rounded-full" style={{ background: SEVERITY_COLORS[entry.severity] }} />
                                <span className="text-soc-muted capitalize">{entry.severity}: {entry.count}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Bottom Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Recent Alerts */}
                <div className="glass-card p-5">
                    <h3 className="text-sm font-semibold text-soc-muted mb-4 flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4 text-red-400" />
                        Recent Alerts
                    </h3>
                    <div className="space-y-2">
                        {recentAlerts.length === 0 ? (
                            <p className="text-soc-dim text-sm text-center py-8">No alerts yet. Run a simulation to generate threat data.</p>
                        ) : (
                            recentAlerts.map((alert) => (
                                <div key={alert.id} className="flex items-center gap-3 p-3 rounded-lg hover:bg-soc-hover/50 transition-colors">
                                    <span className={`px-2 py-0.5 rounded text-xs font-mono font-bold severity-${alert.severity}`}>
                                        {alert.severity?.toUpperCase()}
                                    </span>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm truncate">{alert.title}</p>
                                        <p className="text-xs text-soc-dim">{alert.source_ip} • {alert.mitre_technique || 'N/A'}</p>
                                    </div>
                                    <span className="text-xs text-soc-dim whitespace-nowrap">
                                        {alert.created_at ? new Date(alert.created_at).toLocaleTimeString() : ''}
                                    </span>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Top Attackers */}
                <div className="glass-card p-5">
                    <h3 className="text-sm font-semibold text-soc-muted mb-4 flex items-center gap-2">
                        <Crosshair className="w-4 h-4 text-red-400" />
                        Top Threat Sources
                    </h3>
                    {topAttackers.length === 0 ? (
                        <p className="text-soc-dim text-sm text-center py-8">No threat data available.</p>
                    ) : (
                        <ResponsiveContainer width="100%" height={250}>
                            <BarChart data={topAttackers} layout="vertical">
                                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                                <XAxis type="number" stroke="#64748b" fontSize={11} />
                                <YAxis type="category" dataKey="ip" stroke="#64748b" fontSize={11} width={120} />
                                <Tooltip
                                    contentStyle={{ background: '#1a1f35', border: '1px solid #1e293b', borderRadius: '8px', color: '#e2e8f0' }}
                                />
                                <Bar dataKey="alert_count" fill="#ef4444" radius={[0, 4, 4, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    )}
                </div>
            </div>
        </div>
    );
}
