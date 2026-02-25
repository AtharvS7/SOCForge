import { useState, useEffect } from 'react';
import { detectionAPI } from '../api/client';
import { BookOpen, Plus, Edit2, Trash2, ToggleLeft, ToggleRight, Save, X, Shield } from 'lucide-react';

export default function RuleEditor() {
    const [rules, setRules] = useState([]);
    const [loading, setLoading] = useState(true);
    const [editing, setEditing] = useState(null);
    const [showCreate, setShowCreate] = useState(false);
    const [newRule, setNewRule] = useState({
        name: '', description: '', rule_type: 'threshold', severity: 'medium',
        event_type_filter: '', threshold_count: 5, time_window_seconds: 60,
        group_by_field: 'source_ip', mitre_tactic: '', mitre_technique: '',
        mitre_technique_id: '', condition_logic: { field: 'action', operator: 'equals', value: 'failed' },
    });

    useEffect(() => { loadRules(); }, []);

    const loadRules = async () => {
        try {
            const res = await detectionAPI.listRules();
            setRules(res.data);
        } catch (err) {
            console.error('Failed to load rules:', err);
        } finally {
            setLoading(false);
        }
    };

    const toggleRule = async (rule) => {
        try {
            await detectionAPI.updateRule(rule.id, { enabled: !rule.enabled });
            loadRules();
        } catch (err) {
            console.error('Failed to toggle rule:', err);
        }
    };

    const createRule = async () => {
        try {
            await detectionAPI.createRule(newRule);
            setShowCreate(false);
            loadRules();
            setNewRule({
                name: '', description: '', rule_type: 'threshold', severity: 'medium',
                event_type_filter: '', threshold_count: 5, time_window_seconds: 60,
                group_by_field: 'source_ip', mitre_tactic: '', mitre_technique: '',
                mitre_technique_id: '', condition_logic: { field: 'action', operator: 'equals', value: 'failed' },
            });
        } catch (err) {
            console.error('Failed to create rule:', err);
        }
    };

    const deleteRule = async (id) => {
        if (!confirm('Delete this detection rule?')) return;
        try {
            await detectionAPI.deleteRule(id);
            loadRules();
        } catch (err) {
            console.error('Failed to delete rule:', err);
        }
    };

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold flex items-center gap-3">
                        <BookOpen className="w-7 h-7 text-green-400" />
                        Detection Rule Engine
                    </h1>
                    <p className="text-soc-muted text-sm mt-1">Manage detection rules, thresholds, and MITRE ATT&CK mappings</p>
                </div>
                <button onClick={() => setShowCreate(!showCreate)} className="btn-primary flex items-center gap-2">
                    <Plus className="w-4 h-4" />
                    New Rule
                </button>
            </div>

            {/* Create Form */}
            {showCreate && (
                <div className="glass-card p-6 animate-slide-up border-green-500/30">
                    <h3 className="font-semibold mb-4 flex items-center gap-2">
                        <Plus className="w-5 h-5 text-green-400" />
                        Create Detection Rule
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="text-sm text-soc-muted block mb-1">Rule Name</label>
                            <input className="input-field" value={newRule.name} onChange={(e) => setNewRule({ ...newRule, name: e.target.value })} placeholder="SSH Brute Force Custom" />
                        </div>
                        <div>
                            <label className="text-sm text-soc-muted block mb-1">Severity</label>
                            <select className="input-field" value={newRule.severity} onChange={(e) => setNewRule({ ...newRule, severity: e.target.value })}>
                                <option value="low">Low</option>
                                <option value="medium">Medium</option>
                                <option value="high">High</option>
                                <option value="critical">Critical</option>
                            </select>
                        </div>
                        <div>
                            <label className="text-sm text-soc-muted block mb-1">Event Type Filter</label>
                            <input className="input-field" value={newRule.event_type_filter} onChange={(e) => setNewRule({ ...newRule, event_type_filter: e.target.value })} placeholder="ssh_login_failed" />
                        </div>
                        <div>
                            <label className="text-sm text-soc-muted block mb-1">Rule Type</label>
                            <select className="input-field" value={newRule.rule_type} onChange={(e) => setNewRule({ ...newRule, rule_type: e.target.value })}>
                                <option value="threshold">Threshold</option>
                                <option value="pattern">Pattern</option>
                                <option value="anomaly">Anomaly</option>
                            </select>
                        </div>
                        <div>
                            <label className="text-sm text-soc-muted block mb-1">Threshold Count</label>
                            <input type="number" className="input-field" value={newRule.threshold_count} onChange={(e) => setNewRule({ ...newRule, threshold_count: Number(e.target.value) })} />
                        </div>
                        <div>
                            <label className="text-sm text-soc-muted block mb-1">Time Window (s)</label>
                            <input type="number" className="input-field" value={newRule.time_window_seconds} onChange={(e) => setNewRule({ ...newRule, time_window_seconds: Number(e.target.value) })} />
                        </div>
                        <div>
                            <label className="text-sm text-soc-muted block mb-1">Group By Field</label>
                            <input className="input-field" value={newRule.group_by_field} onChange={(e) => setNewRule({ ...newRule, group_by_field: e.target.value })} placeholder="source_ip" />
                        </div>
                        <div>
                            <label className="text-sm text-soc-muted block mb-1">MITRE Technique ID</label>
                            <input className="input-field" value={newRule.mitre_technique_id} onChange={(e) => setNewRule({ ...newRule, mitre_technique_id: e.target.value })} placeholder="T1110" />
                        </div>
                        <div className="md:col-span-2">
                            <label className="text-sm text-soc-muted block mb-1">Description</label>
                            <textarea className="input-field" rows={2} value={newRule.description} onChange={(e) => setNewRule({ ...newRule, description: e.target.value })} placeholder="Describe what this rule detects..." />
                        </div>
                    </div>
                    <div className="flex gap-3 mt-4">
                        <button onClick={createRule} className="btn-primary flex items-center gap-2">
                            <Save className="w-4 h-4" /> Save Rule
                        </button>
                        <button onClick={() => setShowCreate(false)} className="btn-ghost">
                            <X className="w-4 h-4 mr-1 inline" /> Cancel
                        </button>
                    </div>
                </div>
            )}

            {/* Rules List */}
            <div className="space-y-3">
                {loading ? (
                    <div className="glass-card p-8 text-center text-soc-dim">Loading detection rules...</div>
                ) : rules.length === 0 ? (
                    <div className="glass-card p-8 text-center text-soc-dim">No detection rules configured.</div>
                ) : (
                    rules.map((rule) => (
                        <div key={rule.id} className={`glass-card-hover p-5 ${!rule.enabled ? 'opacity-60' : ''}`}>
                            <div className="flex items-start justify-between">
                                <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-2">
                                        <h4 className="font-semibold">{rule.name}</h4>
                                        <span className={`px-2 py-0.5 rounded text-xs font-bold severity-${rule.severity}`}>
                                            {rule.severity?.toUpperCase()}
                                        </span>
                                        <span className="px-2 py-0.5 rounded text-xs bg-soc-hover text-soc-dim">{rule.rule_type}</span>
                                        {rule.mitre_technique_id && (
                                            <span className="px-2 py-0.5 rounded text-xs bg-purple-500/15 text-purple-300 font-mono">
                                                {rule.mitre_technique_id}
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-sm text-soc-muted">{rule.description}</p>
                                    <div className="flex flex-wrap gap-4 mt-3 text-xs text-soc-dim">
                                        <span>Event: <strong className="text-white">{rule.event_type_filter || 'any'}</strong></span>
                                        <span>Threshold: <strong className="text-white">≥{rule.threshold_count}</strong></span>
                                        <span>Window: <strong className="text-white">{rule.time_window_seconds}s</strong></span>
                                        <span>Group: <strong className="text-white">{rule.group_by_field || 'none'}</strong></span>
                                        <span>Triggers: <strong className="text-soc-cyan">{rule.total_triggers}</strong></span>
                                        <span>FP Rate: <strong className="text-amber-400">{rule.false_positive_rate?.toFixed(1)}%</strong></span>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2 ml-4">
                                    <button
                                        onClick={() => toggleRule(rule)}
                                        className={`p-2 rounded-lg transition-colors ${rule.enabled ? 'text-green-400 hover:bg-green-500/20' : 'text-soc-dim hover:bg-soc-hover'}`}
                                        title={rule.enabled ? 'Disable Rule' : 'Enable Rule'}
                                    >
                                        {rule.enabled ? <ToggleRight className="w-6 h-6" /> : <ToggleLeft className="w-6 h-6" />}
                                    </button>
                                    <button
                                        onClick={() => deleteRule(rule.id)}
                                        className="p-2 rounded-lg text-soc-dim hover:text-red-400 hover:bg-red-500/20 transition-colors"
                                        title="Delete Rule"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>

                            {/* Tags */}
                            {rule.tags && rule.tags.length > 0 && (
                                <div className="flex flex-wrap gap-1.5 mt-3">
                                    {rule.tags.map((tag) => (
                                        <span key={tag} className="px-2 py-0.5 rounded bg-soc-bg text-xs text-soc-dim">#{tag}</span>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
