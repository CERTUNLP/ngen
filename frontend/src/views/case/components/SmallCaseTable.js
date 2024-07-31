import React, { useEffect, useState } from 'react'
import { Button, Card, Col, Row } from 'react-bootstrap'
import { getCase } from '../../../api/services/cases';
import { getMinifiedPriority } from '../../../api/services/priorities';
import { getMinifiedState } from '../../../api/services/states';
import { getMinifiedTlp } from '../../../api/services/tlp';
import { getMinifiedUser } from '../../../api/services/users';
import TableCase from './TableCase'
import { useTranslation, Trans } from 'react-i18next';

const SmallCaseTable = ({ readCase, disableLink, modalCase, modalListCase, modalCaseDetail, deleteCaseFromForm, disableColumOption }) => {

    const [userNames, setUserNames] = useState({});
    const [stateNames, setStateNames] = useState({});
    const [priorityNames, setPriorityNames] = useState({});
    const [caseItem, setCaseItem] = useState([]);
    const [tlpNames, setTlpNames] = useState({});
    const { t } = useTranslation();

    useEffect(() => {

        if (readCase) {
            getCase(readCase).then((response) => {
                setCaseItem([response.data])

            })
                .catch((error) => {
                    console.log(error)
                })
        }
        if (readCase === undefined) {
            setCaseItem([])

        }

        getMinifiedTlp().then((response) => {
            let dicTlp = {};
            response.map((tlp) => {
                dicTlp[tlp.url] = { name: tlp.name, color: tlp.color };
            });
            setTlpNames(dicTlp);
        });


        getMinifiedPriority()
            .then((response) => {
                let dicPriority = {}
                response.map((priority) => {
                    dicPriority[priority.url] = priority.name
                })
                setPriorityNames(dicPriority)

            })
            .catch((error) => {
                console.log(error)
            })

        getMinifiedUser()
            .then((response) => {
                let dicUser = {}
                response.map((user) => {
                    dicUser[user.url] = user.username
                })
                setUserNames(dicUser)
            })
            .catch((error) => {
                console.log(error)
            })

        getMinifiedState()
            .then((response) => {
                let dicState = {}
                response.map((state) => {
                    dicState[state.url] = state.name
                })
                setStateNames(dicState)
            })

    }, [readCase]);

    return (
        <React.Fragment>
            <Card>
                <Card.Header>
                    <Row>

                        <Col sm={12} lg={8}>
                            <Card.Title as="h5">{t('ngen.case_one')}</Card.Title>
                        </Col>
                        {disableLink ?
                            <Col sm={12} lg={2}>
                                <Button
                                    size="lm"
                                    variant="outline-dark"
                                    onClick={() => modalCase()}
                                >
                                    {t('ngen.case.create')}
                                </Button>
                            </Col>
                            : ""
                        }
                        {disableLink ?
                            <Col sm={12} lg={2}>
                                <Button
                                    size="lm"
                                    variant="outline-dark"
                                    onClick={() => modalListCase()}
                                >
                                    {t('ngen.case_link')}
                                </Button>
                            </Col>
                            : ""
                        }


                    </Row>
                </Card.Header>
                <Card.Body>
                    <TableCase cases={caseItem} disableCheckbox={true} disableDateOrdering={true}
                        priorityNames={priorityNames} stateNames={stateNames} userNames={userNames} tlpNames={tlpNames}
                        editColum={false} deleteColum={true} deleteColumForm={true} detailModal={true}
                        navigationRow={false} selectCase={true} disableNubersOfEvents={true} modalCaseDetail={modalCaseDetail}
                        deleteCaseFromForm={deleteCaseFromForm} disableColumOption={disableColumOption} />
                </Card.Body>
            </Card>
        </React.Fragment>
    )
}

export default SmallCaseTable