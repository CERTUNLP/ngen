import { expect, test, describe, vi } from "vitest";
import Badge from "../../../components/Button/BadgeItem";
import { render, screen } from '@testing-library/react'

vi.mock("react-i18next", () => ({
    useTranslation: () => ({
      t: (key) => key, 
    }),
  }));
  
describe("BadgeItem", () => {
    test("Test BadgeItem Component display on screen", () => {
        render( <Badge>

        </Badge>
        
        );
        expect(screen.BadgeItem)

        })
  });

 

