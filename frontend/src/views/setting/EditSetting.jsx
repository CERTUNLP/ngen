import React, { useEffect, useState } from "react";
import { Card, Col, Form, Row, Spinner, Table } from "react-bootstrap";
import Alert from "../../components/Alert/Alert";
import { getSetting, patchSetting } from "../../api/services/setting";
import AdvancedPagination from "../../components/Pagination/AdvancedPagination";
import { useTranslation } from "react-i18next";
import CrudButton from "components/Button/CrudButton";
import PermissionCheck from "components/Auth/PermissionCheck";

const EditSetting = () => {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAlert, setShowAlert] = useState(false);
  const [ifModify, setIfModify] = useState(null);

  const [currentPage, setCurrentPage] = useState(1);
  const [countItems, setCountItems] = useState(0);
  const [updatePagination, setUpdatePagination] = useState(false);
  const [disabledPagination, setDisabledPagination] = useState(true);

  const { t, i18n } = useTranslation();

  const textareaStyle = {
    resize: "none",
    backgroundColor: "transparent",
    border: "none",
    boxShadow: "none"
  };

  useEffect(() => {
    getSetting(currentPage)
      .then((response) => {
        setList(response.data.results);
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
        setLoading(false);
      });
  }, [ifModify, currentPage]);

  function updatePage(chosenPage) {
    setCurrentPage(chosenPage);
  }

  // Function to remove a specific part of a URL
  function removePartOfURL(url) {
    // Using a regular expression to find and replace the part to remove
    var partToRemove = "/?page=" + currentPage;
    return url.replace(new RegExp(partToRemove + ".*?(/|$)"), "");
  }

  function updateConfigs(item) {
    if (item.key === "PAGE_SIZE") {
      localStorage.setItem("page_size", item.value);
    } else if (item.key === "NGEN_LANG") {
      localStorage.setItem("ngen_lang", item.value);
      i18n.changeLanguage(item.value);
    }
  }

  const PatchSetting = (url) => {
    // Aquí puedes implementar la lógica para enviar el patch request
    let item = list[list.findIndex((item) => item.url === url)];

    patchSetting(url, item.value)
      .then((response) => {
        setIfModify(response);
        updateConfigs(item);
      })
      .catch((error) => console.log(error))
      .finally(() => {
        setShowAlert(true);
      });
  };

  const completeField = (event, url) => {
    const newValue = event.target.value;
    const updatedList = list.map((item) => {
      if (item.url === url) {
        return { ...item, value: newValue };
      }
      return item;
    });
    setList(updatedList);
  };

  return (
    <div>
      <Card>
        <Card.Header>
          <Card.Title as="h5">{t("systemConfig")}</Card.Title>
        </Card.Header>
        <Card.Body>
          <ul className="list-group my-4">
            <Table responsive hover className="text-center">
              <thead>
                <tr>
                  <th>{t("ngen.name_one")}</th>
                  <th>{t("ngen.description")}</th>
                  <th>{t("ngen.default")}</th>
                  <th>{t("ngen.value")}</th>
                  <PermissionCheck permissions="change_constance">
                    <th>{t("w.modify")}</th>
                  </PermissionCheck>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan="6">
                      <Row className="justify-content-md-center">
                        <Spinner animation="border" variant="primary" />
                      </Row>
                    </td>
                  </tr>
                ) : (
                  list.map((setting, index) => (
                    <tr key={index}>
                      <td>{setting.key}</td>
                      <td>
                        <Form.Control style={textareaStyle} as="textarea" rows={3} readOnly value={setting.help_text} />
                      </td>
                      <td>{setting.default}</td>
                      <td>
                        <Form.Group controlId={`formGridAddress${index}`}>
                          <Form.Control
                            name="value"
                            value={setting.value}
                            maxLength="150"
                            placeholder={t("w.issue.placeholder")}
                            onChange={(e) => completeField(e, setting.url)}
                          />
                        </Form.Group>
                      </td>
                      <PermissionCheck permissions="change_constance">
                        <td>
                          <CrudButton type="save" variant="outline-warning" onClick={() => PatchSetting(setting.url)} text={t("button.save")} />
                        </td>
                      </PermissionCheck>
                    </tr>
                  ))
                )}
              </tbody>
            </Table>
          </ul>
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

export default EditSetting;
