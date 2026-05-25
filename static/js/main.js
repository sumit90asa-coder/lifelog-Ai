/* ============================================
   Lifelog AI — Shared JS
   Location: static/js/main.js
   ============================================ */

// ── Sidebar toggle ──────────────────────────
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
    document.getElementById('overlay').classList.toggle('open');
}
function closeSidebar() {
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('overlay').classList.remove('open');
}

// ── Logout ──────────────────────────────────
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login/';
}

// ── JWT token refresh ────────────────────────
async function refreshToken() {
    const refresh = localStorage.getItem('refresh_token');
    if (!refresh) return false;
    try {
        const res = await fetch('/api/token/refresh/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh })
        });
        if (!res.ok) return false;
        const data = await res.json();
        localStorage.setItem('access_token', data.access);
        return true;
    } catch { return false; }
}

// ── Authenticated fetch ──────────────────────
async function apiFetch(url, opts = {}) {
    const token = localStorage.getItem('access_token');
    if (!token) { window.location.href = '/login/'; return null; }

    try {
        const res = await fetch(url, {
            ...opts,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token,
                ...(opts.headers || {})
            }
        });

        if (res.status === 401) {
            const refreshed = await refreshToken();
            if (!refreshed) { window.location.href = '/login/'; return null; }
            return fetch(url, {
                ...opts,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
                    ...(opts.headers || {})
                }
            });
        }
        return res;
    } catch (e) {
        console.error('apiFetch error:', url, e);
        return null;
    }
}

// ── Mood color helper ────────────────────────
function moodColor(score) {
    if (score >= 7) return 'mood-high';
    if (score >= 4) return 'mood-mid';
    return 'mood-low';
}

// ── Tag builder ─────────────────────────────
function buildTag(text, cls = 'tag-green') {
    return `<span class="tag ${cls}">${text}</span>`;
}

// ── Auth guard — call on every protected page ─
function requireAuth() {
    if (!localStorage.getItem('access_token')) {
        window.location.href = '/login/';
        return false;
    }
    return true;
}