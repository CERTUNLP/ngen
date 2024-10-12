import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import CrudButton from "../../../components/Button/CrudButton";
import ModalConfirm from "../../../components/Modal/ModalConfirm";
import { deleteTaxonomyGroup } from "../../../api/services/taxonomyGroups";

function ButtonDelete({ taxonomyGroup }) {
  const navigate = useNavigate();
  const [show, setShow] = useState(false);
  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  const removeTaxonomyGroup = (taxonomyGroup) => {
    deleteTaxonomyGroup(taxonomyGroup.url, taxonomyGroup.name)
      .then(() => {
        navigate("/taxonomyGroups");
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
      <CrudButton type="delete" onClick={handleShow} />
      <ModalConfirm
        type="delete"
        component="Taxonomy Group"
        name={taxonomyGroup.name}
        showModal={show}
        onHide={() => handleClose()}
        ifConfirm={() => removeTaxonomyGroup(taxonomyGroup)}
      />
    </>
  );
}

export default ButtonDelete;
