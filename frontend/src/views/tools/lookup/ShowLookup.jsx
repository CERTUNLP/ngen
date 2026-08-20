import React, { useEffect, useState } from "react";
import { Card, Col, Row } from "react-bootstrap";
import { useLocation, useParams } from "react-router-dom";
import Alert from "components/Alert/Alert";
import FormLookup from "views/tools/lookup/FormLookup";
import { useTranslation } from "react-i18next";
import { COMPONENT_URL } from "config/constant";

const ShowLookup = () => {
    const { t } = useTranslation();

    return (
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <Card.Title as="h5">
                {t("ngen.lookup")}
              </Card.Title>
            </Card.Header>
            <Card.Body>
              <FormLookup />
            </Card.Body>
          </Card>
        </Col>
      </Row>
  );
};

export default ShowLookup;
