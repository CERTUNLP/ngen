import { currentUserHasPermissions } from "utils/permissions";

const PermissionCheck = ({ children, permissions, optionalPermissions }) => {
  if (!permissions && !optionalPermissions) {
    return children;
  }

  if (currentUserHasPermissions(permissions, optionalPermissions)) {
    return children;
  }

  return null;
};

export default PermissionCheck;
