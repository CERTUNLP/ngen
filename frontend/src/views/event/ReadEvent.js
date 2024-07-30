import React, { useState, useEffect } from 'react'
import {
    Button, Card, Table, Row, Col, Form
} from 'react-bootstrap';
import CallBackendByName from '../../components/CallBackendByName';
import CallBackendByType from '../../components/CallBackendByType';
import { getTaxonomy } from '../../api/services/taxonomies';
import { getPriority } from '../../api/services/priorities';
import { getUser } from '../../api/services/users';
import { getTLPSpecific } from '../../api/services/tlp';
import { getFeed } from '../../api/services/feeds';
import { getEvent } from '../../api/services/events';
import { useLocation } from "react-router-dom";
import Navigation from '../../components/Navigation/Navigation'
import { getArtefact } from '../../api/services/artifact';
import ViewFiles from '../../components/Button/ViewFiles';
import SmallCaseTable from '../case/components/SmallCaseTable';
import { getEvidence } from '../../api/services/evidences';
import EvidenceCard from '../../components/UploadFiles/EvidenceCard';
import { useTranslation, Trans } from 'react-i18next';

const ReadEvent = () => {
    const location = useLocation();
    const [body, setBody] = useState({})
    const [eventItem, setEventItem] = useState(location?.state?.item || null);
    const [navigationRow, setNavigationRow] = useState(localStorage.getItem('navigation'));
    const [buttonReturn, setButtonReturn] = useState(localStorage.getItem('button return'));
    const [evidences, setEvidences] = useState([]);
    const { t } = useTranslation();


    useEffect(() => {
        console.log(body)
        if (!eventItem) {
            const event = localStorage.getItem('event');
            getEvent(event).then((responsive) => {
                setBody(responsive.data)
                setEventItem(responsive.data)
                console.log(responsive.data)
            }).catch(error => console.log(error));
        }
    }, [eventItem]);

    useEffect(() => {

        const fetchAllEvidences = async () => {
            try {
                // Esperar a que todas las promesas de getEvidence se resuelvan
                const responses = await Promise.all(eventItem.evidence.map((url) => getEvidence(url)));
                // Extraer los datos de las respuestas
                const data = responses.map(response => response.data);
                // Actualizar el estado con los datos de todas las evidencias
                setEvidences(data);

            } catch (error) {
                console.error("Error fetching evidence data:", error);
            }
        };

        // Llamar a la función para obtener los datos de las evidencias
        fetchAllEvidences();
    }, [eventItem]);

    const callbackTaxonomy = (url, setPriority) => {
        getTaxonomy(url)
            .then((response) => {
                console.log(response)
                setPriority(response.data)
            })
            .catch();
    }
    const callbackTlp = (url, setPriority) => {
        getTLPSpecific(url)
            .then((response) => {
                console.log(response)
                setPriority(response.data)
            })
            .catch();
    }
    const callbackFeed = (url, setPriority) => {
        getFeed(url)
            .then((response) => {
                console.log(response)
                setPriority(response.data)
            })
            .catch();
    }
    const callbackPriority = (url, set) => {
        getPriority(url)
            .then((response) => {
                console.log(response)
                set(response.data)
            })
            .catch();
    }
    const callbackReporter = (url, set) => {
        getUser(url)
            .then((response) => {
                console.log(response)
                set(response.data)
            })
            .catch();
    }
    const callbackArtefact = (url, set) => {
        getArtefact(url)
            .then((response) => {
                console.log(response)
                set(response.data)
            })
            .catch();
    }
    const returnBack = () => {
        window.history.back()
    }

    return (
        <div>
            {navigationRow !== "false" ?
                <Row>
                    <Navigation actualPosition={t('ngen.event.detail')} path="/events" index={t('ngen.event_one')} />
                </Row>
                : ""
            }
            <Card>
                <Card.Header>
                    <Card.Title as="h5">{t('menu.principal')}</Card.Title>
                </Card.Header>
                <Card.Body>
                    <Row>
                        <Col sm={12} lg={2}>
                            {t('date.one')}
                        </Col>
                        <Col sm={12} lg={4}>
                            <div>{body.date ? body.date.slice(0, 10) + " " + body.date.slice(11, 19) : "--"}</div>
                        </Col>
                    </Row>
                    <p />
                    <Row>
                        <Col sm={12} lg={2}>
                            {t('ngen.uuid')}
                        </Col>
                        <Col sm={12} lg={4}>
                            <div>{body.uuid}</div>
                        </Col>
                    </Row>
                    <p />
                    <Row>
                        <Col sm={12} lg={2}>
                            {t('ngen.tlp')}
                        </Col>
                        <Col sm={12} lg={4}>
                            {body.tlp !== undefined ?
                                <CallBackendByName url={body.tlp} callback={callbackTlp} /> : "-"}
                        </Col>

                    </Row>
                    <p />
                    <Row>
                        <Col sm={12} lg={2}>
                            {t('ngen.taxonomy_one')}
                        </Col>
                        <Col sm={12} lg={4}>
                            {body.taxonomy !== undefined ?
                                <CallBackendByName url={body.taxonomy} callback={callbackTaxonomy} /> : "-"}
                        </Col>

                    </Row>
                    <p />
                    <Row>
                        <Col sm={12} lg={2}>
                            {t('ngen.feed.information')}
                        </Col>
                        <Col sm={12} lg={4}>
                            {body.feed !== undefined ?
                                <CallBackendByName url={body.feed} callback={callbackFeed} /> : "-"}
                        </Col>

                    </Row>
                    <p />
                    <Row>
                        <Col sm={12} lg={2}>
                            {t('ngen.priority_one')}
                        </Col>
                        <Col sm={12} lg={4}>
                            {body.priority !== undefined ?
                                <CallBackendByName url={body.priority} callback={callbackPriority} /> : "-"}
                        </Col>

                    </Row>
                    <p />
                    <Row>
                        <Col sm={12} lg={2}>
                            {t('reporter')}
                        </Col>
                        <Col sm={12} lg={4}>
                            {body.reporter !== undefined ?
                                <CallBackendByName url={body.reporter} callback={callbackReporter} /> : "-"}
                        </Col>
                    </Row>
                    <br />
                    <Row>
                        <Col sm={12} lg={2}>
                            {t('notes')}
                        </Col>
                        <Col sm={12} lg={4}>
                            {body.notes}
                        </Col>

                    </Row>
                    {/*</Table>*/}
                </Card.Body>
            </Card>
            <Card>
                <Card.Header>
                    <Card.Title as="h5">{t('ngen.affectedResources')}</Card.Title>
                </Card.Header>
                <Card.Body>
                    <Row>
                        <p></p>

                        <Col sm={12} lg={2}>{t('ngen.domain')}</Col>
                        <p></p>

                        <Col sm={12} lg={4}> <Form.Control plaintext readOnly defaultValue={body.domain} /></Col>



                    </Row>
                    <Row>

                        <Col sm={12} lg={2}>{t('ngen.cidr')}</Col>

                        <Col sm={12} lg={4}>  <Form.Control plaintext readOnly defaultValue={body.cidr} /></Col>



                    </Row>
                </Card.Body>
            </Card>
            <SmallCaseTable readCase={body.case} disableColumOption={true} />

            <Card>
                <Card.Header>
                    <Card.Title as="h5">{t('ngen.artifact_other')}</Card.Title>
                </Card.Header>
                <Card.Body>
                    <Row>
                        {body.artifacts !== undefined ?
                            body.artifacts.map((url) => {
                                return (<CallBackendByType url={url} callback={callbackArtefact} useBadge={true} />)
                            }) : ""
                        }
                    </Row>
                </Card.Body>
            </Card>

            <EvidenceCard evidences={evidences} disableDelete={true} disableDragAndDrop={true}
            />

            <Table responsive >
                <Card>
                    <Card.Header>
                        <Card.Title as="h5">{t('ngen.evidences')}Datos adicionales</Card.Title>
                    </Card.Header>
                    <Card.Body>
                        <tr>
                            <td>{t('ngen.comments')}</td>
                            <td>
                                <Form.Control plaintext readOnly defaultValue="" />
                            </td>
                        </tr>

                        <tr>
                            <td>{t('w.creation')}</td>
                            <td>
                                <Form.Control plaintext readOnly defaultValue={body.created !== undefined ? body.created.slice(0, 10) + " " + body.date.slice(11, 19) : ""} />
                            </td>
                        </tr>
                        <tr>
                            <td>{t('w.update')}</td>
                            <td>
                                <Form.Control plaintext readOnly defaultValue={body.modified !== undefined ? body.modified.slice(0, 10) + " " + body.date.slice(11, 19) : ""} />
                            </td>
                        </tr>


                    </Card.Body>
                </Card>
                {buttonReturn !== "false" ?
                    <Button variant="primary" onClick={() => returnBack()}>{t('button.return')}</Button>
                    : ""
                }

            </Table>
        </div>
    )
}

export default ReadEvent