import "./App.css";
import { useState } from "react";
import { Link } from "react-router-dom";
import { supabase } from "../lib/supabase";

function SignUp() {
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    const handleSignUp = async (event) => {
        event.preventDefault();
        if (!supabase) return;
        setError(null);
        setLoading(true);
        const payload = { email, password };
        if (username) payload.options = { data: { username } };
        const { error: err } = await supabase.auth.signUp(payload);
        setLoading(false);
        if (err) {
            setError(err.message);
            return;
        }
        setSuccess(true);
    };

    if (!supabase) {
        return (
            <div>
                <h1>Sign up</h1>
                <p>Supabase is not configured.</p>
            </div>
        );
    }

    if (success) {
        return (
            <div>
                <h1>Account created</h1>
                <p>Sign in with your email and password. Check your email if confirmation is required.</p>
                <Link to="/auth">Sign in</Link>
            </div>
        );
    }

    return (
        <div>
            <h1>Sign up</h1>
            <p>Username, email, and password</p>
            {error && <p style={{ color: "red" }}>{error}</p>}
            <form onSubmit={handleSignUp}>
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    required
                    onChange={(e) => setUsername(e.target.value)}
                />
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
                <button disabled={loading}>{loading ? "Creating account..." : "Sign up"}</button>
            </form>
            <p>Already have an account? <Link to="/auth">Sign in</Link></p>
        </div>
    );
}

export default SignUp;
