import { NavLink, Route, Routes } from 'react-router-dom'
import Assessment from './pages/Assessment'
import CreateScenario from './pages/CreateScenario'
import Dashboard from './pages/Dashboard'
import Home from './pages/Home'
import Simulation from './pages/Simulation'

import Timeline from './components/Timeline'
import Wizard from './pages/Wizard'


export default function App() {
  return (
    <div className="container">
      <nav className="nav">
        <div className="brand">ConceptBridge AI</div>
        <div className="links">
          <NavLink to="/" end>Home</NavLink>
          <NavLink to="/create">Create</NavLink>
          <NavLink to="/simulate">Simulate</NavLink>
          <NavLink to="/assess">Assess</NavLink>
          <NavLink to="/dashboard">Dashboard</NavLink>
          <NavLink to="/wizard">Wizard</NavLink>
          <NavLink to="/timeline">Timeline</NavLink>

        </div>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/create" element={<CreateScenario />} />
        <Route path="/simulate" element={<Simulation />} />
        <Route path="/assess" element={<Assessment />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/wizard" element={<Wizard />} />
        <Route path="/timeline" element={<Timeline />} />

      </Routes>
      <footer className="footer">© {new Date().getFullYear()} ConceptBridge AI</footer>
    </div>
  )
}
