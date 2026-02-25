import { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
    LayoutDashboard, Swords, Bell, Search, BookOpen, FileText,
    Shield, LogOut, Menu, X, ChevronDown, Activity
} from 'lucide-react';

const navItems = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard', end: true },
    { path: '/simulation', icon: Swords, label: 'Attack Simulation' },
    { path: '/alerts', icon: Bell, label: 'Alert Monitor' },
    { path: '/investigation', icon: Search, label: 'Investigation' },
    { path: '/rules', icon: BookOpen, label: 'Detection Rules' },
    { path: '/reports', icon: FileText, label: 'Reports' },
];

export default function Layout() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [sidebarOpen, setSidebarOpen] = useState(true);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="flex h-screen overflow-hidden">
            {/* Sidebar */}
            <aside className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-soc-surface border-r border-soc-border flex flex-col transition-all duration-300 flex-shrink-0`}>
                {/* Logo */}
                <div className="p-4 border-b border-soc-border flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-soc-cyan to-blue-600 flex items-center justify-center flex-shrink-0">
                        <Shield className="w-6 h-6 text-white" />
                    </div>
                    {sidebarOpen && (
                        <div className="animate-fade-in">
                            <h1 className="text-lg font-bold text-gradient">SOCForge</h1>
                            <p className="text-[10px] text-soc-dim uppercase tracking-wider">Threat Operations</p>
                        </div>
                    )}
                </div>

                {/* Navigation */}
                <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
                    {navItems.map(({ path, icon: Icon, label, end }) => (
                        <NavLink
                            key={path}
                            to={path}
                            end={end}
                            className={({ isActive }) =>
                                `nav-link ${isActive ? 'active' : ''} ${!sidebarOpen ? 'justify-center px-3' : ''}`
                            }
                        >
                            <Icon className="w-5 h-5 flex-shrink-0" />
                            {sidebarOpen && <span className="text-sm font-medium">{label}</span>}
                        </NavLink>
                    ))}
                </nav>

                {/* Collapse Toggle */}
                <button
                    onClick={() => setSidebarOpen(!sidebarOpen)}
                    className="p-3 border-t border-soc-border text-soc-dim hover:text-white transition-colors"
                >
                    {sidebarOpen ? <X className="w-5 h-5 mx-auto" /> : <Menu className="w-5 h-5 mx-auto" />}
                </button>

                {/* User */}
                <div className="p-3 border-t border-soc-border">
                    <div className={`flex items-center gap-3 ${!sidebarOpen ? 'justify-center' : ''}`}>
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0">
                            <span className="text-white text-xs font-bold">
                                {user?.username?.charAt(0).toUpperCase() || 'U'}
                            </span>
                        </div>
                        {sidebarOpen && (
                            <div className="flex-1 min-w-0 animate-fade-in">
                                <p className="text-sm font-medium truncate">{user?.username}</p>
                                <p className="text-xs text-soc-dim capitalize">{user?.role}</p>
                            </div>
                        )}
                        <button onClick={handleLogout} className="text-soc-dim hover:text-red-400 transition-colors flex-shrink-0">
                            <LogOut className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-y-auto bg-soc-bg">
                {/* Top Bar */}
                <header className="sticky top-0 z-10 bg-soc-bg/80 backdrop-blur-md border-b border-soc-border px-6 py-3">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Activity className="w-4 h-4 text-green-400 animate-pulse" />
                            <span className="text-sm text-soc-muted">System Status: <span className="text-green-400 font-medium">Operational</span></span>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-soc-dim">
                            <span className="font-mono">{new Date().toLocaleTimeString()}</span>
                        </div>
                    </div>
                </header>

                {/* Page Content */}
                <div className="p-6">
                    <Outlet />
                </div>
            </main>
        </div>
    );
}
