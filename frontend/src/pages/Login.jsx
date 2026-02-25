import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Shield, Lock, User, Mail, Eye, EyeOff, ArrowRight } from 'lucide-react';

export default function Login() {
    const [isLogin, setIsLogin] = useState(true);
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const { login, register } = useAuth();
    const navigate = useNavigate();

    const [form, setForm] = useState({
        username: '', email: '', password: '', full_name: '', role: 'analyst',
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            if (isLogin) {
                await login(form.username, form.password);
            } else {
                await register(form);
            }
            navigate('/');
        } catch (err) {
            setError(err.response?.data?.detail || 'Authentication failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-soc-bg relative overflow-hidden">
            {/* Animated Background */}
            <div className="absolute inset-0 overflow-hidden">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-soc-cyan/5 rounded-full blur-3xl animate-pulse-slow" />
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-600/5 rounded-full blur-3xl animate-pulse-slow delay-1000" />
                <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-purple-600/5 rounded-full blur-3xl animate-pulse-slow delay-500" />
                {/* Grid pattern */}
                <div className="absolute inset-0" style={{
                    backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(6,182,212,0.05) 1px, transparent 0)',
                    backgroundSize: '40px 40px',
                }} />
            </div>

            <div className="relative z-10 w-full max-w-md px-6">
                {/* Logo */}
                <div className="text-center mb-8 animate-fade-in">
                    <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-soc-cyan to-blue-600 flex items-center justify-center shadow-2xl shadow-soc-cyan/30">
                        <Shield className="w-10 h-10 text-white" />
                    </div>
                    <h1 className="text-3xl font-bold text-gradient mb-1">SOCForge</h1>
                    <p className="text-soc-muted text-sm">Enterprise SOC Threat Detection Platform</p>
                </div>

                {/* Form Card */}
                <div className="glass-card p-8 animate-slide-up">
                    <h2 className="text-xl font-semibold mb-6">
                        {isLogin ? 'Sign In to SOC' : 'Create SOC Account'}
                    </h2>

                    {error && (
                        <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="text-sm text-soc-muted mb-1 block">Username</label>
                            <div className="relative">
                                <User className="absolute left-3 top-3 w-4 h-4 text-soc-dim" />
                                <input
                                    type="text"
                                    className="input-field pl-10"
                                    placeholder="Enter username"
                                    value={form.username}
                                    onChange={(e) => setForm({ ...form, username: e.target.value })}
                                    required
                                />
                            </div>
                        </div>

                        {!isLogin && (
                            <>
                                <div>
                                    <label className="text-sm text-soc-muted mb-1 block">Email</label>
                                    <div className="relative">
                                        <Mail className="absolute left-3 top-3 w-4 h-4 text-soc-dim" />
                                        <input
                                            type="email"
                                            className="input-field pl-10"
                                            placeholder="analyst@socforge.io"
                                            value={form.email}
                                            onChange={(e) => setForm({ ...form, email: e.target.value })}
                                            required
                                        />
                                    </div>
                                </div>
                                <div>
                                    <label className="text-sm text-soc-muted mb-1 block">Full Name</label>
                                    <input
                                        type="text"
                                        className="input-field"
                                        placeholder="Full name"
                                        value={form.full_name}
                                        onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="text-sm text-soc-muted mb-1 block">Role</label>
                                    <select
                                        className="input-field"
                                        value={form.role}
                                        onChange={(e) => setForm({ ...form, role: e.target.value })}
                                    >
                                        <option value="analyst">SOC Analyst</option>
                                        <option value="admin">Administrator</option>
                                        <option value="viewer">Viewer</option>
                                    </select>
                                </div>
                            </>
                        )}

                        <div>
                            <label className="text-sm text-soc-muted mb-1 block">Password</label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-3 w-4 h-4 text-soc-dim" />
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    className="input-field pl-10 pr-10"
                                    placeholder="••••••••"
                                    value={form.password}
                                    onChange={(e) => setForm({ ...form, password: e.target.value })}
                                    required
                                    minLength={8}
                                />
                                <button
                                    type="button"
                                    className="absolute right-3 top-3 text-soc-dim hover:text-white"
                                    onClick={() => setShowPassword(!showPassword)}
                                >
                                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                            </div>
                        </div>

                        <button
                            type="submit"
                            className="btn-primary w-full flex items-center justify-center gap-2"
                            disabled={loading}
                        >
                            {loading ? (
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            ) : (
                                <>
                                    {isLogin ? 'Access SOC Platform' : 'Create Account'}
                                    <ArrowRight className="w-4 h-4" />
                                </>
                            )}
                        </button>
                    </form>

                    <div className="mt-6 text-center">
                        <button
                            className="text-sm text-soc-muted hover:text-soc-cyan transition-colors"
                            onClick={() => { setIsLogin(!isLogin); setError(''); }}
                        >
                            {isLogin ? "Don't have an account? Register" : 'Already have an account? Sign In'}
                        </button>
                    </div>
                </div>

                <p className="text-center text-xs text-soc-dim mt-6">
                    SOCForge v1.0 • Enterprise Security Operations
                </p>
            </div>
        </div>
    );
}
