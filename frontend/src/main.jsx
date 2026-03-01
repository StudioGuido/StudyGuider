import { StrictMode } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './pages/App.jsx'
import ParameterCreation from './pages/ParameterCreation'
import Summary from './pages/Summary.jsx'
import Test from './pages/Test.jsx'
import TestResults from './pages/TestResults.jsx'
import Admin from './pages/Admin.jsx'
import Auth from './pages/Auth.jsx'
import SignUp from './pages/SignUp.jsx'

createRoot(document.getElementById('root')).render(
    <StrictMode>
        <Router>
            <Routes>
                <Route path="/" element={<App />} />
                <Route path="/parameter_creation" element={<ParameterCreation />} />
                <Route path="/summary" element={<Summary />} />
                <Route path="/test" element={<Test />} />
                <Route path="/results" element={<TestResults />} />
                <Route path="/admin" element={<Admin /> } />
                <Route path="/auth" element={<Auth /> } />
                <Route path="/signup" element={<SignUp />} />
            </Routes>
        </Router>
    </StrictMode>,
)
