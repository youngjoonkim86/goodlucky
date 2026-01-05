import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { AppDispatch, RootState } from '../store/store'
import {
  fetchRecommendations,
  fetchConfidence,
} from '../store/slices/recommendationSlice'
import './Recommendations.css'

function Recommendations() {
  const dispatch = useDispatch<AppDispatch>()
  const { recommendations, confidence, loading } = useSelector(
    (state: RootState) => state.recommendation
  )
  const [count, setCount] = useState(5)
  const [includeWeather, setIncludeWeather] = useState(true)
  const [includeEconomic, setIncludeEconomic] = useState(true)
  const [customNumbers, setCustomNumbers] = useState('')

  useEffect(() => {
    handleGenerate()
  }, [])

  const handleGenerate = () => {
    dispatch(
      fetchRecommendations({
        count,
        include_weather: includeWeather,
        include_economic: includeEconomic,
      })
    )
  }

  const handleCheckConfidence = () => {
    const numbers = customNumbers
      .split(',')
      .map((n) => parseInt(n.trim()))
      .filter((n) => !isNaN(n) && n >= 1 && n <= 45)

    if (numbers.length === 6) {
      dispatch(fetchConfidence(numbers))
    } else {
      alert('6개의 번호를 입력해주세요 (1-45)')
    }
  }

  return (
    <div className="recommendations">
      <h1>번호 추천</h1>

      <div className="controls card">
        <h2>설정</h2>
        <div className="control-group">
          <label>
            추천 개수:
            <input
              type="number"
              min="1"
              max="20"
              value={count}
              onChange={(e) => setCount(parseInt(e.target.value))}
            />
          </label>
          <label>
            <input
              type="checkbox"
              checked={includeWeather}
              onChange={(e) => setIncludeWeather(e.target.checked)}
            />
            기상 데이터 포함
          </label>
          <label>
            <input
              type="checkbox"
              checked={includeEconomic}
              onChange={(e) => setIncludeEconomic(e.target.checked)}
            />
            경제 지표 포함
          </label>
        </div>
        <button onClick={handleGenerate} className="generate-btn">
          추천 생성
        </button>
      </div>

      {loading && <div className="loading">추천 번호 생성 중...</div>}

      {recommendations.length > 0 && (
        <div className="recommendations-list">
          <h2>추천 번호</h2>
          {recommendations.map((rec, idx) => (
            <div key={idx} className="recommendation-card card">
              <div className="rec-header">
                <span className="rec-index">#{idx + 1}</span>
                <span className="confidence">
                  신뢰도: {(rec.confidence * 100).toFixed(1)}%
                </span>
              </div>
              <div className="numbers">
                {rec.numbers.map((num, i) => (
                  <span key={i} className="number">
                    {num}
                  </span>
                ))}
              </div>
              {rec.explanation && (
                <div className="explanation">{rec.explanation}</div>
              )}
              {rec.features && (
                <div className="features">
                  {Object.entries(rec.features).map(([key, value]) => (
                    <span key={key} className="feature-tag">
                      {key}: {typeof value === 'number' ? value.toFixed(2) : value}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="confidence-checker card">
        <h2>번호 신뢰도 확인</h2>
        <div className="input-group">
          <input
            type="text"
            placeholder="번호를 쉼표로 구분 (예: 1,2,3,4,5,6)"
            value={customNumbers}
            onChange={(e) => setCustomNumbers(e.target.value)}
          />
          <button onClick={handleCheckConfidence}>신뢰도 확인</button>
        </div>
        {confidence && (
          <div className="confidence-result">
            <div className="numbers">
              {confidence.numbers.map((num, i) => (
                <span key={i} className="number">
                  {num}
                </span>
              ))}
            </div>
            <div className="confidence-value">
              신뢰도: {(confidence.confidence * 100).toFixed(1)}%
            </div>
            {confidence.explanation && (
              <div className="explanation">{confidence.explanation}</div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default Recommendations

