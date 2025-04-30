import React, { useState, useEffect } from "react";
import { Row, Spinner, Table, Modal, Col, Card, CloseButton } from "react-bootstrap";
import CrudButton from "../../../components/Button/CrudButton";
import ModalConfirm from "../../../components/Modal/ModalConfirm";
import DateShowField from "../../../components/Field/DateShowField";
import { useTranslation } from "react-i18next";
import { getTaxonomy } from "../../../api/services/taxonomies";
import { deleteAnalyzerMapping, getAnalyzerMapping } from "../../../api/services/analyzerMapping";

const TableAnalyzerMapping = ({ list, loading, order, setOrder, setLoading }) => {
  const [modalDelete, setModalDelete] = useState(false);
  const [modalShow, setModalShow] = useState(false);
  const [selectedMapping, setSelectedMapping] = useState(null);
  const [url, setUrl] = useState(null);
  const [taxonomyNames, setTaxonomyNames] = useState({});
  const { t } = useTranslation();

  useEffect(() => {
    const fetchTaxonomyNames = async () => {
        const names = {};
        for (const mapping of list) {
            try {
                const response = await getTaxonomy(mapping.mapping_from);
                names[mapping.mapping_from] = response.data.name;
            } catch (error) {
                console.error("Error fetching taxonomy name:", error);
                names[mapping.mapping_from] = t("ngen.error");
            }
        }
        setTaxonomyNames(names); 
    };

    fetchTaxonomyNames();
  }, [list]);

  if (loading) {
    return (
      <Row className="justify-content-md-center">
        <Spinner animation="border" variant="primary" />
      </Row>
    );
  }

  const handleClose = () => setModalShow(false);

  const showAnalyzerMapping = (url) => {
    getAnalyzerMapping(url)
      .then((response) => {
        setSelectedMapping({
          ...response.data,
          mapping_from_name: taxonomyNames[response.data.mapping_from],
        });
        setModalShow(true);
      })
      .catch((error) => {
        console.error("Error fetching analyzer mapping details:", error);
      });
  };

  const deleteMapping = (url) => {
    deleteAnalyzerMapping(url, selectedMapping?.mapping_from_name, selectedMapping?.mapping_to, selectedMapping?.analyzer_type)
      .then(() => {
        setLoading(true);
        setModalDelete(false);
      })
      .catch((error) => {
        console.error("Error deleting analyzer mapping:", error);
      });
  };

  return (
    <React.Fragment>
      <Table responsive hover className="text-center">
        <thead>
          <tr>
            <th>{t("ngen.analyzer_mapping.mapping_from")}</th>
            <th>{t("ngen.analyzer_mapping.mapping_to")}</th>
            <th>{t("ngen.analyzer_mapping.analyzer_type")}</th>
            <th>{t("ngen.date.created")}</th>
            <th>{t("ngen.options")}</th>
          </tr>
        </thead>
        <tbody>
          {list.map((mapping, index) => {
            const parts = mapping.url.split("/");
            let itemNumber = parts[parts.length - 2];
            return (
              <tr key={index}>
                <td>{taxonomyNames[mapping.mapping_from]}</td>
                <td>{mapping.mapping_to}</td>
                <td>{mapping.analyzer_type}</td>
                <td>
                  <DateShowField value={mapping.created} />
                </td>
                <td>
                  <CrudButton type="read" onClick={() => showAnalyzerMapping(mapping.url)} />
                  <CrudButton type="edit" to={`/analyzermappings/edit/${itemNumber}`} checkPermRoute />
                  <CrudButton type="delete" onClick={() => { setSelectedMapping(mapping); setUrl(mapping.url); setModalDelete(true); }} />
                </td>
              </tr>
            );
          })}
        </tbody>
      </Table>

      {/* Modal for Viewing Details */}
      <Modal size="lg" show={modalShow} onHide={handleClose} centered>
        <Modal.Body>
          <Row>
            <Col>
              <Card>
                <Card.Header>
                  <Row>
                    <Col>
                      <Card.Title as="h5">{t("ngen.analyzer_mapping.details")}</Card.Title>
                    </Col>
                    <Col sm={12} lg={2}>
                      <CloseButton aria-label={t("w.close")} onClick={handleClose} />
                    </Col>
                  </Row>
                </Card.Header>
                <Card.Body>
                  <Table responsive>
                    <tbody>
                      <tr>
                        <td>{t("ngen.analyzer_mapping.mapping_from")}</td>
                        <td>{selectedMapping?.mapping_from_name}</td>
                      </tr>
                      <tr>
                        <td>{t("ngen.analyzer_mapping.mapping_to")}</td>
                        <td>{selectedMapping?.mapping_to}</td>
                      </tr>
                      <tr>
                        <td>{t("ngen.analyzer_mapping.analyzer_type")}</td>
                        <td>{selectedMapping?.analyzer_type}</td>
                      </tr>
                      <tr>
                        <td>{t("ngen.date.created")}</td>
                        <td>{selectedMapping?.created}</td>
                      </tr>
                      <tr>
                        <td>{t("ngen.date.modified")}</td>
                        <td>{selectedMapping?.modified}</td>
                      </tr>
                    </tbody>
                  </Table>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Modal.Body>
      </Modal>

      {/* Modal for Confirming Deletion */}
      <ModalConfirm
        type="delete"
        component={t("ngen.analyzer_mapping")}
        name={`${taxonomyNames[selectedMapping?.mapping_from]} to ${selectedMapping?.mapping_to} mapping`}
        showModal={modalDelete}
        onHide={() => setModalDelete(false)}
        ifConfirm={() => deleteMapping(url)}
      />
    </React.Fragment>
  );
};

export default TableAnalyzerMapping;