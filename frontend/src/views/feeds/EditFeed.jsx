import React, { useEffect, useState } from "react";
import { Card, Col, Row } from "react-bootstrap";
import { useLocation, useParams } from "react-router-dom";
import Alert from "../../components/Alert/Alert";
import { getFeed, putFeed } from "../../api/services/feeds";
import Navigation from "../../components/Navigation/Navigation";
import FormFeed from "./components/FormFeed";
import { useTranslation } from "react-i18next";
import { COMPONENT_URL } from "config/constant";

const EditFeed = () => {
  const [url, setUrl] = useState("");
  const [name, setName] = useState("");
  const [active, setActive] = useState(true);
  const [description, setDescription] = useState("");
  const [showAlert, setShowAlert] = useState(false);
  const [id, setId] = useState(useParams());
  const [feed, setFeed] = useState({});
  const { t } = useTranslation();

  useEffect(() => {
    if (id.id) {
      getFeed(COMPONENT_URL.feed + id.id + "/")
        .then((response) => {
          setFeed(response.data);
        })
        .catch((error) => console.log(error));
    }
  }, [id]);

  useEffect(() => {
    if (feed) {
      setUrl(feed.url);
      setName(feed.name);
      setActive(feed.active);
      setDescription(feed.description);
    }
  }, [feed]);

  const editFeed = () => {
    putFeed(url, name, description, active)
      .then(() => {
        window.location.href = "/feeds";
      })
      .catch((error) => {
        setShowAlert(true);
        console.log(error);
      });
  };

  const resetShowAlert = () => {
    setShowAlert(false);
  };

  return (
    <React.Fragment>
      <Alert showAlert={showAlert} resetShowAlert={resetShowAlert} component="feed" />
      <Row>
        <Navigation actualPosition={t("ngen.feed.information.edit")} path="/feeds" index={t("ngen.feed.information")} />
      </Row>
      <Row>
        <Col sm={12}>
          <Card>
            <Card.Header>
              <Card.Title as="h5">{t("ngen.feed.information")}</Card.Title>
            </Card.Header>
            <Card.Body>
              <FormFeed
                name={name}
                setName={setName}
                active={active}
                setActive={setActive}
                description={description}
                setDescription={setDescription}
                createFeed={editFeed}
              />
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </React.Fragment>
  );
};

export default EditFeed;
