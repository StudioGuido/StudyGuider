import { supabase } from "../services/supabaseClient"; // Import the client to handle sign out

export default function Layout({ children }) {
  
  // PURPOSE: This function tells Supabase to clear the session, 
  // which triggers the AuthContext to log you out.
  const handleSignOut = async () => {
    await supabase.auth.signOut();
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#050505] text-white">
      {/* Small navigation bar for the Sign Out button */}
      <nav className="p-4 flex justify-end">
        <button 
          onClick={handleSignOut}
          className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded text-sm transition-colors"
        >
          Sign Out
        </button>
      </nav>

      <main className="flex-1 w-full">{children}</main>
    </div>
  );
}
