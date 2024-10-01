import { currentUserHasPermissions } from "utils/permissions";

const PermissionCheck = ({ children, permissions }) => {
  if (!permissions) {
    return children;
  }
  if (currentUserHasPermissions([permissions])) {
    return children;
  }

  return null;
};

export default PermissionCheck;
