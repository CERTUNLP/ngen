import { expect, test, describe, vi } from "vitest";
import ListPriority from "../../priority/ListPriority"
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom';

// Mock the useTranslation function
vi.mock("react-i18next", () => ({
    useTranslation: () => ({
      t: (key) => key, 
    }),
  }));

    const priorities= vi.fn();
    const order= vi.fn();
    const loading= vi.fn();
    const setOrder= vi.fn();
    const setLoading= vi.fn();
    const currentPage= vi.fn();

describe("ListPriority", () => {
    test("Test ListPriority correct display on screen.", () => {
        render(
        <MemoryRouter>
        <ListPriority 
            Priorities={priorities}
            loading={loading}
            order={order}
            setOrder={setOrder}
            setLoading={setLoading}
            currentPage={currentPage}> 
        </ListPriority>
        </MemoryRouter>
        );
        expect(ListPriority).toBeDefined();

        })
  });