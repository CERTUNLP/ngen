import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Form, Button } from 'react-bootstrap';
import Select from 'react-select';
import Alert from '../../components/Alert/Alert';
import Navigation from '../../components/Navigation/Navigation'
import { validateName, validateDescription, validateType, validateUnrequiredInput } from '../../utils/validators/taxonomy';
import { postTaxonomy, getMinifiedTaxonomy } from '../../api/services/taxonomies';
import SelectLabel from '../../components/Select/SelectLabel';
import { useTranslation, Trans } from 'react-i18next';

const CreateTaxonomy = () => {
    const [type, setType] = useState("");
    const [name, setName] = useState("");
    const [description, setDescription] = useState("");
    const [parent, setParent] = useState("");
    const [taxonomies, setTaxonomies] = useState([]);
    const [showAlert, setShowAlert] = useState(false)
    const { t } = useTranslation();

    const [selectTaxonomy, setSelectTaxonomy] = useState()
    const [selectedType, setSelectedType] = useState()

    useEffect(() => {
        getMinifiedTaxonomy()
            .then((response) => {
                let listTaxonomies = []
                response.map((taxonomy) => {
                    listTaxonomies.push({ value: taxonomy.url, label: taxonomy.name })
                })
                setTaxonomies(listTaxonomies)
            })

        const handleResize = (e) => {
            e.preventDefault(); // Detiene el comportamiento predeterminado del evento de redimensionamiento
            // Tu lógica de manejo de redimensionamiento aquí (si es necesario)
        };

        // Agrega un listener de redimensionamiento cuando el componente se monta
        window.addEventListener('resize', handleResize);

        // Elimina el listener cuando el componente se desmonta
        return () => {
            console.log('desmon')
            window.removeEventListener('resize', handleResize);
        };
    }, []);



    const createTaxonomy = () => {
        let active = true
        postTaxonomy(type, name, description, active, parent)
            .then(() => {
                window.location.href = '/taxonomies';
            })
            .catch((error) => {
                console.log(error)
                setShowAlert(true)
            })
    };

    const resetShowAlert = () => {
        setShowAlert(false);
    }

    let typeOption = [
        {
            value: 'vulnerability',
            label: 'Vulnerabilidad'
        },
        {
            value: 'incident',
            label: "Incidente"
        }

    ]

    return (
        <React.Fragment>
            <Alert showAlert={showAlert} resetShowAlert={resetShowAlert} component="taxonomy" />
            <Row>
                <Navigation actualPosition="Agregar taxonomia" path="/taxonomies" index="Taxonomia" />
            </Row>
            <Row>
                <Col sm={12}>
                    <Card>
                        <Card.Header>
                            <Card.Title as="h5">{t('ngen.taxonomy_one')}</Card.Title>
                        </Card.Header>
                        <Card.Body>
                            <Form>
                                <Row>
                                    <Col sm={12} lg={4}>
                                        <Form.Group>
                                            <Form.Label>{t('ngen.name_one')} <b style={{ color: "red" }}>*</b></Form.Label>
                                            <Form.Control
                                                type="text"
                                                placeholder={t('ngen.name_one')}
                                                onChange={(e) => setName(e.target.value)}
                                                isInvalid={!validateName(name)}
                                            />
                                            {validateName(name) ? '' : <div className="invalid-feedback">{t('ngen.name.invalid')}</div>}
                                        </Form.Group>
                                    </Col>
                                    <Col sm={12} lg={4}>
                                        <SelectLabel set={setType} setSelect={setSelectedType} options={typeOption}
                                            value={selectedType} placeholder={t('ngen.type')} required={true} />
                                    </Col>
                                    <Col sm={12} lg={4}>
                                        <SelectLabel set={setParent} setSelect={setSelectTaxonomy} options={taxonomies}
                                            value={selectTaxonomy} placeholder={t('ngen.taxonomy.parent')} />
                                    </Col>
                                </Row>
                                <Row>
                                    <Col sm={12} lg={12}>
                                        <Form.Group>
                                            <Form.Label>{t('ngen.description')}</Form.Label>
                                            <Form.Control
                                                as="textarea"
                                                rows={3}
                                                placeholder={t('ngen.description')}
                                                onChange={(e) => setDescription(e.target.value)}
                                                isInvalid={(validateUnrequiredInput(description)) ? !validateDescription(description) : false}
                                            />
                                            {validateDescription(description) ? '' : <div className="invalid-feedback">{t('w.validateDesc')}</div>}
                                        </Form.Group>
                                    </Col>
                                </Row>
                                <Form.Group as={Col}>
                                    {validateType(type) && validateName(name) && name !== "" ?
                                        <Button variant="primary" onClick={createTaxonomy}>{t('button.save')}</Button>
                                        :
                                        <Button variant="primary" disabled>{t('button.save')}</Button>
                                    }
                                    <Button variant="info" href='/taxonomies'>{t('button.cancel')}</Button>
                                </Form.Group>
                            </Form>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </React.Fragment>
    );
};

export default CreateTaxonomy;
