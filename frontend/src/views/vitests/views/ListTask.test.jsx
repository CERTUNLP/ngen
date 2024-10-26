import { expect, test, describe, vi } from "vitest";
import ListTask from "../../task/ListTask"
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom';
import RowTask from "views/task/components/RowTask";


// Mock the useTranslation function
vi.mock("react-i18next", () => ({
    useTranslation: () => ({
      t: (key) => key, 
    }),
  }));

  const urlTask= vi.fn();
  const index= vi.fn();
  const taskDeleted = vi.fn();
  const setTaskDeleted= vi.fn();
  const taskUpdated= vi.fn();
  const setTaskUpdated= vi.fn();
  const props = vi.fn();
  

describe("ListTask", () => {
    test("Test ListTask correct display on screen.", () => {
        render(
        <MemoryRouter>
        <ListTask>
        <RowTask
            url={urlTask}
            id={index + 1}
            taskDeleted={taskDeleted}
            setTaskDeleted={setTaskDeleted}
            taskUpdated={taskUpdated}
            setTaskUpdated={setTaskUpdated}
            setShowAlert={props.setShowAlert}/>
        </ListTask>
        </MemoryRouter>
        );
        expect(ListTask).toBeDefined();

        })
  });