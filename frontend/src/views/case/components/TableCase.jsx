import React, { useEffect, useState } from "react";
import { Form, Row, Spinner, Table } from "react-bootstrap";
import CrudButton from "components/Button/CrudButton";
import { deleteCase } from "api/services/cases";
import ModalConfirm from "components/Modal/ModalConfirm";
import Ordering from "components/Ordering/Ordering";
import LetterFormat from "components/LetterFormat";
import DateShowField from "components/Field/DateShowField";
import TagContainer from "components/Badges/TagContainer";
import ListDomain from "./ListDomain";
import { useTranslation } from "react-i18next";
import UuidField from "components/Field/UuidField";
import TlpComponent from "../../tanstackquery/TlpComponent";
import PriorityComponent from "../../tanstackquery/PriorityComponent";
import StateComponent from "../../tanstackquery/StateComponent";
import EventComponent from "views/tanstackquery/EventComponent";
import TaxonomyComponent from "views/tanstackquery/TaxonomyComponent";


const TableCase = ({
  setIfModify,
  cases,
  loading,
  setLoading,
  selectedCases,
  setSelectedCases,
  setOrder,
  order,
  priorityNames,
  stateNames,
  tlpNames,
  userNames,
  editColum,
  deleteColum,
  detailModal,
  modalCaseDetail,
  navigationRow,
  selectCase,
  handleClickRadio,
  setSelectCase,
  disableCheckbox,
  disableDate,
  disableName,
  disablePriority,
  disableTlp,
  disableNubersOfEvents,
  disableColumnTag,
  deleteColumForm,
  deleteCaseFromForm,
  disableColumOption,
  disableUuid,
  disableDateModified,
  disableEvents,
  basePath = ""
}) => {
  const [url, setUrl] = useState(null);
  const [modalDelete, setModalDelete] = useState(false);
  const [id, setId] = useState(null);

  //checkbox
  const [isCheckAll, setIsCheckAll] = useState(false);
  const [showFullUuid, setShowFullUuid] = useState(false);
  const [list, setList] = useState([]);

  const { t } = useTranslation();

  //ORDER
  useEffect(() => {
    setList(cases);
  }, [cases]);

  const storageCaseUrl = (url) => {
    localStorage.removeItem("case");
    localStorage.removeItem("navigation");
    localStorage.removeItem("button return");
    localStorage.setItem("case", url);
    localStorage.setItem("navigation", navigationRow);
    localStorage.setItem("button return", navigationRow);
  };

  const handleOnClick = (url) => {
    localStorage.setItem("case", url);
    localStorage.setItem("navigation", navigationRow);
    localStorage.setItem("button return", navigationRow);
  };

  if (loading) {
    return (
      <Row className="justify-content-md-center">
        <Spinner animation="border" variant="primary" />
      </Row>
    );
  }

  //Remove Case
  const Delete = (url, id) => {
    setId(id);
    setUrl(url);
    setModalDelete(true);
  };

  const removeCase = (url) => {
    deleteCase(url)
      .then((response) => {
        setIfModify(response);
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => {
        setModalDelete(false);
      });
  };

  //Checkbox
  const handleToggleUuidDisplay = () => {
    setShowFullUuid(!showFullUuid);
  };

  const handleSelectAll = () => {
    setIsCheckAll(!isCheckAll);
    setSelectedCases(list.filter((item) => !item.blocked).map((li) => li.url));
    if (isCheckAll) {
      setSelectedCases([]);
    }
  };
  const handleClick = (e) => {
    const { id, checked } = e.target;
    setSelectedCases([...selectedCases, id]);
    if (!checked) {
      setSelectedCases(selectedCases.filter((item) => item !== id));
    }
  };

  const letterSize = { fontSize: "1.0em" };
  return (
    <React.Fragment>
      <Table responsive hover className="text-center">
        <thead>
          <tr>
            {!disableCheckbox &&
              (selectCase ? (
                <th></th>
              ) : (
                <th>
                  <Form.Group>
                    <Form.Check
                      type="checkbox"
                      id={"selectAll"}
                      onChange={handleSelectAll}
                      checked={selectedCases.length !== 0 ? selectedCases.length === list.length : false}
                      disabled={list.length === 0}
                    />
                  </Form.Group>
                </th>
              ))}
            {!disableDate && (
              <Ordering
                field="date"
                label={t("ngen.case.management_start_date")}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
                letterSize={letterSize}
              />
            )}
            {!disableDateModified && (
              <Ordering
                field="modified"
                label={t("ngen.date.modified")}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
                letterSize={letterSize}
              />
            )}
            {!disableUuid && (
              <th style={{ textAlign: "center" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <span style={{ marginRight: "8px" }}>{t("ngen.uuid")}</span>
                  <Form.Check type="checkbox" checked={showFullUuid} onChange={handleToggleUuidDisplay} />
                </div>
              </th>
            )}
            {!disableName && <th style={letterSize}> {t("ngen.name_one")} </th>}
            {!disablePriority && (
              <Ordering
                field="priority"
                label={t("ngen.priority_one")}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
                letterSize={letterSize}
              />
            )}
            {!disableTlp && <th style={letterSize}> {t("ngen.tlp")} </th>}
            <th style={letterSize}> {t("ngen.state_one")} </th>
            {!disableEvents && <th style={letterSize}> {t("ngen.event_other")} </th>}
            {!disableNubersOfEvents && <th style={letterSize}> {t("ngen.event.quantity")} </th>}
            <th style={letterSize}> {t("ngen.status.assigned")} </th>
            {!disableColumnTag && <th style={letterSize}>{t("ngen.tag_other")}</th>}
            {!disableColumOption && <th style={letterSize}> {t("ngen.action_one")} </th>}
          </tr>
        </thead>
        <tbody>
        
          {list.map((caseItem, index) => {
            if (!caseItem) {
              // fixes some rendering issues
              return null;
            }
            const parts = caseItem.url.split("/");
            let itemNumber = parts[parts.length - 2];

            return (
              <tr key={index}>
                {!disableCheckbox && (
                  <td>
                    {selectCase ? (
                      <Form.Group>
                        <Form.Check
                          type="checkbox"
                          id={caseItem.url} //Fecha de inicio de gestiónunfold_more	Nombre	Prioridadunfold_more	TLP	Estado	Asignado
                          onChange={(event) =>
                            handleClickRadio(
                              event,
                              caseItem.url,
                              caseItem.name,
                              caseItem.date,
                              priorityNames[caseItem.priority],
                              tlpNames[caseItem.tlp]?.name,
                              stateNames[caseItem.state],
                              userNames[caseItem.user_creator],
                              caseItem.events
                            )
                          }
                          checked={selectedCases.includes(caseItem.url)}
                        />
                      </Form.Group>
                    ) : (
                      <Form.Group>
                        <Form.Check
                          disabled={caseItem.blocked}
                          type="checkbox"
                          id={caseItem.url}
                          onChange={handleClick}
                          checked={selectedCases.includes(caseItem.url)}
                        />
                      </Form.Group>
                    )}
                  </td>
                )}
                {!disableDate && (
                  <td>
                    <DateShowField value={caseItem?.date} />
                  </td>
                )}

                {!disableDateModified && (
                  <td>
                    <DateShowField value={caseItem?.modified} />
                  </td>
                )}

                {!disableUuid && (
                  <td>
                    <UuidField value={caseItem.uuid} fulltext={showFullUuid} />
                  </td>
                )}

                {!disableName && <td>{caseItem.name || "-"}</td>}

                {!disablePriority && <td><PriorityComponent priority={caseItem?.priority}></PriorityComponent></td>}
                {!disableTlp && (
                  <td>
                    <TlpComponent tlp={caseItem?.tlp}></TlpComponent>
                  </td>
                )}
                <td> <StateComponent state={caseItem?.state}></StateComponent></td>
                {!disableEvents && caseItem?.events && (
                  <td>
<EventComponent event={caseItem?.events?.[0]} />
<TaxonomyComponent taxonomy={caseItem?.events?.[0]?.taxonomy || {}} />

                  </td>
                )}
                {!disableNubersOfEvents && <td>{caseItem.events_count}</td>}
                <td>{userNames[caseItem.assigned] || "-"}</td>

                {!disableColumnTag ? (
                  <td>
                    <TagContainer tags={caseItem.tags} />
                  </td>
                ) : (
                  ""
                )}

                <td>
                  {!disableColumOption && detailModal ? (
                    <CrudButton
                      type="read"
                      onClick={() =>
                        modalCaseDetail(
                          caseItem.url,
                          caseItem.name,
                          caseItem.name,
                          caseItem.date,
                          priorityNames[caseItem.priority],
                          tlpNames[caseItem.tlp]?.name,
                          stateNames[caseItem.state],
                          userNames[caseItem.user_creator]
                        )
                      }
                    />
                  ) : (
                    <CrudButton type="read" to={`${basePath}/cases/view/${itemNumber}`} />
                  )}
                  {!disableColumOption && editColum && (
                    <CrudButton type="edit" to={`${basePath}/cases/edit/${itemNumber}`} checkPermRoute />
                  )}
                  {!disableColumOption &&
                    deleteColum &&
                    (deleteColumForm ? (
                      <CrudButton type="delete" onClick={() => deleteCaseFromForm(caseItem.url)} permissions="delete_case" />
                    ) : (
                      <CrudButton type="delete" onClick={() => Delete(caseItem.url)} permissions="delete_case" />
                    ))}
                </td>
              </tr>
            );
          })}
        </tbody>
      </Table>
      <ModalConfirm
        type="delete"
        component="Caso"
        name={`${t("ngen.case_one")}${id}`}
        showModal={modalDelete}
        onHide={() => setModalDelete(false)}
        ifConfirm={() => removeCase(url)}
      />
    </React.Fragment>
  );
};

export default TableCase;
