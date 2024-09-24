import React, { useEffect, useState } from "react";
import { getReports } from "../../api/services/reports";
import { Card, Col, Row } from "react-bootstrap";
import Navigation from "../../components/Navigation/Navigation";
import Search from "../../components/Search/Search";
import CrudButton from "../../components/Button/CrudButton";
import TableReport from "./components/TableReport";
import { getMinifiedTaxonomy } from "../../api/services/taxonomies";
import AdvancedPagination from "../../components/Pagination/AdvancedPagination";
import Alert from "../../components/Alert/Alert";
import { useTranslation } from "react-i18next";

const ListReport = () => {
  const [loading, setLoading] = useState(true);
  const [reports, setReports] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [countItems, setCountItems] = useState(0);
  const [updatePagination, setUpdatePagination] = useState(false);
  const [disabledPagination, setDisabledPagination] = useState(true);
  const [taxonomyNames, setTaxonomyNames] = useState({});

  const [showAlert, setShowAlert] = useState(false);

  const [wordToSearch, setWordToSearch] = useState("");
  const [order, setOrder] = useState("taxonomy__name");
  const { t } = useTranslation();

  function updatePage(chosenPage) {
    setCurrentPage(chosenPage);
  }

  useEffect(() => {
    getReports(currentPage, wordToSearch, order)
      .then((response) => {
        setReports(response.data.results);
        setCountItems(response.data.count);
        if (currentPage === 1) {
          setUpdatePagination(true);
        }
        setDisabledPagination(false);
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => {
        setShowAlert(true);
        setLoading(false);
      });

    getMinifiedTaxonomy().then((response) => {
      let dicTaxonomy = {};
      response.forEach((taxonomy) => {
        dicTaxonomy[taxonomy.url] = taxonomy.name;
      });
      setTaxonomyNames(dicTaxonomy);
    });
  }, [currentPage, wordToSearch, order]);

  return (
    <div>
      <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="report" />
      <Row>
        <Navigation actualPosition={t("ngen.report")} />
      </Row>
      <Card>
        <Card.Header>
          <Row>
            <Col sm={12} lg={9}>
              <Search type=".." setWordToSearch={setWordToSearch} wordToSearch={wordToSearch} setLoading={setLoading} />
            </Col>
            <Col sm={12} lg={3}>
              <CrudButton type="create" name={t("ngen.report")} to="/reports/create" checkPermRoute />
            </Col>
          </Row>
        </Card.Header>
        <Card.Body>
          <TableReport
            list={reports}
            loading={loading}
            taxonomyNames={taxonomyNames}
            order={order}
            setOrder={setOrder}
            setLoading={setLoading}
          />
        </Card.Body>
        <Card.Footer>
          <Row className="justify-content-md-center">
            <Col md="auto">
              <AdvancedPagination
                countItems={countItems}
                updatePage={updatePage}
                updatePagination={updatePagination}
                setUpdatePagination={setUpdatePagination}
                setLoading={setLoading}
                setDisabledPagination={setDisabledPagination}
                disabledPagination={disabledPagination}
              />
            </Col>
          </Row>
        </Card.Footer>
      </Card>
    </div>
  );
};

export default ListReport;
