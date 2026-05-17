import { Route, Routes } from 'react-router'
import './index.css'
import Home from './pages/Home'
import QueryResponse from './pages/QueryResponse'

function App() {
  return (
   <>
    <Routes>
      <Route path='/' element={<Home />} />
      <Route path='/response' element={<QueryResponse />} />
    </Routes>
   </>
  )
}

export default App
