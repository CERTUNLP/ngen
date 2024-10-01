import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "react-bootstrap";
// import { Helmet } from "react-helmet";
import { logout, refreshToken } from "../../../api/services/auth";
import { useTranslation } from "react-i18next";


const Unauthorized = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  return (
    <div className="container">
      {/* <Helmet title="Unauthorized" /> */}
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="text-center">
            <h1 className="display-1">401</h1>
            <h2>Unauthorized</h2>
            <p>You do not have permission to view this resource.</p>
            <Link to="/metrics">Go back to dashboard</Link>
            <br />
            <br />
            <Button onClick={()=> {logout(); navigate('/login')}}>Logout</Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Unauthorized;
