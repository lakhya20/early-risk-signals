import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const RiskChart = ({ data = [] }) => {
  const chartData = {
    labels: data.map((d) => d.date || d.day || ''),
    datasets: [
      {
        label: 'High Risk Count',
        data: data.map((d) => d.value || d.highRisk || 0),
        fill: true,
        backgroundColor: 'rgba(0, 229, 255, 0.1)',
        borderColor: '#00E5FF',
        borderWidth: 2,
        tension: 0.4,
        pointRadius: 4,
        pointBackgroundColor: '#00E5FF',
        pointBorderColor: '#0A0F1A',
        pointBorderWidth: 2,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(10, 15, 26, 0.9)',
        titleColor: '#E4E7EB',
        bodyColor: '#9CA3AF',
        borderColor: 'rgba(0, 229, 255, 0.3)',
        borderWidth: 1,
        padding: 12,
        cornerRadius: 8,
      },
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(255, 255, 255, 0.05)',
        },
        ticks: {
          color: '#9CA3AF',
        },
      },
      y: {
        grid: {
          color: 'rgba(255, 255, 255, 0.05)',
        },
        ticks: {
          color: '#9CA3AF',
        },
      },
    },
  }

  return (
    <div className="chart-wrapper">
      <Line data={chartData} options={options} />
    </div>
  )
}

export default RiskChart

