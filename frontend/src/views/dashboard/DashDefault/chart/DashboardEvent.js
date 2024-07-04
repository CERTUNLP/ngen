import React, { useEffect, useState } from 'react'
import {
    Card
} from 'react-bootstrap';
import { getMinifiedTaxonomy } from '../../../../api/services/taxonomies';
import { getMinifiedFeed } from '../../../../api/services/feeds';
import TableEvents from '../../../event/components/TableEvents';
import { useTranslation, Trans } from 'react-i18next';

const DashboardEvent = ({ list }) => {
    const { t } = useTranslation();

    const [taxonomyNames, setTaxonomyNames] = useState({});
    const [feedNames, setFeedNames] = useState({});


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

    }, [])
    return (
        <div>
            <Card>
                <Card.Header>
                    <Card.Title as="h5">{t('event.last10')}</Card.Title>
                </Card.Header>
                <TableEvents events={list} taxonomyNames={taxonomyNames} feedNames={feedNames} disableDateOrdering={true}
                    disableCheckbox={true} disableDomain={true} disableCidr={true} disableTlp={true} disableColumnEdit={true}
                    disableColumnDelete={true} disableTemplate={true} disableCheckboxAll={true} disableUuid={true} />
            </Card>
        </div>
    )
}

export default DashboardEvent