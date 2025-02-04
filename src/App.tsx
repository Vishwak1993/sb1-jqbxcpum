import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AnalyticsProvider } from './components/providers/AnalyticsProvider';
import { AuthProvider } from './components/providers/AuthProvider';
import { Layout } from './components/Layout';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { ForgotPassword } from './pages/ForgotPassword';
import { Notes } from './pages/Notes';
import { ProtectedRoute } from './components/ProtectedRoute';

function App() {
  return (
    <Router>
      <AnalyticsProvider>
        <AuthProvider>
          <Layout>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/" element={
                <ProtectedRoute>
                  <Notes />
                </ProtectedRoute>
              } />
            </Routes>
          </Layout>
        </AuthProvider>
      </AnalyticsProvider>
    </Router>
  );
}

export default App;