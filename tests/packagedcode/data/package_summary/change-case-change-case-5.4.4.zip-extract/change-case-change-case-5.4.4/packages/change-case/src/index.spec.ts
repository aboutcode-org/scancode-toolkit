import { describe, it, expect } from "vitest";
import {
  camelCase,
  capitalCase,
  constantCase,
  dotCase,
  kebabCase,
  noCase,
  pascalCase,
  pathCase,
  sentenceCase,
  snakeCase,
  split,
  splitSeparateNumbers,
  trainCase,
  Options,
} from "./index.js";

type Result = {
  camelCase: string;
  capitalCase: string;
  constantCase: string;
  dotCase: string;
  kebabCase: string;
  noCase: string;
  pascalCase: string;
  pascalSnakeCase: string;
  pathCase: string;
  sentenceCase: string;
  snakeCase: string;
  trainCase: string;
};

const tests: [string, Result, Options?][] = [
  [
    "",
    {
      camelCase: "",
      capitalCase: "",
      constantCase: "",
      dotCase: "",
      kebabCase: "",
      noCase: "",
      pascalCase: "",
      pascalSnakeCase: "",
      pathCase: "",
      sentenceCase: "",
      snakeCase: "",
      trainCase: "",
    },
  ],
  [
    "test",
    {
      camelCase: "test",
      capitalCase: "Test",
      constantCase: "TEST",
      dotCase: "test",
      kebabCase: "test",
      noCase: "test",
      pascalCase: "Test",
      pascalSnakeCase: "Test",
      pathCase: "test",
      sentenceCase: "Test",
      snakeCase: "test",
      trainCase: "Test",
    },
  ],
  [
    "test string",
    {
      camelCase: "testString",
      capitalCase: "Test String",
      constantCase: "TEST_STRING",
      dotCase: "test.string",
      kebabCase: "test-string",
      noCase: "test string",
      pascalCase: "TestString",
      pascalSnakeCase: "Test_String",
      pathCase: "test/string",
      sentenceCase: "Test string",
      snakeCase: "test_string",
      trainCase: "Test-String",
    },
  ],
  [
    "Test String",
    {
      camelCase: "testString",
      capitalCase: "Test String",
      constantCase: "TEST_STRING",
      dotCase: "test.string",
      kebabCase: "test-string",
      noCase: "test string",
      pascalCase: "TestString",
      pascalSnakeCase: "Test_String",
      pathCase: "test/string",
      sentenceCase: "Test string",
      snakeCase: "test_string",
      trainCase: "Test-String",
    },
  ],
  [
    "Test String",
    {
      camelCase: "test$String",
      capitalCase: "Test$String",
      constantCase: "TEST$STRING",
      dotCase: "test$string",
      kebabCase: "test$string",
      noCase: "test$string",
      pascalCase: "Test$String",
      pascalSnakeCase: "Test$String",
      pathCase: "test$string",
      sentenceCase: "Test$string",
      snakeCase: "test$string",
      trainCase: "Test$String",
    },
    {
      delimiter: "$",
    },
  ],
  [
    "TestV2",
    {
      camelCase: "testV2",
      capitalCase: "Test V2",
      constantCase: "TEST_V2",
      dotCase: "test.v2",
      kebabCase: "test-v2",
      noCase: "test v2",
      pascalCase: "TestV2",
      pascalSnakeCase: "Test_V2",
      pathCase: "test/v2",
      sentenceCase: "Test v2",
      snakeCase: "test_v2",
      trainCase: "Test-V2",
    },
  ],
  [
    "_foo_bar_",
    {
      camelCase: "fooBar",
      capitalCase: "Foo Bar",
      constantCase: "FOO_BAR",
      dotCase: "foo.bar",
      kebabCase: "foo-bar",
      noCase: "foo bar",
      pascalCase: "FooBar",
      pascalSnakeCase: "Foo_Bar",
      pathCase: "foo/bar",
      sentenceCase: "Foo bar",
      snakeCase: "foo_bar",
      trainCase: "Foo-Bar",
    },
  ],
  [
    "version 1.2.10",
    {
      camelCase: "version_1_2_10",
      capitalCase: "Version 1 2 10",
      constantCase: "VERSION_1_2_10",
      dotCase: "version.1.2.10",
      kebabCase: "version-1-2-10",
      noCase: "version 1 2 10",
      pascalCase: "Version_1_2_10",
      pascalSnakeCase: "Version_1_2_10",
      pathCase: "version/1/2/10",
      sentenceCase: "Version 1 2 10",
      snakeCase: "version_1_2_10",
      trainCase: "Version-1-2-10",
    },
  ],
  [
    "version 1.21.0",
    {
      camelCase: "version_1_21_0",
      capitalCase: "Version 1 21 0",
      constantCase: "VERSION_1_21_0",
      dotCase: "version.1.21.0",
      kebabCase: "version-1-21-0",
      noCase: "version 1 21 0",
      pascalCase: "Version_1_21_0",
      pascalSnakeCase: "Version_1_21_0",
      pathCase: "version/1/21/0",
      sentenceCase: "Version 1 21 0",
      snakeCase: "version_1_21_0",
      trainCase: "Version-1-21-0",
    },
  ],
  [
    "TestV2",
    {
      camelCase: "testV_2",
      capitalCase: "Test V 2",
      constantCase: "TEST_V_2",
      dotCase: "test.v.2",
      kebabCase: "test-v-2",
      noCase: "test v 2",
      pascalCase: "TestV_2",
      pascalSnakeCase: "Test_V_2",
      pathCase: "test/v/2",
      sentenceCase: "Test v 2",
      snakeCase: "test_v_2",
      trainCase: "Test-V-2",
    },
    {
      separateNumbers: true,
    },
  ],
  [
    "𝒳123",
    {
      camelCase: "𝒳_123",
      capitalCase: "𝒳 123",
      constantCase: "𝒳_123",
      dotCase: "𝒳.123",
      kebabCase: "𝒳-123",
      noCase: "𝒳 123",
      pascalCase: "𝒳_123",
      pascalSnakeCase: "𝒳_123",
      pathCase: "𝒳/123",
      sentenceCase: "𝒳 123",
      snakeCase: "𝒳_123",
      trainCase: "𝒳-123",
    },
    {
      separateNumbers: true,
    },
  ],
  [
    "1test",
    {
      camelCase: "1Test",
      capitalCase: "1 Test",
      constantCase: "1_TEST",
      dotCase: "1.test",
      kebabCase: "1-test",
      noCase: "1 test",
      pascalCase: "1Test",
      pascalSnakeCase: "1_Test",
      pathCase: "1/test",
      sentenceCase: "1 test",
      snakeCase: "1_test",
      trainCase: "1-Test",
    },
    { separateNumbers: true },
  ],
  [
    "Foo12019Bar",
    {
      camelCase: "foo_12019Bar",
      capitalCase: "Foo 12019 Bar",
      constantCase: "FOO_12019_BAR",
      dotCase: "foo.12019.bar",
      kebabCase: "foo-12019-bar",
      noCase: "foo 12019 bar",
      pascalCase: "Foo_12019Bar",
      pascalSnakeCase: "Foo_12019_Bar",
      pathCase: "foo/12019/bar",
      sentenceCase: "Foo 12019 bar",
      snakeCase: "foo_12019_bar",
      trainCase: "Foo-12019-Bar",
    },
    { separateNumbers: true },
  ],
  [
    "aNumber2in",
    {
      camelCase: "aNumber_2In",
      capitalCase: "A Number 2 In",
      constantCase: "A_NUMBER_2_IN",
      dotCase: "a.number.2.in",
      kebabCase: "a-number-2-in",
      noCase: "a number 2 in",
      pascalCase: "ANumber_2In",
      pascalSnakeCase: "ANumber_2_In",
      pathCase: "a/number/2/in",
      sentenceCase: "A number 2 in",
      snakeCase: "a_number_2_in",
      trainCase: "A-Number-2-In",
    },
    { separateNumbers: true },
  ],
  [
    "V1Test",
    {
      camelCase: "v1Test",
      capitalCase: "V1 Test",
      constantCase: "V1_TEST",
      dotCase: "v1.test",
      kebabCase: "v1-test",
      noCase: "v1 test",
      pascalCase: "V1Test",
      pascalSnakeCase: "V1_Test",
      pathCase: "v1/test",
      sentenceCase: "V1 test",
      snakeCase: "v1_test",
      trainCase: "V1-Test",
    },
  ],
  [
    "V1Test with separateNumbers",
    {
      camelCase: "v_1TestWithSeparateNumbers",
      capitalCase: "V 1 Test With Separate Numbers",
      constantCase: "V_1_TEST_WITH_SEPARATE_NUMBERS",
      dotCase: "v.1.test.with.separate.numbers",
      kebabCase: "v-1-test-with-separate-numbers",
      noCase: "v 1 test with separate numbers",
      pascalCase: "V_1TestWithSeparateNumbers",
      pascalSnakeCase: "V_1_Test_With_Separate_Numbers",
      pathCase: "v/1/test/with/separate/numbers",
      sentenceCase: "V 1 test with separate numbers",
      snakeCase: "v_1_test_with_separate_numbers",
      trainCase: "V-1-Test-With-Separate-Numbers",
    },
    { separateNumbers: true },
  ],
  [
    "__typename",
    {
      camelCase: "__typename",
      capitalCase: "__Typename",
      constantCase: "__TYPENAME",
      dotCase: "__typename",
      kebabCase: "__typename",
      noCase: "__typename",
      pascalCase: "__Typename",
      pascalSnakeCase: "__Typename",
      pathCase: "__typename",
      sentenceCase: "__Typename",
      snakeCase: "__typename",
      trainCase: "__Typename",
    },
    {
      prefixCharacters: "_$",
    },
  ],
  [
    "type__",
    {
      camelCase: "type__",
      capitalCase: "Type__",
      constantCase: "TYPE__",
      dotCase: "type__",
      kebabCase: "type__",
      noCase: "type__",
      pascalCase: "Type__",
      pascalSnakeCase: "Type__",
      pathCase: "type__",
      sentenceCase: "Type__",
      snakeCase: "type__",
      trainCase: "Type__",
    },
    {
      suffixCharacters: "_$",
    },
  ],
  [
    "__type__",
    {
      camelCase: "__type__",
      capitalCase: "__Type__",
      constantCase: "__TYPE__",
      dotCase: "__type__",
      kebabCase: "__type__",
      noCase: "__type__",
      pascalCase: "__Type__",
      pascalSnakeCase: "__Type__",
      pathCase: "__type__",
      sentenceCase: "__Type__",
      snakeCase: "__type__",
      trainCase: "__Type__",
    },
    {
      prefixCharacters: "_",
      suffixCharacters: "_",
    },
  ],
];

