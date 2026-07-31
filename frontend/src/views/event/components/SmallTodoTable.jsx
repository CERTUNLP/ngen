import React, { useCallback, useEffect, useState } from "react";
import { Badge, Card, ProgressBar, Spinner } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import CrudButton from "components/Button/CrudButton";
import { getTodosByEvent, patchTodo } from "api/services/todos";
import { getTask } from "api/services/tasks";
import { getMinifiedUser } from "api/services/users";
import setAlert from "utils/setAlert";
import { currentUserHasPermissions } from "utils/permissions";
import TableTodos from "./TableTodos";

/**
 * Playbook todos of an event, ordered as the playbook orders its tasks. Read
 * only by default, editable on the event edit view: every todo can be
 * completed, annotated and assigned to a user.
 * The card is not rendered when the taxonomy of the event has no playbook.
 */
const SmallTodoTable = ({ eventId, editable = false }) => {
  const { t } = useTranslation();
  const [todos, setTodos] = useState([]);
  const [userOptions, setUserOptions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  // Without change_todotask the card stays read only instead of offering
  // fields that could never be saved
  const canEdit = editable && currentUserHasPermissions(["change_todotask"]);

  const fetchTodos = useCallback(() => {
    if (!eventId) {
      return Promise.resolve();
    }
    setIsLoading(true);
    return getTodosByEvent(eventId)
      .then((results) =>
        // Each todo only holds the url of its task, the task itself has the
        // name, description and priority to show
        Promise.all(
          results.map((todo) =>
            getTask(todo.task)
              .then((response) => ({ ...todo, task_detail: response.data }))
              .catch(() => ({ ...todo, task_detail: null }))
          )
        )
      )
      .then((results) => setTodos(results))
      .catch(() => setTodos([]))
      .finally(() => setIsLoading(false));
  }, [eventId]);

  useEffect(() => {
    fetchTodos();
  }, [fetchTodos]);

  useEffect(() => {
    if (!canEdit) {
      return;
    }
    getMinifiedUser()
      .then((response) => {
        setUserOptions(response.map((user) => ({ value: user.url, label: user.username })));
      })
      .catch((error) => {
        console.log(error);
      });
  }, [canEdit]);

  const handleChange = (url, field, value) => {
    setTodos((current) => current.map((todo) => (todo.url === url ? { ...todo, [field]: value, modified_locally: true } : todo)));
  };

  const modifiedTodos = todos.filter((todo) => todo.modified_locally);

  const handleSave = () => {
    setIsSaving(true);
    Promise.all(
      modifiedTodos.map((todo) =>
        patchTodo(todo.url, {
          completed: todo.completed,
          note: todo.note ? todo.note : null,
          assigned_to: todo.assigned_to ? todo.assigned_to : null
        })
      )
    )
      .then(() => {
        setAlert(t("ngen.todo.edit.success"), "success", "todo");
        return fetchTodos();
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => setIsSaving(false));
  };

  const completedCount = todos.filter((todo) => todo.completed).length;

  if (!eventId) {
    return null;
  }

  if (isLoading) {
    return (
      <Card>
        <Card.Body>
          <Spinner animation="border" size="sm" />
        </Card.Body>
      </Card>
    );
  }

  // Events whose taxonomy has no playbook have nothing to show here
  if (todos.length === 0) {
    return null;
  }

  return (
    <Card>
      <Card.Header>
        <div className="d-flex align-items-center">
          <Card.Title as="h5" className="mb-0">
            {t("ngen.todo_other")}
          </Card.Title>
          <Badge bg="secondary" className="ms-3">
            {completedCount}/{todos.length}
          </Badge>
          {canEdit ? (
            <span className="ms-3">
              <CrudButton
                type="save"
                text={modifiedTodos.length > 0 ? `${t("crud.save")} (${modifiedTodos.length})` : t("crud.save")}
                permissions="change_todotask"
                disabled={isSaving || modifiedTodos.length === 0}
                onClick={handleSave}
              />
            </span>
          ) : (
            ""
          )}
          {isSaving ? <Spinner animation="border" size="sm" className="ms-2" /> : ""}
        </div>
        <ProgressBar
          className="mt-2"
          style={{ height: "0.35rem" }}
          now={(completedCount * 100) / todos.length}
          aria-label={t("ngen.todo_other")}
        />
      </Card.Header>
      <Card.Body>
        <TableTodos todos={todos} editable={canEdit} userOptions={userOptions} onChange={handleChange} disabled={isSaving} />
      </Card.Body>
    </Card>
  );
};

export default SmallTodoTable;
