import React from 'react'
import { Line } from 'react-chartjs-2'
import { Chart as ChartJS, LineElement, CategoryScale, LinearScale, PointElement, Filler, Tooltip, Legend } from 'chart.js'

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Filler, Tooltip, Legend)

export default function TrendChart({ data }) {
  const chartData = {
    labels: data?.labels || ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: data?.datasets || [
      {
        label: 'Low',
        fill: true,
        tension: 0.5, // Smooth spline curve
        data: [45, 50, 48, 52, 55, 53],
        backgroundColor: 'rgba(0, 229, 255, 0.15)',
        borderColor: '#00E5FF',
        borderWidth: 3,
        pointRadius: 0, // No points for cleaner look
        pointHoverRadius: 6,
        pointBackgroundColor: '#00E5FF',
        pointBorderColor: '#00E5FF',
        pointBorderWidth: 2,
        pointHoverBackgroundColor: '#00E5FF',
        pointHoverBorderColor: '#00E5FF',
        pointHoverBorderWidth: 3,
      },
      {
        label: 'Medium',
        fill: true,
        tension: 0.5, // Smooth spline curve
        data: [25, 28, 30, 28, 26, 28],
        backgroundColor: 'rgba(168, 85, 247, 0.15)',
        borderColor: '#A855F7',
        borderWidth: 3,
        pointRadius: 0, // No points for cleaner look
        pointHoverRadius: 6,
        pointBackgroundColor: '#A855F7',
        pointBorderColor: '#A855F7',
        pointBorderWidth: 2,
        pointHoverBackgroundColor: '#A855F7',
        pointHoverBorderColor: '#00E5FF',
        pointHoverBorderWidth: 3,
      },
      {
        label: 'High',
        fill: true,
        tension: 0.5, // Smooth spline curve
        data: [10, 12, 11, 13, 12, 13],
        backgroundColor: 'rgba(255, 79, 107, 0.15)',
        borderColor: '#FF4F6B',
        borderWidth: 3,
        pointRadius: 0, // No points for cleaner look
        pointHoverRadius: 6,
        pointBackgroundColor: '#FF4F6B',
        pointBorderColor: '#FF4F6B',
        pointBorderWidth: 2,
        pointHoverBackgroundColor: '#FF4F6B',
        pointHoverBorderColor: '#00E5FF',
        pointHoverBorderWidth: 3,
      }
    ]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      intersect: false,
      mode: 'index',
    },
    plugins: {
      legend: {
        display: true,
        position: 'bottom',
        align: 'center',
        labels: {
          color: '#bfefff',
          padding: 16,
          font: {
            size: 12,
            weight: '500',
            family: '"Inter", sans-serif'
          },
          usePointStyle: true,
          pointStyle: 'circle',
          boxWidth: 8,
          boxHeight: 8,
        }
      },
      tooltip: {
        backgroundColor: 'rgba(10, 20, 40, 0.98)',
        titleColor: '#dfefff',
        bodyColor: '#9fcbdc',
        borderColor: 'rgba(0, 255, 255, 0.4)',
        borderWidth: 1.5,
        padding: 14,
        cornerRadius: 10,
        displayColors: true,
        titleFont: {
          size: 13,
          weight: '600',
          family: '"Inter", sans-serif'
        },
        bodyFont: {
          size: 12,
          family: '"Inter", sans-serif'
        },
        boxPadding: 6,
        backdropFilter: 'blur(10px)',
        callbacks: {
          label: function(context) {
            return `${context.dataset.label}: ${context.parsed.y}%`;
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          display: true,
          color: 'rgba(157, 183, 198, 0.1)',
          drawBorder: false,
        },
        ticks: {
          color: '#9db7c6',
          font: {
            size: 12,
            weight: '500',
            family: '"Inter", sans-serif'
          },
          padding: 8,
        },
        border: {
          display: false,
        }
      },
      y: {
        grid: {
          color: 'rgba(157, 183, 198, 0.1)',
          drawBorder: false,
        },
        ticks: {
          color: '#9db7c6',
          font: {
            size: 12,
            weight: '500',
            family: '"Inter", sans-serif'
          },
          padding: 8,
        },
        border: {
          display: false,
        },
        beginAtZero: true,
        max: 80,
      }
    },
    elements: {
      line: {
        borderJoinStyle: 'round',
        borderCapStyle: 'round',
      }
    }
  }

  return (
    <div className="chart-wrapper">
      <Line data={chartData} options={options} />
    </div>
  )
}
