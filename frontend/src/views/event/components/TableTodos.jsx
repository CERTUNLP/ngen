import React from "react";
import { Form, Table } from "react-bootstrap";
import Select from "react-select";
import { useTranslation } from "react-i18next";
import DateShowField from "components/Field/DateShowField";
import PriorityComponent from "views/tanstackquery/PriorityComponent";
import UserComponent from "views/tanstackquery/UserComponent";

const TableTodos = ({ todos, editable = false, userOptions = [], onChange, disabled = false }) => {
  const { t } = useTranslation();

  return (
    <Table responsive hover>
      <thead>
        <tr>
          <th style={{ width: "3rem" }}>{t("w.done")}</th>
          <th style={{ minWidth: "20rem" }}>{t("ngen.task")}</th>
          <th style={{ minWidth: "12rem" }}>{t("ngen.todo.assigned_to")}</th>
          <th style={{ minWidth: "14rem" }}>{t("ngen.todo.note")}</th>
          <th className="text-nowrap">{t("ngen.todo.completed_date")}</th>
        </tr>
      </thead>
      <tbody>
        {todos.map((todo) => (
          <tr key={todo.url}>
            <td className="align-middle">
              <Form.Check
                type="checkbox"
                aria-label={`${t("w.done")}: ${todo.task_detail?.name ?? ""}`}
                checked={todo.completed}
                disabled={!editable || disabled}
                onChange={(event) => onChange(todo.url, "completed", event.target.checked)}
              />
            </td>
            {/* Table cells are nowrap and clipped by the theme, but the task description is
                the step the analyst has to follow, so it wraps inside a bounded width */}
            <td className="align-middle" style={{ minWidth: "20rem", whiteSpace: "normal" }}>
              <div className="d-flex align-items-center gap-2">
                {todo.modified_locally ? <i className="fa fa-pen text-warning" title={t("ngen.todo.unsaved")} /> : ""}
                <span>{todo.task_detail?.name ?? "-"}</span>
                {todo.task_detail?.priority ? <PriorityComponent priority={todo.task_detail.priority} /> : ""}
              </div>
              {todo.task_detail?.description ? (
                <div className="text-muted small" style={{ maxWidth: "26rem" }} title={todo.task_detail.description}>
                  {todo.task_detail.description}
                </div>
              ) : (
                ""
              )}
            </td>
            <td className="align-middle">
              {editable ? (
                <Select
                  classNamePrefix="react-select"
                  options={userOptions}
                  value={userOptions.find((option) => option.value === todo.assigned_to) ?? null}
                  isClearable
                  isDisabled={disabled}
                  placeholder={t("ngen.todo.assigned_to.placeholder")}
                  onChange={(option) => onChange(todo.url, "assigned_to", option ? option.value : null)}
                />
              ) : todo.assigned_to ? (
                <UserComponent user={todo.assigned_to} />
              ) : (
                "-"
              )}
            </td>
            <td className="align-middle" style={{ whiteSpace: "normal" }}>
              {editable ? (
                <Form.Control
                  as="textarea"
                  rows={2}
                  value={todo.note ?? ""}
                  disabled={disabled}
                  aria-label={`${t("ngen.todo.note")}: ${todo.task_detail?.name ?? ""}`}
                  placeholder={t("ngen.todo.note.placeholder")}
                  onChange={(event) => onChange(todo.url, "note", event.target.value)}
                />
              ) : (
                <div style={{ maxWidth: "20rem" }}>{todo.note || "-"}</div>
              )}
            </td>
            <td className="align-middle text-nowrap">
              <DateShowField value={todo.completed_date} />
            </td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
};

export default TableTodos;
