import React, { useState, useEffect } from 'react'
import { Table, Modal, Row, Col, Form, Spinner, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom'
import CrudButton from '../../../components/Button/CrudButton';
import ModalConfirm from '../../../components/Modal/ModalConfirm';
import { deleteEvent } from "../../../api/services/events";
import Ordering from '../../../components/Ordering/Ordering'
import LetterFormat from '../../../components/LetterFormat';
import { useTranslation, Trans } from 'react-i18next';

const TableEvents = ({ events, loading, selectedEvent, setSelectedEvent, order, setOrder, setLoading, taxonomyNames, feedNames, tlpNames, disableDateOrdering, disableCheckbox, disableDomain, disableCidr, disableTlp, disableColumnEdit, disableColumnDelete, disableTemplate, disableNubersOfEvents, disableCheckboxAll, modalEventDetail, formCaseCheckbok, detailModal, deleteColumForm, deleteEventFromForm, disableColumOption, disableUuid }) => {

    const [deleteName, setDeleteName] = useState()
    const [deleteUrl, setDeleteUrl] = useState()
    const [remove, setRemove] = useState()
    const [modalShow, setModalShow] = useState(false);
    //checkbox
    const [isCheckAll, setIsCheckAll] = useState(false);
    const [list, setList] = useState([]);
    const { t } = useTranslation();

    if (selectedEvent === undefined) {
        selectedEvent = []
    }

    useEffect(() => {
        setList(events)

    }, [events]);

    if (loading) {
        return (
            <Row className='justify-content-md-center'>
                <Spinner animation='border' variant='primary' size='sm' />
            </Row>
        );
    }

    const modalDelete = (name, url) => {
        setDeleteName(name)
        setDeleteUrl(url)
        setRemove(true)
    }

    const handleDelete = () => {
        deleteEvent(deleteUrl).then(() => {
            window.location.href = '/events';
        })
            .catch((error) => {
                console.log(error)
            })
    }

    const handleSelectAll = e => {
        setIsCheckAll(!isCheckAll);
        setSelectedEvent(events.filter(item => !item.blocked).map(li => li.url));
        if (isCheckAll) {
            setSelectedEvent([]);
        }
    };
    const handleClickFormCase = (e, date, address_value, domain, cidr, tlp, taxonomy, feed) => {
        const { id, checked } = e.target;
        console.log("handleClickFormCase")
        setSelectedEvent([...selectedEvent, { url: id, date: date, address_value: address_value, domain: domain, cidr: cidr, tlp: tlp, taxonomy: taxonomy, feed: feed }]);
        if (!checked) {
            selectedEvent.filter(item => item.url !== id)
            setSelectedEvent(selectedEvent.filter(item => item.url !== id));
        }
    };

    const handleClick = e => {
        const { id, checked } = e.target;
        setSelectedEvent([...selectedEvent, id]);
        if (!checked) {
            setSelectedEvent(selectedEvent.filter(item => item !== id));
        }
    };

    const storageEventUrl = (url) => {
        localStorage.setItem('event', url);
    };

    const letterSize = { fontSize: '1.1em' }
    return (
        <div>

            <ul className="list-group my-4">
                <Table responsive hover className="text-center">
                    <thead>
                        <tr>
                            {!disableCheckboxAll && !disableCheckbox &&
                                <th>
                                    <Form.Group>
                                        <Form.Check type="checkbox" id={"selectAll"}
                                            onChange={handleSelectAll} checked={selectedEvent.length !== 0 ? isCheckAll : false} />
                                    </Form.Group>
                                </th>}

                            {disableDateOrdering ?
                                <th style={letterSize}>{t('ngen.event_date')} </th>
                                :
                                <Ordering field="date" label={t('ngen.event_date')} order={order} setOrder={setOrder} setLoading={setLoading} letterSize={letterSize} />
                            }
                            {!disableUuid &&
                                <th style={letterSize}>{t('ngen.uuid')}</th>
                            }
                            <th style={letterSize}>{t('ngen.identifier')}</th>
                            <th style={letterSize}>{t('ngen.domain')}/{t('ngen.cidr')}</th>
                            {!disableTlp &&
                                <th style={letterSize}>{t('ngen.tlp')}</th>
                            }
                            <th style={letterSize}>{t('ngen.taxonomy_one')}</th>
                            <th style={letterSize}>{t('ngen.feed.information')}</th>
                            {!disableColumOption &&
                                <th style={letterSize}>{t('ngen.options')}</th>
                            }
                        </tr>
                    </thead>
                    <tbody>
                        {list.map((event, index) => {
                            // console.log("event", index, event);
                            // console.log(disableCheckboxAll, disableCheckbox);
                            // console.log(!disableCheckboxAll && !disableCheckbox);
                            if (event) {
                                return (
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
                                                            onChange={(e) => handleClickFormCase(
                                                                e,
                                                                event.date,
                                                                event.address_value,
                                                                event.domain,
                                                                event.cidr,
                                                                event.tlp,
                                                                event.taxonomy,
                                                                event.feed
                                                            )}
                                                            checked={selectedEvent.some(eventList => eventList.url === event.url)}
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

                                        <td>{event.date ? event.date.slice(0, 10) + " " + event.date.slice(11, 19) : ""}</td>
                                        {!disableUuid &&
                                            <td>{event.uuid}</td>
                                        }
                                        <td>{event.address_value}</td>
                                        <td>{event.domain}{event.cidr}</td>
                                        {!disableTlp &&
                                            <td>
                                                <LetterFormat useBadge={true} stringToDisplay={tlpNames[event.tlp].name} color={tlpNames[event.tlp].color} />
                                            </td>
                                        }

                                        <td>{taxonomyNames[event.taxonomy]}</td>

                                        <td>{feedNames[event.feed]}</td>

                                        <td>
                                            {disableColumOption ?
                                                ""
                                                :
                                                detailModal ?
                                                    <CrudButton type="read" onClick={() => modalEventDetail(event.url, event.date, event.address_value, event.domain,
                                                        event.cidr, event.tlp, event.taxonomy, event.feed)} />
                                                    :
                                                    <Link to={{ pathname: "/events/view", state: event }} >
                                                        <CrudButton type='read' onClick={() => storageEventUrl(event.url)} />
                                                    </Link>
                                            }
                                            {disableColumOption ?
                                                ""
                                                :
                                                !disableColumnEdit && !event.blocked ? (
                                                    <Link to={{ pathname: "/events/edit", state: event }} >
                                                        <CrudButton type='edit' />
                                                    </Link>
                                                ) : (
                                                    <CrudButton type='edit' disabled={true} />
                                                )
                                            }
                                            {disableColumOption ?
                                                ""
                                                :
                                                disableColumnDelete ? ""
                                                    :
                                                    deleteColumForm ?
                                                        <CrudButton type='delete' onClick={() => deleteEventFromForm(event.url)} />
                                                        :
                                                        <CrudButton type='delete' onClick={() => modalDelete(event.name, event.url)} />
                                            }
                                            {disableTemplate ? ""
                                                :
                                                event.case ? <Button className="btn-icon btn-rounded" disabled variant="outline-primary"
                                                    style={{
                                                        border: "1px solid #555",
                                                        borderRadius: "50px",
                                                        color: "#555",
                                                    }}
                                                    onClick={() => console.log("")}>
                                                    <i className="fa fa-plus" aria-hidden="true"></i>
                                                </Button> :
                                                    <Link to={{ pathname: "/templates/create", state: event }} >
                                                        <Button className="btn-icon btn-rounded" variant="outline-primary" onClick={() => console.log("")}>
                                                            <i className="fa fa-plus" aria-hidden="true"></i>
                                                        </Button>
                                                    </Link>}
                                        </td>
                                    </tr>
                                )
                            }
                        })}

                    </tbody>
                </Table>
            </ul>
            <ModalConfirm type='delete' component='Evento' name={"el evento"} showModal={remove} onHide={() => setRemove(false)} ifConfirm={() => handleDelete(deleteUrl)} />
        </div>
    )
}

export default TableEvents