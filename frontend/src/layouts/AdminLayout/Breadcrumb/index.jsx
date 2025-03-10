import React, { useEffect, useState } from "react";
import { ListGroup } from "react-bootstrap";
import { Link, useLocation } from "react-router-dom";

import navigation from "../../../menu-items";
import { BASE_TITLE } from "../../../config/constant";

import { useTranslation } from "react-i18next";

const Breadcrumb = () => {
  const location = useLocation();
  const { t } = useTranslation();

  const [main, setMain] = useState([]);
  const [item, setItem] = useState([]);

  useEffect(() => {
    navigation.items.map((item, index) => {
      if (item.type && item.type === "group") {
        getCollapse(item, index);
      }
      return false;
    });
  });

  const getCollapse = (item, index) => {
    if (item.children) {
      item.children.filter((collapse) => {
        if (collapse.type && collapse.type === "collapse") {
          getCollapse(collapse, index);
        } else if (collapse.type && collapse.type === "item") {
          if (location.pathname.startsWith(collapse.url)) {
            setMain(item);
            setItem(collapse);
          }
        }
        return false;
      });
    }
  };

  let mainContent, itemContent;
  let breadcrumbContent = "";
  let title = "";
  let method = "";
  let methodContent = "";

  if (main && main.type === "collapse") {
    mainContent = (
      <ListGroup.Item as="li" bsPrefix=" " className="breadcrumb-item">
        <Link to="#">{main.title ? t(main.title) : ""}</Link>
      </ListGroup.Item>
    );
  }

  if (item && item.type === "item") {
    title = item.title ? t(item.title) : "";
    let fullpath = location.pathname;
    // check if last part of the path is a number
    let lastPart = fullpath.split("/").pop();
    let path_up = fullpath.split("/");
    path_up.pop();
    if (!isNaN(lastPart)) {
      fullpath = fullpath.substring(0, fullpath.lastIndexOf("/"));
      path_up.pop();
    }


    if (fullpath.includes("/edit")) {
      method = t("w.edit");
    } else if (fullpath.includes("/create")) {
      method = t("w.create");
    } else if (fullpath.includes("/view")) {
      method = t("w.detail");
    }

    if (method === "") {
      itemContent = (
        <ListGroup.Item as="li" bsPrefix=" " className="breadcrumb-item">
          <Link to="#">{title}</Link>
        </ListGroup.Item>
      );
    } else {

      itemContent = (
        <ListGroup.Item as="li" bsPrefix=" " className="breadcrumb-item">
          <Link to={path_up.join("/")}>{title}</Link>
        </ListGroup.Item>
      );
      methodContent = (
        <ListGroup.Item as="li" bsPrefix=" " className="breadcrumb-item">
          <Link to="#">{method}</Link>
        </ListGroup.Item>
      );
    }

    if (item.breadcrumbs !== false) {
      breadcrumbContent = (
        <div className="page-header">
          <div className="page-block">
            <div className="row align-items-center">
              <div className="col-md-12">
                <div className="page-header-title">
                  {/* <h5 className="m-b-10">{title}</h5> */}
                </div>
                <ListGroup as="ul" bsPrefix=" " className="breadcrumb">
                  <ListGroup.Item as="li" bsPrefix=" " className="breadcrumb-item">
                    <Link to="/">
                      <i className="feather icon-home" />
                    </Link>
                  </ListGroup.Item>
                  {mainContent}
                  {itemContent}
                  {methodContent}
                </ListGroup>
              </div>
            </div>
          </div>
        </div>
      );
    }

    document.title = title + BASE_TITLE;
  }

  return <React.Fragment>{breadcrumbContent}</React.Fragment>;
};

export default Breadcrumb;
