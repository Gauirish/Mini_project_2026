import { useState, useEffect } from "react";
import { supabase } from "../supabaseClient";

function ProfilePage({ session, onBack }) {
    const user = session?.user;

    // Initializing state from session metadata or email
    const [firstName, setFirstName] = useState(user?.user_metadata?.first_name || user?.email?.split('@')[0] || "");
    const [lastName, setLastName] = useState(user?.user_metadata?.last_name || "");
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState({ type: '', text: '' });

    const handleLogout = async () => {
        if (supabase) {
            await supabase.auth.signOut();
        }
    };

    const handleSave = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage({ type: '', text: '' });

        try {
            const { error } = await supabase.auth.updateUser({
                data: {
                    first_name: firstName,
                    last_name: lastName,
                    full_name: `${firstName} ${lastName}`.trim()
                }
            });

            if (error) throw error;
            setMessage({ type: 'success', text: 'Profile updated successfully!' });
        } catch (error) {
            setMessage({ type: 'error', text: error.message });
        } finally {
            setLoading(false);
        }
    };

    const fullName = `${firstName} ${lastName}`.trim();

    return (
        <div className="profile-page-container">
            <div className="profile-card">

                <div className="profile-header">
                    <div className="profile-avatar">
                        {(firstName || user?.email || "U").charAt(0).toUpperCase()}
                    </div>
                    <h2>{fullName || "User Profile"}</h2>
                </div>

                <form onSubmit={handleSave} className="profile-form">
                    <div className="profile-details">
                        <div className="detail-item">
                            <label htmlFor="firstName">First Name</label>
                            <input
                                id="firstName"
                                type="text"
                                value={firstName}
                                onChange={(e) => setFirstName(e.target.value)}
                                placeholder="Edit first name"
                                className="profile-input"
                                required
                            />
                        </div>
                        <div className="detail-item">
                            <label htmlFor="lastName">Last Name</label>
                            <input
                                id="lastName"
                                type="text"
                                value={lastName}
                                onChange={(e) => setLastName(e.target.value)}
                                placeholder="Edit last name"
                                className="profile-input"
                            />
                        </div>
                        <div className="detail-item">
                            <label>Email Address</label>
                            <p className="static-detail">{user?.email}</p>
                        </div>
                    </div>

                    {message.text && (
                        <div className={`profile-message ${message.type}`}>
                            {message.text}
                        </div>
                    )}

                    <div className="profile-actions-column">
                        <button type="submit" className="save-btn-full" disabled={loading}>
                            {loading ? 'Saving...' : 'Save Changes'}
                        </button>
                        <button type="button" onClick={handleLogout} className="logout-btn-full">
                            Sign Out
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default ProfilePage;
