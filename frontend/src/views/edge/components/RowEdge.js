import React, { useEffect, useState } from 'react';
import ModalDetailEdge from './ModalDetailEdge';
import ModalConfirm from '../../../components/Modal/ModalConfirm';
import CrudButton from '../../../components/Button/CrudButton';
import ModalEditEdge from './ModalEditEdge';
import { deleteEdge, getEdge } from "../../../api/services/edges";
import { useTranslation } from 'react-i18next';

const RowEdge = (props) => {
  const [edge, setEdge] = useState('');

  const [modalShow, setModalShow] = useState(false)
  const [modalEdit, setModalEdit] = useState(false)
  const [modalDelete, setModalDelete] = useState(false)
  const { t } = useTranslation();

  useEffect(() => { //props.setShowAlert
    // let isMounted = true;
    showEdgeData(props.url)
    return () => {
      // isMounted = false; // Marca el componente como desmontado cuando se desmonta
    };
  }, [props.url, props.edgeDeleted, props.edgeUpdated]);

  //Read State
  const showEdgeData = (url) => {
    getEdge(url).then((response) => {
      setEdge(response.data)
    }).catch((error) => {
      console.log(error)
      props.setShowAlert(true)
    });
  }

  //Delete State
  const removeEdge = (url, name,) => {
    deleteEdge(url, name).then((response) => {
      const filteredData = props.edges.filter(item => item.url !== url);
      props.setEdges(filteredData)
      props.setEdgeDeleted(response)
    }).catch((error) => {
      console.log(error)
    }).finally(() => {
      setModalDelete(false)
      props.setShowAlert(true)
    })
  };

  return (
    edge ?
      <React.Fragment>
        <tr key={edge.url}>
          <th scope="row">{props.id}</th>
          <td>{edge.discr}</td>
          <td>{props.urlByStateName[edge.child]} </td>

          <td>
            <CrudButton type='read' onClick={() => setModalShow(true)}/>
            <CrudButton type='edit' onClick={() => setModalEdit(true)}/>
            <CrudButton type='delete' onClick={() => setModalDelete(true)}/>
          </td>
        </tr>

        <ModalDetailEdge show={modalShow} edge={edge} laterStateName={props.urlByStateName[edge.child]}
                         onHide={() => setModalShow(false)}/>
        <ModalEditEdge show={modalEdit} edge={edge} nameState={props.urlByStateName[edge.child]}
                       childrens={props.listChildren} onHide={() => setModalEdit(false)}
                       ifEdit={props.setEdgeUpdated} setShowAlert={props.setShowAlert}/>
        <ModalConfirm showModal={modalDelete} type='delete' component={t('ngen.edge_one')} name={edge.discr}
                      onHide={() => setModalDelete(false)} ifConfirm={() => removeEdge(edge.url, edge.discr)}/>

      </React.Fragment>
      :
      <></>
  );
}

export default RowEdge
