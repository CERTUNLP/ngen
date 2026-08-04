import React, { useCallback, useEffect, useState } from "react";
import { Button, Form } from "react-bootstrap";
import { deleteTask, getTask, moveTask } from "../../../api/services/tasks";
import PriorityButton from "../../../components/Button/PriorityButton";
import ModalDetailTask from "./ModalDetailTask";
import ModalConfirm from "../../../components/Modal/ModalConfirm";
import CrudButton from "../../../components/Button/CrudButton";
import ModalEditTask from "./ModalEditTask";
import { useTranslation } from "react-i18next";
import PermissionCheck from "../../../components/Auth/PermissionCheck";

const RowTask = (props) => {
  //url, key, taskDeleted,  setTaskDeleted, setTaskUpdated, setShowAlert

  const [task, setTask] = useState("");

  const [modalShow, setModalShow] = useState(false);
  const [modalEdit, setModalEdit] = useState(false);
  const [modalDelete, setModalDelete] = useState(false);

  const [row, setRow] = useState(1); //tamano del textarea
  const [isMoving, setIsMoving] = useState(false);
  const { t } = useTranslation();

  // The tasks of a playbook are the steps of a procedure, so their order is
  // edited by moving them and not by changing their priority
  const move = (direction) => {
    setIsMoving(true);
    moveTask(props.url, direction)
      .then(() => props.setTaskUpdated(Date.now()))
      .catch((error) => console.log(error))
      .finally(() => setIsMoving(false));
  };

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
          <PermissionCheck permissions={["change_task"]}>
            <Button
              className="btn-icon btn-rounded"
              variant="outline-secondary"
              title={t("ngen.task.move.up")}
              disabled={isMoving || props.isFirst}
              onClick={() => move("up")}
            >
              <i className="fa fa-arrow-up" />
            </Button>{" "}
            <Button
              className="btn-icon btn-rounded"
              variant="outline-secondary"
              title={t("ngen.task.move.down")}
              disabled={isMoving || props.isLast}
              onClick={() => move("down")}
            >
              <i className="fa fa-arrow-down" />
            </Button>{" "}
          </PermissionCheck>
          <CrudButton type="read" onClick={() => setModalShow(true)} />
          <CrudButton type="edit" onClick={() => setModalEdit(true)} permissions="change_task" />
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
