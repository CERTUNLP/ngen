import React, { useEffect, useState } from 'react';
import { Button, Modal } from 'react-bootstrap';
import { getTaxonomy } from '../../api/services/taxonomies';

const ModalConfirm = (props) => { // props: showModal, onHide, ifConfirm, type, component, state, name
    const [warning, setWarning] = useState('');
    const [eventOrCase, setEventOrCase] = useState('');

    useEffect(() => {
        let names = Object.values(props.name || '');
        const eventOrCase = names.some((el) => el.includes("event")) ? "eventos" : "casos";
        setEventOrCase(eventOrCase);
    }, [props.name]);

    useEffect(() => {
        if (props.type === "merge" && eventOrCase === "eventos") {
            const fetchTaxonomies = async () => {
                try {
                    let names = Object.values(props.name);
                    // Fetch event data
                    const eventData = await Promise.all(names.map(url => getTaxonomy(url.trim())));
                    const taxonomyUrls = eventData.map(event => event.data.taxonomy);
                    // Fetch Domain or Cidr data
                    const dOrCidr = eventData.map(event => event.data.domain ? event.data.domain : event.data.cidr);
                    // Fetch taxonomy data
                    const taxonomyData = await Promise.all(taxonomyUrls.map(url => getTaxonomy(url.trim())));
                    const taxonomyNames = taxonomyData.map(data => data.data.name);
                    const diffTax = (new Set(taxonomyNames).size > 1);
                    const diffDOrCidr = (new Set(dOrCidr).size > 1);
                    const warning = diffTax && diffDOrCidr 
                        ? "(Advertencia: las taxonomias y domain/cidr de los eventos son diferentes)"
                        : diffTax 
                        ? "(Advertencia: las taxonomias de los eventos son diferentes)" 
                        : diffDOrCidr 
                        ? "(Advertencia: los domain/cidr de los eventos son diferentes)" 
                        : "";
                    setWarning(warning);
                } catch (error) {
                    console.error('Error fetching taxonomies:', error);
                }
            };

            fetchTaxonomies();
        }
    }, [props.name, props.type, eventOrCase]);

    const type = {
        editState:
        {
            header: `${props.component ? `Estado de ${props.component}` : 'Estado'}`,
            message: `${props.state ? `Desea desactivar ${props.name}?` : `Desea activar ${props.name}?`}`,
            variantButtonConfirm: `${props.state ? 'outline-danger' : 'outline-primary'}`,
            textButtonConfirm: `${props.state ? 'Desactivar' : 'Activar'}`
        },
        delete:
        {
            header: `${props.component ? `Eliminar ${props.component}` : 'Eliminar'}`,
            message: `${`¿Desea eliminar ${props.name}?`}`,
            variantButtonConfirm: 'outline-danger',
            textButtonConfirm: 'Eliminar'
        },
        merge:
        {
            header: `${props.component ? `Merge de ${props.component}` : 'Merge'}`,
            message: `¿Desea mergear los ${eventOrCase} seleccionados? ${warning}`,
            variantButtonConfirm: 'outline-primary',
            textButtonConfirm: 'Aceptar'
        },
    }

    return (
        <React.Fragment>
            <Modal show={props.showModal} onHide={props.onHide} aria-labelledby="contained-modal-title-vcenter" centered>
                <Modal.Header closeButton>
                    <Modal.Title>{type[props.type].header}</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {type[props.type].message}
                </Modal.Body>
                <Modal.Footer>
                    <Button variant={type[props.type].variantButtonConfirm} onClick={props.ifConfirm}>
                        {type[props.type].textButtonConfirm}
                    </Button>

                    <Button variant="outline-secondary" onClick={props.onHide}>Cancelar</Button>
                </Modal.Footer>
            </Modal>
        </React.Fragment>
    );
};

export default ModalConfirm;