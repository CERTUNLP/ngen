import React, { useState, useEffect } from 'react';
import { Row, Col, Card } from 'react-bootstrap';
import { postReport } from '../../api/services/reports';
import FormReport from './components/FormReport';
import Navigation from '../../components/Navigation/Navigation';
import Alert from '../../components/Alert/Alert';
import { getAllTaxonomies, getMinifiedTaxonomy } from "../../api/services/taxonomies";
import { useTranslation, Trans } from 'react-i18next';

const CreateReport = () => {
    const [body, setBody] = useState({
        problem: "",
        derived_problem: "", //required
        verification: "",//required
        recommendations: "",//required
        more_information: "",//required
        lang: "",
        taxonomy: "-1"//required
    })
    const [taxonomies, setTaxonomies] = useState([])
    const [loading, setLoading] = useState(true)
    const { t } = useTranslation();
    //Alert
    const [showAlert, setShowAlert] = useState(false);

    useEffect(() => {
        getMinifiedTaxonomy().then((response) => {
            let listTaxonomies = []
            response.map((taxonomy) => {
                listTaxonomies.push({ value: taxonomy.url, label: taxonomy.name })
            })
            setTaxonomies(listTaxonomies)
        })
            .catch((error) => {
                console.log(error)
            }).finally(() => {
                setLoading(false)
            })

    }, []);


    //Create
    const addReport = () => {
        postReport(body.problem, body.derived_problem, body.verification, body.recommendations, body.more_information, body.lang, body.taxonomy)
            .then((response) => {
                window.location.href = "/reports"
            })
            .catch((error) => {

                setShowAlert(true)
            })
    };

    return (
        <React.Fragment>
            <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="report" />
            <Row>
                <Navigation actualPosition="Crear reporte" path="/reports" index="Reportes" />
            </Row>
            <Row>
                <Col sm={12}>
                    <Card>
                        <Card.Header>
                            <Card.Title as="h5">{t('ngen.report')}</Card.Title>
                            <span className="d-block m-t-5">{t('w.add')} {t('ngen.report')}</span>
                        </Card.Header>
                        <Card.Body>
                            <Row>
                                <Col sm={12} lg={12}>
                                    <FormReport body={body} setBody={setBody} taxonomies={taxonomies}
                                        createOrEdit={addReport} />
                                </Col>
                            </Row>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </React.Fragment>
    );
};

export default CreateReport