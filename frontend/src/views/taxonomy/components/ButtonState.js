import React, { useState } from 'react';
import ActiveButton from '../../../components/Button/ActiveButton';
import ModalConfirm from '../../../components/Modal/ModalConfirm';
import { putActivationStatus } from '../../../api/services/taxonomies';
import { useTranslation, Trans } from 'react-i18next';

function ButtonState({ taxonomy }) {
    const [show, setShow] = useState(false);
    const handleClose = () => setShow(false);
    const handleShow = () => setShow(true);

    const changeState = (taxonomy) => {
        putActivationStatus(taxonomy.url, !taxonomy.active, taxonomy.name).
            then(() => {
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
            <ActiveButton active={+taxonomy.active} onClick={handleShow} />
            <ModalConfirm type='editState' component='Taxonomia' name={taxonomy.name} state={+taxonomy.active} showModal={show} onHide={() => handleClose()} ifConfirm={() => changeState(taxonomy)} />
        </>
    );
}

export default ButtonState;