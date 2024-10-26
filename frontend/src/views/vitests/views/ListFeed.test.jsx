import { expect, test, describe, vi } from "vitest";
import ListFeed from "../../feeds/ListFeed"
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom';

// Mock the useTranslation function
vi.mock("react-i18next", () => ({
    useTranslation: () => ({
      t: (key) => key, 
    }),
  }));

    const feeds= vi.fn();
    const loading= vi.fn();
    const order= vi.fn();
    const setOrder= vi.fn();
    const setLoading= vi.fn();
    const currentPage= vi.fn();

describe("ListFeed", () => {
    test("Test ListFeed correct display on screen.", () => {
        render(
        <MemoryRouter>
        <ListFeed
        feeds={feeds}
        loading={loading}
        order={order}
        setOrder={setOrder}
        setLoading={setLoading}
        currentPage={currentPage}>
        </ListFeed>
        </MemoryRouter>
        );
        expect(ListFeed).toBeDefined();

        })
  });