import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Form } from 'react-bootstrap';
import FeedGraph from './chart/FeedGraph';
import EntityGraph from './chart/EntityGraph';
import DashboardEvent from './chart/DashboardEvent';
import DashboardCases from './chart/DashboardCases';
import { getDashboardFeed } from '../../../api/services/dashboards';
import { getDashboardEvent } from '../../../api/services/dashboards';
import { getDashboardCases } from '../../../api/services/dashboards';
import { getDashboardNetworkEntities } from '../../../api/services/dashboards';
import { getMinifiedTaxonomy } from '../../../api/services/taxonomies';
import { getMinifiedFeed } from '../../../api/services/feeds';
import { useTranslation, Trans } from 'react-i18next';


const DashDefault = () => {

    const [dashboardFeed, setDashboardFeed] = useState([]);
    const [dashboardEvent, setDashboardEvent] = useState([]);
    const [dashboardCases, setDashboardCases] = useState([]);
    const [dashboardNetworkEntities, setDashboardNetworkEntities] = useState([]);

    const [starDate, setStarDate] = useState(getDateTimeSevenDaysAgo())
    const [endDate, setEndDate] = useState(getCurrentDateTime())
    const [starDateFilter, setStarDateFilter] = useState(getDateTimeSevenDaysAgoFilter())
    const [endDateFilter, setEndDateFilter] = useState(getCurrentDateTimeFilter())
    const [starDateNotification, setStarDateNotification] = useState(false)
    const [endDateNotification, setEndDateNotification] = useState(false)

    const [taxonomyNames, setTaxonomyNames] = useState({});
    const [feedNames, setFeedNames] = useState({});


    const [loading, setLoading] = useState(true)
    useEffect(() => {
        getMinifiedTaxonomy().then((response) => {
            let dicTaxonomy = {};
            response.map((taxonomy) => {
                dicTaxonomy[taxonomy.url] = taxonomy.name;
            });
            setTaxonomyNames(dicTaxonomy);
        });
        getMinifiedFeed().then((response) => {
            let dicFeed = {};
            response.map((feed) => {
                dicFeed[feed.url] = feed.name;
            });
            setFeedNames(dicFeed);
        });


        getDashboardFeed(starDateFilter + endDateFilter)
            .then((response) => {
                setDashboardFeed(response.data.feeds_in_events)
            })
            .catch((error) => {
                // Show alert
            })
            .finally(() => {
            })

        getDashboardEvent(starDateFilter + endDateFilter)
            .then((response) => {
                setDashboardEvent(response.data.events)
            })
            .catch((error) => {
                // Show alert
            })
            .finally(() => {
            })

        getDashboardCases(starDateFilter + endDateFilter)
            .then((response) => {

                setDashboardCases(response.data.cases)
            })
            .catch((error) => {
                // Show alert
            })
            .finally(() => {
                setLoading(false)
            })

        getDashboardNetworkEntities(starDateFilter + endDateFilter)
            .then((response) => {
                let entitiesNetwork = [{
                    key: 'Cumulative Return',
                    values: []
                }]
                const entitiesWithEventCount = response.data.network_entities.map(entity => {
                    // Agregar la propiedad 'eventCount' con la cantidad de eventos

                    entity.eventCount = entity.events.length;
                    return entity;
                });
                entitiesNetwork[0].values = entitiesWithEventCount

                //console.log(entitiesWithEventCount)
                setDashboardNetworkEntities(entitiesNetwork)

            })
            .catch((error) => {
                // Show alert
            })
            .finally(() => {
                setLoading(false)
            })


    }, [starDateFilter, endDateFilter])
    const completeDateStar = (date) => {
        console.log(date)
        if (getCurrentDateTime() >= date && date <= endDate) {
            setStarDate(date)
            setStarDateFilter("date_from=" + date + ":00Z" + '&')
            setStarDateNotification(false)
        } else {
            setStarDateNotification(true)
        }
    }

    const completeDateEnd = (date) => {
        console.log(endDate)
        if (getCurrentDateTime() >= date && date >= starDate && endDate >= starDate) {
            console.log(endDate)
            console.log(endDateFilter)
            setEndDate(date)
            setEndDateFilter("date_to=" + date + ":00Z")
            setEndDateNotification(false)
        } else {
            setEndDateNotification(true)
        }
    }

    function getCurrentDateTime() {
        // Create a new Date instance to get the current date and time
        const now = new Date();

        // Get the year, month, day, hour, and minute
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0'); // Months are zero-based, so we add 1
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');

        // Format the date and time in the desired format
        const formattedDateTime = `${year}-${month}-${day}T${hours}:${minutes}`;

        return formattedDateTime;
    }

    function getDateTimeSevenDaysAgo() {
        // Create a new Date instance and set it to 7 days ago
        const now = new Date();
        now.setDate(now.getDate() - 7);

        // Get the year, month, day, hour, and minute
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0'); // Months are zero-based, so we add 1
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');

        // Format the date and time in the desired format
        const formattedDateTime = `${year}-${month}-${day}T${hours}:${minutes}`;

        return formattedDateTime;
    }
    function getCurrentDateTimeFilter() {
        // Create a new Date instance to get the current date and time
        const now = new Date();

        // Get the year, month, day, hour, minute, and second
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0'); // Months are zero-based, so we add 1
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');

        // Format the date and time in the desired format
        const formattedDateTime = `${year}-${month}-${day}T${hours}:${minutes}:${seconds}Z`;

        return "date_to=" + formattedDateTime;
    }

    function getDateTimeSevenDaysAgoFilter() {
        // Create a new Date instance to get the current date and time
        const now = new Date();

        // Subtract 7 days from the current date
        now.setDate(now.getDate() - 7);

        // Get the year, month, day, hour, minute, and second
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0'); // Months are zero-based, so we add 1
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');

        // Format the date and time in the desired format
        const formattedDateTime = `${year}-${month}-${day}T${hours}:${minutes}:${seconds}Z`;

        return "date_from=" + formattedDateTime + "&";
    }
    const { t } = useTranslation();

    return (
        <React.Fragment>
            <Row>
                <Col sm={12} lg={6}>
                    <Form.Group controlId="formGridAddress1">
                        <Form.Label>{t('date.condition_from')}</Form.Label>
                        <Form.Control
                            type="datetime-local"
                            maxLength="150"
                            placeholder={t('date.condition_from')}
                            max={getCurrentDateTime()}
                            value={starDate}
                            isInvalid={starDateNotification}
                            onChange={(e) => completeDateStar(e.target.value)}
                            name="date"
                        />
                        {starDateNotification ? <div className="invalid-feedback">{t('date.invalid')}</div> : ""}
                    </Form.Group>
                </Col>
                <Col sm={12} lg={6}>
                    <Form.Group controlId="formGridAddress1">
                        <Form.Label>{t('date.condition_to')}</Form.Label>
                        <Form.Control
                            type="datetime-local"
                            maxLength="150"
                            max={getCurrentDateTime()}
                            value={endDate}
                            isInvalid={endDateNotification}
                            onChange={(e) => completeDateEnd(e.target.value)}
                            name="date"
                        />
                        {endDateNotification ? <div className="invalid-feedback"> {t('date.invalid')}</div> : ""}
                    </Form.Group>
                </Col>
            </Row>
            <Row>
                <Col md={6}>
                    <Card>
                        <Card.Header>
                            <Card.Title as="h5">{t('feeds_graphic')}</Card.Title>
                        </Card.Header>
                        <Card.Body className="text-center">
                            <FeedGraph dashboardFeed={dashboardFeed} />
                        </Card.Body>
                    </Card>
                </Col>
                <Col md={6}>
                    <Card>
                        <Card.Header>
                            <Card.Title as="h5">{t('ngen.entity_graphic')}</Card.Title>
                        </Card.Header>
                        <Card.Body className="text-center">
                            <EntityGraph list={dashboardNetworkEntities.length > 0 ? dashboardNetworkEntities[0].values : []} />
                        </Card.Body>
                    </Card>
                </Col>
                <Col>
                    <DashboardEvent list={dashboardEvent} feedNames={feedNames} taxonomyNames={taxonomyNames} />
                </Col>
                <Col>
                    <DashboardCases list={dashboardCases} loading={loading} />
                </Col>
            </Row>
        </React.Fragment >
    );
};

export default DashDefault;
