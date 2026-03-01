import "./App.css";
import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { supabase } from "../lib/supabase";

function Auth() {
    const [loading, setLoading] = useState(false);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [user, setUser] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!supabase) return;
        supabase.auth.getSession().then(({ data: { session } }) => {
            if (session) {
                localStorage.setItem("access_token", session.access_token);
                setUser(session.user);
            }
        });
        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
            if (session) {
                localStorage.setItem("access_token", session.access_token);
                setUser(session.user);
            } else {
                localStorage.removeItem("access_token");
                setUser(null);
            }
        });
        return () => subscription.unsubscribe();
    }, []);

    const handleLogin = async (event) => {
        event.preventDefault();
        if (!supabase) return;
        setError(null);
        setLoading(true);
        const { data, error: err } = await supabase.auth.signInWithPassword({ email, password });
        setLoading(false);
        if (err) {
            setError(err.message);
            return;
        }
        if (data.session) {
            localStorage.setItem("access_token", data.session.access_token);
            setUser(data.user);
        }
    };

    const handleLogout = async () => {
        if (supabase) await supabase.auth.signOut();
        localStorage.removeItem("access_token");
        setUser(null);
        setError(null);
    };

    if (!supabase) {
        return (
            <div>
                <h1>Sign in</h1>
                <p>Supabase is not configured. Set VITE_SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY in .env.</p>
            </div>
        );
    }

    if (user) {
        return (
            <div>
                <h1>Welcome!</h1>
                <p>You are logged in as: {user.email}</p>
                <button onClick={handleLogout}>Sign out</button>
            </div>
        );
    }

    return (
        <div>
            <h1>Sign in</h1>
            <p>Email and password</p>
            {error && <p style={{ color: "red" }}>{error}</p>}
            <form onSubmit={handleLogin}>
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    required
                    onChange={(e) => setEmail(e.target.value)}
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    required
                    onChange={(e) => setPassword(e.target.value)}
                />
                <button disabled={loading}>{loading ? "Signing in..." : "Sign in"}</button>
            </form>
            <p>Don&apos;t have an account? <Link to="/signup">Sign up</Link></p>
        </div>
    );
}

export default Auth;
