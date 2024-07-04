import React, { useState } from 'react';
import { deleteEvidence } from '../../api/services/evidences';
import { Button, Card } from 'react-bootstrap';
import ModalConfirm from '../Modal/ModalConfirm';
import Alert from '../Alert/Alert';

// Función para obtener el ícono de acuerdo al tipo de archivo
const getFileIcon = (mimeType, fileType) => {
    const type = mimeType || fileType;
    if (type.includes('pdf')) {
        return 'fas fa-file-pdf';
    } else if (type.includes('spreadsheet') || type.includes('excel')) {
        return 'fas fa-file-excel';
    } else if (type.includes('word') || type.includes('document')) {
        return 'fas fa-file-word';
    } else if (type.includes('text')) {
        return 'fas fa-file-alt';
    } else {
        return 'fas fa-file';
    }
};

const ViewFiles = (props) => {
    const [modalDelete, setModalDelete] = useState(false);
    const [name, setName] = useState("");
    const [showAlert, setShowAlert] = useState(false)

    const openFile = () => {
        if (props.file.url) {
            window.open(props.file.file, props.index);
        }
    };

    const deleteFile = (name) => {
        setModalDelete(true);
        setName(name);
    };

    const resetShowAlert = () => {
        setShowAlert(false);
    }

    const removeCase = (file) => {
        if (file.url) {
            deleteEvidence(file.url)
                .then((response) => {
                    props.setUpdateCase(response);
                })
                .catch((error) => {
                    console.log(error);
                })
                .finally(() => {
                    setModalDelete(false);
                });
        } else {
            setModalDelete(false);
            props.removeFile(props.index);
        }
    };

    const fileIcon = getFileIcon(props.file.mime, props.file.type);

    return (
        <>
            <ModalConfirm
                type='delete'
                component='Evidencia'
                name={`La evidencia ${name}`}
                showModal={modalDelete}
                onHide={() => setModalDelete(false)}
                ifConfirm={() => removeCase(props.file)}
            />
            <Alert showAlert={showAlert} resetShowAlert={resetShowAlert} />
            <Card className="file-card">
                <Card.Body>
                    <div className="file-info">
                        <div
                            onClick={props.file.url ? openFile : null}
                            className={`file-details ${props.file.url ? '' : 'disabled'}`}
                        >
                            <i className={`${fileIcon} file-icon`}></i>
                            <div>
                                <p className="file-name">{props.file.original_filename? props.file.original_filename.slice(0, 20) + "... ":""
                                || props.file.name ? props.file.name.slice(0, 20) + "... ": ""}</p>
                                <p className="file-meta">Mime: {props.file.mime || props.file.type}</p>
                                <p className="file-meta">Tamaño: {props.file.size} KB</p>
                                <p className="file-meta">
                                    Fecha de creación: {props.file.created ? props.file.created.slice(0, 10) + " " + props.file.created.slice(11, 19) : "No creado en el sistema"}
                                </p>
                            </div>
                        </div>
                        {props.disableDelete?"":
                        <Button
                            size='sm'
                            className='btn-icon btn-rounded delete-button'
                            variant='outline-danger'
                            title={'Eliminar evidencia ' + props.index}
                            onClick={() => deleteFile(props.file.original_filename || props.file.name)}
                        >
                            <i className='fas fa-trash-alt' />
                        </Button>
                        }
                    </div>
                </Card.Body>
            </Card>
        </>
    );
};

export default ViewFiles;