describe("change case", () => {
  for (const [input, result, options] of tests) {
    it(input, () => {
      expect(camelCase(input, options)).toEqual(result.camelCase);
      expect(capitalCase(input, options)).toEqual(result.capitalCase);
      expect(constantCase(input, options)).toEqual(result.constantCase);
      expect(dotCase(input, options)).toEqual(result.dotCase);
      expect(trainCase(input, options)).toEqual(result.trainCase);
      expect(kebabCase(input, options)).toEqual(result.kebabCase);
      expect(noCase(input, options)).toEqual(result.noCase);
      expect(pascalCase(input, options)).toEqual(result.pascalCase);
      expect(pathCase(input, options)).toEqual(result.pathCase);
      expect(sentenceCase(input, options)).toEqual(result.sentenceCase);
      expect(snakeCase(input, options)).toEqual(result.snakeCase);
    });
  }

  describe("split", () => {
    it("should split an empty string", () => {
      expect(split("")).toEqual([]);
    });
  });

  describe("pascal case merge option", () => {
    it("should merge numbers", () => {
      const input = "version 1.2.10";

      expect(camelCase(input, { mergeAmbiguousCharacters: true })).toEqual(
        "version1210",
      );
      expect(pascalCase(input, { mergeAmbiguousCharacters: true })).toEqual(
        "Version1210",
      );
    });
  });
});
