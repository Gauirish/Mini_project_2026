import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// Initialize Supabase client
let supabaseInstance = null;

try {
    if (supabaseUrl && supabaseUrl.startsWith('http')) {
        supabaseInstance = createClient(supabaseUrl, supabaseAnonKey);
        console.log("Supabase client initialized successfully");
    } else {
        console.warn("Supabase credentials missing or invalid in .env:", { supabaseUrl });
    }
} catch (e) {
    console.error("Failed to initialize Supabase client:", e);
}

export const supabase = supabaseInstance;
