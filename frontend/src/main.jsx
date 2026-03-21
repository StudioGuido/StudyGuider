import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// ADD THIS: Import the provider you created in the context folder
import { AuthProvider } from './context/AuthContext'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    
     {/* ADD THIS: Wrap App so the auth state is shared everywhere */}
    <AuthProvider>
      <App />
    </AuthProvider>

  </StrictMode>,
)
