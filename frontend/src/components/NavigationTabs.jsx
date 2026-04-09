import React from 'react'

export default function NavigationTabs({value, onChange}){
  const tabs = ['Сегодня','Неделя','Месяц','Год']
  return (
    <div className="inline-flex bg-gray-200 rounded-full p-1">
      {tabs.map(t=> (
        <button key={t} onClick={()=>onChange?.(t)} className={'px-3 py-1 rounded-full text-sm ' + (t===value? 'bg-white shadow' : 'text-gray-600')}>{t}</button>
      ))}
    </div>
  )
}
