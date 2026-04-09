import React, {useEffect} from 'react'
import { useNavigate } from 'react-router-dom'

export default function Splash(){
  const nav = useNavigate()
  useEffect(()=>{
    const t = setTimeout(()=> nav('/login'), 800)
    return ()=> clearTimeout(t)
  },[])
  return (
    <div className="flex items-center justify-center h-[70vh]">
      <div className="bg-white rounded-2xl p-10 shadow text-center">
        <div className="text-6xl mb-2">📈</div>
        <h1 className="text-2xl font-bold mb-2">FinanceTrack</h1>
        <div className="mt-4">Загрузка...</div>
      </div>
    </div>
  )
}
