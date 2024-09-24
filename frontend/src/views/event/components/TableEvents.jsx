import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Form, Row, Spinner, Table } from "react-bootstrap";
import { Link } from "react-router-dom";
import CrudButton from "../../../components/Button/CrudButton";
import ModalConfirm from "../../../components/Modal/ModalConfirm";
import { deleteEvent } from "../../../api/services/events";
import Ordering from "../../../components/Ordering/Ordering";
import LetterFormat from "../../../components/LetterFormat";
import { useTranslation } from "react-i18next";

const TableEvents = ({
  events,
  loading,
  selectedEvent,
  setSelectedEvent,
  order,
  setOrder,
  setLoading,
  taxonomyNames,
  feedNames,
  tlpNames,
  disableDate,
  disableCheckbox,
  disableDomain,
  disableCidr,
  disableTlp,
  disableColumnEdit,
  disableColumnDelete,
  disableTemplate,
  disableNubersOfEvents,
  disableCheckboxAll,
  modalEventDetail,
  formCaseCheckbok,
  detailModal,
  deleteColumForm,
  deleteEventFromForm,
  disableColumOption,
  disableColumView,
  disableUuid,
  disableMerged,
  disableDateModified,
  disableOrdering,
  disableColumnCase
}) => {
  const [deleteUrl, setDeleteUrl] = useState();
  const [remove, setRemove] = useState();
  //checkbox
  const [isCheckAll, setIsCheckAll] = useState(false);
  const [list, setList] = useState([]);
  const { t } = useTranslation();
  const navigate = useNavigate();

  if (selectedEvent === undefined) {
    selectedEvent = [];
  }

  useEffect(() => {
    setList(events);
  }, [events]);

  if (loading) {
    return (
      <Row className="justify-content-md-center">
        <Spinner animation="border" variant="primary" />
      </Row>
    );
  }

  const modalDelete = (name, url) => {
    setDeleteUrl(url);
    setRemove(true);
  };

  const handleDelete = () => {
    deleteEvent(deleteUrl)
      .then(() => {
        window.location.href = "/events";
      })
      .catch((error) => {
        console.log(error);
      });
  };

  const handleSelectAll = (e) => {
    setIsCheckAll(!isCheckAll);
    setSelectedEvent(events.filter((item) => !item.blocked).map((li) => li.url));
    if (isCheckAll) {
      setSelectedEvent([]);
    }
  };
  const handleClickFormCase = (e, date, address_value, domain, cidr, tlp, taxonomy, feed) => {
    const { id, checked } = e.target;
    setSelectedEvent([
      ...selectedEvent,
      {
        url: id,
        date: date,
        address_value: address_value,
        domain: domain,
        cidr: cidr,
        tlp: tlp,
        taxonomy: taxonomy,
        feed: feed
      }
    ]);
    if (!checked) {
      selectedEvent.filter((item) => item.url !== id);
      setSelectedEvent(selectedEvent.filter((item) => item.url !== id));
    }
  };

  const handleClick = (e) => {
    const { id, checked } = e.target;
    setSelectedEvent([...selectedEvent, id]);
    if (!checked) {
      setSelectedEvent(selectedEvent.filter((item) => item !== id));
    }
  };

  const navigateToEvent = (url) => {
    localStorage.setItem("event", url);
    navigate("/events/view");
  };

  const navigateToCase = (url) => {
    localStorage.setItem("case", url);
    navigate("/cases/view");
  };

  const letterSize = { fontSize: "1.1em" };
  return (
    <React.Fragment>
      <ul className="list-group my-4">
        <Table responsive hover className="text-center">
          <thead>
            <tr>
              {!disableCheckboxAll && !disableCheckbox && (
                <th>
                  <Form.Group>
                    <Form.Check
                      type="checkbox"
                      id={"selectAll"}
                      onChange={handleSelectAll}
                      checked={selectedEvent.length !== 0 ? isCheckAll : false}
                    />
                  </Form.Group>
                </th>
              )}

              {!disableDateModified ? (
                disableOrdering ? (
                  <th style={letterSize}>{t("ngen.event.date")} </th>
                ) : (
                  <Ordering
                    field="modified"
                    label={t("ngen.date.modified")}
                    order={order}
                    setOrder={setOrder}
                    setLoading={setLoading}
                    letterSize={letterSize}
                  />
                )
              ) : (
                ""
              )}
              {!disableDate ? (
                disableOrdering ? (
                  <th style={letterSize}>{t("ngen.event.date")} </th>
                ) : (
                  <Ordering
                    field="date"
                    label={t("ngen.event.date")}
                    order={order}
                    setOrder={setOrder}
                    setLoading={setLoading}
                    letterSize={letterSize}
                  />
                )
              ) : (
                ""
              )}
              {!disableUuid && <th style={letterSize}>{t("ngen.uuid")}</th>}
              <th style={letterSize}>{t("ngen.identifier")}</th>
              {!disableTlp && <th style={letterSize}>{t("ngen.tlp")}</th>}
              {!disableMerged && <th style={letterSize}>{t("ngen.event.merged")}</th>}
              <th style={letterSize}>{t("ngen.taxonomy_one")}</th>
              <th style={letterSize}>{t("ngen.feed.information")}</th>
              {!disableColumnCase && <th style={letterSize}>{t("ngen.case_one")}</th>}
              {!disableColumOption && <th style={letterSize}>{t("ngen.options")}</th>}
            </tr>
          </thead>
          <tbody>
            {list.map((event, index) => {
              return event ? (
                <tr key={index}>
                  {/* <td>{event.date ? event.date.slice(0, 10) + " " + event.date.slice(11, 19) : ""}</td> */}
                  {!disableCheckbox && (
                    <th>
                      {formCaseCheckbok ? (
                        <Form.Group>
                          <Form.Check
                            disabled={event.blocked}
                            type="checkbox"
                            id={event.url}
                            onChange={(e) =>
                              handleClickFormCase(
                                e,
                                event.date,
                                event.address_value,
                                event.domain,
                                event.cidr,
                                event.tlp,
                                event.taxonomy,
                                event.feed
                              )
                            }
                            checked={selectedEvent.some((eventList) => eventList.url === event.url)}
                          />
                        </Form.Group>
                      ) : (
                        <Form.Group>
                          <Form.Check
                            disabled={event.blocked}
                            type="checkbox"
                            id={event.url}
                            onChange={handleClick}
                            checked={selectedEvent.includes(event.url)}
                          />
                        </Form.Group>
                      )}
                    </th>
                  )}
                  {!disableDateModified ? <td>{event.modified.slice(0, 10) + " " + event.modified.slice(11, 19)}</td> : ""}
                  {!disableDate ? <td>{event.date ? event.date.slice(0, 10) + " " + event.date.slice(11, 19) : ""}</td> : ""}
                  {!disableUuid && <td>{event.uuid}</td>}
                  <td>{event.address_value}</td>
                  {!disableTlp && (
                    <td>
                      <LetterFormat useBadge={true} stringToDisplay={tlpNames[event.tlp].name} color={tlpNames[event.tlp].color} />
                    </td>
                  )}
                  {!disableMerged && event.parent ? (
                    <td>
                      <Link to="/events/view" state={event.parent}>
                        <Button
                          className="fa fa-eye mx-auto font-weight-light"
                          variant="outline-primary"
                          onClick={() => navigateToEvent(event.parent)}
                        >
                          {" " + t("ngen.event.parent")}
                        </Button>
                      </Link>
                    </td>
                  ) : (
                    <td>{event.children ? event.children.length : 0}</td>
                  )}

                  <td>{taxonomyNames[event.taxonomy]}</td>

                  <td>{feedNames[event.feed]}</td>

                  {!disableColumnCase ? (
                    event.case ? (
                      <td>
                        <CrudButton type="read" to="/cases/view" state={event.case} onClick={() => navigateToCase(event.case)} text={t("ngen.case_one")} />
                      </td>
                    ) : (
                      <td></td>
                    )
                  ) : (
                    ""
                  )}

                  {!disableColumOption ? (
                    <td>
                      {disableColumView ? (
                        ""
                      ) : (
                        <CrudButton type="read" to="/events/view" state={event} onClick={() => navigateToEvent(event.url)} />
                      )}
                      {disableColumOption ? (
                        ""
                      ) : disableColumnEdit ? (
                        ""
                      ) : (
                        <CrudButton type="edit" to="/events/edit" state={event} disabled={event.blocked || event.parent} />
                      )}
                      {disableColumOption ? (
                        ""
                      ) : disableColumnDelete ? (
                        ""
                      ) : deleteColumForm ? (
                        <CrudButton type="delete" onClick={() => deleteEventFromForm(event.url)} permissions="delete_event" />
                      ) : (
                        <CrudButton type="delete" onClick={() => modalDelete(event.name, event.url)} permissions="delete_event" />
                      )}
                      {disableTemplate ? "" : <CrudButton type="plus" to="/templates/create" checkPermRoute disabled={event.case} />}
                    </td>
                  ) : (
                    ""
                  )}
                </tr>
              ) : (
                <tr>
                  <td colSpan="9"></td>
                </tr>
              );
            })}
          </tbody>
        </Table>
      </ul>
      <ModalConfirm
        type="delete"
        component="Evento"
        name={`${t("ngen.event_one")}`}
        showModal={remove}
        onHide={() => setRemove(false)}
        ifConfirm={() => handleDelete(deleteUrl)}
      />
    </React.Fragment>
  );
};

export default TableEvents;
