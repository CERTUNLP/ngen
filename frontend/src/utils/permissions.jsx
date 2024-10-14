import routes from "routes";
import store from "../store";

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
  rp = rp ? rp : requiredPermissions.every((perm) => userPermissions.includes(perm));
  op = optionalPermissions ? optionalPermissions.some((perm) => userPermissions.includes(perm)) : true;
  return rp && op;
};

const routePermissions = (route_path) => {
  // split route path to get the last part
  const route_path_array = route_path.split("/");
  const id = route_path_array[route_path_array.length - 1];
  // if the last part is a number, replace it with ":id"
  if (!isNaN(id)) {
    route_path_array[route_path_array.length - 1] = ":id";
  }
  route_path = route_path_array.join("/");
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

const userIsStaff = () => {
  return getCurrentUser().is_staff;
}

const userIsSuperuser = () => {
  return getCurrentUser().is_superuser;
}

const getCurrentUser = () => {
  return getCurrentAccount()?.user || {};
};

const getCurrentAccount = () => {
  const state = store.getState();
  return state.account || {};
};

export {
  currentUserHasPermissions,
  currentUserHasPermissionsRoute,
  routePermissions,
  userIsNetworkAdmin,
  getCurrentUser,
  getCurrentAccount,
  userIsStaff,
  userIsSuperuser
};
