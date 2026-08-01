import React, { forwardRef, useCallback, useEffect, useImperativeHandle, useState } from "react";
import { Badge, Button, Card, ProgressBar, Spinner } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import CrudButton from "components/Button/CrudButton";
import { getTodosByEvent, patchTodo } from "api/services/todos";
import { getTask } from "api/services/tasks";
import { getMinifiedUser } from "api/services/users";
import setAlert from "utils/setAlert";
import { currentUserHasPermissions } from "utils/permissions";
import TableTodos from "./TableTodos";

const savedValues = (todo) => ({
  completed: todo.completed,
  note: todo.note ?? "",
  assigned_to: todo.assigned_to ?? null
});

const isModified = (todo) => {
  const current = savedValues(todo);
  return current.completed !== todo.saved.completed || current.note !== todo.saved.note || current.assigned_to !== todo.saved.assigned_to;
};

/**
 * Playbook todos of an event, ordered as the playbook orders its tasks. Every
 * todo can be completed, annotated and assigned to a user.
 * The card is not rendered when the taxonomy of the event has no playbook.
 *
 * Todos are their own resource with their own permissions: editing them needs
 * change_todotask and not the right to edit the event, so the card is editable
 * wherever it is shown. Roles like Incident Responder can complete the steps of
 * a playbook without being able to edit events. Without change_todotask the
 * card stays read only instead of offering fields that could never be saved.
 *
 * They are saved on their own, but the ref exposes savePending() for the event
 * form to flush them with its own save.
 */
const SmallTodoTable = forwardRef(({ eventId }, ref) => {
  const { t } = useTranslation();
  const [todos, setTodos] = useState([]);
  const [userOptions, setUserOptions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const canEdit = currentUserHasPermissions(["change_todotask"]);

  const fetchTodos = useCallback(() => {
    if (!eventId) {
      return Promise.resolve();
    }
    setIsLoading(true);
    return (
      getTodosByEvent(eventId)
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
        // The saved values are kept to tell apart the todos really modified from
        // the ones edited back to what they already were
        .then((results) => setTodos(results.map((todo) => ({ ...todo, saved: savedValues(todo) }))))
        .catch(() => setTodos([]))
        .finally(() => setIsLoading(false))
    );
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
    setTodos((current) => current.map((todo) => (todo.url === url ? { ...todo, [field]: value } : todo)));
  };

  const modifiedTodos = todos.filter(isModified);

  const savePending = useCallback(() => {
    const pending = todos.filter(isModified);
    if (pending.length === 0) {
      return Promise.resolve();
    }
    setIsSaving(true);
    return Promise.all(
      pending.map((todo) =>
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
  }, [todos, fetchTodos, t]);

  // The save button of the event form flushes the pending todos too, so that
  // saving the event never leaves them silently behind
  useImperativeHandle(ref, () => ({ savePending, hasPendingChanges: () => modifiedTodos.length > 0 }), [savePending, modifiedTodos.length]);

  const discardChanges = () => {
    setTodos((current) => current.map((todo) => ({ ...todo, ...todo.saved })));
  };

  // The router of the app cannot block in-app navigation, but leaving the page
  // or reloading it with pending changes is warned about
  useEffect(() => {
    if (modifiedTodos.length === 0) {
      return undefined;
    }
    const warn = (event) => {
      event.preventDefault();
      event.returnValue = "";
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [modifiedTodos.length]);

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
        <div className="d-flex align-items-center flex-wrap">
          <Card.Title as="h5" className="mb-0">
            {t("ngen.todo_other")}
          </Card.Title>
          <Badge bg="secondary" className="ms-3">
            {completedCount}/{todos.length}
          </Badge>
          {modifiedTodos.length > 0 ? (
            <Badge bg="warning" text="dark" className="ms-2">
              <i className="fa fa-pen me-1" />
              {modifiedTodos.length} {t("ngen.todo.pending")}
            </Badge>
          ) : (
            ""
          )}
          {canEdit ? (
            <span className="ms-3">
              <CrudButton
                type="save"
                text={modifiedTodos.length > 0 ? `${t("crud.save")} (${modifiedTodos.length})` : t("crud.save")}
                permissions="change_todotask"
                disabled={isSaving || modifiedTodos.length === 0}
                onClick={savePending}
              />{" "}
              {/* CrudButton has no discard type, and its 'cancel' one navigates back */}
              <Button
                className="text-capitalize"
                variant="outline-secondary"
                title={t("ngen.todo.discard")}
                disabled={isSaving || modifiedTodos.length === 0}
                onClick={discardChanges}
              >
                <i className="fa fa-undo" /> {t("ngen.todo.discard")}
              </Button>
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
        <TableTodos
          todos={todos.map((todo) => ({ ...todo, modified_locally: isModified(todo) }))}
          editable={canEdit}
          userOptions={userOptions}
          onChange={handleChange}
          disabled={isSaving}
        />
      </Card.Body>
    </Card>
  );
});

SmallTodoTable.displayName = "SmallTodoTable";

export default SmallTodoTable;
