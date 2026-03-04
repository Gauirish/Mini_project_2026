import { useState } from 'react';
import { supabase } from '../supabaseClient';

function Auth() {
    console.log("Auth Component Rendering");
    const [loading, setLoading] = useState(false);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [isSignUp, setIsSignUp] = useState(false);
    const [message, setMessage] = useState('');

    const handleAuth = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage('');

        try {
            if (isSignUp) {
                const { error } = await supabase.auth.signUp({
                    email,
                    password,
                    options: {
                        data: {
                            first_name: firstName,
                            last_name: lastName,
                            full_name: `${firstName} ${lastName}`.trim()
                        }
                    }
                });
                if (error) throw error;
                setMessage('Signup successful! Check your email for a confirmation link.');
            } else {
                const { error } = await supabase.auth.signInWithPassword({ email, password });
                if (error) throw error;
            }
        } catch (error) {
            setMessage(error.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-wrapper">
            <div className="auth-container">
                <h1 className="brand-title">CineSense</h1>
                <h2 className="auth-title">{isSignUp ? 'Create Account' : 'Welcome Back'}</h2>
                <p className="auth-subtitle">
                    {isSignUp ? 'Join our community of movie lovers' : 'Sign in to access your movie collection'}
                </p>

                <form onSubmit={handleAuth} className="auth-form">
                    <div className="input-group">
                        <label htmlFor="email">Email Address</label>
                        <input
                            id="email"
                            type="email"
                            placeholder="name@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    {isSignUp && (
                        <div className="input-group">
                            <label htmlFor="firstName">First Name</label>
                            <input
                                id="firstName"
                                type="text"
                                placeholder="Your first name"
                                value={firstName}
                                onChange={(e) => setFirstName(e.target.value)}
                                required
                            />
                        </div>
                    )}
                    {isSignUp && (
                        <div className="input-group">
                            <label htmlFor="lastName">Last Name</label>
                            <input
                                id="lastName"
                                type="text"
                                placeholder="Your last name"
                                value={lastName}
                                onChange={(e) => setLastName(e.target.value)}
                                required
                            />
                        </div>
                    )}
                    <div className="input-group">
                        <label htmlFor="password">Password</label>
                        <input
                            id="password"
                            type="password"
                            placeholder="••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    <button type="submit" className="auth-button" disabled={loading}>
                        {loading ? 'Processing...' : (isSignUp ? 'Sign Up' : 'Sign In')}
                    </button>
                </form>

                {message && <p className={`auth-message ${message.includes('successful') ? 'success' : 'error'}`}>{message}</p>}

                <div className="auth-toggle">
                    <span>{isSignUp ? 'Already have an account?' : "Don't have an account?"}</span>
                    <button onClick={() => setIsSignUp(!isSignUp)} className="toggle-link">
                        {isSignUp ? 'Sign In' : 'Sign Up'}
                    </button>
                </div>
            </div>
        </div>
    );
}

export default Auth;
