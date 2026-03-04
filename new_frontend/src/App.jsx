import { useState, useMemo, useEffect } from "react";
import { supabase } from "./supabaseClient";
import Auth from "./pages/Auth";
import { filterMovies } from "./utils/filtermovies";
import { paginate } from "./utils/paginate";
import Header from "./components/Header";
import Filterchips from "./components/Filterchips";
import Pagination from "./components/Pagination";
import Moviecard from "./components/Moviecard";
import Moviedetail from "./components/Moviedetail";
import ProfilePage from "./pages/ProfilePage";

import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import MovieDetailsPage from "./pages/MovieDetailsPage";
import YourReviewsPage from "./pages/YourReviewsPage";
import RecommendationsPage from "./pages/RecommendationsPage";

function App() {
  const [session, setSession] = useState(null);

  // 🔐 Check session on mount
  useEffect(() => {
    if (!supabase) return;

    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, []);

  const handleLogout = async () => {
    if (supabase) {
      await supabase.auth.signOut();
    }
  };

  if (!supabase) {
    return (
      <div className="auth-wrapper">
        <div className="auth-container">
          <h1 className="brand-title">CineSense</h1>
          <h2 className="auth-title">Configuration Required</h2>
          <p className="auth-subtitle">
            Please update your <code>.env</code> file with your Supabase credentials to enable authentication and access the app.
          </p>
          <div className="auth-message error">
            Missing <code>VITE_SUPABASE_URL</code> or <code>VITE_SUPABASE_ANON_KEY</code>.
          </div>
        </div>
      </div>
    );
  }

  if (!session) {
    return <Auth />;
  }

  return (
    <div className="app-container">
      <Routes>
        <Route path="/" element={<Home session={session} handleLogout={handleLogout} />} />
        <Route path="/movie/:id" element={<MovieDetailsPage session={session} />} />
        <Route path="/profile" element={<ProfilePage session={session} onBack={() => window.history.back()} />} />
        <Route path="/your-reviews" element={<YourReviewsPage session={session} />} />
        <Route path="/recommendations" element={<RecommendationsPage session={session} />} />
      </Routes>
    </div>
  );
}

export default App;