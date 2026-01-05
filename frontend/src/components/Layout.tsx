import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import './Layout.css'

interface LayoutProps {
  children: ReactNode
}

function Layout({ children }: LayoutProps) {
  const location = useLocation()

  return (
    <div className="layout">
      <header className="header">
        <div className="container">
          <h1 className="logo">🎱 로또 분석 플랫폼</h1>
          <nav className="nav">
            <Link
              to="/"
              className={location.pathname === '/' ? 'active' : ''}
            >
              홈
            </Link>
            <Link
              to="/history"
              className={location.pathname === '/history' ? 'active' : ''}
            >
              당첨 이력
            </Link>
            <Link
              to="/analytics"
              className={location.pathname === '/analytics' ? 'active' : ''}
            >
              분석
            </Link>
            <Link
              to="/recommendations"
              className={location.pathname === '/recommendations' ? 'active' : ''}
            >
              추천
            </Link>
          </nav>
        </div>
      </header>
      <main className="main">
        <div className="container">
          {children}
        </div>
      </main>
      <footer className="footer">
        <div className="container">
          <p>&copy; 2024 로또 번호 분석 및 추천 플랫폼</p>
        </div>
      </footer>
    </div>
  )
}

export default Layout

