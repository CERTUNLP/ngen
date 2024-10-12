import React from "react";
import { Link } from "react-router-dom";
import { Breadcrumb } from "react-bootstrap";

import { BASE_URL } from "../../config/constant";

const Navigation = ({ actualPosition, path = false, index = "" }) => {
  return (
    <React.Fragment>
      <Breadcrumb>
        <Breadcrumb.Item linkAs={Link} linkProps={{ to: BASE_URL }}>
          <i className="fas fa-home" />
        </Breadcrumb.Item>
        {path ? (
          <Breadcrumb.Item linkAs={Link} linkProps={{ to: path }}>
            {index}
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
