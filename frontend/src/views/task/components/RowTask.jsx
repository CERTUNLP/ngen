import React, { useCallback, useEffect, useState } from "react";
import { Form } from "react-bootstrap";
import { deleteTask, getTask } from "../../../api/services/tasks";
import PriorityButton from "../../../components/Button/PriorityButton";
import ModalDetailTask from "./ModalDetailTask";
import ModalConfirm from "../../../components/Modal/ModalConfirm";
import CrudButton from "../../../components/Button/CrudButton";
import ModalEditTask from "./ModalEditTask";

const RowTask = (props) => {
  //url, key, taskDeleted,  setTaskDeleted, setTaskUpdated, setShowAlert

  const [task, setTask] = useState("");

  const [modalShow, setModalShow] = useState(false);
  const [modalEdit, setModalEdit] = useState(false);
  const [modalDelete, setModalDelete] = useState(false);

  const [row, setRow] = useState(1); //tamano del textarea

  //Read Task
  const showTaskData = useCallback(
    (url) => {
      getTask(url)
        .then((response) => {
          setTask(response.data);
          setRow(response.data.description.length / 20);
        })
        .catch((error) => {
          console.log(error);
          props.setShowAlert(true);
        });
    },
    [props]
  );

  useEffect(() => {
    //props.setShowAlert
    showTaskData(props.url);
  }, [props.url, props.taskDeleted, props.taskUpdated, showTaskData]);

  //Delete Task
  const removeTask = (url, name) => {
    deleteTask(url, name)
      .then((response) => {
        props.setTaskDeleted(response);
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => {
        setModalDelete(false);
        props.setShowAlert(true);
      });
  };

  const textareaStyle = {
    resize: "none",
    backgroundColor: "transparent",
    border: "none",
    boxShadow: "none"
  };

  return task ? (
    <React.Fragment>
      <tr key={task.url}>
        <th scope="row">{props.id}</th>
        <td>{task.name}</td>
        <td>
          <PriorityButton url={task.priority} />
        </td>
        <td>
          <Form.Control
            readOnly
            className="text-center"
            vertical-align="middle"
            value={task.description === null ? "No tiene descripcion" : task.description}
            style={textareaStyle}
            as="textarea"
            rows={row}
          />
        </td>
        <td>
          <CrudButton type="read" onClick={() => setModalShow(true)} />
          <CrudButton type="edit" onClick={() => setModalEdit(true)} permissions="edit_task" />
          <CrudButton type="delete" onClick={() => setModalDelete(true)} permissions="delete_task" />
        </td>
      </tr>

      <ModalDetailTask show={modalShow} task={task} onHide={() => setModalShow(false)} />
      <ModalEditTask
        show={modalEdit}
        task={task}
        onHide={() => setModalEdit(false)}
        ifEdit={props.setTaskUpdated}
        setShowAlert={props.setShowAlert}
      />
      <ModalConfirm
        showModal={modalDelete}
        type="delete"
        component="Task"
        name={task.name}
        onHide={() => setModalDelete(false)}
        ifConfirm={() => removeTask(task.url, task.name)}
      />
    </React.Fragment>
  ) : (
    <></>
  );
};

export default RowTask;
