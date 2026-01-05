import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { AppDispatch, RootState } from '../store/store'
import {
  fetchFrequency,
  fetchPatterns,
  fetchVariables,
} from '../store/slices/analyticsSlice'
import { Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import './Analytics.css'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

function Analytics() {
  const dispatch = useDispatch<AppDispatch>()
  const { frequency, patterns, variables, loading } = useSelector(
    (state: RootState) => state.analytics
  )

  useEffect(() => {
    dispatch(fetchFrequency(45))
    dispatch(fetchPatterns())
    dispatch(fetchVariables())
  }, [dispatch])

  if (loading) {
    return <div className="loading">로딩 중...</div>
  }

  const frequencyChartData = frequency?.frequency
    ? {
        labels: Object.keys(frequency.frequency).map(
          (k) => frequency.frequency[k].number
        ),
        datasets: [
          {
            label: '출현 빈도',
            data: Object.keys(frequency.frequency).map(
              (k) => frequency.frequency[k].count
            ),
            backgroundColor: 'rgba(102, 126, 234, 0.6)',
            borderColor: 'rgba(102, 126, 234, 1)',
            borderWidth: 1,
          },
        ],
      }
    : null

  return (
    <div className="analytics">
      <h1>데이터 분석</h1>

      {frequency && frequencyChartData && (
        <div className="card">
          <h2>번호별 출현 빈도</h2>
          <div className="chart-container">
            <Bar
              data={frequencyChartData}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    display: false,
                  },
                  title: {
                    display: true,
                    text: '번호별 출현 횟수',
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                  },
                },
              }}
            />
          </div>
        </div>
      )}

      {patterns && (
        <div className="patterns-grid">
          <div className="card">
            <h3>패턴 분석</h3>
            <div className="pattern-item">
              <span>연속 번호 출현 비율:</span>
              <strong>
                {(patterns.consecutive_frequency * 100).toFixed(1)}%
              </strong>
            </div>
            <div className="pattern-item">
              <span>평균 홀수 개수:</span>
              <strong>{patterns.avg_odd_count?.toFixed(2)}개</strong>
            </div>
            <div className="pattern-item">
              <span>평균 합계:</span>
              <strong>{patterns.avg_sum?.toFixed(0)}</strong>
            </div>
            {patterns.sum_range && (
              <div className="pattern-item">
                <span>합계 범위:</span>
                <strong>
                  {patterns.sum_range.min} ~ {patterns.sum_range.max}
                </strong>
              </div>
            )}
          </div>
        </div>
      )}

      {variables && (
        <div className="card">
          <h2>환경변수 분석</h2>
          <div className="variables-info">
            <div>
              <strong>분석 기간:</strong> {variables.period?.start} ~{' '}
              {variables.period?.end}
            </div>
            <div>
              <strong>데이터 건수:</strong> 로또 {variables.data_counts?.lotto_draws}회,
              기상 {variables.data_counts?.weather_records}건, 경제{' '}
              {variables.data_counts?.economic_records}건
            </div>
            {variables.weather_analysis && (
              <div className="weather-analysis">
                <h3>기상 분석</h3>
                <div>평균 기온: {variables.weather_analysis.avg_temp?.toFixed(1)}°C</div>
                <div>
                  평균 습도: {variables.weather_analysis.avg_humidity?.toFixed(1)}%
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default Analytics

