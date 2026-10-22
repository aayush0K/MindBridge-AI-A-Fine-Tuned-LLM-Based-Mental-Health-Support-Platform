import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ── Token helpers ────────────────────────────────────────────────────────────
export function setTokens(access: string, refresh: string) {
    if (typeof window !== "undefined") {
        localStorage.setItem("access_token", access);
        localStorage.setItem("refresh_token", refresh);
    }
}

export function getAccessToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("access_token");
}

export function getRefreshToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("refresh_token");
}

export function clearTokens() {
    if (typeof window !== "undefined") {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("user");
    }
}

// ── Axios instance with auth interceptor ─────────────────────────────────────
const api = axios.create({ baseURL: API_BASE });

api.interceptors.request.use((config) => {
    const token = getAccessToken();
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

api.interceptors.response.use(
    (res) => res,
    async (error) => {
        const original = error.config;
        if (error.response?.status === 401 && !original._retry) {
            original._retry = true;
            const refresh = getRefreshToken();
            if (refresh) {
                try {
                    const { data } = await axios.post(`${API_BASE}/api/v1/auth/refresh`, {
                        refresh_token: refresh,
                    });
                    setTokens(data.access_token, getRefreshToken()!);
                    original.headers.Authorization = `Bearer ${data.access_token}`;
                    return api(original);
                } catch {
                    clearTokens();
                }
            }
        }
        return Promise.reject(error);
    }
);

// ── Auth API ─────────────────────────────────────────────────────────────────
export const authApi = {
    register: (data: { email: string; password: string; full_name?: string }) =>
        api.post("/api/v1/auth/register", data),

    login: (data: { email: string; password: string }) =>
        api.post("/api/v1/auth/login", data),

    logout: () => api.post("/api/v1/auth/logout"),
};

// ── Chat API ─────────────────────────────────────────────────────────────────
export const chatApi = {
    sendMessage: (message: string, session_id?: string) =>
        api.post("/api/v1/chat/message", { message, session_id }),

    getSessions: () => api.get("/api/v1/chat/sessions"),

    getMessages: (sessionId: string) =>
        api.get(`/api/v1/chat/sessions/${sessionId}/messages`),

    deleteSession: (sessionId: string) =>
        api.delete(`/api/v1/chat/sessions/${sessionId}`),
};

// ── Mood API ─────────────────────────────────────────────────────────────────
export const moodApi = {
    log: (data: { mood_score: number; mood_label?: string; notes?: string }) =>
        api.post("/api/v1/mood/log", data),

    history: (days: number = 30) =>
        api.get(`/api/v1/mood/history?days=${days}`),

    stats: () => api.get("/api/v1/mood/stats"),

    trends: (days: number = 30) =>
        api.get(`/api/v1/mood/trends?days=${days}`),
};

// ── User API ─────────────────────────────────────────────────────────────────
export const userApi = {
    me: () => api.get("/api/v1/users/me"),

    update: (data: { full_name?: string; emergency_email?: string }) =>
        api.patch("/api/v1/users/me", data),

    delete: () => api.delete("/api/v1/users/me"),
};

// ── Report API ───────────────────────────────────────────────────────────────
export const reportApi = {
    generate: (days: number = 30) =>
        api.post(`/api/v1/reports/generate?days=${days}`),

    list: () => api.get("/api/v1/reports/"),

    get: (reportId: string) =>
        api.get(`/api/v1/reports/${reportId}`),

    download: (reportId: string) =>
        api.get(`/api/v1/reports/${reportId}/download`, { responseType: "blob" }),
};

// ── Journal API ──────────────────────────────────────────────────────────────
export const journalApi = {
    list: () => api.get("/api/v1/journal"),
    get: (id: string) => api.get(`/api/v1/journal/${id}`),
    create: (data: { title: string; content: string; mood_tag?: string }) =>
        api.post("/api/v1/journal", data),
    update: (id: string, data: { title?: string; content?: string; mood_tag?: string }) =>
        api.put(`/api/v1/journal/${id}`, data),
    delete: (id: string) => api.delete(`/api/v1/journal/${id}`),
};

export default api;

