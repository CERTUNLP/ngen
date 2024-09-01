import React from "react";
import { Link } from "react-router-dom";
import { Breadcrumb } from "react-bootstrap";

const Navigation = ({ actualPosition, path = false, index = "" }) => {
  return (
    <React.Fragment>
      <Breadcrumb>
        <Breadcrumb.Item>
          <Link to="/app/dashboard/default">
            <i className="fas fa-home" />
          </Link>
        </Breadcrumb.Item>
        {path ? (
          <Breadcrumb.Item>
            <Link to={path}>{index}</Link>
          </Breadcrumb.Item>
        ) : (
          ""
        )}
        <Breadcrumb.Item active>
          <b>{actualPosition}</b>
        </Breadcrumb.Item>
      </Breadcrumb>
    </React.Fragment>
  );
};

export default Navigation;
