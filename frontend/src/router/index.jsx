// Optional: central router file (not used heavily here, but present for extension)
import React from 'react'
import { Routes, Route } from 'react-router-dom'

export default function AppRouter({children}){
  return <Routes>{children}</Routes>
}
