import React, { useState } from 'react';
import CrudButton from '../../../components/Button/CrudButton';
import ModalConfirm from '../../../components/Modal/ModalConfirm';
import { deleteTaxonomy } from '../../../api/services/taxonomies';
import { useTranslation, Trans } from 'react-i18next';

function ButtonDelete({ taxonomy }) {
  const [show, setShow] = useState(false);
  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  const removeTaxonomy = (taxonomy) => {
    deleteTaxonomy(taxonomy.url, taxonomy.name)
      .then(() => {

        window.location.href = '/taxonomies';
      })
      .catch((error) => {
        console.log(error)
      })
      .finally(() => {
        handleClose();
      })
  };

  return (
    <>
      <CrudButton type='delete' onClick={handleShow} />
      <ModalConfirm type='delete' component='Taxonomia' name={taxonomy.name} showModal={show} onHide={() => handleClose()} ifConfirm={() => removeTaxonomy(taxonomy)} />
    </>
  );
}

export default ButtonDelete;