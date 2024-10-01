// import { useSelector } from "react-redux";
import routes from "routes";

const currentUserHasPermissions = (requiredPermissions) => {
  if (requiredPermissions === "" || requiredPermissions == [] || requiredPermissions === undefined) {
    return true;
  }
  const account = localStorage.getItem("ngen-account") || {};
  const user = JSON.parse(JSON.parse(account).user) || {};
  const userPermissions = user.permissions || [];
  if (user.is_superuser) {
    return true;
  }
  if (typeof requiredPermissions === "string") {
    requiredPermissions = [requiredPermissions];
  }
  return requiredPermissions.every((perm) => userPermissions.includes(perm));
};

const routePermissions = (route_path) => {
  const f = routes.filter((route) => {
    if (route.path === route_path) {
      return route;
    }
  });
  return f.length > 0 ? f[0].permissions : [];
}

const currentUserHasPermissionsRoute = (route_path) => {
  return currentUserHasPermissions(routePermissions(route_path));
}


export { currentUserHasPermissions, currentUserHasPermissionsRoute, routePermissions };
