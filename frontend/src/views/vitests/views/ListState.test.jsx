import { expect, test, describe, vi } from "vitest";
import ListState from "../../state/ListState"
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom';
import TableStates from "views/state/components/TableStates";

// Mock the useTranslation function
vi.mock("react-i18next", () => ({
    useTranslation: () => ({
      t: (key) => key, 
    }),
  }));

  const states= vi.fn();
  const loading= vi.fn();
  const currentPage = vi.fn();
  

describe("ListState", () => {
    test("Test ListState correct display on screen.", () => {
        render(
        <MemoryRouter>
        <ListState>
        <TableStates 
        states={states} 
        loading={loading} 
        currentPage={currentPage}
        />
        </ListState>
        </MemoryRouter>
        );
        expect(ListState).toBeDefined();

        })
  });