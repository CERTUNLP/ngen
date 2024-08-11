import React, { useEffect, useState } from 'react';
import { Button, Modal } from 'react-bootstrap';
import { getTaxonomy } from '../../api/services/taxonomies';
import { useTranslation } from 'react-i18next';

const ModalConfirm = (props) => { // props: showModal, onHide, ifConfirm, type, component, state, name
  const [warning, setWarning] = useState('');
  const [eventOrCase, setEventOrCase] = useState('');
  const { t } = useTranslation();

  useEffect(() => {
    const eventOrCase = props.component.toLowerCase().includes("event") ? "events" : "cases";
    setEventOrCase(eventOrCase);
  }, [props.component]);

  useEffect(() => {
    if (props.type === "merge" && eventOrCase.includes("event")) {
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
            ? `(${t('ngen.warning.modal.taxonomy.domain')})`
            : diffTax
              ? `(${t('ngen.warning.modal.taxonomy')})`
              : diffDOrCidr
                ? `(${t('ngen.warning.modal.domain')})`
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
        header: `${props.component ? `${t('ngen.edit.header.of')} ${props.component}` : t('ngen.edit.header')}`,
        message: `${props.state ? `${t('ngen.edit.message.disable')} ${props.name}?` : `${t('ngen.edit.message.enable')} ${props.name}?`}`,
        variantButtonConfirm: `${props.state ? 'outline-danger' : 'outline-primary'}`,
        textButtonConfirm: `${props.state ? t('ngen.disable') : t('ngen.enable')}`
      },
    delete:
      {
        header: `${props.component ? eventOrCase.includes("event") ? t('ngen.delete.header.event') : t('ngen.delete.header.case') : t('ngen.delete')}`,
        message: `${`${t('ngen.delete.message')} ${props.name}?`}`,
        variantButtonConfirm: 'outline-danger',
        textButtonConfirm: t('ngen.delete')
      },
    merge:
      {
        header: `${props.component ? eventOrCase.includes("event") ? t('ngen.merge.header.event') : t('ngen.merge.header.case') : 'Merge'}`,
        message: eventOrCase.includes("event") ? `${t('ngen.merge.message.event')} ${warning}` : `${t('ngen.merge.message.case')} ${warning}`,
        variantButtonConfirm: 'outline-primary',
        textButtonConfirm: t('ngen.accept')
      },
  }

  return (
    <React.Fragment>
      <Modal show={props.showModal} onHide={props.onHide} aria-labelledby="contained-modal-title-vcenter"
             centered>
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

          <Button variant="outline-secondary" onClick={props.onHide}>{t('ngen.cancel')}</Button>
        </Modal.Footer>
      </Modal>
    </React.Fragment>
  );
};

export default ModalConfirm;
