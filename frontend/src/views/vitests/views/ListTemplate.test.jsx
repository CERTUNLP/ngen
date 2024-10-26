import { expect, test, describe, vi } from "vitest";
import ListTemplate from "../../template/ListTemplate"
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom';
import TableTemplete from "views/template/components/TableTemplete";

// Mock the useTranslation function
vi.mock("react-i18next", () => ({
    useTranslation: () => ({
      t: (key) => key, 
    }),
  }));

  const templete= vi.fn();
  const loading= vi.fn();
  const order= vi.fn();
  const setOrder = vi.fn();
  const setLoading = vi.fn();
  const currentPage = vi.fn();
  const taxonomyNames = vi.fn();
  const feedNames = vi.fn();
  const tlpNames = vi.fn();
  const priorityNames = vi.fn();
  const stateNames = vi.fn();

  

describe("ListTemplate", () => {
    test("Test ListTemplate correct display on screen.", () => {
        render(
        <MemoryRouter>
        <ListTemplate>
        <TableTemplete
                list={templete}
                loading={loading}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
                currentPage={currentPage}
                taxonomyNames={taxonomyNames}
                feedNames={feedNames}
                tlpNames={tlpNames}
                priorityNames={priorityNames}
                stateNames={stateNames}
              />
        </ListTemplate>
        </MemoryRouter>
        );
        expect(ListTemplate).toBeDefined();

        })
  });