import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('socforge_token'));
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (token) {
            authAPI.me()
                .then((res) => setUser(res.data))
                .catch(() => { logout(); })
                .finally(() => setLoading(false));
        } else {
            setLoading(false);
        }
    }, [token]);

    const login = async (username, password) => {
        const res = await authAPI.login({ username, password });
        const { access_token, user: userData } = res.data;
        localStorage.setItem('socforge_token', access_token);
        localStorage.setItem('socforge_user', JSON.stringify(userData));
        setToken(access_token);
        setUser(userData);
        return userData;
    };

    const register = async (data) => {
        const res = await authAPI.register(data);
        const { access_token, user: userData } = res.data;
        localStorage.setItem('socforge_token', access_token);
        localStorage.setItem('socforge_user', JSON.stringify(userData));
        setToken(access_token);
        setUser(userData);
        return userData;
    };

    const logout = () => {
        localStorage.removeItem('socforge_token');
        localStorage.removeItem('socforge_user');
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, token, loading, login, register, logout, isAuthenticated: !!token }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);
