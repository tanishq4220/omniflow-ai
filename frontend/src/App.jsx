import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { Activity, ShieldAlert, Users, Settings, BarChart2 } from 'lucide-react'

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: BarChart2 },
  { path: '/agents', label: 'Agents', icon: Users },
  { path: '/alerts', label: 'Alerts', icon: ShieldAlert },
  { path: '/simulation', label: 'Simulation', icon: Activity },
  { path: '/admin', label: 'Admin', icon: Settings }
]

function Layout({ children }) {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-dark text-white">
      <nav className="w-64 glass border-r flex flex-col p-4 space-y-4 shadow-xl" aria-label="Sidebar">
        <h1 className="text-2xl font-bold mb-6 text-primary tracking-wide">OmniFlow AI</h1>
        {navItems.map((item) => (
          <Link key={item.path} to={item.path} className="flex items-center gap-3 p-3 rounded-lg hover:bg-card focus:ring-2 focus:ring-primary transition-all">
            <item.icon className="w-5 h-5 text-accent" aria-hidden="true" />
            <span className="font-medium">{item.label}</span>
          </Link>
        ))}
      </nav>
      <main className="flex-1 overflow-auto p-8" role="main">
        {children}
      </main>
    </div>
  )
}

function PlaceholderPage({ title }) {
  return (
    <div className="flex flex-col items-center justify-center h-full">
      <h2 className="text-4xl font-bold mb-4 glass px-8 py-4 rounded-xl">{title}</h2>
      <p className="text-gray-400">OmniFlow real-time view initializing...</p>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<PlaceholderPage title="System Dashboard" />} />
          <Route path="/dashboard" element={<PlaceholderPage title="Analytics Dashboard" />} />
          <Route path="/agents" element={<PlaceholderPage title="Multi-Agent Monitor" />} />
          <Route path="/alerts" element={<PlaceholderPage title="Live Alerts" />} />
          <Route path="/simulation" element={<PlaceholderPage title="Scenario Simulator" />} />
          <Route path="/admin" element={<PlaceholderPage title="Admin Controls" />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
