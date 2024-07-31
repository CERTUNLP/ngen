import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Button, Card, Col, Row } from 'react-bootstrap';
import { putPlaybook } from '../../api/services/playbooks';
import FormCreatePlaybook from '../playbook/components/FormCreatePlaybook';
import { getAllTaxonomies, getMinifiedTaxonomy } from '../../api/services/taxonomies';
import ListTask from '../task/ListTask';
import Navigation from '../../components/Navigation/Navigation';
import Alert from '../../components/Alert/Alert';
import { useTranslation, Trans } from 'react-i18next';

const EditPlaybook = () => {
    const location = useLocation();
    const fromState = location.state;
    const [playbook, setPlaybook] = useState(fromState);
    const { t } = useTranslation();

    const [url, setUrl] = useState(playbook.url);
    const [name, setName] = useState(playbook.name);
    const [taxonomy, setTaxonomy] = useState(playbook.taxonomy);

    //Dropdown
    const [allTaxonomies, setAllTaxonomies] = useState([])

    //Alert
    const [showAlert, setShowAlert] = useState(false);

    useEffect(() => {
        getMinifiedTaxonomy().then((response) => {
            let listTaxonomies = []
            response.map((taxonomyItem) => {
                listTaxonomies.push({ value: taxonomyItem.url, label: taxonomyItem.name + ' (' + labelTaxonomy[taxonomyItem.type] + ')' })
            })
            setAllTaxonomies(listTaxonomies)
            })

    }, [])

    const labelTaxonomy = {
        vulnerability: 'Vulnerabilidad',
        incident: 'Incidente',
    };


    const editPlaybook = () => {
        putPlaybook(url, name, taxonomy)
            .then()
            .catch()
            .finally(() => {
                setShowAlert(true)
            })
    };

    return (
        <React.Fragment>
            <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="playbook" />
            <Row>
                <Navigation actualPosition={t('ngen.playbook.edit')} path="/playbooks" index="Playbook" />
            </Row>

            <Row>
                <Col>
                    <Card>
                        <Card.Header>
                            <Card.Title as="h5">{t('ngen.playbook')}</Card.Title>
                            <span className="d-block m-t-5">{t('ngen.playbook.edit')}</span>
                        </Card.Header>
                        <Card.Body>
                            <FormCreatePlaybook
                                name={name} setName={setName}
                                taxonomy={taxonomy} setTaxonomy={setTaxonomy}
                                ifConfirm={editPlaybook}
                                allTaxonomies={allTaxonomies}
                                save={t('button.savechanges')} />
                        </Card.Body>
                    </Card>

                    <ListTask urlPlaybook={url} sectionAddTask={true} setShowAlert={setShowAlert} />

                    <Button variant="primary" href="/playbooks">{t('button.return')}</Button>
                </Col>
            </Row>
        </React.Fragment>
    )
}

export default EditPlaybook;    
