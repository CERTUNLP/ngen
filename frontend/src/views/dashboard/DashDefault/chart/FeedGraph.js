import NVD3Chart from 'react-nvd3';
import React, { useState, useEffect } from 'react'
import { useTranslation, Trans } from 'react-i18next';

const FeedGraph = ({ dashboardFeed }) => {

    const [feed, setFeed] = useState([]);

    const filtrarEventosNoCero = (datos) => { //opino que se debe mostrar aquellas fuentes que este asociados a uno amas eventos 
        return datos.filter((objeto) => objeto.event_count !== 0);
    };

    useEffect(() => {
        setFeed(filtrarEventosNoCero(dashboardFeed))

    }, [dashboardFeed])
    const { t } = useTranslation();

    return (
        <div>
            {
                feed.length > 0 ? <NVD3Chart id="chart" height={600} type="pieChart" datum={feed} x="feed_name" y="event_count" donut labelType="percent" /> :
                    t('feeds_noEventsAssociated')

            }
        </div>
    );
}

export default FeedGraph