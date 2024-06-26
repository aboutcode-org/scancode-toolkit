import { describe, it, expect } from "vitest";
import { inspect } from "util";
import { titleCase, Options } from "./index.js";

/**
 * Original tests from https://github.com/gouch/to-title-case/blob/master/test/tests.json.
 */
const TEST_CASES: [string, string, Options?][] = [
  ["one two", "One Two"],
  ["one two three", "One Two Three"],
  [
    "Start a an and as at but by en for if in nor of on or per the to v vs via end",
    "Start a an and as at but by en for if in nor of on or per the to v vs via End",
  ],
  ["a small word starts", "A Small Word Starts"],
  ["small word ends on", "Small Word Ends On"],
  ["questions?", "Questions?"],
  ["Two questions?", "Two Questions?"],
  ["one sentence. two sentences.", "One Sentence. Two Sentences."],
  ["we keep NASA capitalized", "We Keep NASA Capitalized"],
  ["pass camelCase through", "Pass camelCase Through"],
  ["this sub-phrase is nice", "This Sub-Phrase Is Nice"],
  ["follow step-by-step instructions", "Follow Step-by-Step Instructions"],
  ["easy as one-two-three end", "Easy as One-Two-Three End"],
  ["start on-demand end", "Start On-Demand End"],
  ["start in-or-out end", "Start In-or-Out End"],
  ["start e-commerce end", "Start E-Commerce End"],
  ["start e-mail end", "Start E-Mail End"],
  ["your hair[cut] looks (nice)", "Your Hair[cut] Looks (Nice)"],
  ["keep that colo(u)r", "Keep that Colo(u)r"],
  ["leave Q&A unscathed", "Leave Q&A Unscathed"],
  [
    "piña colada while you listen to ænima",
    "Piña Colada While You Listen to Ænima",
  ],
  ["start title – end title", "Start Title – End Title"],
  ["start title–end title", "Start Title–End Title"],
  ["start title — end title", "Start Title — End Title"],
  ["start title—end title", "Start Title—End Title"],
  ["start title - end title", "Start Title - End Title"],
  ["don't break", "Don't Break"],
  ['"double quotes"', '"Double Quotes"'],
  ['double quotes "inner" word', 'Double Quotes "Inner" Word'],
  ["fancy double quotes “inner” word", "Fancy Double Quotes “Inner” Word"],
  ["'single quotes'", "'Single Quotes'"],
  ["single quotes 'inner' word", "Single Quotes 'Inner' Word"],
  ["fancy single quotes ‘inner’ word", "Fancy Single Quotes ‘Inner’ Word"],
  ["“‘a twice quoted subtitle’”", "“‘A Twice Quoted Subtitle’”"],
  ["have you read “The Lottery”?", "Have You Read “The Lottery”?"],
  ["one: two", "One: Two"],
  ["one two: three four", "One Two: Three Four"],
  ['one two: "Three Four"', 'One Two: "Three Four"'],
  ["one on: an end", "One On: An End"],
  ['one on: "an end"', 'One On: "An End"'],
  ["email email@example.com address", "Email email@example.com Address"],
  [
    "you have an https://example.com/ title",
    "You Have an https://example.com/ Title",
  ],
  ["_underscores around words_", "_Underscores Around Words_"],
  ["*asterisks around words*", "*Asterisks Around Words*"],
  ["this vs that", "This vs That"],
  ["this *vs* that", "This *vs* That"],
  ["this v that", "This v That"],
  // Contractions with a period are not supported due to sentence support.
  // It's difficult to tell if a period is part of a contraction or not.
  ["this vs. that", "This Vs. That"],
  ["this v. that", "This V. That"],
  ["", ""],
  [
    "Scott Moritz and TheStreet.com’s million iPhone la-la land",
    "Scott Moritz and TheStreet.com’s Million iPhone La-La Land",
  ],
  [
    "Notes and observations regarding Apple’s announcements from ‘The Beat Goes On’ special event",
    "Notes and Observations Regarding Apple’s Announcements From ‘The Beat Goes On’ Special Event",
  ],
  ["2018", "2018"],
  [
    "the quick brown fox jumps over the lazy dog",
    "The Quick Brown Fox Jumps over the Lazy Dog",
  ],
  ["newcastle upon tyne", "Newcastle upon Tyne"],
  ["newcastle *upon* tyne", "Newcastle *upon* Tyne"],
  [
    "Is human activity responsible for the climate emergency? New report calls it ‘unequivocal.’",
    "Is Human Activity Responsible for the Climate Emergency? New Report Calls It ‘Unequivocal.’",
  ],
  ["лев николаевич толстой", "Лев Николаевич Толстой"],
  ["Read foo-bar.com", "Read foo-bar.com"],
  ["cowboy bebop: the movie", "Cowboy Bebop: The Movie"],
  ["a thing. the thing. and more.", "A Thing. The Thing. And More."],
  ['"a quote." a test.', '"A Quote." A Test.'],
  ['"The U.N." a quote.', '"The U.N." A Quote.'],
  ['"The U.N.". a quote.', '"The U.N.". A Quote.'],
  ['"The U.N.". a quote.', '"The U.N.". A quote.', { sentenceCase: true }],
  ['"go without"', '"Go Without"'],
  ["the iPhone: a quote", "The iPhone: A Quote"],
  ["the iPhone: a quote", "The iPhone: a quote", { sentenceCase: true }],
  ["the U.N. and me", "The U.N. and Me"],
  ["the *U.N.* and me", "The *U.N.* and Me"],
  ["the U.N. and me", "The U.N. and me", { sentenceCase: true }],
  ["the U.N. and me", "The U.N. And Me", { smallWords: new Set() }],
  ["start-and-end", "Start-and-End"],
  ["go-to-iPhone", "Go-to-iPhone"],
  ["the go-to", "The Go-To"],
  ["the go-to", "The go-to", { sentenceCase: true }],
  ["this to-go", "This To-Go"],
  ["test(ing)", "Test(ing)"],
  ["test(s)", "Test(s)"],
  ["Keep #tag", "Keep #tag"],
  ['"Hello world", says John.', '"Hello World", Says John.'],
  [
    '"Hello world", says John.',
    '"Hello world", says John.',
    { sentenceCase: true },
  ],
  ["foo/bar", "Foo/Bar"],
  ["this is the *end.*", "This Is the *End.*"],
  ["*something about me?* and you.", "*Something About Me?* And You."],
  [
    "*something about me?* and you.",
    "*Something about me?* And you.",
    { sentenceCase: true },
  ],
  ["something about _me-too?_ and you.", "Something About _Me-Too?_ And You."],
  ["something about _me_? and you.", "Something About _Me_? And You."],
  [
    "something about _me_? and you.",
    "Something about _me_? And you.",
    { sentenceCase: true },
  ],
  [
    "something about _me-too_? and you too.",
    "Something About _Me-Too_? And You Too.",
  ],
  ["an example. i.e. test.", "An Example. I.e. Test."],
  ["an example, i.e. test.", "An Example, I.e. Test."],
  ['an example. "i.e. test."', 'An Example. "I.e. Test."'],
  ["an example. i.e. test.", "An example. I.e. test.", { sentenceCase: true }],
  ["an example, i.e. test.", "An example, i.e. test.", { sentenceCase: true }],
  [
    'an example. "i.e. test."',
    'An example. "I.e. test."',
    { sentenceCase: true },
  ],
];

describe("swap case", () => {
  for (const [input, result, options] of TEST_CASES) {
    it(`${inspect(input)} (${
      options ? JSON.stringify(options) : "null"
    }) -> ${inspect(result)}`, () => {
      expect(titleCase(input, options)).toEqual(result);
    });
  }
});
