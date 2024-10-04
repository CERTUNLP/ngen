import routes from "routes";
import store from '../store';


const currentUserHasPermissions = (requiredPermissions, optionalPermissions) => {
  let rp = false;
  let op = false;
  // Check if the user has all of the required permissions and at least one of the optional permissions
  if (requiredPermissions === "" || requiredPermissions == [] || requiredPermissions === undefined) {
    rp = true;
  }
  
  const user = getCurrentUser();
  const userPermissions = user.permissions || [];

  if (user.is_superuser) {
    return true;
  }
  if (typeof requiredPermissions === "string") {
    requiredPermissions = [requiredPermissions];
  }
  if (typeof optionalPermissions === "string") {
    optionalPermissions = [optionalPermissions];
  }
  rp = rp ? rp : requiredPermissions.every((perm) => userPermissions.includes(perm)) 
  op = optionalPermissions ? optionalPermissions.some((perm) => userPermissions.includes(perm)) : true;
  return rp && op;
};

const routePermissions = (route_path) => {
  const f = routes.filter((route) => {
    if (route.path === route_path) {
      return route;
    }
  });
  return f.length > 0 ? f[0].permissions : false;
};

const currentUserHasPermissionsRoute = (route_path) => {
  return currentUserHasPermissions(routePermissions(route_path));
};

const userIsNetworkAdmin = () => {
  return getCurrentUser().is_network_admin;
};

const getCurrentUser = () => {
  return getCurrentAccount()?.user || {};
};

const getCurrentAccount = () => {
  const state = store.getState();
  return state.account || {};
};

export { currentUserHasPermissions, currentUserHasPermissionsRoute, routePermissions, userIsNetworkAdmin, getCurrentUser, getCurrentAccount };
