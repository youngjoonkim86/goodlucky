import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { AppDispatch, RootState } from '../store/store'
import { fetchHistory } from '../store/slices/lottoSlice'
import './History.css'

function History() {
  const dispatch = useDispatch<AppDispatch>()
  const { draws, loading } = useSelector((state: RootState) => state.lotto)
  const [page, setPage] = useState(1)
  const limit = 20

  useEffect(() => {
    dispatch(fetchHistory({ skip: (page - 1) * limit, limit }))
  }, [dispatch, page])

  if (loading) {
    return <div className="loading">로딩 중...</div>
  }

  return (
    <div className="history">
      <h1>당첨 이력</h1>
      <div className="draws-list">
        {draws.map((draw) => (
          <div key={draw.id} className="draw-card card">
            <div className="draw-header">
              <span className="draw-no">제 {draw.draw_no}회</span>
              <span className="draw-date">{draw.draw_date}</span>
            </div>
            <div className="numbers">
              {draw.numbers.map((num, idx) => (
                <span key={idx} className="number">
                  {num}
                </span>
              ))}
              <span className="bonus">+ {draw.bonus}</span>
            </div>
            <div className="draw-details">
              <div>1등: {draw.first_prize_winners}명</div>
              <div>{draw.first_prize_amount.toLocaleString()}원</div>
            </div>
          </div>
        ))}
      </div>
      <div className="pagination">
        <button
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page === 1}
        >
          이전
        </button>
        <span>페이지 {page}</span>
        <button
          onClick={() => setPage((p) => p + 1)}
          disabled={draws.length < limit}
        >
          다음
        </button>
      </div>
    </div>
  )
}

export default History

