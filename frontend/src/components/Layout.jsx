import { supabase } from "../services/supabaseClient";

export default function Layout({ children }) {
  
  // PURPOSE: This function tells Supabase to clear the session, 
  // which triggers the AuthContext to log you out.
  const handleSignOut = async () => {
    await supabase.auth.signOut();
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#050505] text-white">
      <main className="flex-1 w-full">{children}</main>
    </div>
  );
}
