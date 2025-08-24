import { NavLink, Route, Routes } from 'react-router-dom'
// import Assessment from './pages/Assessment'
// import CreateScenario from './pages/CreateScenario'
import Dashboard from './pages/Dashboard'
// import Home from './pages/Home'
import DeeperInsight from './pages/DeeperInsight'

import Timeline from './components/Timeline'
// import Wizard from './pages/Wizard'


export default function App() {
  return (
    <div className="container">
      <nav className="nav">
        <div className="brand">ConceptBridge AI</div>
          <Timeline />
        <div className="links">
          <NavLink to="/" end>Home</NavLink>
          {/* <NavLink to="/create">Create</NavLink>
          <NavLink to="/simulate">Simulate</NavLink>
          <NavLink to="/assess">Assess</NavLink> */}
          <NavLink to="/dashboard">Dashboard</NavLink>
          {/* <NavLink to="/wizard">Wizard</NavLink>*/}


        </div>
      </nav>
      <Routes>

        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/deeper-insight" element={<DeeperInsight />} />

      </Routes>
      <footer className="footer">© {new Date().getFullYear()} ConceptBridge AI</footer>
    </div>
  )
}
