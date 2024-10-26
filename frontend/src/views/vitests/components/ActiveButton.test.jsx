import { expect, test, describe, vi } from "vitest";
import ActiveButton from "../../../components/Button/ActiveButton";
import { render, screen } from '@testing-library/react'

vi.mock("react-i18next", () => ({
    useTranslation: () => ({
      t: (key) => key, 
    }),
  }));
  
describe("ActiveButton", () => {
    test("Test ActiveButton Component display on screen", () => {
        render( <ActiveButton>

        </ActiveButton>
        
        );
        expect(screen.ActiveButton)

        })
  });

 

