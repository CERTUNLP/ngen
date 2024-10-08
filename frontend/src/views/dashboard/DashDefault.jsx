import React, { useEffect, useState } from "react";
import { Card, Col, Form, Row } from "react-bootstrap";
import FeedGraph from "./chart/FeedGraph";
import EntityGraph from "./chart/EntityGraph";
import DashboardEvent from "./chart/DashboardEvent";
import DashboardCases from "./chart/DashboardCases";
import {
  getDashboardCases,
  getDashboardEvent,
  getDashboardFeed,
  getDashboardNetworkEntities
} from "../../api/services/dashboards";
import { getMinifiedTaxonomy } from "../../api/services/taxonomies";
import { getMinifiedFeed } from "../../api/services/feeds";
import { useTranslation } from "react-i18next";
import { currentUserHasPermissions } from "utils/permissions";
import PermissionCheck from "components/Auth/PermissionCheck";

const DashDefault = ({ routeParams }) => {
  // TODO: Remove this when home page is implemented
  if (!currentUserHasPermissions(["view_dashboard"])) {
    return <React.Fragment></React.Fragment>;
  }

  const [dashboardFeed, setDashboardFeed] = useState([]);
  const [dashboardEvent, setDashboardEvent] = useState([]);
  const [dashboardCases, setDashboardCases] = useState([]);
  const [dashboardNetworkEntities, setDashboardNetworkEntities] = useState([]);

  // network admin
  const [myDashboardEvent, setMyDashboardEvent] = useState([]);
  const [myDashboardCases, setMyDashboardCases] = useState([]);

  const [starDate, setStarDate] = useState(getDateTimeSevenDaysAgo());
  const [endDate, setEndDate] = useState(getCurrentDateTime());
  const [starDateFilter, setStarDateFilter] = useState(getDateTimeSevenDaysAgoFilter());
  const [endDateFilter, setEndDateFilter] = useState(getCurrentDateTimeFilter());
  const [starDateNotification, setStarDateNotification] = useState(false);
  const [endDateNotification, setEndDateNotification] = useState(false);

  const [taxonomyNames, setTaxonomyNames] = useState({});
  const [feedNames, setFeedNames] = useState({});

  const [loadingCases, setLoadingCases] = useState(true);
  const [loadingEvents, setLoadingEvents] = useState(true);
  const [loadingFeeds, setLoadingFeeds] = useState(true);
  const [loadingEntities, setLoadingEntities] = useState(true);
  useEffect(() => {
    setLoadingCases(true);
    setLoadingEvents(true);
    setLoadingFeeds(true);
    setLoadingEntities(true);
    getMinifiedTaxonomy().then((response) => {
      let dicTaxonomy = {};
      response.forEach((taxonomy) => {
        dicTaxonomy[taxonomy.url] = taxonomy.name;
      });
      setTaxonomyNames(dicTaxonomy);
    });

    getMinifiedFeed().then((response) => {
      let dicFeed = {};
      response.forEach((feed) => {
        dicFeed[feed.url] = feed.name;
      });
      setFeedNames(dicFeed);
    });

    if (currentUserHasPermissions("view_dashboard")) {
      getDashboardFeed(starDateFilter + endDateFilter)
        .then((response) => {
          setDashboardFeed(response.data.feeds_in_events);
        })
        .catch(() => {
          // Show alert
        })
        .finally(() => {
          setLoadingFeeds(false);
        });

      getDashboardEvent(starDateFilter + endDateFilter)
        .then((response) => {
          setDashboardEvent(response.data.events);
        })
        .catch(() => {
          // Show alert
        })
        .finally(() => {
          setLoadingEvents(false);
        });

      getDashboardCases(starDateFilter + endDateFilter)
        .then((response) => {
          setDashboardCases(response.data.cases);
        })
        .catch(() => {})
        .finally(() => {
          setLoadingCases(false);
        });

      getDashboardNetworkEntities(starDateFilter + endDateFilter)
        .then((response) => {
          setDashboardNetworkEntities(response.data.network_entities);
        })
        .catch(() => {})
        .finally(() => {
          setLoadingEntities(false);
        });
    }

  }, [starDateFilter, endDateFilter]);
  const completeDateStar = (date) => {
    if (getCurrentDateTime() >= date && date <= endDate) {
      setStarDate(date);
      setStarDateFilter("date_from=" + date + ":00Z&");
      setStarDateNotification(false);
    } else {
      setStarDateNotification(true);
    }
  };

  const completeDateEnd = (date) => {
    if (getCurrentDateTime() >= date && date >= starDate && endDate >= starDate) {
      setEndDate(date);
      setEndDateFilter("date_to=" + date + ":00Z");
      setEndDateNotification(false);
    } else {
      setEndDateNotification(true);
    }
  };

  function getCurrentDateTime() {
    // Create a new Date instance to get the current date and time
    const now = new Date();

    // Get the year, month, day, hour, and minute
    const year = now.getUTCFullYear();
    const month = String(now.getUTCMonth() + 1).padStart(2, "0"); // Months are zero-based, so we add 1
    const day = String(now.getUTCDate()).padStart(2, "0");
    const hours = String(now.getUTCHours()).padStart(2, "0");
    const minutes = String(now.getUTCMinutes()).padStart(2, "0");

    // Format the date and time in the desired format
    const formattedDateTime = `${year}-${month}-${day}T${hours}:${minutes}`;

    return formattedDateTime;
  }

  function getDateTimeSevenDaysAgo() {
    // Create a new Date instance and set it to 7 days ago
    const now = new Date();
    now.setDate(now.getDate() - 7);

    const year = now.getUTCFullYear();
    const month = (now.getUTCMonth() + 1).toString().padStart(2, "0");
    const day = now.getUTCDate().toString().padStart(2, "0");
    const hours = now.getUTCHours().toString().padStart(2, "0");
    const minutes = now.getUTCMinutes().toString().padStart(2, "0");

    // Format the date and time in the desired format
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  }

  function getCurrentDateTimeFilter() {
    // Create a new Date instance to get the current date and time
    const now = new Date();

    const year = now.getUTCFullYear();
    const month = (now.getUTCMonth() + 1).toString().padStart(2, "0");
    const day = now.getUTCDate().toString().padStart(2, "0");
    const hours = now.getUTCHours().toString().padStart(2, "0");
    const minutes = now.getUTCMinutes().toString().padStart(2, "0");
    const seconds = now.getUTCSeconds().toString().padStart(2, "0");

    // Format the date and time in the desired format
    const formattedDateTime = `${year}-${month}-${day}T${hours}:${minutes}:${seconds}Z`;

    return "date_to=" + formattedDateTime;
  }

  function getDateTimeSevenDaysAgoFilter() {
    // Create a new Date instance to get the current date and time
    const now = new Date();

    // Subtract 7 days from the current date
    now.setDate(now.getDate() - 7);

    const year = now.getUTCFullYear();
    const month = (now.getUTCMonth() + 1).toString().padStart(2, "0");
    const day = now.getUTCDate().toString().padStart(2, "0");
    const hours = now.getUTCHours().toString().padStart(2, "0");
    const minutes = now.getUTCMinutes().toString().padStart(2, "0");
    const seconds = now.getUTCSeconds().toString().padStart(2, "0");

    // Format the date and time in the desired format
    const formattedDateTime = `${year}-${month}-${day}T${hours}:${minutes}:${seconds}Z`;

    return "date_from=" + formattedDateTime + "&";
  }

  const { t } = useTranslation();

  return (
    <React.Fragment>
      <Row>
        <Col sm={12} lg={6}>
          <Form.Group controlId="formGridAddress1">
            <Form.Label>{t("date.condition_from")}</Form.Label>
            <Form.Control
              type="datetime-local"
              maxLength="150"
              placeholder={t("date.condition_from")}
              max={getCurrentDateTime()}
              value={starDate}
              isInvalid={starDateNotification}
              onChange={(e) => completeDateStar(e.target.value)}
              name="date"
            />
            {starDateNotification ? <div className="invalid-feedback">{t("date.invalid")}</div> : ""}
          </Form.Group>
        </Col>
        <Col sm={12} lg={6}>
          <Form.Group controlId="formGridAddress1">
            <Form.Label>{t("date.condition_to")}</Form.Label>
            <Form.Control
              type="datetime-local"
              maxLength="150"
              max={getCurrentDateTime()}
              value={endDate}
              isInvalid={endDateNotification}
              onChange={(e) => completeDateEnd(e.target.value)}
              name="date"
            />
            {endDateNotification ? <div className="invalid-feedback"> {t("date.invalid")}</div> : ""}
          </Form.Group>
        </Col>
        <PermissionCheck permissions="view_dashboard">
          <Col md={6}>
            <Card>
              <Card.Header>
                <Card.Title as="h5">{t("ngen.dashboard.feeds_graphic")}</Card.Title>
              </Card.Header>
              <Card.Body className="text-center">
                <FeedGraph list={dashboardFeed} loading={loadingFeeds} />
              </Card.Body>
            </Card>
          </Col>
          <Col md={6}>
            <Card>
              <Card.Header>
                <Card.Title as="h5">{t("ngen.dashboard.entities_graphic")}</Card.Title>
              </Card.Header>
              <Card.Body className="text-center">
                <EntityGraph list={dashboardNetworkEntities} loading={loadingEntities} />
              </Card.Body>
            </Card>
          </Col>
          <Col>
            <DashboardEvent list={dashboardEvent} feedNames={feedNames} taxonomyNames={taxonomyNames} loading={loadingEvents} />
          </Col>
          <Col>
            <DashboardCases list={dashboardCases} loading={loadingCases} />
          </Col>
        </PermissionCheck>
      </Row>
    </React.Fragment>
  );
};

export default DashDefault;
