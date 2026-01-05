import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { AppDispatch, RootState } from '../store/store'
import { fetchLatest, fetchStatistics } from '../store/slices/lottoSlice'
import './Home.css'

function Home() {
  const dispatch = useDispatch<AppDispatch>()
  const { latest, statistics, loading } = useSelector(
    (state: RootState) => state.lotto
  )

  useEffect(() => {
    dispatch(fetchLatest())
    dispatch(fetchStatistics())
  }, [dispatch])

  if (loading) {
    return <div className="loading">로딩 중...</div>
  }

  return (
    <div className="home">
      <h1>로또 번호 분석 및 추천 플랫폼</h1>
      <p className="subtitle">
        환경변수를 고려한 데이터 기반 로또 번호 분석 및 추천 서비스
      </p>

      {latest && (
        <div className="latest-draw card">
          <h2>최신 당첨 정보</h2>
          <div className="draw-info">
            <div className="draw-header">
              <span className="draw-no">제 {latest.draw_no}회</span>
              <span className="draw-date">{latest.draw_date}</span>
            </div>
            <div className="numbers">
              {latest.numbers.map((num, idx) => (
                <span key={idx} className="number">
                  {num}
                </span>
              ))}
              <span className="bonus">+ {latest.bonus}</span>
            </div>
            <div className="draw-details">
              <div>
                <strong>1등 당첨자:</strong> {latest.first_prize_winners}명
              </div>
              <div>
                <strong>1등 당첨금:</strong>{' '}
                {latest.first_prize_amount.toLocaleString()}원
              </div>
            </div>
          </div>
        </div>
      )}

      {statistics && (
        <div className="statistics-grid">
          <div className="card">
            <h3>통계 요약</h3>
            <div className="stat-item">
              <span>총 추첨 횟수:</span>
              <strong>{statistics.total_draws}회</strong>
            </div>
            {statistics.most_frequent_numbers && (
              <div className="stat-item">
                <span>자주 나온 번호 (상위 5개):</span>
                <div className="frequent-numbers">
                  {statistics.most_frequent_numbers
                    .slice(0, 5)
                    .map((item: [number, number]) => (
                      <span key={item[0]} className="number small">
                        {item[0]}
                      </span>
                    ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default Home

