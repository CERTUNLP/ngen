import React from "react";
import { Navigate } from "react-router-dom";
import { currentUserHasPermissions, userIsNetworkAdmin } from "../../utils/permissions";

const Home = () => {
  if (currentUserHasPermissions(["view_dashboard"])) {
    return <Navigate to="/metrics" />;
  } else if (userIsNetworkAdmin()) {
    return <Navigate to="/networkadmin/events" />;
  }
  console.log("You are not a network admin or do not have permission to view the dashboard");
};

export default Home;
