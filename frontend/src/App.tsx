import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import History from './pages/History'
import Analytics from './pages/Analytics'
import Recommendations from './pages/Recommendations'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/history" element={<History />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/recommendations" element={<Recommendations />} />
      </Routes>
    </Layout>
  )
}

export default App

