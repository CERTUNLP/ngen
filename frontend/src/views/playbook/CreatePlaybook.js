import React, { useState, useEffect } from 'react';
import { Button, Card, Col, Collapse, Row } from 'react-bootstrap';
import { postPlaybook, putPlaybook } from '../../api/services/playbooks';
import FormCreatePlaybook from '../playbook/components/FormCreatePlaybook';
import { getAllTaxonomies } from '../../api/services/taxonomies';
import ListTask from '../task/ListTask';
import Navigation from '../../components/Navigation/Navigation';
import Alert from '../../components/Alert/Alert';
import { useTranslation, Trans } from 'react-i18next';

const CreatePlaybook = () => {

    const [url, setUrl] = useState('');
    const [name, setName] = useState('');
    const [taxonomy, setTaxonomy] = useState([]);
    const { t } = useTranslation();

    //Renderizar
    const [allTaxonomies, setAllTaxonomies] = useState([]) //lista con formato para multiselect value, label

    //Collapse
    const [sectionAddTask, setSectionAddTask] = useState(false);

    //Alert
    const [showAlert, setShowAlert] = useState(false);

    useEffect(() => {

        getAllTaxonomies()// en TableCase
            .then((response) => {
                let listTaxonomies = []
                response.map((taxonomyItem) => {
                    listTaxonomies.push({ value: taxonomyItem.url, label: taxonomyItem.name + ' (' + labelTaxonomy[taxonomyItem.type] + ')' })
                    setAllTaxonomies(listTaxonomies)
                })
            }).catch();

    }, [sectionAddTask])

    const createPlaybook = () => {
        postPlaybook(name, taxonomy)
            .then((response) => {
                setUrl(response.data.url) // y la url
                setSectionAddTask(true)
            })
            .catch()
            .finally(() => {
                setShowAlert(true)
            })
    };

    const editPlaybook = () => {
        putPlaybook(url, name, taxonomy)
            .then()
            .catch()
            .finally(() => {
                setShowAlert(true)
            })
    };

    const labelTaxonomy = {
        vulnerability: 'Vulnerabilidad',
        incident: 'Incidente',
    };

    return (
        <React.Fragment>
            <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="playbook" />
            <Row>
                <Navigation actualPosition={t('ngen.playbook.add')} path="/playbooks" index="Playbook" />
            </Row>
            <Row>
                <Col sm={12}>
                    <Card>
                        <Card.Header>
                            <Card.Title as="h5">{t('ngen.playbook')}</Card.Title>
                            <span className="d-block m-t-5">{t('ngen.playbook.add')}</span>
                        </Card.Header>
                        <Card.Body>
                            <FormCreatePlaybook
                                name={name} setName={setName}
                                taxonomy={taxonomy} setTaxonomy={setTaxonomy}
                                ifConfirm={!sectionAddTask ? createPlaybook : editPlaybook}
                                allTaxonomies={allTaxonomies}
                                save={!sectionAddTask ? 'Crear' : 'Guardar Cambios'} />
                        </Card.Body>
                    </Card>

                    <ListTask urlPlaybook={url} sectionAddTask={sectionAddTask} setShowAlert={setShowAlert} />

                    <Button variant="primary" href="/playbooks">{t('button.return')}</Button>
                </Col>
            </Row>
        </React.Fragment>
    )
}

export default CreatePlaybook; 
