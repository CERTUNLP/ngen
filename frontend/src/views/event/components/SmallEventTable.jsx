import React, { useEffect, useState } from "react";
import { Button, Card, Col, Row } from "react-bootstrap";
import { getMinifiedTaxonomy } from "../../../api/services/taxonomies";
import { getMinifiedTlp } from "../../../api/services/tlp";
import { getMinifiedFeed } from "../../../api/services/feeds";
import TableEvents from "./TableEvents";
import { useTranslation } from "react-i18next";

const SmallEventTable = ({
  list,
  title,
  disableLink,
  modalListEvent,
  modalEventDetail,
  deleteEventFromForm,
  disableColumOption,
  modalEvent,
  disableMerged,
  disableUuid,
  disableColumnDelete,
  disableColumnCase
}) => {
  const [taxonomyNames, setTaxonomyNames] = useState({});
  const [feedNames, setFeedNames] = useState({});
  const [tlpNames, setTlpNames] = useState({});
  const { t } = useTranslation();

  useEffect(() => {
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
    getMinifiedTlp().then((response) => {
      let dicTlp = {};
      response.forEach((tlp) => {
        dicTlp[tlp.url] = { name: tlp.name, color: tlp.color };
      });
      setTlpNames(dicTlp);
    });
  }, []);

  return (
    <React.Fragment>
      <Card>
        <Card.Header>
          <Row>
            <Col sm={12} lg={8}>
              <Card.Title as="h5">{title || t("ngen.event_other")}</Card.Title>
            </Col>
            {disableLink ? (
              ""
            ) : (
              <Col sm={12} lg={2}>
                <Button size="lm" variant="outline-dark" onClick={() => modalEvent()}>
                  {t("button.create")} {t("ngen.event_one")}
                </Button>
              </Col>
            )}
            {disableLink ? (
              ""
            ) : (
              <Col sm={12} lg={2}>
                <Button size="lm" variant="outline-dark" onClick={() => modalListEvent()}>
                  {t("button.link")} {t("ngen.event_one")}
                </Button>
              </Col>
            )}
          </Row>
        </Card.Header>
        <Card.Body>
          {(list.length === 0) ?
            t("ngen.no_event_in_case") :

            <TableEvents
              events={list}
              taxonomyNames={taxonomyNames}
              feedNames={feedNames}
              tlpNames={tlpNames}
              disableDate={true}
              disableCheckbox={true}
              disableTemplate={true}
              deleteColumForm={true}
              disableColumnEdit={true}
              disableCheckboxAll={true}
              detailModal={false}
              modalEventDetail={modalEventDetail}
              deleteEventFromForm={deleteEventFromForm}
              disableColumOption={disableColumOption}
              disableUuid={disableUuid}
              disableDateModified={true}
              disableColumnDelete={disableColumnDelete}
              disableMerged={disableMerged}
              disableColumnCase={disableColumnCase}
            />
          }
        </Card.Body>
      </Card>
    </React.Fragment>
  );
};

export default SmallEventTable;
