import React, { useEffect, useState } from "react";
import { Button, Card, Col, Row, Table } from "react-bootstrap";
import CrudButton from "components/Button/CrudButton";
import AdvancedPagination from "components/Pagination/AdvancedPagination";
import Search from "components/Search/Search";
import { useTranslation } from "react-i18next";
import { getTags, deleteTag } from "api/services/tags";
import CreateTagModal from "./components/CreateTagModal";
import PermissionCheck from "components/Auth/PermissionCheck";
import ModalConfirm from "components/Modal/ModalConfirm";

const ListTag = (props) => {
  const basePath = props.routeParams?.basePath ? props.routeParams?.basePath : "";

  //props setAlert

  const [tags, setTags] = useState([]);

  //Create Tag
  const [modalCreate, setModalCreate] = useState(false);
  const [value, setValue] = useState(""); //required
  const [colorTag, setColorTag] = useState("#563d7c"); //required
  const [isUpdate, setIsUpdate] = useState(false);
  const [tagUrl, setTagUrl] = useState(null);
  const { t } = useTranslation();

  const [tagCreated, setTagCreated] = useState(null);
  const [tagDeleted, setTagDeleted] = useState(null);
  const [tagUpdated, setTagUpdated] = useState(null);
  const [modalDelete, setModalDelete] = useState(false);

  //AdvancedPagination
  //filters and search
  const [currentPage, setCurrentPage] = useState(1);
  const [countItems, setCountItems] = useState(0);
  const [wordToSearch, setWordToSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [updatePagination, setUpdatePagination] = useState(false);
  const [disabledPagination, setDisabledPagination] = useState(true);
  const [order] = useState("");
  const [isModify, setIsModify] = useState(null);

  function updatePage(chosenPage) {
    setCurrentPage(chosenPage);
  }

  useEffect(() => {
    getTags(currentPage, wordToSearch, order)
      .then((response) => {
        setTags(response.data.results);
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
  }, [currentPage, wordToSearch, order, isModify, tagDeleted, tagUpdated, tagCreated]);

  const reloadPage = () => {
    setTagCreated(!tagCreated);
    setTagDeleted(!tagDeleted);
    setTagUpdated(!tagUpdated);
    setIsModify(!isModify);
  };

  const ifConfirm = (response) => {
    setModalCreate(false);
    reloadPage();
  };

  return (
    <React.Fragment>
      <Card>
        <Card.Header>
          <Row>
            <Col>
              <Search
                type={t("ngen.tag_one")}
                setWordToSearch={setWordToSearch}
                wordToSearch={wordToSearch}
                setLoading={setLoading}
                setCurrentPage={setCurrentPage}
              />
            </Col>
            <Col>
              <Button size="lm" variant="outline-primary" onClick={() => reloadPage()}>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  fill="currentColor"
                  className="bi bi-arrow-clockwise"
                  viewBox="0 0 16 16"
                >
                  <path fillRule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2z" />
                  <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466" />
                </svg>
              </Button>
              <PermissionCheck optionalPermissions={["create_tag", "create_tag_network_admin"]}>
                <Button
                  size="lm"
                  variant="outline-dark"
                  onClick={() => {
                    setValue("");
                    setColorTag("#563d7c");
                    setIsUpdate(false);
                    setModalCreate(true);
                  }}
                >
                  {t("button.create")} {t("ngen.tag_one")}
                </Button>
              </PermissionCheck>
            </Col>
          </Row>
        </Card.Header>
        <Card.Body>
          <Table responsive hover className="text-center">
            <thead>
              <tr>
                <th>{t("ngen.tag.name")}</th>
                <th>{t("ngen.tag.slug")}</th>
                <th>{t("ngen.tag.color")}</th>
                <th>{t("ngen.options")}</th>
              </tr>
            </thead>
            <tbody>
              {tags?.map((tag) => (
                <tr key={tag.url}>
                  <td>{tag.name}</td>
                  <td>{tag.slug}</td>
                  <td>
                    <div
                      style={{
                        backgroundColor: tag.color,
                        width: "20px",
                        height: "20px",
                        borderRadius: "50%",
                        display: "inline-block"
                      }}
                    ></div>
                  </td>
                  <td>
                    <CrudButton
                      type="edit"
                      onClick={() => {
                        setValue(tag.name);
                        setColorTag(tag.color);
                        setIsUpdate(true);
                        setModalCreate(true);
                        setTagUrl(tag.url);
                      }}
                    />
                    <CrudButton
                      type="delete"
                      onClick={() => {
                        setValue(tag.name);
                        setTagUrl(tag.url);
                        setModalDelete(true);
                      }}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
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

      <CreateTagModal
        show={modalCreate}
        onHide={() => setModalCreate(false)}
        value={value}
        setValue={setValue}
        colorTag={colorTag}
        setColorTag={setColorTag}
        isUpdate={isUpdate}
        url={tagUrl}
        createTag={ifConfirm}
      />

      <ModalConfirm
        type="delete"
        component="Tag"
        name={value}
        showModal={modalDelete}
        onHide={() => setModalDelete(false)}
        ifConfirm={() => {
          deleteTag(tagUrl).then(() => {
            setModalDelete(false);
            reloadPage();
          });
        }}
      />
    </React.Fragment>
  );
};

export default ListTag;
