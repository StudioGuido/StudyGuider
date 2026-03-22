import { useState } from 'react';
import { supabase } from '../../services/supabaseClient';

export default function Auth() {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });

    if (error) {
      alert(error.message);
    } else {
      console.log("Logged in user:", data.user);
    }
  };

  const handleSignUp = async (e) => {
    e.preventDefault();
    if (!email.trim() || !firstName.trim() || !lastName.trim() || !password || !confirmPassword) {
      alert("Please fill in all fields.");
      return;
    }
    if (password !== confirmPassword) {
      alert("Passwords do not match!");
      return;
    }
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: { firstName, lastName },
      },
    });

    if (error) {
      alert(error.message);
    } else {
      console.log("Signed up user:", data.user);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center px-4">
      <div className="relative w-full max-w-md">
        <div className="bg-[#0b0b0b] border border-gray-800 rounded-2xl p-8 shadow-xl">
          {/* Toggle tabs */}
          <div className="flex mb-8 border border-gray-700 rounded-full overflow-hidden">
            <button
              type="button"
              onClick={() => setIsSignUp(false)}
              className={`flex-1 py-2.5 text-sm font-medium transition-colors !rounded-full !border-0 ${
                !isSignUp
                  ? '!bg-white !text-black'
                  : '!bg-transparent text-gray-400 hover:text-white'
              }`}
            >
              Login
            </button>
            <button
              type="button"
              onClick={() => setIsSignUp(true)}
              className={`flex-1 py-2.5 text-sm font-medium transition-colors !rounded-full !border-0 ${
                isSignUp
                  ? '!bg-white !text-black'
                  : '!bg-transparent text-gray-400 hover:text-white'
              }`}
            >
              Signup
            </button>
          </div>

          {/* Form */}
          <form className="space-y-5" onSubmit={isSignUp ? handleSignUp : handleLogin}>
            <div>
              <label className="block text-sm font-medium text-white mb-1.5">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2.5 bg-transparent border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-gray-500 transition-colors"
              />
            </div>

            {isSignUp && (
              <>
                <div>
                  <label className="block text-sm font-medium text-white mb-1.5">First Name</label>
                  <input
                    type="text"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    className="w-full px-4 py-2.5 bg-transparent border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-gray-500 transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-white mb-1.5">Last Name</label>
                  <input
                    type="text"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    className="w-full px-4 py-2.5 bg-transparent border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-gray-500 transition-colors"
                  />
                </div>
              </>
            )}

            <div>
              <label className="block text-sm font-medium text-white mb-1.5">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2.5 bg-transparent border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-gray-500 transition-colors"
              />
            </div>

            {isSignUp && (
              <div>
                <label className="block text-sm font-medium text-white mb-1.5">Confirm Password</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full px-4 py-2.5 bg-transparent border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-gray-500 transition-colors"
                />
              </div>
            )}

            <button
              type="submit"
              className="w-full py-3 mt-2 !bg-white !text-black font-semibold !rounded-full hover:!bg-gray-200 transition-colors !border-0"
            >
              {isSignUp ? 'Signup' : 'Login'}
            </button>
          </form>
        </div>
      </div>
    </main>
  );
}
