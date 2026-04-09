import React from 'react'

export default function ChartPlaceholder({title}){
  return (
    <div className="bg-white rounded-xl shadow p-4 h-64 flex items-center justify-center text-gray-400">
      {title || 'Chart'}
    </div>
  )
}
