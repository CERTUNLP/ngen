import React, { useEffect, useState } from "react";
import { Card, Col, Form, Row, Spinner, Table } from "react-bootstrap";
import Alert from "../../components/Alert/Alert";
import { getTLP } from "../../api/services/tlp";
import Search from "../../components/Search/Search";
import Ordering from "../../components/Ordering/Ordering";
import { useTranslation } from "react-i18next";

const ListTLP = () => {
  const { t } = useTranslation();
  const [tlp, setTLP] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAlert, setShowAlert] = useState(false);
  const [wordToSearch, setWordToSearch] = useState("");

  const [order, setOrder] = useState("");

  const textareaStyle = {
    resize: "none",
    backgroundColor: "transparent",
    border: "none",
    boxShadow: "none"
  };

  useEffect(() => {
    getTLP(wordToSearch, order)
      .then((response) => {
        setTLP(response.data.results);
      })
      .catch((error) => {
        console.log(error);
        setShowAlert(true);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [wordToSearch, order]);

  const resetShowAlert = () => {
    setShowAlert(false);
  };

  const letterSize = { fontSize: "1.1em" };

  return (
    <React.Fragment>
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <Row>
                <Col>
                  <div className="input-group">
                    <Search
                      type={t("search.bycode")}
                      setWordToSearch={setWordToSearch}
                      wordToSearch={wordToSearch}
                      setLoading={setLoading}
                    />
                  </div>
                </Col>
              </Row>
            </Card.Header>
            <Card.Body>
              <Table responsive hover className="text-center">
                <thead>
                  <tr>
                    <Ordering
                      field="code"
                      label={t("ngen.tlp.code")}
                      order={order}
                      setOrder={setOrder}
                      setLoading={setLoading}
                      letterSize={letterSize}
                    />
                    <th style={letterSize}>{t("ngen.description")}</th>
                    <th style={letterSize}>{t("when.use")}</th>
                    <th style={letterSize}>{t("when.share")}</th>
                  </tr>
                </thead>
                <tbody>
                  {loading && (
                    <tr>
                      <td colSpan="4">
                        <Spinner animation="border" variant="primary" size="sm" />
                      </td>
                    </tr>
                  )}
                  {tlp.map((item) => {
                    const parts = item.url.split("/");
                    let itemNumber = parts[parts.length - 2];

                    return (
                      <tr key={itemNumber}>
                        <td>
                          <p className="p-3 mb-2 bg-dark rounded" style={{ color: item.color }}>
                            <b>{item.information}</b>
                          </p>
                        </td>
                        <td>
                          <Form.Control style={textareaStyle} as="textarea" rows={3} readOnly value={item.description} />
                        </td>
                        <td>
                          <Form.Control style={textareaStyle} as="textarea" rows={3} readOnly value={item.when} />
                        </td>
                        <td>
                          <Form.Control style={textareaStyle} as="textarea" rows={3} readOnly value={item.why} />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </React.Fragment>
  );
};

export default ListTLP;
