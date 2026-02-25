import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/layout/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import SimulationPanel from './pages/SimulationPanel';
import AlertMonitor from './pages/AlertMonitor';
import Investigation from './pages/Investigation';
import RuleEditor from './pages/RuleEditor';
import Reports from './pages/Reports';

function ProtectedRoute({ children }) {
    const { isAuthenticated, loading } = useAuth();
    if (loading) return (
        <div className="h-screen flex items-center justify-center bg-soc-bg">
            <div className="flex flex-col items-center gap-4">
                <div className="w-12 h-12 border-4 border-soc-cyan/30 border-t-soc-cyan rounded-full animate-spin" />
                <p className="text-soc-muted animate-pulse">Initializing SOCForge...</p>
            </div>
        </div>
    );
    return isAuthenticated ? children : <Navigate to="/login" />;
}

export default function App() {
    return (
        <AuthProvider>
            <BrowserRouter>
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
                        <Route index element={<Dashboard />} />
                        <Route path="simulation" element={<SimulationPanel />} />
                        <Route path="alerts" element={<AlertMonitor />} />
                        <Route path="investigation" element={<Investigation />} />
                        <Route path="investigation/:id" element={<Investigation />} />
                        <Route path="rules" element={<RuleEditor />} />
                        <Route path="reports" element={<Reports />} />
                    </Route>
                </Routes>
            </BrowserRouter>
        </AuthProvider>
    );
}
