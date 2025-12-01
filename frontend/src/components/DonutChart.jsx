import React from 'react'
import { Doughnut } from 'react-chartjs-2'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

export default function DonutChart({ data }) {
  const chartData = {
    labels: data?.labels || ['Low', 'Medium', 'High'],
    datasets: [{
      data: data?.values || [53, 34, 13],
      backgroundColor: [
        'rgba(0, 229, 255, 0.9)',
        'rgba(168, 85, 247, 0.9)',
        'rgba(255, 79, 107, 0.9)'
      ],
      borderColor: [
        '#00E5FF',
        '#A855F7',
        '#FF4F6B'
      ],
      borderWidth: 5, // Thick neon ring
      hoverBorderWidth: 6,
      hoverOffset: 8,
    }]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '65%',
    plugins: {
      legend: {
        position: 'bottom',
        align: 'center',
        labels: {
          color: '#bfefff',
          padding: 18,
          font: {
            size: 12,
            weight: '500',
            family: '"Inter", sans-serif'
          },
          usePointStyle: true,
          pointStyle: 'circle',
          boxWidth: 10,
          boxHeight: 10,
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
            const label = context.label || ''
            const value = context.parsed || 0
            const total = context.dataset.data.reduce((a, b) => a + b, 0)
            const percentage = ((value / total) * 100).toFixed(1)
            return `${label}: ${percentage}% (${value})`
          }
        }
      }
    }
  }

  return (
    <div className="chart-wrapper-small">
      <Doughnut data={chartData} options={options} />
    </div>
  )
}
