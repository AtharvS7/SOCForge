import { useState, useEffect } from 'react';
import { simulationAPI } from '../api/client';
import {
    Swords, Play, Loader, CheckCircle, Zap, Shield, Crosshair,
    Globe, Terminal, ArrowRight, AlertTriangle, Activity
} from 'lucide-react';

const SCENARIO_ICONS = {
    full_attack_chain: Swords,
    ssh_brute_force: Terminal,
    port_scan: Globe,
    web_attack: Zap,
    lateral_movement: ArrowRight,
};

const INTENSITY_COLORS = {
    low: 'text-blue-400 bg-blue-500/10 border-blue-500/30',
    medium: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
    high: 'text-red-400 bg-red-500/10 border-red-500/30',
};

export default function SimulationPanel() {
    const [scenarios, setScenarios] = useState([]);
    const [selectedScenario, setSelectedScenario] = useState('full_attack_chain');
    const [intensity, setIntensity] = useState('medium');
    const [duration, setDuration] = useState(60);
    const [includeBenign, setIncludeBenign] = useState(true);
    const [running, setRunning] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');

    useEffect(() => {
        simulationAPI.scenarios().then(res => setScenarios(res.data)).catch(() => { });
    }, []);

    const startSimulation = async () => {
        setRunning(true);
        setResult(null);
        setError('');
        try {
            const res = await simulationAPI.start({
                scenario: selectedScenario,
                intensity,
                duration_seconds: duration,
                target_network: '10.0.1.0/24',
                include_benign_traffic: includeBenign,
            });
            setResult(res.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Simulation failed');
        } finally {
            setRunning(false);
        }
    };

    return (
        <div className="space-y-6 animate-fade-in">
            <div>
                <h1 className="text-2xl font-bold flex items-center gap-3">
                    <Swords className="w-7 h-7 text-red-400" />
                    Attack Simulation Control
                </h1>
                <p className="text-soc-muted text-sm mt-1">
                    Launch simulated cyber attacks to test detection rules and train SOC analysts
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Scenario Selection */}
                <div className="lg:col-span-2 space-y-4">
                    <h3 className="text-sm font-semibold text-soc-muted uppercase tracking-wider">Select Attack Scenario</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {scenarios.map((scenario) => {
                            const Icon = SCENARIO_ICONS[scenario.id] || Shield;
                            const isSelected = selectedScenario === scenario.id;
                            return (
                                <button
                                    key={scenario.id}
                                    onClick={() => setSelectedScenario(scenario.id)}
                                    className={`glass-card-hover p-4 text-left transition-all duration-300 ${isSelected ? 'border-soc-cyan/50 bg-soc-cyan/5 shadow-lg shadow-soc-cyan/10' : ''
                                        }`}
                                >
                                    <div className="flex items-start gap-3">
                                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${isSelected ? 'bg-soc-cyan/20' : 'bg-soc-hover'
                                            }`}>
                                            <Icon className={`w-5 h-5 ${isSelected ? 'text-soc-cyan' : 'text-soc-dim'}`} />
                                        </div>
                                        <div>
                                            <h4 className="font-semibold text-sm">{scenario.name}</h4>
                                            <p className="text-xs text-soc-dim mt-1 line-clamp-2">{scenario.description}</p>
                                            <div className="flex items-center gap-2 mt-2">
                                                <span className={`text-xs px-2 py-0.5 rounded border severity-${scenario.severity}`}>
                                                    {scenario.severity}
                                                </span>
                                                <span className="text-xs text-soc-dim">{scenario.estimated_events} events</span>
                                            </div>
                                        </div>
                                    </div>
                                </button>
                            );
                        })}
                    </div>
                </div>

                {/* Control Panel */}
                <div className="space-y-4">
                    <h3 className="text-sm font-semibold text-soc-muted uppercase tracking-wider">Configuration</h3>

                    <div className="glass-card p-5 space-y-5">
                        {/* Intensity */}
                        <div>
                            <label className="text-sm text-soc-muted mb-2 block">Attack Intensity</label>
                            <div className="flex gap-2">
                                {['low', 'medium', 'high'].map((level) => (
                                    <button
                                        key={level}
                                        onClick={() => setIntensity(level)}
                                        className={`flex-1 py-2 px-3 rounded-lg border text-sm font-medium capitalize transition-all ${intensity === level ? INTENSITY_COLORS[level] : 'border-soc-border text-soc-dim hover:border-soc-dim'
                                            }`}
                                    >
                                        {level}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Duration */}
                        <div>
                            <label className="text-sm text-soc-muted mb-2 block">
                                Duration: <span className="text-white font-mono">{duration}s</span>
                            </label>
                            <input
                                type="range"
                                min="10"
                                max="300"
                                step="10"
                                value={duration}
                                onChange={(e) => setDuration(Number(e.target.value))}
                                className="w-full accent-soc-cyan"
                            />
                            <div className="flex justify-between text-xs text-soc-dim mt-1">
                                <span>10s</span>
                                <span>300s</span>
                            </div>
                        </div>

                        {/* Benign Traffic */}
                        <label className="flex items-center gap-3 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={includeBenign}
                                onChange={(e) => setIncludeBenign(e.target.checked)}
                                className="w-4 h-4 accent-soc-cyan rounded"
                            />
                            <div>
                                <span className="text-sm">Include Benign Traffic</span>
                                <p className="text-xs text-soc-dim">Mix in normal traffic for realistic FP testing</p>
                            </div>
                        </label>

                        {/* Launch */}
                        <button
                            onClick={startSimulation}
                            disabled={running}
                            className="btn-danger w-full flex items-center justify-center gap-2 text-base"
                        >
                            {running ? (
                                <>
                                    <Loader className="w-5 h-5 animate-spin" />
                                    Executing Attack...
                                </>
                            ) : (
                                <>
                                    <Play className="w-5 h-5" />
                                    Launch Simulation
                                </>
                            )}
                        </button>
                    </div>

                    {/* Results */}
                    {result && (
                        <div className="glass-card p-5 animate-slide-up border-green-500/30">
                            <div className="flex items-center gap-2 mb-4">
                                <CheckCircle className="w-5 h-5 text-green-400" />
                                <h4 className="font-semibold text-green-400">Simulation Complete</h4>
                            </div>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-soc-muted">Events Generated</span>
                                    <span className="font-mono font-bold text-soc-cyan">{result.events_generated}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-soc-muted">Alerts Triggered</span>
                                    <span className="font-mono font-bold text-amber-400">{result.alerts_triggered}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-soc-muted">Incidents Created</span>
                                    <span className="font-mono font-bold text-red-400">{result.incidents_created}</span>
                                </div>
                            </div>
                        </div>
                    )}

                    {error && (
                        <div className="glass-card p-4 border-red-500/30 animate-slide-up">
                            <div className="flex items-center gap-2 text-red-400 text-sm">
                                <AlertTriangle className="w-4 h-4" />
                                {error}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
