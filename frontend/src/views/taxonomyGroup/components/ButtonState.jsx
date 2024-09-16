import React, { useState } from "react";
import ActiveButton from "../../../components/Button/ActiveButton";
import ModalConfirm from "../../../components/Modal/ModalConfirm";
import { putActivationStatus } from "../../../api/services/taxonomyGroups";
import { useTranslation } from "react-i18next";

function ButtonState({ taxonomyGroup }) {
  const { t } = useTranslation();
  const [show, setShow] = useState(false);
  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  const changeState = (taxonomyGroup) => {
    putActivationStatus(taxonomyGroup.url, !taxonomyGroup.active, taxonomyGroup.name)
      .then(() => {
        window.location.href = "/taxonomyGroups";
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => {
        handleClose();
      });
  };

  return (
    <>
      <ActiveButton active={+taxonomyGroup.active} onClick={handleShow} />
      <ModalConfirm
        type="editState"
        component={t("ngen.taxonomy_one")}
        name={taxonomyGroup.name}
        state={+taxonomyGroup.active}
        showModal={show}
        onHide={() => handleClose()}
        ifConfirm={() => changeState(taxonomyGroup)}
      />
    </>
  );
}

export default ButtonState;
