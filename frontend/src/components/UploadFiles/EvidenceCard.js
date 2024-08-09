import React, { useEffect } from 'react';
import { Card, Form, Row, Col } from 'react-bootstrap';
import ViewFiles from '../Button/ViewFiles';
import FileUpload from './FileUpload/FileUpload';
import './EvidenceCard.css';
import { useTranslation, Trans } from 'react-i18next';

const EvidenceCard = (props) => {
    const { t } = useTranslation();

    useEffect(() => {
    }, [props.evidences]);

    const handleDragOver = (event) => {
        event.preventDefault();
    };

    const handleDrop = (event) => {
        event.preventDefault();
        const filesToUpload = event.dataTransfer.files;
        props.setEvidences([...props.evidences, ...filesToUpload]);
    };

    const removeFile = (position) => {
        if (props.evidences.length > 0) {
            props.setEvidences(props.evidences.filter((file, index) => index !== position));
        }
    };

    return (
        <Card>
            <Card.Header>
                <Card.Title as="h5">{t('ngen.evidences')}</Card.Title>
            </Card.Header>
            <Card.Body>
                <Form>
                    {props.disableDragAndDrop ?
                        ""
                        :
                        <Form.Group controlId="Form.Case.Evidences.Drag&Drop">
                            <div
                                className="dropzone"
                                onDragOver={handleDragOver}
                                onDrop={handleDrop}
                            >
                                <FileUpload files={props.evidences} setFiles={props.setEvidences} removeFile={removeFile} />


                            </div>
                        </Form.Group>
                    }
                    <div className="evidence-container">
                        <Row>
                            {props.evidences.map((file, index) => (
                                <Col key={index} md={4} className="d-flex">
                                    <ViewFiles
                                        file={file}
                                        index={index}
                                        disableDelete={props.disableDelete}
                                        setUpdateCase={props.setUpdateCase}
                                        removeFile={removeFile}
                                    />
                                </Col>
                            ))}
                        </Row>
                    </div>
                </Form>
            </Card.Body>
        </Card>
    );
};

export default EvidenceCard;


