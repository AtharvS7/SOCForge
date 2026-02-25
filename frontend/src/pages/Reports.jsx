import { useState, useEffect } from 'react';
import { reportsAPI, incidentsAPI } from '../api/client';
import { FileText, Download, Plus, Loader, CheckCircle, Eye, Calendar, AlertTriangle } from 'lucide-react';

export default function Reports() {
    const [reports, setReports] = useState([]);
    const [incidents, setIncidents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [selectedIncident, setSelectedIncident] = useState('');
    const [reportTitle, setReportTitle] = useState('');
    const [viewReport, setViewReport] = useState(null);
    const [success, setSuccess] = useState('');

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [reportsRes, incidentsRes] = await Promise.all([
                reportsAPI.list(),
                incidentsAPI.list({ limit: 50 }),
            ]);
            setReports(reportsRes.data);
            setIncidents(incidentsRes.data);
        } catch (err) {
            console.error('Failed to load data:', err);
        } finally {
            setLoading(false);
        }
    };

    const generateReport = async () => {
        if (!selectedIncident) return;
        setGenerating(true);
        setSuccess('');
        try {
            await reportsAPI.generate({
                title: reportTitle || `Investigation Report - ${new Date().toLocaleDateString()}`,
                report_type: 'incident',
                incident_id: selectedIncident,
            });
            setSuccess('Report generated successfully!');
            setReportTitle('');
            setSelectedIncident('');
            loadData();
        } catch (err) {
            console.error('Failed to generate report:', err);
        } finally {
            setGenerating(false);
        }
    };

    const downloadPdf = async (id) => {
        try {
            const res = await reportsAPI.downloadPdf(id);
            const url = window.URL.createObjectURL(new Blob([res.data]));
            const a = document.createElement('a');
            a.href = url;
            a.download = `SOCForge_Report_${id}.pdf`;
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error('Failed to download PDF:', err);
        }
    };

    return (
        <div className="space-y-6 animate-fade-in">
            <div>
                <h1 className="text-2xl font-bold flex items-center gap-3">
                    <FileText className="w-7 h-7 text-blue-400" />
                    Report Generation
                </h1>
                <p className="text-soc-muted text-sm mt-1">Generate structured investigation reports with PDF export</p>
            </div>

            {/* Generate Report */}
            <div className="glass-card p-6">
                <h3 className="font-semibold mb-4 flex items-center gap-2">
                    <Plus className="w-5 h-5 text-soc-cyan" />
                    Generate New Report
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="text-sm text-soc-muted mb-1 block">Select Incident</label>
                        <select
                            className="input-field"
                            value={selectedIncident}
                            onChange={(e) => setSelectedIncident(e.target.value)}
                        >
                            <option value="">Choose an incident...</option>
                            {incidents.map((inc) => (
                                <option key={inc.id} value={inc.id}>
                                    [{inc.severity?.toUpperCase()}] {inc.title?.slice(0, 60)}
                                </option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label className="text-sm text-soc-muted mb-1 block">Report Title (optional)</label>
                        <input
                            className="input-field"
                            value={reportTitle}
                            onChange={(e) => setReportTitle(e.target.value)}
                            placeholder="Auto-generated if empty"
                        />
                    </div>
                    <div className="flex items-end">
                        <button
                            onClick={generateReport}
                            disabled={generating || !selectedIncident}
                            className="btn-primary w-full flex items-center justify-center gap-2"
                        >
                            {generating ? (
                                <>
                                    <Loader className="w-4 h-4 animate-spin" />
                                    Generating...
                                </>
                            ) : (
                                <>
                                    <FileText className="w-4 h-4" />
                                    Generate Report
                                </>
                            )}
                        </button>
                    </div>
                </div>
                {success && (
                    <div className="mt-3 flex items-center gap-2 text-green-400 text-sm">
                        <CheckCircle className="w-4 h-4" />
                        {success}
                    </div>
                )}
            </div>

            {/* Reports List */}
            <div className="space-y-3">
                <h3 className="text-sm font-semibold text-soc-muted uppercase tracking-wider">Generated Reports</h3>
                {loading ? (
                    <div className="glass-card p-8 text-center text-soc-dim">Loading reports...</div>
                ) : reports.length === 0 ? (
                    <div className="glass-card p-8 text-center text-soc-dim text-sm">
                        No reports generated yet. Select an incident above to create one.
                    </div>
                ) : (
                    reports.map((report) => (
                        <div key={report.id} className="glass-card-hover p-5">
                            <div className="flex items-start justify-between">
                                <div className="flex-1">
                                    <h4 className="font-semibold">{report.title}</h4>
                                    <div className="flex items-center gap-3 mt-2 text-xs text-soc-dim">
                                        <span className="flex items-center gap-1">
                                            <Calendar className="w-3 h-3" />
                                            {report.created_at ? new Date(report.created_at).toLocaleString() : 'N/A'}
                                        </span>
                                        <span className="px-2 py-0.5 rounded bg-blue-500/15 text-blue-300">{report.report_type}</span>
                                        {report.findings && (
                                            <span>{report.findings.length} findings</span>
                                        )}
                                        {report.ioc_list && (
                                            <span>{report.ioc_list.length} IOCs</span>
                                        )}
                                    </div>
                                    {report.summary && (
                                        <p className="text-sm text-soc-muted mt-2 line-clamp-2">{report.summary.slice(0, 200)}...</p>
                                    )}
                                </div>
                                <div className="flex gap-2 ml-4">
                                    <button
                                        onClick={() => setViewReport(viewReport?.id === report.id ? null : report)}
                                        className="btn-ghost text-sm flex items-center gap-1"
                                    >
                                        <Eye className="w-4 h-4" />
                                        {viewReport?.id === report.id ? 'Hide' : 'View'}
                                    </button>
                                    <button
                                        onClick={() => downloadPdf(report.id)}
                                        className="btn-primary text-sm py-1.5 flex items-center gap-1"
                                    >
                                        <Download className="w-4 h-4" />
                                        PDF
                                    </button>
                                </div>
                            </div>

                            {/* Expanded View */}
                            {viewReport?.id === report.id && (
                                <div className="mt-4 pt-4 border-t border-soc-border space-y-4 animate-slide-up">
                                    {/* Summary */}
                                    {report.summary && (
                                        <div>
                                            <h5 className="text-sm font-semibold text-soc-muted mb-2">Executive Summary</h5>
                                            <pre className="text-sm text-soc-text whitespace-pre-wrap bg-soc-bg p-4 rounded-lg font-sans">
                                                {report.summary}
                                            </pre>
                                        </div>
                                    )}

                                    {/* Findings */}
                                    {report.findings && report.findings.length > 0 && (
                                        <div>
                                            <h5 className="text-sm font-semibold text-soc-muted mb-2">Findings</h5>
                                            <div className="space-y-2">
                                                {report.findings.map((finding, i) => (
                                                    <div key={i} className="p-3 rounded-lg bg-soc-bg">
                                                        <div className="flex items-center gap-2 mb-1">
                                                            <span className={`px-2 py-0.5 rounded text-xs font-bold severity-${finding.severity}`}>
                                                                {finding.severity?.toUpperCase()}
                                                            </span>
                                                            <span className="text-sm font-medium">{finding.title}</span>
                                                        </div>
                                                        {finding.mitre_technique && (
                                                            <span className="text-xs text-purple-400">{finding.mitre_technique} ({finding.mitre_technique_id})</span>
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* IOCs */}
                                    {report.ioc_list && report.ioc_list.length > 0 && (
                                        <div>
                                            <h5 className="text-sm font-semibold text-soc-muted mb-2">IOCs</h5>
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                                {report.ioc_list.map((ioc, i) => (
                                                    <div key={i} className="flex items-center gap-2 p-2 rounded bg-soc-bg text-sm">
                                                        <span className="px-2 py-0.5 rounded bg-red-500/15 text-red-300 text-xs">{ioc.type}</span>
                                                        <span className="font-mono text-soc-cyan">{ioc.value}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Recommendations */}
                                    {report.recommendations && report.recommendations.length > 0 && (
                                        <div>
                                            <h5 className="text-sm font-semibold text-soc-muted mb-2">Recommendations</h5>
                                            <ul className="space-y-1.5">
                                                {report.recommendations.map((rec, i) => (
                                                    <li key={i} className="text-sm text-soc-muted flex items-start gap-2">
                                                        <span className="text-soc-cyan mt-0.5">▸</span>
                                                        {rec}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
