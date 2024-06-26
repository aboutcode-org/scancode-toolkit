import { describe, it, expect } from "vitest";
import { camelCase } from "./keys";
import * as changeCase from "./index.js";

type TestCase = [
  unknown,
  number | undefined,
  unknown,
  (changeCase.Options | changeCase.PascalCaseOptions)?,
];

const TEST_CASES: TestCase[] = [
  [
    {
      first_name: "bob",
      last_name: "the builder",
      credentials: [{ built_things: true }],
    },
    Infinity,
    {
      firstName: "bob",
      lastName: "the builder",
      credentials: [{ builtThings: true }],
    },
  ],
  [
    {
      first_name: "bob",
      price: 8.21,
      favoriteAnimals: ["red", "green", 3, null, 7],
    },
    Infinity,
    {
      firstName: "bob",
      price: 8.21,
      favoriteAnimals: ["red", "green", 3, null, 7],
    },
  ],
  [
    {
      TEST_KEY: {
        FOO_BAR: true,
      },
    },
    undefined,
    {
      testKey: {
        FOO_BAR: true,
      },
    },
  ],
  [{ TEST: true }, 0, { TEST: true }],
  [null, 1, null],
  [
    {
      outer_property_1_2: "outer",
      an_array: [{ inner_property_3_4: true }],
    },
    Infinity,
    {
      outerProperty12: "outer",
      anArray: [{ innerProperty34: true }],
    },
    { mergeAmbiguousCharacters: true },
  ],
];

describe("change keys", () => {
  for (const [input, depth, result, options] of TEST_CASES) {
    it(`${input} -> ${result}`, () => {
      expect(camelCase(input, depth, options)).toEqual(result);
    });
  }
});
