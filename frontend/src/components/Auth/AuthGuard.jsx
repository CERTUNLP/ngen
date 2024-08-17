import React from 'react';
import { Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';

const AuthGuard = ({ children }) => {
  const account = useSelector((state) => state.account);
  const { isLoggedIn } = account;

  if (!isLoggedIn) {
    return <Navigate to="/login" />;
  }

  return children;
};

export default AuthGuard;
