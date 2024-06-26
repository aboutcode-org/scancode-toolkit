const TOKENS = /(\S+)|(.)/g;
const IS_SPECIAL_CASE = /[\.#]\p{Alphabetic}/u; // #tag, example.com, etc.
const IS_MANUAL_CASE = /\p{Ll}(?=[\p{Lu}])/u; // iPhone, iOS, etc.
const ALPHANUMERIC_PATTERN = /\p{Alphabetic}+/gu;
const IS_ACRONYM =
  /^(\P{Alphabetic})*(?:\p{Alphabetic}\.){2,}(\P{Alphabetic})*$/u;

export const WORD_SEPARATORS = new Set(["—", "–", "-", "―", "/"]);

export const SENTENCE_TERMINATORS = new Set([".", "!", "?"]);

export const TITLE_TERMINATORS = new Set([
  ...SENTENCE_TERMINATORS,
  ":",
  '"',
  "'",
  "”",
]);

export const SMALL_WORDS = new Set([
  "a",
  "an",
  "and",
  "as",
  "at",
  "because",
  "but",
  "by",
  "en",
  "for",
  "if",
  "in",
  "neither",
  "nor",
  "of",
  "on",
  "only",
  "or",
  "over",
  "per",
  "so",
  "some",
  "than",
  "that",
  "the",
  "to",
  "up",
  "upon",
  "v",
  "versus",
  "via",
  "vs",
  "when",
  "with",
  "without",
  "yet",
]);

export interface Options {
  locale?: string | string[];
  sentenceCase?: boolean;
  sentenceTerminators?: Set<string>;
  smallWords?: Set<string>;
  titleTerminators?: Set<string>;
  wordSeparators?: Set<string>;
}

export function titleCase(
  input: string,
  options: Options | string[] | string = {},
) {
  const {
    locale = undefined,
    sentenceCase = false,
    sentenceTerminators = SENTENCE_TERMINATORS,
    titleTerminators = TITLE_TERMINATORS,
    smallWords = SMALL_WORDS,
    wordSeparators = WORD_SEPARATORS,
  } = typeof options === "string" || Array.isArray(options)
    ? { locale: options }
    : options;

  const terminators = sentenceCase ? sentenceTerminators : titleTerminators;
  let result = "";
  let isNewSentence = true;

  // tslint:disable-next-line
  for (const m of input.matchAll(TOKENS)) {
    const { 1: token, 2: whiteSpace, index = 0 } = m;

    if (whiteSpace) {
      result += whiteSpace;
      continue;
    }

    // Ignore URLs, email addresses, acronyms, etc.
    if (IS_SPECIAL_CASE.test(token)) {
      const acronym = token.match(IS_ACRONYM);

      // The period at the end of an acronym is not a new sentence,
      // but we should uppercase first for i.e., e.g., etc.
      if (acronym) {
        const [_, prefix = "", suffix = ""] = acronym;
        result +=
          sentenceCase && !isNewSentence
            ? token
            : upperAt(token, prefix.length, locale);
        isNewSentence = terminators.has(suffix.charAt(0));
        continue;
      }

      result += token;
      isNewSentence = terminators.has(token.charAt(token.length - 1));
    } else {
      const matches = Array.from(token.matchAll(ALPHANUMERIC_PATTERN));
      let value = token;
      let isSentenceEnd = false;

      for (let i = 0; i < matches.length; i++) {
        const { 0: word, index: wordIndex = 0 } = matches[i];
        const nextChar = token.charAt(wordIndex + word.length);

        isSentenceEnd = terminators.has(nextChar);

        // Always the capitalize first word and reset "new sentence".
        if (isNewSentence) {
          isNewSentence = false;
        }
        // Skip capitalizing all words if sentence case is enabled.
        else if (sentenceCase || IS_MANUAL_CASE.test(word)) {
          continue;
        }
        // Handle simple words.
        else if (matches.length === 1) {
          // Avoid capitalizing small words, except at the end of a sentence.
          if (smallWords.has(word)) {
            const isFinalToken = index + token.length === input.length;

            if (!isFinalToken && !isSentenceEnd) {
              continue;
            }
          }
        }
        // Multi-word tokens need to be parsed differently.
        else if (i > 0) {
          // Avoid capitalizing words without a valid word separator,
          // e.g. "apple's" or "test(ing)".
          if (!wordSeparators.has(token.charAt(wordIndex - 1))) {
            continue;
          }

          // Ignore small words in the middle of hyphenated words.
          if (smallWords.has(word) && wordSeparators.has(nextChar)) {
            continue;
          }
        }

        value = upperAt(value, wordIndex, locale);
      }

      result += value;
      isNewSentence =
        isSentenceEnd || terminators.has(token.charAt(token.length - 1));
    }
  }

  return result;
}

function upperAt(
  input: string,
  index: number,
  locale: string | string[] | undefined,
) {
  return (
    input.slice(0, index) +
    input.charAt(index).toLocaleUpperCase(locale) +
    input.slice(index + 1)
  );
}
