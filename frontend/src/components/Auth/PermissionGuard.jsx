import React from "react";
import { Navigate } from "react-router-dom";
import { useSelector } from "react-redux";

const PermissionGuard = ({ permissions = [], children }) => {
  const account = useSelector((state) => state.account);
  const { isLoggedIn, user } = account;
  const userPermissions = user?.permissions || [];
  const isSuperAdmin = user?.is_superuser || false;
  const isStaff = user?.is_staff || false;

  if (!isLoggedIn) {
    return <Navigate to="/login" />;
  }

  const hasPermission = permissions.every((perm) => userPermissions.includes(perm));

  if (!isSuperAdmin && !isStaff && !hasPermission) {
    return <Navigate to="/unauthorized" />;
  }

  return children;
};

export default PermissionGuard;
