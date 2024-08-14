import React from 'react'
import { Navigate } from 'react-router-dom'
import { useSelector } from 'react-redux'
import { BASE_URL } from '../../config/constant'

const GuestGuard = ({ children }) => {
  const account = useSelector((state) => state.account)
  const { isLoggedIn } = account

  if (isLoggedIn) {
    return <Navigate to={BASE_URL}/>
  }

  return <React.Fragment>{children}</React.Fragment>
}

export default GuestGuard
